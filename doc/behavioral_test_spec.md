# ScientoPy Behavioral Test Specification

## Overview

This document specifies a behavioral test suite for ScientoPy based on **artificial data with known results**. The approach:

1. A Python script (`tests/generate_test_data.py`) generates synthetic WoS and Scopus input files with fully controlled content.
2. Because the data is artificial and deterministic, all expected outputs are known in advance.
3. A test runner (`tests/run_behavioral_tests.py`) executes the ScientoPy pipeline and asserts the actual outputs match the expected values.

---

## 1. Artificial Data Generator

### 1.1 Script: `tests/generate_test_data.py`

Generates two files in a temporary folder (e.g., `tests/dataInTest/`):

- `test_scopus.csv` — Scopus CSV format (comma-delimited, UTF-8 with BOM `\ufeff`)
- `test_wos.txt` — WoS tab-delimited format (UTF-8 with BOM `\ufeff`)

### 1.2 Scopus CSV Format

Header row (comma-delimited):

```
Authors,Title,Year,Source title,Volume,Issue,Art. No.,Page start,Page end,Cited by,DOI,Link,Affiliations,Authors with affiliations,Abstract,Author Keywords,Index Keywords,Document Type,Source,EID
```

Separator: `,`  
Document Type valid values: `Article`, `Conference Paper`, `Review`, `Proceedings Paper`, `Article in Press`

### 1.3 WoS TXT Format

Header row (tab-delimited):

```
PT\tAU\tAF\tTI\tSO\tLA\tDT\tDE\tID\tAB\tC1\tTC\tPY\tDI\tSC\tUT
```

Separator: `\t`  
`DT` valid values: `Article`, `Proceedings Paper`, `Review`

---

## 2. Controlled Dataset Design

### 2.1 Paper Definitions

The generator creates **30 papers total** distributed as follows:

#### Group A — Keyword "Alpha" (10 papers, years 2018–2022, Scopus only)

| Field | Value |
|---|---|
| Author Keywords | `Alpha` |
| Index Keywords | `Alpha index` |
| Document Type | `Article` |
| Country (Affiliations) | `United States` |
| Institution | `MIT` |
| Source | `Scopus` |
| Cited by | 10 each |
| Years | 2 papers each year: 2018, 2019, 2020, 2021, 2022 |

#### Group B — Keyword "Beta" (8 papers, years 2020–2023, WoS only)

| Field | Value |
|---|---|
| Author Keywords (`DE`) | `Beta` |
| Index Keywords (`ID`) | `Beta index` |
| Document Type | `Article` |
| Country (C1 field) | `Germany` |
| Institution | `TU Berlin` |
| Source | `WoS` |
| Cited by (`TC`) | 5 each |
| Years | 2 papers each year: 2020, 2021, 2022, 2023 |

#### Group C — Keyword "Gamma" (6 papers, years 2021–2023, split: 3 Scopus + 3 WoS)

| Field | Value |
|---|---|
| Author Keywords | `Gamma` |
| Document Type | `Conference Paper` (Scopus) / `Proceedings Paper` (WoS) |
| Country | `Brazil` |
| Institution | `USP` |
| Cited by | 2 each |
| Years | 2 papers each year: 2021, 2022, 2023 |

#### Group D — Duplicate papers (4 papers: 2 Scopus + 2 WoS, same DOI)

Same papers appear in both databases. DOIs:
- `10.0000/dup001`
- `10.0000/dup002`

| Field | Value |
|---|---|
| Author Keywords | `Delta` |
| Document Type | `Article` |
| Country | `France` |
| Years | 2022, 2023 |

After deduplication, only 2 unique papers remain.

#### Group E — Omitted document types (2 papers, Scopus only)

| Field | Value |
|---|---|
| Document Type | `Book Chapter` (not in `INCLUDED_TYPES`) |
| Author Keywords | `Epsilon` |

These papers must be **absent** from all outputs.

