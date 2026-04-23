# ScientoPy Performance Improvement Specification

## 1. Overview

This document specifies a re-architecture of the ScientoPy data pipeline to address severe performance bottlenecks observed on large datasets (~300 k papers across 267 Scopus/WoS files, ~727 MB total input).

**Current version:** 3.0.1
**Affected scripts:** `preProcess.py`, `scientoPy.py`, `generateBibtex.py`, and the GUI (`ScientoPyGui.py`)

### 1.1 Observed Pain Points

| Stage | Symptom | Root cause (verified in code) |
|---|---|---|
| Reading input files | > 100 s for 300 k papers / 267 files | `paperUtils.openFileToDict` — pure-Python `csv.reader`, single-threaded, iterates file-by-file, row-by-row, performs hundreds of `if headerCol == "X"` string comparisons per row, plus regex + `unidecode` + quadratic `[x.upper() for x in …]` de-duplication inside each paper |
| In-memory processing | Large RAM footprint; slow sorts/filters | `paperDict = list[dict]` — one Python dict per paper with ~45 keys; GC-heavy, cache-unfriendly, no vectorization |
| Writing `papersPreprocessed.csv` | Slow; dominates the tail of preprocess | `paperSave.saveResults` — `csv.DictWriter.writerow` row-by-row, ~40 columns × 300 k rows, Python-level string encoding per cell |
| Opening `papersPreprocessed.csv` for analysis | Full re-parse every run; no incremental reuse | `ScientoPyClass.scientoPy` calls the same `openFileToDict` on the saved CSV, re-running the entire normalization pipeline even though the data is already clean |
| "Save results during analysis" | Surprise CSV writes in `results/` | `ScientoPyClass.scientoPy` calls `paperSave.saveResults(papersDictOut, results/papersPreprocessed.csv)` at the end of every non-`--previousResults` run (`ScientoPyClass.py:509-510`). Users pay CSV-write cost on every analysis even when they do not want an export |
| `SAVE_RESULTS_ON` semantics | Format chosen at preprocess time, hardcoded in `globalVar.py` | `globalVar.SAVE_RESULTS_ON` is read by both `paperUtils.normalizeOpenAccess` (at parse) and `paperSave.saveResults` (at write). Parsing normalizes Open-Access tags into the chosen format **before** storage, so switching formats later without re-preprocessing yields wrong output. WoS-format export also drops many fields (no `authorFull`, `bothKeywords`, `emailHost`, `institution`, etc.) — lossy round-trip |

### 1.2 Goals

1. **10× or better reduction** in preprocess wall-clock time at the 300 k-paper scale.
2. **Sub-second load** of the preprocessed dataset before every analysis run.
3. Remove the implicit "save CSV during analysis" behavior — analysis must be read-only with respect to the `results/` folder unless the user explicitly exports.
4. Surface export as a first-class feature (new CLI flags + new GUI **Export** tab) with two output profiles (Scopus fields, WoS fields) and two sources (preprocessed corpus, last analysis results).
5. Keep the CLI (`preProcess.py`, `scientoPy.py`) fully functional and scriptable. GUI wraps the CLI semantics.
6. Preserve **bit-exact compatibility** of all analysis metrics (totals, AGR, ADY, PDLY, h-index) with the current output.

---

## 2. Current Data Flow (verified)

```
┌──────────────────────────┐
│  dataIn/*.csv  (~267 f.) │
│  Scopus + WoS exports    │
└────────────┬─────────────┘
             │  openFileToDict (serial, dict-per-paper)
             ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│  paperDict: list[dict]   │────▶ │ removeDuplicates         │
│  ~300 k Python dicts     │      │ (sort + adjacent compare)│
└────────────┬─────────────┘      └────────────┬─────────────┘
             │                                 │
             │                                 ▼
             │                    ┌──────────────────────────┐
             │                    │ saveResults (csv.Writer) │
             │                    │ dataPre/papersPrep.csv   │
             │                    └────────────┬─────────────┘
             ▼                                 │
┌──────────────────────────┐                   │
│ scientoPy.py analysis    │◀──────────────────┘
│  openFileToDict AGAIN    │   (re-parses the CSV every run)
│  computes AGR/ADY/…      │
└────────────┬─────────────┘
             ▼
   results/*.csv  (top results, extended results)
   results/papersPreprocessed.csv  ← side-effect we want to remove
```

