# The MIT License (MIT)
# Copyright (c) 2026 - Universidad del Cauca, Juan Ruiz-Rosero
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

"""Co-occurrence network maps (VOSviewer-style) for ScientoPy.

Pipeline:

1. Read the preprocessed corpus (or the last analysis subset) and keep the
   documents inside the year range.
2. Split the chosen criterion (keywords, authors, countries, ...) into items,
   pick the top items by occurrences and count how often every pair of items
   appears in the same document (full or fractional counting).
3. Normalize the co-occurrence counts with the association strength, the same
   similarity measure VOSviewer uses by default.
4. Cluster the items by optimizing the VOSviewer quality function
   sum(s_ij - resolution) over pairs in the same cluster (Louvain moves with
   several random starts) and merge clusters below the minimum size.
5. Lay out the items with the VOS mapping technique (minimize the weighted
   sum of squared distances, keeping the average distance fixed) in 3D and 2D,
   with an optional extra attraction inside clusters (cohesion).
6. Write a self-contained interactive HTML viewer plus data exports
   (JSON, CSV, GEXF and VOSviewer map/network files).

The same clusters feed the thematic map (strategic diagram): every cluster is
a theme, placed by its Callon centrality and density (see thematic_map).

No network access is needed to build or view the map: the HTML file embeds
its scripts, styles and data.
"""

import csv
import datetime
import heapq
import json
import os
import sys
from collections import Counter, defaultdict
from xml.sax.saxutils import escape as xml_escape

import numpy as np

import globalVar


class NetworkError(Exception):
    pass


class NetworkCanceled(NetworkError):
    pass


# Default parameters (also used to build the reproducible CLI command)
DEFAULT_LENGTH = 300
DEFAULT_MIN_OCCURRENCES = 2
DEFAULT_RESOLUTION = 1.0
DEFAULT_MIN_CLUSTER_SIZE = 3
DEFAULT_MIN_LINK_STRENGTH = 0
DEFAULT_COUNTING = "full"
DEFAULT_WINDOW_WIDTH = 2
DEFAULT_TOP_PAPERS = 3
DEFAULT_COHESION = 0.5
DEFAULT_THEME_LABELS = 3
MAX_LENGTH = 2000

THEMATIC_AXES = ["rank", "value"]
THEME_MOTOR = "Motor theme"
THEME_NICHE = "Niche theme"
THEME_EMERGING = "Emerging or declining theme"
THEME_BASIC = "Basic theme"

COUNTING_METHODS = ["full", "fractional"]

# Neon palette tuned for the dark viewer; cycled for more than 12 clusters.
CLUSTER_COLORS = [
    "#ff4f9a", "#36d6e7", "#ffd166", "#7cf29c", "#a98bff", "#ff8c42",
    "#5ab0ff", "#c6f36b", "#ff6b6b", "#3ef0c8", "#e879f9", "#9fb3c8",
]

CRITERION_LABELS = {
    "authorKeywords": "Author keywords",
    "indexKeywords": "Index keywords",
    "bothKeywords": "Author + index keywords",
    "author": "Authors",
    "country": "Countries",
    "institution": "Institutions",
    "institutionWithCountry": "Institutions",
    "subject": "Subject areas",
}

VIEWER_DIR = "networkViewer"
VIEWER_JS_FILES = [
    "util.js", "data.js", "camera.js", "renderer.js", "spider.js",
    "overlay.js", "hud.js", "export.js", "main.js",
]