### 2.2 Summary of Expected Counts

| Metric | Expected Value |
|---|---|
| Total loaded papers (before omit) | 32 |
| Omitted papers (Group E) | 2 |
| Papers after omit removal | 30 |
| Loaded from Scopus (after omit) | 17 (10A + 3C + 2D_scopus + 2E omitted → actually 15 valid) |
| Loaded from WoS (after omit) | 13 (8B + 3C + 2D_wos) |
| Duplicates removed | 2 (Group D: DOI match) |
| **Final total after deduplication** | **28** |

> Note: exact counts must be recalculated when implementing the generator by tracing `paperUtils.openFileToDict` → `paperUtils.removeDuplicates` logic.

---

## 3. Expected Pipeline Outputs

### 3.1 Stage 1: `preProcess.py tests/dataInTest`

**Output file:** `dataPre/papersPreprocessed.csv`

Assertions:
- File exists and is non-empty.
- Total rows (excluding header) == **28**.
- No paper with `Document Type` == `Book Chapter` appears.
- The 2 duplicate papers (DOI `10.0000/dup001`, `10.0000/dup002`) appear **exactly once** each.

**Output file:** `dataPre/PreprocessedBrief.csv`

Assertions:
- Row `"Loaded papers"` → Number == `32`
- Row `"Omitted papers by document type"` → Number == `2`
- Row `"Total papers after omitted papers removed"` → Number == `30`
- Row `"Papers from Scopus"` → Number == `15`
- Row `"Papers from WoS"` → Number == `13`

---

### 3.2 Stage 2: `scientoPy.py -c authorKeywords --noPlot`

**Output file:** `results/AuthorKeywords.csv`

Columns: `Pos., AuthorKeywords, Total, AGR, ADY, PDLY, hIndex, <year columns>`

Assertions (top 4 topics by total):

| Pos. | Topic | Total |
|---|---|---|
| 1 | ALPHA | 10 |
| 2 | BETA | 8 |
| 3 | GAMMA | 6 |
| 4 | DELTA | 2 |

- `EPSILON` must **not** appear (omitted document type).
- Year columns for `ALPHA`: `2018=2, 2019=2, 2020=2, 2021=2, 2022=2`, all other years `0`.
- Year columns for `BETA`: `2020=2, 2021=2, 2022=2, 2023=2`, all other years `0`.

---

### 3.3 Stage 2: `scientoPy.py -c country --noPlot`

**Output file:** `results/Country.csv`

Assertions:

| Topic | Total |
|---|---|
| UNITED STATES | 10 |
| GERMANY | 8 |
| BRAZIL | 6 |
| FRANCE | 2 |

---

### 3.4 Stage 2: `scientoPy.py -c institution --noPlot`

**Output file:** `results/Institution.csv`

Assertions:

| Topic | Total |
|---|---|
| MIT | 10 |
| TU BERLIN | 8 |
| USP | 6 |

---

### 3.5 Stage 2: `scientoPy.py -c authorKeywords --startYear 2021 --endYear 2023 --noPlot`

**Output file:** `results/AuthorKeywords.csv`

Assertions — only papers within 2021–2023 are counted:

| Topic | Total |
|---|---|
| ALPHA | 4 (2021+2022 only) |
| BETA | 6 (2021+2022+2023) |
| GAMMA | 6 (2021+2022+2023) |

---

### 3.6 Stage 2: `scientoPy.py -c authorKeywords -t "Alpha" --noPlot`

**Output file:** `results/AuthorKeywords.csv`

Assertions:
- Only row `ALPHA` present.
- Total == `10`.
- `hIndex` == `10` (each of the 10 papers has 10 citations).

---

### 3.7 Stage 2: `scientoPy.py -c dataBase --noPlot`

**Output file:** `results/DataBase.csv`

Assertions:

| Topic | Total |
|---|---|
| SCOPUS | 15 |
| WOS | 13 |