---

## 3. Target Architecture

### 3.1 New Dependencies

| Package | Role | Rationale |
|---|---|---|
| `polars>=1.0` | Parallel CSV reader + in-memory DataFrame | Rust-backed, multi-core, SIMD, Arrow-native; drop-in replacement for the `csv` + `list[dict]` combo. Published benchmarks (see §10) show 10×–50× ingestion speedups at this scale |
| `pyarrow>=15` | Parquet writer/reader used by Polars | Required transitively; also used directly by the export tab |

`pandas` already exists in `requirements.txt` (used only by `disam_names_scopus`) and is retained for now. `numpy`, `matplotlib`, `scipy`, `unidecode`, `Pillow`, `wordcloud`, `PySide6` are unchanged.

### 3.2 New On-Disk Layout

```
dataPre/
├── papersPreprocessed.parquet   ← NEW: canonical preprocessed store
│                                  (Snappy or Zstd compression; single file)
├── PreprocessedBrief.csv        ← kept (small human-readable log)
└── papersPreprocessed.csv       ← DELETED in normal flow; produced only on
                                   explicit export

results/
├── AuthorKeywords.csv                   ← top-results table (unchanged)
├── AuthorKeywords_extended.csv          ← extended results (unchanged)
└── papersPreprocessed.csv               ← DELETED: never auto-written
                                          during analysis
```

Parquet expected size: ~60–100 MB (vs. ~500 MB CSV) with Zstd. Load time measured in tens-to-hundreds of milliseconds at 300 k rows, vs. tens of seconds for the CSV parse path.

### 3.3 New Data Flow

```
dataIn/*.csv                         ┌──────────────────────────────┐
┌──────────────────────┐   Polars    │ preProcess.py                │
│ scan_csv("*.csv")    │────────────▶│  - parallel read (Scopus+WoS)│
│ + eager collect()    │             │  - vectorized normalization  │
└──────────────────────┘             │  - dedup via Polars joins    │
                                     └────────────┬─────────────────┘
                                                  ▼
                                     dataPre/papersPreprocessed.parquet
                                                  │
                                                  ▼
                                     ┌──────────────────────────────┐
                                     │ scientoPy.py analysis        │
                                     │  - pl.read_parquet()         │
                                     │  - group_by / agg on Polars  │
                                     │  - outputs:                  │
                                     │     results/*.csv (top/ext)  │
                                     │  - NO papersPreprocessed copy│
                                     └──────────────────────────────┘

Export (opt-in, on demand):
  preProcess.py --export <format>  OR
  scientoPy.py  --export-results   OR
  GUI "Export" tab
        │
        ▼
  user-chosen path / results folder
  format:  scopus | wos
  source:  preprocessed | last-results
```

---

## 4. Tooling Rationale

Based on the Python ecosystem comparison (see §10 citations):

| Concern | Choice | Why not the alternatives |
|---|---|---|
| Multi-core CSV read | **Polars** `pl.read_csv(glob)` | pandas-pyarrow still returns a pandas DF (conversion cost); DuckDB would add a second query engine for no net gain; PyArrow CSV is a lower-level API without a first-class DataFrame |
| In-memory representation | **Polars DataFrame** | Arrow-backed (~2–4× less RAM than pandas for strings), lazy optimizer, GIL-free Rust kernels |
| On-disk preprocessed store | **Parquet** (Zstd or Snappy) | Columnar, 5–15× smaller than CSV; single file; readable by Polars, pandas, DuckDB, PyArrow, R; no server process |
| Duplicate removal | **Polars** `group_by(title_key, first_author_key).agg(...)` + DOI map | Replaces current `O(N)` sort-and-sweep with a hash-group in Rust |
| SQLite | **Rejected** | Row-oriented; slower group-bys than Polars at this scale; and a prior SQLite migration was already rolled back (see git history). No write-concurrency requirement justifies re-introducing it |

---

## 5. Implementation Plan

### Phase 1 — Preprocess rewrite to Polars/Parquet