def _viewer_path(filename):
    """Resolve a viewer asset for both PyInstaller bundles and source mode."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, VIEWER_DIR, filename)


def _progress(text, per):
    globalVar.progressText = text
    globalVar.progressPer = per
    if globalVar.cancelProcess:
        raise NetworkCanceled("Canceled")


def _criterion_file_name(criterion):
    return criterion[0].upper() + criterion[1:]


# ── Loading ─────────────────────────────────────────────────────────────────

def load_papers(previous_results=False):
    """Load the preprocessed corpus, or the last analysis subset."""
    # Imported here so the GUI can import this module without loading polars
    import paperIO
    import paperUtils

    if previous_results:
        path = os.path.join(globalVar.RESULTS_FOLDER, globalVar.LAST_ANALYSIS_FILE)
        if not os.path.isfile(path):
            raise NetworkError(
                "File not found: %s\nRun an analysis first to use previous results." % path)
        papers = paperIO.read_preprocessed(path)
        return paperUtils.removeDuplicates(papers)

    path = os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_PARQUET)
    if os.path.isfile(path):
        return paperIO.read_preprocessed(path)

    legacy = os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_NAME)
    if os.path.isfile(legacy):
        papers = []
        with open(legacy, "r", encoding="utf-8") as ifile:
            paperUtils.openFileToDict(ifile, papers)
        return papers

    raise NetworkError(
        "File not found: %s\nMake sure you have run the preprocess step first." % path)


def parse_synonyms(spec):
    """Synonym groups as {UPPER_VARIANT: canonical label}.

    spec is either ScientoPy topic-group syntax, "internet of things, iot;
    bluetooth low energy, ble" (the first item of each group names it), or the
    path of a VOSviewer thesaurus file: tab separated "label<TAB>replace by"
    lines with a header. An empty "replace by" leaves the item out, as in
    VOSviewer.
    """
    mapping = {}
    if not spec or not spec.strip():
        return mapping
    if os.path.isfile(spec):
        with open(spec, "r", encoding="utf-8-sig") as f:
            for k, line in enumerate(f):
                parts = line.rstrip("\r\n").split("\t")
                if k == 0 and parts[0].strip().lower() == "label":
                    continue
                if len(parts) < 2 or not parts[0].strip():
                    continue
                mapping[parts[0].strip().upper()] = parts[1].strip()
        return mapping
    for group in spec.split(";"):
        names = [name.strip() for name in group.split(",") if name.strip()]
        for name in names:
            mapping[name.upper()] = names[0]
    return mapping


def _paper_items(paper, criterion, synonyms=None):
    """Unique items of a paper for the criterion, as {UPPER_KEY: label}."""
    items = {}
    for raw in paper.get(criterion, "").split(";"):
        label = raw.strip()
        if not label:
            continue
        key = label.upper()
        if synonyms and key in synonyms:
            label = synonyms[key]
            if not label:
                continue
            key = label.upper()
        if key not in items:
            items[key] = label
    return items


# ── Clustering ──────────────────────────────────────────────────────────────

def _local_moving(adj, sizes, resolution, rng):
    """One level of Louvain local moving for the CPM-style quality function.

    Moving node i into cluster C gains  w(i, C) - resolution * n_i * N_C,
    where w(i, C) is the summed weight between i and C and N_C the cluster
    size. Returns the cluster of every node and whether anything moved.
    """
    m = len(adj)
    comm = list(range(m))
    comm_size = list(sizes)
    empty = []
    moved_any = False

    for _ in range(100):
        improved = False
        for i in rng.permutation(m):
            ci = comm[i]
            si = sizes[i]
            weights_to = defaultdict(float)
            for j, w in adj[i].items():
                weights_to[comm[j]] += w

            comm_size[ci] -= si
            best_c = ci
            best_gain = weights_to.get(ci, 0.0) - resolution * si * comm_size[ci]
            for c, w in weights_to.items():
                gain = w - resolution * si * comm_size[c]
                if gain > best_gain + 1e-12:
                    best_c, best_gain = c, gain

            # Being alone (gain 0) beats every negative option
            if best_gain < -1e-12 and comm_size[ci] > 0:
                best_c = empty.pop()

            comm_size[best_c] += si
            if best_c != ci:
                comm[i] = best_c
                improved = moved_any = True
                if comm_size[ci] == 0:
                    empty.append(ci)
        if not improved:
            break

    return comm, moved_any


def _louvain_once(n, adj, resolution, rng):
    node_members = [[i] for i in range(n)]
    sizes = [1] * n
    cur_adj = adj

    while True:
        comm, moved = _local_moving(cur_adj, sizes, resolution, rng)
        relabel = {c: k for k, c in enumerate(dict.fromkeys(comm))}
        k = len(relabel)
        if not moved or k == len(cur_adj):
            break

        new_adj = [defaultdict(float) for _ in range(k)]
        new_sizes = [0] * k
        new_members = [[] for _ in range(k)]
        for i, nbrs in enumerate(cur_adj):
            ci = relabel[comm[i]]
            new_sizes[ci] += sizes[i]
            new_members[ci].extend(node_members[i])
            for j, w in nbrs.items():
                cj = relabel[comm[j]]
                if ci != cj:
                    new_adj[ci][cj] += w
        cur_adj, sizes, node_members = new_adj, new_sizes, new_members

    # Apply the moves of the last level to the original nodes
    membership = np.zeros(n, dtype=int)
    for i, members in enumerate(node_members):
        membership[members] = relabel[comm[i]]
    return membership


def _cluster_quality(membership, rows, cols, weights, resolution):
    same = membership[rows] == membership[cols]
    internal = weights[same].sum()  # rows/cols hold each pair once
    sizes = np.bincount(membership)
    return internal - resolution * (sizes * (sizes - 1) / 2.0).sum()


def cluster_network(n, rows, cols, weights, resolution=DEFAULT_RESOLUTION,
                    min_cluster_size=DEFAULT_MIN_CLUSTER_SIZE, n_starts=10, seed=0):
    """Cluster a weighted undirected graph (pairs given once, i < j).

    Returns an array of cluster indices numbered by size (0 = largest).
    """
    rows = np.asarray(rows, dtype=int)
    cols = np.asarray(cols, dtype=int)
    weights = np.asarray(weights, dtype=float)
    if n == 0:
        return np.zeros(0, dtype=int)

    adj = [dict() for _ in range(n)]
    for i, j, w in zip(rows, cols, weights):
        adj[i][j] = adj[i].get(j, 0.0) + w
        adj[j][i] = adj[j].get(i, 0.0) + w

    rng = np.random.default_rng(seed)
    best, best_q = None, -np.inf
    for _ in range(max(1, n_starts)):
        membership = _louvain_once(n, adj, resolution, rng)
        q = _cluster_quality(membership, rows, cols, weights, resolution)
        if q > best_q + 1e-9:
            best, best_q = membership, q

    best = _merge_small_clusters(best, rows, cols, weights, min_cluster_size)
    return _renumber_by_size(best)


def _merge_small_clusters(membership, rows, cols, weights, min_size):
    """Merge clusters smaller than min_size into their most connected cluster
    (VOSviewer behavior). Clusters with no links stay as they are."""
    membership = membership.copy()
    if min_size <= 1:
        return membership
    while True:
        sizes = np.bincount(membership)
        small = [c for c in np.argsort(sizes, kind="stable") if 0 < sizes[c] < min_size]
        merged = False
        for c in small:
            in_r = membership[rows] == c
            in_c = membership[cols] == c
            links = (np.bincount(membership[cols[in_r & ~in_c]], weights=weights[in_r & ~in_c],
                                 minlength=len(sizes))
                     + np.bincount(membership[rows[in_c & ~in_r]], weights=weights[in_c & ~in_r],
                                   minlength=len(sizes)))
            if links.max() > 0:
                membership[membership == c] = int(np.argmax(links))
                merged = True
                break  # sizes changed, recompute
        if not merged:
            return membership


def _renumber_by_size(membership):
    sizes = np.bincount(membership)
    order = sorted(range(len(sizes)), key=lambda c: (-sizes[c], c))
    order = [c for c in order if sizes[c] > 0]
    relabel = {c: k for k, c in enumerate(order)}
    return np.array([relabel[c] for c in membership], dtype=int)


# ── Layout ──────────────────────────────────────────────────────────────────

def _pairwise_distances(X):
    sq = (X * X).sum(1)
    d2 = sq[:, None] + sq[None, :] - 2.0 * X @ X.T
    np.maximum(d2, 0.0, out=d2)
    return np.sqrt(d2)


def _normalize_mean_distance(X):
    X = X - X.mean(0)
    n = len(X)
    if n < 2:
        return X
    mean_d = _pairwise_distances(X).sum() / (n * (n - 1))
    return X / mean_d if mean_d > 0 else X


def vos_layout(S, dim=3, init=None, iterations=400, seed=0, gravity=0.05):
    """VOS mapping: minimize sum_ij s_ij d_ij^2 / (sum_ij d_ij)^2.

    The objective is scale invariant, which is the VOS formulation with the
    average distance constrained to 1. A weak gravity term keeps
    unconnected items from drifting away. Optimized with Adam.
    """
    n = S.shape[0]
    rng = np.random.default_rng(seed)
    if n == 1:
        return np.zeros((1, dim))
    X = init.copy() if init is not None else rng.normal(size=(n, dim))
    X = _normalize_mean_distance(X + rng.normal(scale=1e-3, size=X.shape))
    if n == 2:
        return X

    row_sum = S.sum(1)
    g = gravity * row_sum.sum() / n
    m = np.zeros_like(X)
    v = np.zeros_like(X)
    beta1, beta2, eps = 0.9, 0.999, 1e-12
    eye = np.eye(n, dtype=bool)

    for t in range(1, iterations + 1):
        lr = 0.002 + 0.5 * (0.03 - 0.002) * (1 + np.cos(np.pi * t / iterations))
        D = _pairwise_distances(X)
        D[eye] = 1.0
        inv_d = 1.0 / D
        inv_d[eye] = 0.0
        D[eye] = 0.0

        A = 0.5 * (S * D * D).sum() + g * (X * X).sum()
        B = 0.5 * D.sum()
        grad_a = 2.0 * (row_sum[:, None] * X - S @ X) + 2.0 * g * X
        grad_b = inv_d.sum(1)[:, None] * X - inv_d @ X
        grad = grad_a / B ** 2 - 2.0 * A * grad_b / B ** 3

        m = beta1 * m + (1 - beta1) * grad
        v = beta2 * v + (1 - beta2) * grad * grad
        X = X - lr * (m / (1 - beta1 ** t)) / (np.sqrt(v / (1 - beta2 ** t)) + eps)
        X = _normalize_mean_distance(X)

    return X


def _fit_unit_radius(X, clamp=1.35):
    """Center, scale so the 95th-percentile radius is 1, clamp outliers."""
    X = X - X.mean(0)
    r = np.sqrt((X * X).sum(1))
    scale = np.percentile(r, 95) if len(r) > 1 else 1.0
    if scale <= 0:
        scale = 1.0
    X = X / scale
    r = np.sqrt((X * X).sum(1))
    too_far = r > clamp
    X[too_far] *= (clamp / r[too_far])[:, None]
    return X


def _initial_positions(membership, dim, rng):
    """Seed the layout with clusters spread on a sphere (or circle)."""
    k = membership.max() + 1 if len(membership) else 0
    centers = np.zeros((max(k, 1), dim))
    golden = np.pi * (3.0 - np.sqrt(5.0))
    for c in range(k):
        if dim == 3:
            y = 1 - 2 * (c + 0.5) / k
            r = np.sqrt(max(0.0, 1 - y * y))
            centers[c] = [np.cos(golden * c) * r, y, np.sin(golden * c) * r]
        else:
            a = 2 * np.pi * c / k
            centers[c] = [np.cos(a), np.sin(a)]
    return centers[membership] + rng.normal(scale=0.25, size=(len(membership), dim))


def _principal_axes(X):
    """Rotate X so its largest spread lies along x, then y (det +1)."""
    Xc = X - X.mean(0)
    _, _, vt = np.linalg.svd(Xc, full_matrices=False)
    if np.linalg.det(vt) < 0:
        vt[-1] *= -1
    return Xc @ vt.T


def _align_to(X, target):
    """Orthogonal Procrustes: rotate/reflect X to best match target."""
    u, _, vt = np.linalg.svd(X.T @ target)
    return X @ (u @ vt)


# ── Network construction ────────────────────────────────────────────────────

def build_network(papers, criterion="authorKeywords",
                  start_year=globalVar.DEFAULT_START_YEAR,
                  end_year=globalVar.DEFAULT_END_YEAR,
                  length=DEFAULT_LENGTH,
                  min_occurrences=DEFAULT_MIN_OCCURRENCES,
                  skip_first=0,
                  exclude=(),
                  synonyms="",
                  counting=DEFAULT_COUNTING,
                  min_link_strength=DEFAULT_MIN_LINK_STRENGTH,
                  resolution=DEFAULT_RESOLUTION,
                  min_cluster_size=DEFAULT_MIN_CLUSTER_SIZE,
                  window_width=DEFAULT_WINDOW_WIDTH,
                  top_papers=DEFAULT_TOP_PAPERS,
                  cohesion=DEFAULT_COHESION,
                  seed=0,
                  title="",
                  command="",
                  layout=True):
    """Build the network map data (a JSON-serializable dict).

    layout=False skips the map layout (all positions are 0), for the outputs
    that only need the items, links and clusters, like the thematic map.
    """
    if criterion not in globalVar.validNetworkCriterion:
        raise NetworkError("Criterion '%s' is not valid for network maps. Use one of: %s"
                           % (criterion, ", ".join(globalVar.validNetworkCriterion)))
    if start_year > end_year:
        raise NetworkError("startYear (%d) > endYear (%d)" % (start_year, end_year))
    if counting not in COUNTING_METHODS:
        raise NetworkError("counting must be one of: %s" % ", ".join(COUNTING_METHODS))
    if window_width < 1:
        raise NetworkError("Minimum windowWidth is 1")
    if length < 1:
        raise NetworkError("length must be at least 1")
    if length > MAX_LENGTH:
        raise NetworkError("length must be at most %d" % MAX_LENGTH)

    from scipy import sparse

    _progress("Reading items", 5)
    synonym_map = parse_synonyms(synonyms)
    years = list(range(start_year, end_year + 1))
    n_years = len(years)

    docs = []
    docs_per_year = [0] * n_years
    occurrences = Counter()
    variants = defaultdict(Counter)
    for paper in papers:
        year = paper.get("year", "")
        if not year.isdigit() or not (start_year <= int(year) <= end_year):
            continue
        docs_per_year[int(year) - start_year] += 1
        items = _paper_items(paper, criterion, synonym_map)
        if not items:
            continue
        docs.append((paper, list(items.keys())))
        for key, label in items.items():
            occurrences[key] += 1
            variants[key][label] += 1

    papers_in_range = sum(docs_per_year)
    if papers_in_range == 0:
        raise NetworkError("No papers found in the range %d - %d" % (start_year, end_year))

    excluded = {e.strip().upper() for e in exclude if e and e.strip()}
    candidates = [(k, c) for k, c in occurrences.items()
                  if c >= min_occurrences and k not in excluded]
    candidates.sort(key=lambda kc: (-kc[1], kc[0]))
    selected = [k for k, _ in candidates[skip_first:skip_first + length]]
    if not selected:
        raise NetworkError(
            "No %s items with at least %d occurrences in %d - %d"
            % (criterion, min_occurrences, start_year, end_year))

    n = len(selected)
    index = {k: i for i, k in enumerate(selected)}

    # Most frequent spelling wins; ties go to the first one seen
    labels = [variants[k].most_common(1)[0][0] for k in selected]

    _progress("Counting co-occurrences", 20)
    inc_rows, inc_cols, doc_weights, doc_items = [], [], [], []
    for paper, keys in docs:
        idxs = [index[k] for k in keys if k in index]
        if not idxs:
            continue
        r = len(doc_items)
        doc_items.append((paper, idxs))
        if counting == "fractional":
            doc_weights.append(1.0 / (len(keys) - 1) if len(keys) > 1 else 0.0)
        else:
            doc_weights.append(1.0)
        inc_rows.extend([r] * len(idxs))
        inc_cols.extend(idxs)

    incidence = sparse.csr_matrix(
        (np.ones(len(inc_rows)), (inc_rows, inc_cols)), shape=(len(doc_items), n))
    weighted = sparse.diags(np.array(doc_weights)) @ incidence
    co = sparse.triu((incidence.T @ weighted).tocsr(), k=1).tocoo()

    if min_link_strength > 0:
        keep = co.data >= min_link_strength - 1e-9
    else:
        keep = co.data > 1e-12
    e_rows, e_cols, e_w = co.row[keep], co.col[keep], co.data[keep]

    degree = np.bincount(np.concatenate([e_rows, e_cols]), minlength=n)
    tls = (np.bincount(e_rows, weights=e_w, minlength=n)
           + np.bincount(e_cols, weights=e_w, minlength=n))

    # Association strength s_ij = 2m c_ij / (k_i k_j)
    total = tls.sum()
    if len(e_w):
        assoc = total * e_w / (tls[e_rows] * tls[e_cols])
    else:
        assoc = np.zeros(0)

    _progress("Clustering", 35)
    membership = cluster_network(n, e_rows, e_cols, assoc, resolution=resolution,
                                 min_cluster_size=min_cluster_size, seed=seed)
    n_clusters = int(membership.max()) + 1

    if layout:
        _progress("Computing 3D layout", 50)
        S = np.zeros((n, n))
        S[e_rows, e_cols] = assoc
        S[e_cols, e_rows] = assoc
        if S.max() > 0:
            S /= S.max()
            # Extra attraction inside clusters so each one reads as its own region
            # (0 = plain VOS mapping)
            if cohesion > 0:
                same = membership[:, None] == membership[None, :]
                np.fill_diagonal(same, False)
                S = S + cohesion * S[S > 0].mean() * same
        rng = np.random.default_rng(seed)
        iterations = 400 if n <= 600 else 250
        pos3 = vos_layout(S, dim=3, init=_initial_positions(membership, 3, rng),
                          iterations=iterations, seed=seed)
        _progress("Computing 2D layout", 70)
        pos3 = _principal_axes(pos3) if n > 2 else pos3
        pos2 = vos_layout(S, dim=2, init=pos3[:, :2] if n > 2 else None,
                          iterations=iterations, seed=seed)
        # The 2D map matches the front view of the 3D map, so the viewer can
        # morph between them smoothly
        pos3 = _fit_unit_radius(pos3)
        pos2 = _fit_unit_radius(_align_to(pos2 - pos2.mean(0), pos3[:, :2])) if n > 2 \
            else _fit_unit_radius(pos2)
    else:
        pos3 = np.zeros((n, 3))
        pos2 = np.zeros((n, 2))

    _progress("Computing statistics", 85)
    year_counts = np.zeros((n, n_years), dtype=int)
    cluster_year_counts = np.zeros((n_clusters, n_years), dtype=int)
    cites = [[] for _ in range(n)]
    best_papers = [[] for _ in range(n)]
    for order, (paper, idxs) in enumerate(doc_items):
        y = int(paper["year"]) - start_year
        cited = int(paper["citedBy"]) if str(paper.get("citedBy", "")).isdigit() else 0
        entry = (cited, -order, paper)
        for i in idxs:
            year_counts[i, y] += 1
            cites[i].append(cited)
            if len(best_papers[i]) < top_papers:
                heapq.heappush(best_papers[i], entry)
            elif top_papers > 0 and entry[:2] > best_papers[i][0][:2]:
                heapq.heapreplace(best_papers[i], entry)
        for c in set(membership[idxs]):
            cluster_year_counts[c, y] += 1

    end_idx = n_years - 1
    start_idx = max(0, end_idx - (window_width - 1))
    year_arr = np.array(years, dtype=float)

    nodes = []
    for i in range(n):
        counts = year_counts[i]
        occ = int(counts.sum())
        rates = np.diff(np.concatenate([[0], counts]))
        c_sorted = sorted(cites[i], reverse=True)
        h_index = sum(1 for rank, c in enumerate(c_sorted, 1) if c >= rank)
        first_year = years[int(np.nonzero(counts)[0][0])] if occ else start_year
        top = sorted(best_papers[i], key=lambda e: (-e[0], -e[1]))
        nodes.append({
            "id": i + 1,
            "label": labels[i],
            "c": int(membership[i]),
            "occ": occ,
            "links": int(degree[i]),
            "tls": round(float(tls[i]), 3),
            "avgYear": round(float((counts * year_arr).sum() / occ), 2) if occ else None,
            "avgCit": round(float(np.mean(cites[i])), 2) if occ else 0,
            "h": h_index,
            "agr": round(float(np.mean(rates[start_idx:end_idx + 1])), 1),
            "pdly": round(100.0 * counts[start_idx:end_idx + 1].sum() / occ, 2) if occ else 0,
            "firstYear": first_year,
            "y": counts.tolist(),
            "p3": [round(float(v), 4) for v in pos3[i]],
            "p2": [round(float(v), 4) for v in pos2[i]],
            "papers": [[p.get("title", ""), int(p["year"]), p_cited, p.get("doi", "")]
                       for p_cited, _, p in top],
        })

    order = np.argsort(-e_w, kind="stable")
    links = [[int(e_rows[k]), int(e_cols[k]),
              round(float(e_w[k]), 3) if counting == "fractional" else int(e_w[k])]
             for k in order]

    clusters = []
    for c in range(n_clusters):
        members = sorted(np.nonzero(membership == c)[0], key=lambda i: (-nodes[i]["occ"], labels[i]))
        cy = cluster_year_counts[c]
        docs_c = int(cy.sum())
        clusters.append({
            "id": c + 1,
            "label": labels[members[0]],
            "color": CLUSTER_COLORS[c % len(CLUSTER_COLORS)],
            "size": len(members),
            "occ": int(sum(nodes[i]["occ"] for i in members)),
            "docs": docs_c,
            "avgYear": round(float((cy * year_arr).sum() / docs_c), 2) if docs_c else None,
            "top": [labels[i] for i in members[:5]],
            "y": cy.tolist(),
        })

    meta = {
        "app": "ScientoPy",
        "version": globalVar.SCIENTOPY_VERSION,
        "criterion": criterion,
        "criterionLabel": CRITERION_LABELS.get(criterion, criterion),
        "title": title or "",
        "startYear": start_year,
        "endYear": end_year,
        "papersInRange": papers_in_range,
        "papersWithItems": len(doc_items),
        "length": length,
        "minOccurrences": min_occurrences,
        "skipFirst": skip_first,
        "exclude": sorted(excluded),
        "synonyms": len(synonym_map),
        "counting": counting,
        "minLinkStrength": min_link_strength,
        "resolution": resolution,
        "minClusterSize": min_cluster_size,
        "cohesion": cohesion,
        "windowWidth": window_width,
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "command": command,
        "docsPerYear": docs_per_year,
    }

    return {"meta": meta, "years": years, "nodes": nodes, "links": links, "clusters": clusters}


# ── Writers ─────────────────────────────────────────────────────────────────

def network_json(data):
    """JSON safe to embed inside a <script> element."""
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return text.replace("<", "\\u003c")


def write_html(data, path):
    with open(_viewer_path("template.html"), "r", encoding="utf-8") as f:
        html = f.read()
    with open(_viewer_path("viewer.css"), "r", encoding="utf-8") as f:
        css = f.read()
    scripts = []
    for name in VIEWER_JS_FILES:
        with open(_viewer_path(os.path.join("js", name)), "r", encoding="utf-8") as f:
            scripts.append("// ── %s ──\n%s" % (name, f.read()))

    title = data["meta"]["title"] or ("%s network" % data["meta"]["criterionLabel"])
    html = html.replace("__SP_TITLE__", xml_escape(title))
    html = html.replace("/*__SP_STYLE__*/", css)
    html = html.replace("/*__SP_SCRIPT__*/", "\n".join(scripts))
    # Data goes in last so its contents are never scanned for placeholders
    head, tail = html.split("__SP_DATA__", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(head)
        f.write(network_json(data))
        f.write(tail)


def write_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def _clean_field(text):
    return str(text).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def write_vosviewer_map(data, path):
    """VOSviewer map file (tab separated, opens with 'Create map > based on
    network data' or 'Open map')."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("id\tlabel\tx\ty\tcluster\tweight<Links>\tweight<Total link strength>"
                "\tweight<Occurrences>\tscore<Avg. pub. year>\tscore<Avg. citations>\n")
        for node in data["nodes"]:
            f.write("%d\t%s\t%.4f\t%.4f\t%d\t%d\t%s\t%d\t%s\t%s\n" % (
                node["id"], _clean_field(node["label"]), node["p2"][0], node["p2"][1],
                node["c"] + 1, node["links"], _num(node["tls"]), node["occ"],
                _num(node["avgYear"]) if node["avgYear"] is not None else "",
                _num(node["avgCit"])))