---

### 3.8 Stage 2 with `--previousResults`: chained analysis

Run sequence:
```
python3 scientoPy.py -c country -t "United States" --noPlot
python3 scientoPy.py -c authorKeywords -r --noPlot
```

Assertions on second run (`results/AuthorKeywords.csv`):
- Only `ALPHA` appears with Total == `10`.
- No keywords from other countries.

---

## 4. Validation of `dataPre/papersPreprocessed.csv`

This section specifies how to verify that `preProcess.py` correctly merged the two source files into a single output. The merged file is read with `csv.DictReader` using the Scopus output fields (see `paperSave.py`).

### 4.1 Output Schema

The output CSV uses **Scopus-style column names** regardless of the paper's origin:

| Output column | Source Scopus field | Source WoS field | Notes |
|---|---|---|---|
| `Authors` | `Authors` | `AU` | WoS authors are reformatted with dots after initials |
| `Title` | `Title` | `TI` | |
| `Year` | `Year` | `PY` | |
| `Source title` | `Source title` | `SO` | |
| `Cited by` | `Cited by` | `Z9` | Averaged if paper was duplicated |
| `DOI` | `DOI` | `DI` | |
| `Affiliations` | `Affiliations` | `C1` | |
| `Abstract` | `Abstract` | `AB` | |
| `Author Keywords` | `Author Keywords` | `DE` | |
| `Index Keywords` | `Index Keywords` | `ID` | |
| `Document Type` | `Document Type` | `DT` | |
| `Source` | `"Scopus"` | `"WoS"` | Derived from EID prefix |
| `EID` | `EID` (starts with `2-`) | `UT` (starts with `WOS`) | Used to identify source |
| `duplicatedIn` | — | — | Semicolon-separated EIDs of removed duplicates |
| `country` | Extracted from `Affiliations` | Extracted from `C1` | Last item of each `, `-split affiliation segment |
| `institution` | *(empty — Scopus not supported)* | Extracted from `C1` | Second item of each `, `-split segment; WoS only |
| `institutionWithCountry` | *(empty)* | `"<institution>, <country>"` | WoS only |
| `bothKeywords` | Union of `Author Keywords` + `Index Keywords` | Same | Deduped, case-insensitive |

### 4.2 Test Data Paper Reference

The generator must assign known, verifiable values to specific fields. The table below defines one representative paper per group for field-level validation:

#### Reference Paper S1 (Scopus, Group A — "Alpha")

| Field | Value in generated file |
|---|---|
| `Authors` | `Smith, J.` |
| `Title` | `Alpha Paper 2020 A` |
| `Year` | `2020` |
| `Author Keywords` | `Alpha` |
| `Index Keywords` | `Alpha index` |
| `Cited by` | `10` |
| `DOI` | `10.0001/alpha-2020-a` |
| `Document Type` | `Article` |
| `Affiliations` | `MIT, Cambridge, United States` |
| `Open Access` | `All Open Access; Gold Open Access` |
| `EID` | `2-s2.0-test-alpha-2020-a` |
| `Source` | `Scopus` |

#### Reference Paper W1 (WoS, Group B — "Beta")

| Field | Value in generated file |
|---|---|
| `Authors` | `Muller, H.` |
| `Title` | `Beta Paper 2021 A` |
| `Year` | `2021` |
| `Author Keywords` (`DE`) | `Beta` |
| `Index Keywords` (`ID`) | `Beta index` |
| `Cited by` (`Z9`) | `5` |
| `DOI` (`DI`) | `10.0002/beta-2021-a` |
| `Document Type` (`DT`) | `Article` |
| `Affiliations` (`C1`) | `[Muller, Hans] TU Berlin, Berlin, Germany` |
| `OA` | `gold` |
| `EID` (`UT`) | `WOS:test-beta-2021-a` |

#### Reference Papers D1a/D1b (Duplicate pair, Group D)