#### 5.1 New module `paperIO.py`

Replace `paperUtils.openFileToDict` with column-oriented helpers:

```python
# paperIO.py  (new)
import polars as pl

def scan_scopus_csv(path: str) -> pl.LazyFrame: ...
def scan_wos_csv(path: str) -> pl.LazyFrame: ...
def load_folder(folder: str) -> pl.DataFrame:
    """Read every *.csv / *.txt under folder in parallel, dispatch to the
    right schema (Scopus vs WoS), concat, and return a canonical DataFrame."""

def write_preprocessed(df: pl.DataFrame, path: str) -> None:
    df.write_parquet(path, compression="zstd", compression_level=3)

def read_preprocessed(path: str) -> pl.DataFrame:
    return pl.read_parquet(path)
```

Detection of Scopus vs WoS is done from the header row: the existing heuristic (`"\t"` present ⇒ WoS) is preserved. Scopus files have a BOM + comma header; WoS files are tab-separated.

#### 5.2 Canonical schema

All the internal field names currently used by `paperUtils.openFileToDict` (`author`, `authorFull`, `title`, `year`, `sourceTitle`, `citedBy`, `doi`, `eid`, `documentType`, `source`, `dataBase`, `openAccess`, `affiliations`, `country`, `institution`, `institutionWithCountry`, `emailHost`, `bothKeywords`, `authorKeywords`, `indexKeywords`, `abstract`, `duplicatedIn`, …) are retained as column names.

Column types:

| Column | Type |
|---|---|
| `year`, `citedBy` | `Int32` / `Int64` |
| `duplicatedIn` | `List[Utf8]` (Parquet supports nested types natively) |
| everything else | `Utf8` |

#### 5.3 Vectorized normalization

The per-row transformations in `openFileToDict` map cleanly to Polars expressions:

| Current per-row code | Polars equivalent |
|---|---|
| `unidecode(author)` | `.str.decode("utf-8", "ignore")` + UDF chunked with `.map_batches` (unidecode has no vectorized replacement; chunk call is still dominated by Rust string ops around it) |
| `author.replace(";", ",")` | `pl.col("author").str.replace_all(";", ",")` |
| author-initial dot insertion | `pl.col("author").str.replace_all(r"([A-Z])(?=[A-Z,])", "$1.")` (regex) |
| `re.split("; (?=[^\]]*(?:\[|$))", affiliations)` → country/institution extraction | `.str.split(...)` then `.list.last()` / `.list.slice(1,1)` / `.list.eval(...)` |
| Document-type filter (`INCLUDED_TYPES`) | `.filter(pl.col("documentType").str.contains_any(INCLUDED_TYPES, ascii_case_insensitive=True))` |
| Invalid-year / empty-title filters | `.filter((pl.col("year").is_between(1900, 2100)) & (pl.col("title").str.len_chars() > 0))` |

The heavy `[x.upper() for x in …]` de-duplication inside `openFileToDict` (for countries, institutions, bothKeywords) is replaced by `pl.col(...).list.unique(maintain_order=True)`.

#### 5.4 Open-Access normalization untangled

The current design intertwines parsing and formatting via `globalVar.SAVE_RESULTS_ON`. The new design stores a **canonical** representation and formats on export only:

- In-memory / Parquet column `openAccess` is a `List[Utf8]` of canonical tags:
  `"Gold" | "Hybrid" | "Bronze" | "Green" | "Green Submitted" | "Green Accepted" | "Green Published"`
- Scopus-format export re-emits `All Open Access; Gold Open Access; …`
- WoS-format export re-emits `gold, hybrid, …`

This fixes the latent bug where switching `SAVE_RESULTS_ON` between preprocess and export produces inconsistent output.

#### 5.5 Vectorized duplicate removal

