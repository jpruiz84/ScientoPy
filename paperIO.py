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

"""Polars-based I/O for the ScientoPy preprocessed corpus.

This module replaces the performance-critical parts of paperUtils:

- load_folder()        reads all Scopus/WoS CSV/TXT files under a folder using
                       Polars (Rust, multi-core, SIMD) and dispatches each row
                       through paperUtils._process_paper_row for the exact same
                       per-row normalization as the legacy csv.reader path.

- write_preprocessed() writes the deduplicated list[dict] to a single Parquet
                       file (Zstd). ~10-15x smaller than CSV, order-of-magnitude
                       faster to reload.

- read_preprocessed()  reads the Parquet back into a list[dict] that matches
                       the in-memory shape the rest of the codebase expects.

See doc/performance_improvement_spec.md for the rationale.
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import polars as pl

import globalVar
import paperUtils


# Environment variable that tells Polars how many Rust worker threads to use
# inside each read_csv call. Set to 1 inside ProcessPoolExecutor workers so
# N Python processes × M Polars threads do not oversubscribe the machine.
_POLARS_THREADS_ENV = "POLARS_MAX_THREADS"


def _read_one_file(path):
    """Read a single Scopus or WoS file into a Polars DataFrame with every
    column kept as Utf8. Delimiter is auto-detected from the first line:
    tab ⇒ WoS export, otherwise comma ⇒ Scopus export.

    Returns None on any parse failure (the legacy path behaves the same way by
    silently skipping unreadable files).
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            first = f.readline()
        sep = "\t" if "\t" in first else ","
        # WoS exports are tab-separated with free-form text in fields (abstracts
        # containing raw ", parens, etc.); they are NOT CSV-quoted. Passing
        # quote_char=None disables CSV-style quote parsing so a stray " in an
        # abstract does not blow up the whole file. Scopus exports are proper
        # RFC-4180 CSV so keep the default double-quote for them.
        kwargs = dict(
            separator=sep,
            has_header=True,
            infer_schema_length=0,
            ignore_errors=True,
            truncate_ragged_lines=True,
            encoding="utf8-lossy",
        )
        if sep == "\t":
            kwargs["quote_char"] = None
        return pl.read_csv(path, **kwargs)
    except Exception as e:
        # Scopus/WoS exports sometimes emit malformed RFC-4180 quoting
        # (unescaped " inside a quoted field); Polars refuses the whole
        # file. The stdlib csv fallback is lenient and parses them fine,
        # so there is no data loss — just keep the warning short.
        print("  (lenient fallback for %s)" % os.path.basename(path))
        return _legacy_read(path)


def _legacy_read(path):
    """Fallback reader for files Polars chokes on. Returns a DataFrame with
    the same `headers | row` shape _read_one_file normally produces, built
    via stdlib csv."""
    import csv as _csv
    try:
        _csv.field_size_limit(int(2e9))
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            first = f.readline()
            f.seek(0)
            sep = "\t" if "\t" in first else ","
            # quoting=_csv.QUOTE_NONE keeps tab-separated WoS abstracts intact.
            if sep == "\t":
                reader = _csv.reader(f, delimiter=sep, quoting=_csv.QUOTE_NONE)
            else:
                reader = _csv.reader(f, delimiter=sep)
            rows = list(reader)
        if not rows:
            return None
        header = [h.replace("\ufeff", "") for h in rows[0]]
        data = [
            row + [""] * (len(header) - len(row)) if len(row) < len(header) else row[: len(header)]
            for row in rows[1:]
        ]
        return pl.DataFrame({h: [r[i] for r in data] for i, h in enumerate(header)})
    except Exception as e:
        print("WARN: csv fallback also failed for %s: %s" % (path, e))
        return None


def _process_file_worker(path):
    """Worker entry point for ProcessPoolExecutor.

    Reads ONE input file with Polars, applies paperUtils._process_paper_row_pure
    to each row, and returns a tuple

        (papers_list, loaded, omitted, scopus, wos, read_ok)

    `papers_list` contains only the canonical dicts for papers accepted by
    the document-type filter ("added"). The three counter ints tally the
    totals this worker saw so the main process can aggregate them into
    globalVar. `read_ok` is False when the file could not be parsed at all
    (Polars + csv fallback both failed or the file was empty).

    Runs in its own OS process — pickle-safe. No globalVar touches.
    """
    # Keep Polars single-threaded inside the worker so N workers do not
    # fight over the machine. The outer pool does the parallelism across
    # files; inside a worker, all the heavy lifting is Python anyway.
    os.environ[_POLARS_THREADS_ENV] = "1"

    # Local imports so each worker has a clean module graph on `spawn` start
    # methods (macOS / Windows). On fork (Linux default) these are essentially
    # free because the parent's modules are already in memory.
    import paperUtils as _paperUtils  # noqa: F401

    df = _read_one_file(path)
    if df is None or df.is_empty():
        return [], 0, 0, 0, 0, False

    headers = df.columns
    papers = []
    loaded = omitted = scopus = wos = 0
    for row in df.iter_rows():
        values = ["" if v is None else str(v) for v in row]
        paper, outcome = _paperUtils._process_paper_row_pure(headers, values)
        if outcome == "filtered":
            continue
        loaded += 1
        if outcome == "added":
            papers.append(paper)
            db = paper["dataBase"]
            if db == "WoS":
                wos += 1
            elif db == "Scopus":
                scopus += 1
        else:  # "omitted"
            omitted += 1

    return papers, loaded, omitted, scopus, wos, True