def write_vosviewer_network(data, path):
    nodes = data["nodes"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        for i, j, w in data["links"]:
            f.write("%d\t%d\t%s\n" % (nodes[i]["id"], nodes[j]["id"], _num(w)))


def _num(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def write_nodes_csv(data, path):
    clusters = data["clusters"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["Id", "Label", "Cluster", "Cluster label", "Occurrences", "Links",
                         "Total link strength", "Avg. pub. year", "Avg. citations",
                         "hIndex", "AGR", "PDLY", "First year", "x", "y", "x3", "y3", "z3"]
                        + data["years"])
        for node in data["nodes"]:
            writer.writerow([node["id"], node["label"], node["c"] + 1,
                             clusters[node["c"]]["label"], node["occ"], node["links"],
                             _num(node["tls"]), node["avgYear"], node["avgCit"], node["h"],
                             node["agr"], node["pdly"], node["firstYear"]]
                            + node["p2"] + node["p3"] + node["y"])


def write_links_csv(data, path):
    nodes = data["nodes"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["Source", "Target", "Source label", "Target label", "Weight"])
        for i, j, w in data["links"]:
            writer.writerow([nodes[i]["id"], nodes[j]["id"], nodes[i]["label"],
                             nodes[j]["label"], _num(w)])


def write_gexf(data, path):
    """GEXF 1.3 with positions and colors (opens in Gephi)."""
    nodes, clusters = data["nodes"], data["clusters"]
    max_occ = max(node["occ"] for node in nodes) or 1
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gexf xmlns="http://gexf.net/1.3" xmlns:viz="http://gexf.net/1.3/viz" version="1.3">',
        '  <meta lastmodifieddate="%s"><creator>ScientoPy %s</creator><description>%s</description></meta>'
        % (datetime.date.today().isoformat(), globalVar.SCIENTOPY_VERSION,
           xml_escape("%s co-occurrence network" % data["meta"]["criterionLabel"])),
        '  <graph defaultedgetype="undirected" mode="static">',
        '    <attributes class="node">',
        '      <attribute id="0" title="cluster" type="integer"/>',
        '      <attribute id="1" title="occurrences" type="integer"/>',
        '      <attribute id="2" title="avg_pub_year" type="double"/>',
        '      <attribute id="3" title="avg_citations" type="double"/>',
        '      <attribute id="4" title="total_link_strength" type="double"/>',
        '    </attributes>',
        '    <nodes>',
    ]
    for node in nodes:
        color = clusters[node["c"]]["color"].lstrip("#")
        r, g, b = (int(color[k:k + 2], 16) for k in (0, 2, 4))
        avg_year = node["avgYear"] if node["avgYear"] is not None else 0
        out.append('      <node id="%d" label="%s"><attvalues>'
                   '<attvalue for="0" value="%d"/><attvalue for="1" value="%d"/>'
                   '<attvalue for="2" value="%s"/><attvalue for="3" value="%s"/>'
                   '<attvalue for="4" value="%s"/></attvalues>'
                   '<viz:color r="%d" g="%d" b="%d"/>'
                   '<viz:position x="%.2f" y="%.2f" z="0"/>'
                   '<viz:size value="%.2f"/></node>'
                   % (node["id"], xml_escape(node["label"], {'"': "&quot;"}),
                      node["c"] + 1, node["occ"], avg_year, node["avgCit"], node["tls"],
                      r, g, b, node["p2"][0] * 500, -node["p2"][1] * 500,
                      4 + 26 * (node["occ"] / max_occ) ** 0.5))
    out.append('    </nodes>')
    out.append('    <edges>')
    for k, (i, j, w) in enumerate(data["links"]):
        out.append('      <edge id="%d" source="%d" target="%d" weight="%s"/>'
                   % (k, nodes[i]["id"], nodes[j]["id"], _num(w)))
    out.append('    </edges>')
    out.append('  </graph>')
    out.append('</gexf>')
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


# ── Thematic map ────────────────────────────────────────────────────────────

def thematic_map(data):
    """Themes of the thematic map (strategic diagram), one per cluster.

    Follows Callon's co-word analysis. The strength of the link between two
    items is the equivalence index e_ij = c_ij^2 / (c_i * c_j), with c_ij the
    documents with both items and c_i, c_j the documents with each one. Then,
    for every cluster:

      centrality = 10 * sum of e_ij between its items and the other clusters
                   (how much the theme is tied to the rest of the field)
      density    = 100 * sum of e_ij between its own items / number of items
                   (how developed the theme is)

    Themes above the median centrality are central, and above the median
    density developed: motor themes (both), niche themes (developed only),
    basic themes (central only) and emerging or declining themes (neither).
    Items with no links are not a theme, so clusters of one item are left out.

    Returns a list of themes ordered by cluster: {"cluster", "label", "items"
    (by occurrences), "size", "occ", "docs", "avgYear", "centrality",
    "density", "rankCentrality", "rankDensity", "theme"}.
    """
    from scipy.stats import rankdata

    nodes, clusters = data["nodes"], data["clusters"]
    n_clusters = len(clusters)
    occ = np.array([node["occ"] for node in nodes], dtype=float)
    cluster_of = np.array([node["c"] for node in nodes], dtype=int)

    internal = np.zeros(n_clusters)
    external = np.zeros(n_clusters)
    for i, j, w in data["links"]:
        e = float(w) ** 2 / (occ[i] * occ[j])
        if cluster_of[i] == cluster_of[j]:
            internal[cluster_of[i]] += e
        else:
            external[cluster_of[i]] += e
            external[cluster_of[j]] += e

    themes = []
    for c, cluster in enumerate(clusters):
        if cluster["size"] < 2:
            continue
        members = sorted(np.nonzero(cluster_of == c)[0],
                         key=lambda i: (-nodes[i]["occ"], nodes[i]["label"]))
        themes.append({
            "cluster": cluster["id"],
            "label": cluster["label"],
            "items": [nodes[i]["label"] for i in members],
            "size": cluster["size"],
            "occ": cluster["occ"],
            "docs": cluster["docs"],
            "avgYear": cluster["avgYear"],
            "centrality": round(float(10.0 * external[c]), 4),
            "density": round(float(100.0 * internal[c] / cluster["size"]), 4),
        })
    if not themes:
        return themes

    rank_c = rankdata([theme["centrality"] for theme in themes])
    rank_d = rankdata([theme["density"] for theme in themes])
    mid_c, mid_d = np.median(rank_c), np.median(rank_d)
    for theme, rc, rd in zip(themes, rank_c, rank_d):
        theme["rankCentrality"] = float(rc)
        theme["rankDensity"] = float(rd)
        central, developed = rc >= mid_c, rd >= mid_d
        if central and developed:
            theme["theme"] = THEME_MOTOR
        elif developed:
            theme["theme"] = THEME_NICHE
        elif central:
            theme["theme"] = THEME_BASIC
        else:
            theme["theme"] = THEME_EMERGING
    return themes


def write_clusters_csv(data, path, themes=None, only_themes=False):
    """One row per cluster with every item of the cluster and, for the
    clusters that are themes, the thematic map values.

    only_themes leaves out the clusters that are not on the thematic map.
    """
    if themes is None:
        themes = thematic_map(data)
    by_cluster = {theme["cluster"]: theme for theme in themes}
    cluster_of = defaultdict(list)
    for node in data["nodes"]:
        cluster_of[node["c"]].append(node)

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["Cluster", "Label", "Items", "Occurrences", "Documents",
                         "Avg. pub. year", "Callon centrality", "Callon density",
                         "Centrality rank", "Density rank", "Theme", "Item labels"])
        for c, cluster in enumerate(data["clusters"]):
            theme = by_cluster.get(cluster["id"])
            if only_themes and theme is None:
                continue
            members = sorted(cluster_of[c], key=lambda node: (-node["occ"], node["label"]))
            row = [cluster["id"], cluster["label"], cluster["size"], cluster["occ"],
                   cluster["docs"], cluster["avgYear"] if cluster["avgYear"] is not None else ""]
            if theme is not None:
                row += [theme["centrality"], theme["density"], _num(theme["rankCentrality"]),
                        _num(theme["rankDensity"]), theme["theme"]]
            else:
                row += ["", "", "", "", ""]
            row.append("; ".join(node["label"] for node in members))
            writer.writerow(row)