```python
# Build normalization keys
df = df.with_columns(
    pl.col("title").str.to_uppercase()
      .str.replace_all(r"[\(\[].*?[\)\]]", "")
      .str.replace_all(r"[^A-Z0-9]+", "")
      .alias("titleKey"),
    pl.col("author").str.to_uppercase()
      .str.replace_all(r";|\.|,", " ")
      .str.extract(r"^\s*([A-Z]+)", 1)
      .alias("firstAuthorKey"),
)

# Prefer WoS over Scopus when both exist
df = df.sort(["titleKey", "firstAuthorKey", "dataBase"], descending=[False, False, True])

# Group and take first; collect the dropped EIDs into duplicatedIn
dedup = (
    df.group_by(["titleKey", "firstAuthorKey"], maintain_order=True)
      .agg([
          pl.all().first(),
          pl.col("eid").slice(1).alias("duplicatedIn"),
          pl.col("citedBy").mean().cast(pl.Int64).alias("citedByAvg"),
      ])
)
```

A second pass handles DOI-based duplicates that didn't collide on title/author (current `paperUtils.removeDuplicates` already does this; we mirror it as a left-anti + group).

**Correctness gate:** the test suite (`tests/run_behavioral_tests.py`, see `doc/behavioral_test_spec.md`) must continue to pass unchanged.

### Phase 2 — Analysis rewrite to read Parquet

#### 5.6 `ScientoPyClass.scientoPy` rewrite

```python
# Replace openFileToDict(ifile, self.papersDict)
df = pl.read_parquet(PAPERS_PARQUET)

# Year-range filter (vectorized)
inside = df.filter(pl.col("year").is_between(args.startYear, args.endYear))

# Top-topics discovery: explode criterion, group_by, sort
criterion_df = (
    inside.select(
        pl.col(args.criterion).str.split(";").alias("terms"),
        pl.col("year"),
        pl.col("citedBy"),
    )
    .explode("terms")
    .with_columns(pl.col("terms").str.strip_chars().str.to_uppercase())
    .filter(pl.col("terms") != "")
)

counts = (
    criterion_df.group_by("terms")
    .agg(pl.len().alias("count"))
    .sort("count", descending=True)
    .head(args.length + args.skipFirst)
    .slice(args.skipFirst)
)
```

Year-series per topic, cited-by totals, AGR/ADY/PDLY, and h-index all translate to `group_by(["terms", "year"])` aggregations followed by pivots. Numeric outputs must be validated against the current Python implementation on at least one real dataset (see §7).

#### 5.7 Remove the implicit CSV write

Delete these lines from `ScientoPyClass.scientoPy`:

```python
if not args.previousResults:
    paperSave.saveResults(papersDictOut, os.path.join(
        globalVar.RESULTS_FOLDER, globalVar.OUTPUT_FILE_NAME))
```

The `results/papersPreprocessed.csv` file is **only** created when the user explicitly invokes export (see §6).

`--previousResults` must still work: it reads back the last exported CSV if present, else it reads from the Parquet store filtered by the last topic's EIDs. The Parquet path is preferred.

#### 5.8 `generateBibtex.py`

Swap `openFileToDict` for `pl.read_parquet`, filter by EID set, iterate the filtered DataFrame to write the `.bib` file. The BibTeX escaping logic is unchanged.

### Phase 3 — Export feature

#### 5.9 CLI (built first — GUI wraps it)

New script **`exportPapers.py`** (and a subcommand on `preProcess.py` / `scientoPy.py` for convenience):

```
usage: exportPapers.py [-h]
                       --source {preprocessed,results}
                       --format {scopus,wos}
                       [--output PATH]

  --source preprocessed   Export dataPre/papersPreprocessed.parquet
                          (the full deduplicated corpus)
  --source results        Export all CSVs already present in results/
                          (re-emit them in the chosen field format)
  --format scopus         Scopus field names and separators
  --format wos            WoS field names and separators (tab-delimited)
  --output PATH           Destination file (preprocessed) or directory
                          (results). Defaults:
                            preprocessed -> export/papersPreprocessed.csv
                            results      -> export/results/
```

`--format` selection replaces the global `globalVar.SAVE_RESULTS_ON`. The variable is retained only as a default and marked deprecated; all export paths read the CLI argument.

`--source results` re-emits the CSVs already generated during analysis (top-results and extended-results). These are ScientoPy's own tabular outputs, not Scopus/WoS-native records, so "Scopus vs WoS" only affects field names where a column corresponds to a Scopus/WoS native column (author, title, etc. in the extended-results file).