| Field | Scopus version (D1a) | WoS version (D1b) |
|---|---|---|
| `Title` | `Delta Duplicate Paper 2022` | `Delta Duplicate Paper 2022` |
| `DOI` | `10.0000/dup001` | `10.0000/dup001` |
| `Cited by` | `20` | `10` |
| `EID` | `2-s2.0-test-dup001` | `WOS:test-dup001` |

### 4.3 Field Mapping Assertions

#### Test T-M01: Scopus paper fields mapped correctly

Read `dataPre/papersPreprocessed.csv`, find the row where `EID == "2-s2.0-test-alpha-2020-a"`.

| Column | Expected value |
|---|---|
| `Title` | `Alpha Paper 2020 A` |
| `Year` | `2020` |
| `Author Keywords` | `Alpha` |
| `Index Keywords` | `Alpha index` |
| `Cited by` | `10` |
| `DOI` | `10.0001/alpha-2020-a` |
| `Document Type` | `Article` |
| `Source` | `Scopus` |
| `duplicatedIn` | *(empty)* |

#### Test T-M02: WoS paper fields mapped correctly

Find the row where `EID == "WOS:test-beta-2021-a"`.

| Column | Expected value |
|---|---|
| `Title` | `Beta Paper 2021 A` |
| `Year` | `2021` |
| `Author Keywords` | `Beta` |
| `Index Keywords` | `Beta index` |
| `Cited by` | `5` |
| `DOI` | `10.0002/beta-2021-a` |
| `Document Type` | `Article` |
| `Source` | `WoS` |
| `duplicatedIn` | *(empty)* |

### 4.4 Duplicate Merging Assertions

The duplicate detection logic in `paperUtils.removeDuplicates` matches papers when:
- `firstAuthorLastName` AND normalized `titleB` are equal, **OR**
- `doi` is equal (and non-empty)

Papers are sorted with WoS first (alphabetically: `"WoS" > "Scopus"`), so the **WoS version is kept** and the Scopus version is removed.

#### Test T-M03: Duplicate paper kept and marked

Find the row where `DOI == "10.0000/dup001"`.

| Column | Expected value |
|---|---|
| `Source` | `WoS` (WoS kept, Scopus removed) |
| `EID` | `WOS:test-dup001` |
| `duplicatedIn` | `2-s2.0-test-dup001` |
| `Cited by` | `15` (average of 20 and 10) |

#### Test T-M04: Removed duplicate is absent

Assert that no row in the CSV has `EID == "2-s2.0-test-dup001"`.

#### Test T-M05: Total duplicate count

Assert that the number of rows where `duplicatedIn` is non-empty == **2** (one per duplicate pair in Group D).

### 4.5 Country Extraction Assertions

#### Test T-M06: Country from Scopus affiliation

Scopus `Affiliations` format: `Institution Name, City, Country`

The last comma-separated element is the country.

For paper `EID == "2-s2.0-test-alpha-2020-a"` with `Affiliations = "MIT, Cambridge, United States"`:

| Column | Expected value |
|---|---|
| `country` | `United States` |

#### Test T-M07: Country from WoS C1 field

WoS `C1` format: `[Author Name] Institution Name, City, Country`

The last comma-separated element (after the `]` split) is the country.

For paper `EID == "WOS:test-beta-2021-a"` with `C1 = "[Muller, Hans] TU Berlin, Berlin, Germany"`:

| Column | Expected value |
|---|---|
| `country` | `Germany` |

#### Test T-M08: Multiple countries in one paper

Create one additional paper (Group C representative) with two authors from different institutions/countries:

Scopus `Affiliations`: `USP, Sao Paulo, Brazil; MIT, Cambridge, United States`

| Column | Expected value |
|---|---|
| `country` | `Brazil;United States` (semicolon-separated, in affiliation order, no duplicates) |

### 4.6 Institution Extraction Assertions