def load_folder(folder, papersDict, max_workers=None):
    """Read every *.csv / *.txt under `folder` in parallel using a pool of
    worker processes, then append the accepted papers to `papersDict`.

    Each worker parses one file with Polars and applies the per-row
    normalization from paperUtils, returning a list of canonical paper dicts
    plus counter tallies. The main process aggregates counters into globalVar
    and concatenates the paper lists.

    File reading is I/O-bound and Polars CSV parsing releases the GIL (Rust),
    so threads provide real parallelism without fork-safety issues in the GUI.

    max_workers: cap on the number of worker processes. Defaults to
    os.cpu_count(), which saturates the machine for the AI dataset.
    """
    # Walk the tree so datasets organized in sub-folders (e.g. dataIn/scopus/
    # + dataIn/wos/) are all picked up. Sorted for stable order across runs.
    files = []
    for root, _dirs, names in os.walk(folder):
        for name in names:
            if name.lower().endswith((".csv", ".txt")):
                files.append(os.path.join(root, name))
    files.sort()
    total = len(files)
    print("Files to read: %d (recursively under %s)" % (total, folder))

    # progressText is set by the orchestrator (PreProcessClass._announce_step)
    # so the step counter stays visible in the GUI — here we only drive the
    # progress bar as individual files complete.
    globalVar.progressPer = 0

    if total == 0:
        return

    if max_workers is None:
        max_workers = os.cpu_count() or 4
    # Never launch more workers than files to avoid idle-worker overhead.
    max_workers = max(1, min(max_workers, total))

    done = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_process_file_worker, p): p for p in files}
        for fut in as_completed(futures):
            if globalVar.cancelProcess:
                # Best-effort cancel — let in-flight futures complete on their own.
                return
            path = futures[fut]
            try:
                papers, loaded, omitted, scopus, wos, read_ok = fut.result()
            except Exception as e:
                print("WARN: worker failed for %s: %s" % (path, e))
                done += 1
                globalVar.progressPer = int(done / total * 100)
                continue

            done += 1
            globalVar.progressPer = int(done / total * 100)

            if not read_ok:
                print("Reading file: %s (empty or failed)" % path)
                continue

            print("Reading file: %s (+%d papers)" % (path, len(papers)))
            papersDict.extend(papers)
            globalVar.loadedPapers += loaded
            globalVar.omittedPapers += omitted
            globalVar.papersScopus += scopus
            globalVar.papersWoS += wos


def write_preprocessed(papers, path):
    """Persist a list[dict] of canonical papers to a single Parquet file.

    Using Zstd level 3 as a good balance between size and write speed. The
    `duplicatedIn` field (a list[str]) is stored natively as a list column.

    Builds columns manually instead of going through pl.from_dicts: on the
    AI corpus (~274 k papers) from_dicts spends ~5 s building a schema and
    row-wise coercing, whereas a straight list-comprehension per column
    does the same work in ~2 s.
    """
    if not papers:
        # Still emit a well-formed (empty) Parquet so downstream readers
        # do not have to special-case missing files.
        pl.DataFrame().write_parquet(path, compression="zstd")
        return

    # Union of keys across all papers (most come from _process_paper_row_pure
    # which initializes the full dict, but optional columns like `author_ids`
    # only appear in newer Scopus exports).
    keys = set()
    for p in papers:
        keys.update(p.keys())
    keys = list(keys)

    # Build columns. `p.get(k)` fills missing keys with None, which Polars
    # will infer to the right nullable type per column.
    cols = {k: [p.get(k) for p in papers] for k in keys}
    try:
        df = pl.DataFrame(cols)
    except Exception:
        # Fallback: tolerate mixed scalar types within a column (older
        # snapshots on disk may have int-typed `citedBy` from pre-fix code).
        df = pl.DataFrame(cols, strict=False)
    df.write_parquet(path, compression="zstd", compression_level=3)