def save_network_outputs(data):
    """Write the HTML viewer and the data exports. Returns {kind: path}."""
    for folder in (globalVar.GRAPHS_OUT_FOLDER, globalVar.RESULTS_FOLDER):
        if not os.path.exists(folder):
            os.makedirs(folder)

    base = _criterion_file_name(data["meta"]["criterion"])
    files = {
        "html": os.path.join(globalVar.GRAPHS_OUT_FOLDER, base + "_network.html"),
        "json": os.path.join(globalVar.RESULTS_FOLDER, base + "_network.json"),
        "nodes": os.path.join(globalVar.RESULTS_FOLDER, base + "_network_nodes.csv"),
        "links": os.path.join(globalVar.RESULTS_FOLDER, base + "_network_links.csv"),
        "clusters": os.path.join(globalVar.RESULTS_FOLDER, base + "_network_clusters.csv"),
        "gexf": os.path.join(globalVar.RESULTS_FOLDER, base + "_network.gexf"),
        "vosMap": os.path.join(globalVar.RESULTS_FOLDER, base + "_vosviewer_map.txt"),
        "vosNetwork": os.path.join(globalVar.RESULTS_FOLDER, base + "_vosviewer_network.txt"),
    }
    write_html(data, files["html"])
    write_json(data, files["json"])
    write_nodes_csv(data, files["nodes"])
    write_links_csv(data, files["links"])
    write_clusters_csv(data, files["clusters"])
    write_gexf(data, files["gexf"])
    write_vosviewer_map(data, files["vosMap"])
    write_vosviewer_network(data, files["vosNetwork"])
    return files