Institution extraction is performed **only for WoS papers** (from the `C1` field). For Scopus papers, the `institution` column is left empty by `paperUtils`.

#### Test T-M09: Institution from WoS C1 field

WoS `C1` splitting logic:
1. Split by `; ` (ignoring content inside `[]`) to get individual affiliations
2. For each affiliation, split by `, ` and take index `[1]` (second element) as institution

For paper `EID == "WOS:test-beta-2021-a"` with `C1 = "[Muller, Hans] TU Berlin, Berlin, Germany"`:

After splitting by `]`: `afSections = ["[Muller, Hans", " TU Berlin", " Berlin", " Germany"]`  
`institution = afSections[1].strip()` → `"TU Berlin"`

| Column | Expected value |
|---|---|
| `institution` | `TU Berlin` |
| `institutionWithCountry` | `TU Berlin, Germany` |

#### Test T-M10: Institution empty for Scopus papers

For any Scopus paper (e.g., `EID == "2-s2.0-test-alpha-2020-a"`):

| Column | Expected value |
|---|---|
| `institution` | *(empty string)* |
| `institutionWithCountry` | *(empty string)* |

### 4.7 `bothKeywords` Computation Assertions

`bothKeywords` = union of `authorKeywords` and `indexKeywords`, deduped (case-insensitive), semicolon-separated.

#### Test T-M11: bothKeywords for Scopus paper

For paper `EID == "2-s2.0-test-alpha-2020-a"` with:
- `Author Keywords = "Alpha"`
- `Index Keywords = "Alpha index"`

| Column | Expected value |
|---|---|
| `bothKeywords` | `Alpha;Alpha index` |

#### Test T-M12: bothKeywords deduplication

Create one paper where `Author Keywords = "Gamma"` and `Index Keywords = "Gamma; Extra keyword"`.

| Column | Expected value |
|---|---|
| `bothKeywords` | `Gamma;Extra keyword` (Gamma not duplicated) |

### 4.8 Open Access Normalization Assertions

`paperUtils.normalizeOpenAccess` standardizes OA tags from WoS and Scopus into the format specified by `globalVar.SAVE_RESULTS_ON`. Since the default is `SCOPUS_FIELDS`, WoS OA values are converted to Scopus format.

**Mapping (WoS → Scopus):**

| WoS value | Scopus equivalent |
|---|---|
| `gold` | `Gold Open Access` |
| `hybrid` | `Hybrid Gold Open Access` |
| `Bronze` | `Bronze Open Access` |
| `Green Submitted` / `Green Accepted` / `Green Published` | `Green Open Access` |

Scopus output always includes the `All Open Access` prefix when any OA tag is present.

#### Test T-M16a: Scopus Gold OA preserved

Paper `EID == "2-s2.0-test-alpha-2020-a"` with `Open Access = "All Open Access; Gold Open Access"`:

| Column | Expected value |
|---|---|
| `Open Access` | `All Open Access; Gold Open Access` |

#### Test T-M16b: Scopus Green OA preserved

Paper `EID == "2-s2.0-test-alpha-2020-b"` with `Open Access = "All Open Access; Green Open Access"`:

| Column | Expected value |
|---|---|
| `Open Access` | `All Open Access; Green Open Access` |

#### Test T-M16c: WoS gold normalized to Scopus format

Paper `EID == "WOS:test-beta-2021-a"` with WoS `OA = "gold"`:

| Column | Expected value |
|---|---|
| `Open Access` | `All Open Access; Gold Open Access` |

#### Test T-M16d: WoS multi-value normalized to Scopus format

Paper `EID == "WOS:test-beta-2021-b"` with WoS `OA = "Green Submitted, hybrid"`:

| Column | Expected value |
|---|---|
| `Open Access` | `All Open Access; Green Open Access; Hybrid Gold Open Access` |

#### Test T-M16e: Empty OA stays empty

Paper `EID == "2-s2.0-test-alpha-2018-a"` with `Open Access = ""`:

| Column | Expected value |
|---|---|
| `Open Access` | *(empty string)* |

### 4.9 Document Type Omission Assertions

#### Test T-M13: Omitted papers absent from output

Assert that no row in `papersPreprocessed.csv` has `Document Type == "Book Chapter"`.

#### Test T-M14: All included document types present

Assert that all 28 remaining papers have a `Document Type` value that matches one of:
`Article`, `Conference Paper`, `Review`, `Proceedings Paper`, `Article in Press`

### 4.10 Source Distribution in Output

#### Test T-M15: Source field distribution

Count rows by the `Source` column:

| Source | Expected count |
|---|---|
| `Scopus` | 15 |
| `WoS` | 13 |
| Total | 28 |

> Note: Group D keeps the WoS version, so the 2 removed Scopus duplicates reduce the Scopus count from 17 to 15, while WoS keeps all 13 (the 2 removed WoS duplicates — if any — must be adjusted in the generator).

---

## 5. Test Runner Specification

### 4.1 Script: `tests/run_behavioral_tests.py`

**Responsibilities:**
1. Call `generate_test_data.py` to create `tests/dataInTest/`.
2. Change working directory to ScientoPy root (so output folders `dataPre/`, `results/` are created there, or use a temp dir).
3. Run `preProcess.py` via `subprocess` or by importing `PreProcessClass` directly.
4. Run `scientoPy.py` scenarios via `subprocess` or by importing `ScientoPyClass` directly.
5. Read output CSV files and assert expected values.
6. Print PASS / FAIL per test case.
7. Exit with code `0` if all tests pass, `1` if any fail.

### 4.2 Test isolation

Each test run should use a **temporary working directory** (e.g., `tempfile.mkdtemp()`) so that:
- `dataPre/`, `results/`, `graphs/` are not left behind.
- Tests do not interfere with each other.
- The real `dataPre/` and `results/` folders in the project root are not overwritten.

### 4.3 Test cases summary