def read_preprocessed(path):
    """Load a Parquet produced by write_preprocessed() back into a list[dict]
    in the exact shape the rest of ScientoPy expects.

    Also resets the `loadedPapers` / `papersScopus` / `papersWoS` counters so
    callers that display preprocessing stats (the GUI and scientoPy.py) stay
    consistent.
    """
    df = pl.read_parquet(path)
    papers = df.to_dicts()

    # Normalize types that matter to the analysis paths:
    # - citedBy is used as int() in ScientoPyClass and removeDuplicates
    # - duplicatedIn must be a list (Parquet preserves this, but fall-back
    #   CSV reads may return a string with ';' separators)
    for p in papers:
        if p.get("citedBy") is None:
            p["citedBy"] = "0"
        else:
            p["citedBy"] = str(p["citedBy"])
        if "duplicatedIn" not in p or p["duplicatedIn"] is None:
            p["duplicatedIn"] = []
        elif isinstance(p["duplicatedIn"], str):
            p["duplicatedIn"] = [s for s in p["duplicatedIn"].split(";") if s]

    # Refresh counters so any downstream code that reads globalVar still sees
    # the right totals. These are informational, not authoritative.
    globalVar.loadedPapers = len(papers)
    globalVar.papersScopus = sum(1 for p in papers if p.get("dataBase") == "Scopus")
    globalVar.papersWoS = sum(1 for p in papers if p.get("dataBase") == "WoS")
    globalVar.OriginalTotalPapers = len(papers)
    globalVar.totalPapers = len(papers)

    return papers


def _dedup_keys_chunk(pairs):
    """Worker: each element of `pairs` is a (title, author) tuple. Returns
    a list of (titleB, firstAuthorLastName) tuples in the same order.

    Passing bare strings (not full paper dicts) keeps the pickle payload
    small — crucial because each dict has ~45 fields and pickling 300 k of
    them dominates the speedup otherwise.
    """
    import paperUtils as _paperUtils
    title_re1 = _paperUtils._TITLE_BRACKETS_RE
    title_re2 = _paperUtils._TITLE_NONALNUM_RE
    author_re1 = _paperUtils._AUTHOR_SEP_RE
    author_re2 = _paperUtils._AUTHOR_NONALPHA_RE
    unidecode = _paperUtils.unidecode.unidecode

    out = []
    for title, author in pairs:
        t = unidecode(title or "")
        t = title_re1.sub("", t.upper()).strip()
        t = title_re2.sub("", t)

        a = unidecode(author or "")
        a = a.upper().strip()
        a = author_re1.sub(" ", a).split(" ")[0]
        a = author_re2.sub("", a)

        out.append((t, a))
    return out


def compute_dedup_keys_parallel(papersDict, max_workers=None):
    """Populate titleB and firstAuthorLastName on every paper using a
    ProcessPoolExecutor. Replaces the serial loop at the top of
    paperUtils.removeDuplicates so the per-paper unidecode + regex pass
    scales across cores.

    The workers receive only (title, author) string tuples — not the full
    paper dicts — to keep pickle/IPC costs under the speedup from parallel
    regex + unidecode work.
    """
    total = len(papersDict)
    if total == 0:
        return
    if max_workers is None:
        max_workers = os.cpu_count() or 4
    max_workers = max(1, min(max_workers, total))

    # Small datasets: serial avoids multiprocessing startup cost.
    if total < 5000 or max_workers == 1:
        for p in papersDict:
            p["titleB"], p["firstAuthorLastName"] = (
                paperUtils._dedup_key_for_paper(p)
            )
        return

    # Slice the lightweight (title, author) projection. This list is small:
    # two strings per paper instead of a 45-field dict.
    pairs = [(p.get("title", ""), p.get("author", "")) for p in papersDict]
    chunk_size = (total + max_workers - 1) // max_workers
    chunks = [pairs[i : i + chunk_size] for i in range(0, total, chunk_size)]

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        results = list(pool.map(_dedup_keys_chunk, chunks))

    # Stitch key tuples back into the original dicts, in order.
    idx = 0
    for keys in results:
        for title_key, author_key in keys:
            papersDict[idx]["titleB"] = title_key
            papersDict[idx]["firstAuthorLastName"] = author_key
            idx += 1


def parquet_exists(folder):
    """Helper for callers that want to prefer Parquet over CSV if both exist."""
    return os.path.isfile(os.path.join(folder, globalVar.OUTPUT_FILE_PARQUET))


def parquet_path(folder):
    return os.path.join(folder, globalVar.OUTPUT_FILE_PARQUET)