def cli_command(criterion, start_year, end_year, length, min_occurrences, skip_first,
                exclude, synonyms, counting, min_link_strength, resolution, min_cluster_size,
                cohesion, window_width, previous_results):
    """The scientoPyNetwork.py command that reproduces a map."""
    parts = ["python", "scientoPyNetwork.py", "-c", criterion,
             "--startYear", str(start_year), "--endYear", str(end_year)]
    if length != DEFAULT_LENGTH:
        parts += ["-l", str(length)]
    if min_occurrences != DEFAULT_MIN_OCCURRENCES:
        parts += ["--minOccurrences", str(min_occurrences)]
    if skip_first:
        parts += ["-s", str(skip_first)]
    if exclude:
        parts += ["--exclude", '"%s"' % "; ".join(exclude)]
    if synonyms and synonyms.strip():
        parts += ["--synonyms", '"%s"' % synonyms.strip()]
    if counting != DEFAULT_COUNTING:
        parts += ["--counting", counting]
    if min_link_strength != DEFAULT_MIN_LINK_STRENGTH:
        parts += ["--minLinkStrength", _num(float(min_link_strength))]
    if resolution != DEFAULT_RESOLUTION:
        parts += ["--resolution", _num(float(resolution))]
    if min_cluster_size != DEFAULT_MIN_CLUSTER_SIZE:
        parts += ["--minClusterSize", str(min_cluster_size)]
    if cohesion != DEFAULT_COHESION:
        parts += ["--cohesion", _num(float(cohesion))]
    if window_width != DEFAULT_WINDOW_WIDTH:
        parts += ["--windowWidth", str(window_width)]
    if previous_results:
        parts += ["-r"]
    return " ".join(parts)