#### 5.10 WoS export: restore missing fields

The current `paperSave.saveResults` WoS branch writes only 15 of the ~40 canonical columns. The new exporter must either:

1. Use the **full** WoS field set (the full list used by WoS Record Export) and leave empty columns blank, **or**
2. Extend the WoS header with a documented set of "scientopy extension columns" (`country`, `institution`, `institutionWithCountry`, `emailHost`, `bothKeywords`, `authorFull`, `duplicatedIn`) — this matches what the Scopus exporter already does.

Option 2 is preferred; it gives round-trip parity with the Scopus exporter.

#### 5.11 GUI — new **Export** tab

Added as tab 5 in `ScientoPyGui.py`, after "Extended Results":

```
┌─ 5. Export ─────────────────────────────────────────────┐
│  Source                                                 │
│   ◉ Preprocessed corpus (dataPre/papersPreprocessed)    │
│   ○ Last analysis results (results/*.csv)               │
│                                                         │
│  Format                                                 │
│   ◉ Scopus fields                                       │
│   ○ WoS fields                                          │
│                                                         │
│  Destination                                            │
│   [ path/to/output            ] [ Browse… ]             │
│                                                         │
│                                 [  Export  ]            │
└─────────────────────────────────────────────────────────┘
```

Clicking **Export** calls the same code path as the CLI (`exportPapers.export(...)`). A success message shows the path(s) written and offers an **Open folder** button.

The **Export** button is disabled when:
- `preprocessed` is selected and `dataPre/papersPreprocessed.parquet` does not exist.
- `results` is selected and `results/` contains no `*.csv` files.

---

## 6. Behavior Changes Visible to Users

| Change | Migration |
|---|---|
| `dataPre/papersPreprocessed.csv` no longer produced by `preProcess.py` | Run `./exportPapers.py --source preprocessed --format scopus -o dataPre/papersPreprocessed.csv` to reproduce the old file |
| `results/papersPreprocessed.csv` no longer produced by `scientoPy.py` | Run `./exportPapers.py --source results --format scopus` after an analysis |
| `globalVar.SAVE_RESULTS_ON` deprecated | Kept for one release cycle; emits a `DeprecationWarning` at import time |
| First analysis after upgrade | If `papersPreprocessed.parquet` is missing but the legacy CSV exists, auto-convert once (`pl.read_csv(legacy).write_parquet(...)`) and reuse thereafter |

---

## 7. Testing & Validation

### 7.1 Correctness — bit-exact comparison

On the AI dataset (`data_artificial_inteligence/scopusData/`, ~300 k papers):

1. Run current code end-to-end; snapshot `PreprocessedBrief.csv`, top-10 author/country/keyword rankings, AGR/ADY/PDLY/h-index for each.
2. Run new code end-to-end.
3. Diff. Acceptable tolerance: **zero** for integer counts; `±0.05` for AGR/ADY/PDLY floats (window-edge rounding in numpy vs Polars).

Additionally: the existing behavioral tests (`tests/run_behavioral_tests.py`, see `doc/behavioral_test_spec.md`) must continue to pass unchanged.

### 7.2 Performance — measurable targets

| Metric | Current | Target |
|---|---|---|
| `preProcess.py data_artificial_inteligence/scopusData/` | > 100 s | ≤ 15 s on a 4-core laptop |
| Analysis load (reading preprocessed store) | 20–40 s (CSV re-parse) | ≤ 1 s (Parquet) |
| `papersPreprocessed` on-disk size | ~500 MB CSV | ≤ 100 MB Parquet |

Measurements are collected with `time` on the reference dataset, reported in the PR description.

### 7.3 Export correctness

- Round-trip test: `preprocess → export scopus → re-preprocess export → export scopus` must produce byte-identical CSVs after the second cycle.
- Same for `--format wos`.
- `--source results` must produce the same top-results CSV as the one produced by the old `paperSave.saveTopResults` on the same analysis.

---

## 8. Backward Compatibility