| ID | Description | Command | File Checked | Key Assertion |
|---|---|---|---|---|
| T01 | Preprocess total papers | `preProcess.py` | `dataPre/papersPreprocessed.csv` | rows == 28 |
| T02 | Preprocess brief — loaded | `preProcess.py` | `dataPre/PreprocessedBrief.csv` | Loaded == 32 |
| T03 | Preprocess brief — omitted | `preProcess.py` | `dataPre/PreprocessedBrief.csv` | Omitted == 2 |
| T04 | Preprocess brief — duplicates | `preProcess.py` | `dataPre/PreprocessedBrief.csv` | After dedup == 28 |
| T05 | Top keywords total counts | `scientoPy.py -c authorKeywords` | `results/AuthorKeywords.csv` | ALPHA=10, BETA=8, GAMMA=6 |
| T06 | Keyword year distribution | `scientoPy.py -c authorKeywords` | `results/AuthorKeywords.csv` | ALPHA years 2018–2022 each == 2 |
| T07 | Omitted types absent | `scientoPy.py -c authorKeywords` | `results/AuthorKeywords.csv` | EPSILON not present |
| T08 | Country analysis | `scientoPy.py -c country` | `results/Country.csv` | US=10, Germany=8 |
| T09 | Institution analysis | `scientoPy.py -c institution` | `results/Institution.csv` | MIT=10, TU BERLIN=8 |
| T10 | Year range filter | `scientoPy.py -c authorKeywords --startYear 2021 --endYear 2023` | `results/AuthorKeywords.csv` | ALPHA=4, BETA=6 |
| T11 | Custom topic | `scientoPy.py -c authorKeywords -t "Alpha"` | `results/AuthorKeywords.csv` | Total=10, hIndex=10 |
| T12 | Database source | `scientoPy.py -c dataBase` | `results/DataBase.csv` | Scopus=15, WoS=13 |
| T13 | Previous results chaining | two-step command | `results/AuthorKeywords.csv` | Only ALPHA=10 |
| T-M01 | Scopus field mapping | `preProcess.py` | `dataPre/papersPreprocessed.csv` | EID `2-s2.0-test-alpha-2020-a` fields correct |
| T-M02 | WoS field mapping | `preProcess.py` | `dataPre/papersPreprocessed.csv` | EID `WOS:test-beta-2021-a` fields correct |
| T-M03 | Duplicate kept + marked | `preProcess.py` | `dataPre/papersPreprocessed.csv` | WoS kept, `duplicatedIn` has Scopus EID, citedBy averaged |
| T-M04 | Removed duplicate absent | `preProcess.py` | `dataPre/papersPreprocessed.csv` | Scopus EID of dup001 not in output |
| T-M05 | Duplicate count | `preProcess.py` | `dataPre/papersPreprocessed.csv` | 2 rows with non-empty `duplicatedIn` |
| T-M06 | Country from Scopus | `preProcess.py` | `dataPre/papersPreprocessed.csv` | `country == "United States"` |
| T-M07 | Country from WoS | `preProcess.py` | `dataPre/papersPreprocessed.csv` | `country == "Germany"` |
| T-M08 | Multiple countries | `preProcess.py` | `dataPre/papersPreprocessed.csv` | `country == "Brazil;United States"` |
| T-M09 | Institution from WoS | `preProcess.py` | `dataPre/papersPreprocessed.csv` | `institution == "TU Berlin"` |
| T-M10 | Institution empty for Scopus | `preProcess.py` | `dataPre/papersPreprocessed.csv` | `institution == ""` |
| T-M11 | bothKeywords union | `preProcess.py` | `dataPre/papersPreprocessed.csv` | `bothKeywords == "Alpha;Alpha index"` |
| T-M12 | bothKeywords dedup | `preProcess.py` | `dataPre/papersPreprocessed.csv` | Gamma not doubled |
| T-M13 | Omitted types absent | `preProcess.py` | `dataPre/papersPreprocessed.csv` | No `Book Chapter` rows |
| T-M14 | Valid document types | `preProcess.py` | `dataPre/papersPreprocessed.csv` | All 28 rows have included doc type |
| T-M15 | Source distribution | `preProcess.py` | `dataPre/papersPreprocessed.csv` | Scopus=15, WoS=13 |
| T-M16 | OA normalization | `preProcess.py` | `dataPre/papersPreprocessed.csv` | WoS OA tags normalized to Scopus format |

---

## 5. File Structure

```
ScientoPy/
├── doc/
│   └── behavioral_test_spec.md      ← this file
├── tests/
│   ├── generate_test_data.py        ← creates synthetic WoS + Scopus files
│   └── run_behavioral_tests.py      ← executes pipeline and asserts results
```

---

## 6. Implementation Notes

### Affiliations format for country/institution extraction

ScientoPy extracts `country` and `institution` from the `Affiliations` field in Scopus or `C1` in WoS.

**Scopus affiliations format:**
```
Author Name, Institution Name, City, Country; Author Name 2, Institution 2, City, Country
```
Example: `Smith J., MIT, Cambridge, United States; Jones A., MIT, Cambridge, United States`

**WoS C1 format:**
```
[Author Name] Institution Name, City, Country
```
Example: `[Smith, John] MIT, Cambridge, MA, United States`

The generator must use these formats so that `paperUtils` correctly extracts `country` and `institution` fields.

### Duplicate detection

`paperUtils.removeDuplicates` matches papers by **DOI** (case-insensitive, normalized). The Group D papers must have identical DOI values in both Scopus and WoS records to trigger deduplication.

### Document type mapping

WoS `DT` field uses different type names than Scopus `Document Type`. The generator must use the exact strings that ScientoPy's `docType` matching logic recognizes as included types (see `globalVar.INCLUDED_TYPES` and the matching logic in `paperUtils`).