def generate_network_map(criterion="authorKeywords",
                         start_year=globalVar.DEFAULT_START_YEAR,
                         end_year=globalVar.DEFAULT_END_YEAR,
                         length=DEFAULT_LENGTH,
                         min_occurrences=DEFAULT_MIN_OCCURRENCES,
                         skip_first=0,
                         exclude=(),
                         synonyms="",
                         counting=DEFAULT_COUNTING,
                         min_link_strength=DEFAULT_MIN_LINK_STRENGTH,
                         resolution=DEFAULT_RESOLUTION,
                         min_cluster_size=DEFAULT_MIN_CLUSTER_SIZE,
                         cohesion=DEFAULT_COHESION,
                         window_width=DEFAULT_WINDOW_WIDTH,
                         previous_results=False,
                         title=""):
    """Load the corpus, build the map and write every output file.

    Returns (data, files). Raises NetworkError on invalid input and
    NetworkCanceled when globalVar.cancelProcess is set.
    """
    globalVar.cancelProcess = False
    _progress("Reading dataset", 0)
    papers = load_papers(previous_results)
    exclude = [e.strip() for e in exclude if e and e.strip()]
    command = cli_command(criterion, start_year, end_year, length, min_occurrences,
                          skip_first, exclude, synonyms, counting, min_link_strength, resolution,
                          min_cluster_size, cohesion, window_width, previous_results)
    data = build_network(papers, criterion=criterion, start_year=start_year,
                         end_year=end_year, length=length, min_occurrences=min_occurrences,
                         skip_first=skip_first, exclude=exclude, synonyms=synonyms,
                         counting=counting,
                         min_link_strength=min_link_strength, resolution=resolution,
                         min_cluster_size=min_cluster_size, cohesion=cohesion,
                         window_width=window_width, title=title, command=command)
    _progress("Writing network map", 95)
    files = save_network_outputs(data)
    globalVar.progressPer = 101
    return data, files