- CLI entry points (`preProcess.py`, `scientoPy.py`, `generateBibtex.py`) keep the same argument names; only new flags are added.
- `globalVar.SAVE_RESULTS_ON` remains readable; if the CLI flag is not passed, the variable's value is used as the default.
- The on-disk Parquet layout is new; a legacy-CSV auto-convert shim ships with the release (§ 6) so upgrading users do not lose data.
- BibTeX generation, word clouds, and all graph types continue to consume the same internal schema.

---

## 9. Phased Rollout

| Phase | Scope | Duration |
|---|---|---|
| 1 | `paperIO.py` + `PreProcessClass` rewrite; Parquet writer; existing behavioral tests pass | 3–4 days |
| 2 | `ScientoPyClass` rewrite to read Parquet; `generateBibtex.py` migration; remove implicit `results/papersPreprocessed.csv` write | 3 days |
| 3 | `exportPapers.py` CLI + documented `--source/--format` semantics; WoS-export field-set fix (§ 5.10) | 2 days |
| 4 | GUI **Export** tab; wire up to `exportPapers.export(...)`; disabled-state handling | 1–2 days |
| 5 | Benchmarking pass on the AI dataset; update `README.md` and `Manual/` screenshots | 1 day |

Each phase lands behind a feature-flag-style import guard (`try: import polars` with a clear error message) so a partial install still runs the legacy path.

---

## 10. References

- Polars CSV & performance docs — https://docs.pola.rs/user-guide/io/csv/
- DuckDB CSV parallel reading — https://duckdb.org/2023/03/31/csv-parallel-reading.html
- Apache Arrow / Parquet — https://arrow.apache.org/docs/python/parquet.html
- db-benchmark (group-by/join comparison across Polars, DuckDB, pandas) — https://duckdblabs.github.io/db-benchmark/

---

## 11. Files to Create or Modify

| File | Action | Notes |
|---|---|---|
| `paperIO.py` | Create | Polars-based reader/writer; Scopus+WoS schema dispatch; Parquet I/O |
| `paperUtils.py` | Modify | `openFileToDict` kept only as a thin adapter over `paperIO.load_folder` for legacy callers; `removeDuplicates` re-implemented in Polars or removed in favor of the dedup inside `paperIO.load_folder` |
| `PreProcessClass.py` | Modify | Replace the per-file `openFileToDict` loop with a single `paperIO.load_folder(args.dataInFolder)`; write Parquet via `paperIO.write_preprocessed`; keep the `PreprocessedBrief.csv` log |
| `ScientoPyClass.py` | Modify | Swap CSV read for `pl.read_parquet`; rewrite the inner Python loops (topic count, per-year series, AGR/ADY/PDLY/h-index) as Polars expressions; **delete** the `paperSave.saveResults(papersDictOut, results/papersPreprocessed.csv)` call at the end of the analysis |
| `paperSave.py` | Modify | `saveResults(...)` and the export-format helpers become `exportPapers.export_scopus(df, path)` / `export_wos(df, path)`. `saveTopResults` / `saveExtendedResults` (CSVs in `results/`) unchanged |
| `exportPapers.py` | Create | New CLI (`--source`, `--format`, `--output`) that calls into `paperSave`/`paperIO` |
| `generateBibtex.py` | Modify | Read Parquet via `paperIO.read_preprocessed`; iterate the filtered DataFrame to emit the `.bib` |
| `globalVar.py` | Modify | Mark `SAVE_RESULTS_ON` deprecated (kept as default for exportPapers if the CLI flag is absent); add `OUTPUT_FILE_PARQUET = "papersPreprocessed.parquet"` |
| `ScientoPyGui.py` | Modify | Add "5. Export" tab (§ 5.11); wire to `exportPapers.export(...)`; drop any reference to the side-effect `results/papersPreprocessed.csv` |
| `requirements.txt` / `pyproject.toml` | Modify | Add `polars>=1.0`, `pyarrow>=15` to runtime deps |
| `tests/run_behavioral_tests.py` | Modify | Add assertions that (a) `dataPre/papersPreprocessed.parquet` exists after preprocess, (b) `results/papersPreprocessed.csv` does **not** exist after analysis, (c) an export of each format produces the expected column set and row count |
| `README.md`, `Manual/*` | Modify | Document the new Export tab and CLI; note that preprocessed CSV is no longer auto-generated |