def generate_thematic_map(criterion="authorKeywords",
                          start_year=globalVar.DEFAULT_START_YEAR,
                          end_year=globalVar.DEFAULT_END_YEAR,
                          length=DEFAULT_LENGTH,
                          min_occurrences=DEFAULT_MIN_OCCURRENCES,
                          skip_first=0,
                          exclude=(),
                          synonyms="",
                          counting=DEFAULT_COUNTING,
                          min_link_strength=DEFAULT_MIN_LINK_STRENGTH,
                          resolution=DEFAULT_RESOLUTION,
                          min_cluster_size=DEFAULT_MIN_CLUSTER_SIZE,
                          previous_results=False,
                          title=""):
    """Load the corpus, cluster the items and compute the thematic map.

    Uses the same items, links and clusters as generate_network_map with the
    same parameters, so the themes are the clusters of the network map.
    Writes results/<Criterion>_thematic_map.csv and returns (data, themes,
    files); the plot is drawn by graphUtils.plot_thematic_map. Raises
    NetworkError on invalid input or when no theme is found, and
    NetworkCanceled when globalVar.cancelProcess is set.
    """
    globalVar.cancelProcess = False
    _progress("Reading dataset", 0)
    papers = load_papers(previous_results)
    exclude = [e.strip() for e in exclude if e and e.strip()]
    data = build_network(papers, criterion=criterion, start_year=start_year,
                         end_year=end_year, length=length, min_occurrences=min_occurrences,
                         skip_first=skip_first, exclude=exclude, synonyms=synonyms,
                         counting=counting, min_link_strength=min_link_strength,
                         resolution=resolution, min_cluster_size=min_cluster_size,
                         title=title, layout=False)
    _progress("Computing themes", 90)
    themes = thematic_map(data)
    if not themes:
        raise NetworkError(
            "No themes found: the %s items do not appear together in the documents. "
            "Try a lower minOccurrences or more items." % criterion)

    if not os.path.exists(globalVar.RESULTS_FOLDER):
        os.makedirs(globalVar.RESULTS_FOLDER)
    files = {"themes": os.path.join(globalVar.RESULTS_FOLDER,
                                    _criterion_file_name(criterion) + "_thematic_map.csv")}
    write_clusters_csv(data, files["themes"], themes=themes, only_themes=True)
    globalVar.progressPer = 101
    return data, themes, files
