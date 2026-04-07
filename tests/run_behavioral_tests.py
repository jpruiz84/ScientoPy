#!/usr/bin/env python3
"""
Behavioral test runner for ScientoPy.

Generates synthetic data, runs the ScientoPy pipeline, and asserts that
actual outputs match the expected values defined in doc/behavioral_test_spec.md.

Usage:
    python tests/run_behavioral_tests.py
"""

import csv
import os
import shutil
import subprocess
import sys
import tempfile

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from tests.generate_test_data import generate

# ── Helpers ──

passed = 0
failed = 0
errors = []


def check(test_id, description, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {test_id}: {description}")
    else:
        failed += 1
        msg = f"  FAIL  {test_id}: {description}"
        if detail:
            msg += f" — {detail}"
        print(msg)
        errors.append(msg)


def read_csv(path):
    """Read a CSV file and return list of dicts."""
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def read_brief(path):
    """Read PreprocessedBrief.csv and return dict of Info -> Number."""
    rows = read_csv(path)
    return {row["Info"].strip(): row.get("Number", "").strip() for row in rows}


def run_cmd(cmd, cwd):
    """Run a command in cwd and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"    CMD FAILED: {' '.join(cmd)}")
        print(f"    STDOUT: {result.stdout[-500:]}")
        print(f"    STDERR: {result.stderr[-500:]}")
    return result


def find_row(rows, column, value):
    """Find first row where column matches value."""
    for row in rows:
        if row.get(column, "").strip() == value:
            return row
    return None


def get_topic_row(rows, criterion_col, topic_name):
    """Find a row in results CSV by topic name (case-insensitive)."""
    for row in rows:
        if row.get(criterion_col, "").strip().upper() == topic_name.upper():
            return row
    return None


# ── Main ──

def main():
    global passed, failed

    # Generate test data into tmp_test_data/; run scripts from there using PROJECT_ROOT paths
    test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp_test_data")
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir)
    data_in_dir = os.path.join(test_data_dir, "dataInTest")
    work_dir = test_data_dir  # cwd for subprocess calls — outputs land here

    print(f"Test data directory: {test_data_dir}")
    print(f"Project root: {PROJECT_ROOT}")

    try:
        # Generate test data
        print("\n=== Generating test data ===")
        generate(data_in_dir)

        python = sys.executable

        # ── Stage 1: preProcess ──
        print("\n=== Stage 1: preProcess ===")
        result = run_cmd(
            [python, os.path.join(PROJECT_ROOT, "preProcess.py"),
             "dataInTest", "--savePlot", "test.png"],
            cwd=work_dir,
        )

        preprocessed_path = os.path.join(work_dir, "dataPre", "papersPreprocessed.csv")
        brief_path = os.path.join(work_dir, "dataPre", "PreprocessedBrief.csv")

        # ── T01: Total papers after dedup ──
        print("\n--- Preprocess tests ---")
        if os.path.isfile(preprocessed_path):
            papers = read_csv(preprocessed_path)
            # 30 papers loaded, 2 omitted (Group E), 2 deduped (Group D Scopus) = 26
            check("T01", "Preprocess total papers == 26", len(papers) == 26,
                  f"got {len(papers)}")
        else:
            check("T01", "papersPreprocessed.csv exists", False, "file not found")
            papers = []

        # ── T02–T04: Brief file checks ──
        if os.path.isfile(brief_path):
            brief = read_brief(brief_path)

            # 17 Scopus + 13 WoS = 30 total input papers
            check("T02", "Brief: Loaded papers == 30",
                  brief.get("Loaded papers") == "30",
                  f"got {brief.get('Loaded papers')}")

            check("T03", "Brief: Omitted papers == 2",
                  brief.get("Omitted papers by document type") == "2",
                  f"got {brief.get('Omitted papers by document type')}")

            # 30 loaded - 2 omitted (Group E Book Chapter) = 28
            check("T04", "Brief: Total after omit == 28",
                  brief.get("Total papers after omitted papers removed") == "28",
                  f"got {brief.get('Total papers after omitted papers removed')}")
        else:
            for tid in ["T02", "T03", "T04"]:
                check(tid, "PreprocessedBrief.csv exists", False, "file not found")

        # ── T-M01: Scopus field mapping ──
        print("\n--- Field mapping tests ---")
        if papers:
            s1 = find_row(papers, "EID", "2-s2.0-test-alpha-2020-a")
            if s1:
                check("T-M01a", "Scopus: Title", s1["Title"] == "Alpha Paper 2020 A",
                      f"got '{s1['Title']}'")
                check("T-M01b", "Scopus: Year", s1["Year"] == "2020",
                      f"got '{s1['Year']}'")
                check("T-M01c", "Scopus: Author Keywords", s1["Author Keywords"] == "Alpha",
                      f"got '{s1['Author Keywords']}'")
                check("T-M01d", "Scopus: Index Keywords", s1["Index Keywords"] == "Alpha index",
                      f"got '{s1['Index Keywords']}'")
                check("T-M01e", "Scopus: Cited by", s1["Cited by"] == "10",
                      f"got '{s1['Cited by']}'")
                check("T-M01f", "Scopus: DOI", s1["DOI"] == "10.0001/alpha-2020-a",
                      f"got '{s1['DOI']}'")
                check("T-M01g", "Scopus: Document Type", s1["Document Type"] == "Article",
                      f"got '{s1['Document Type']}'")
                check("T-M01h", "Scopus: Source", s1["Source"] == "Scopus",
                      f"got '{s1['Source']}'")
                check("T-M01i", "Scopus: duplicatedIn empty",
                      s1.get("duplicatedIn", "").strip() == "",
                      f"got '{s1.get('duplicatedIn', '')}'")
            else:
                check("T-M01", "Scopus ref paper found", False, "EID 2-s2.0-test-alpha-2020-a not found")

            # ── T-M02: WoS field mapping ──
            w1 = find_row(papers, "EID", "WOS:test-beta-2021-a")
            if w1:
                check("T-M02a", "WoS: Title", w1["Title"] == "Beta Paper 2021 A",
                      f"got '{w1['Title']}'")
                check("T-M02b", "WoS: Year", w1["Year"] == "2021",
                      f"got '{w1['Year']}'")
                check("T-M02c", "WoS: Author Keywords", w1["Author Keywords"] == "Beta",
                      f"got '{w1['Author Keywords']}'")
                check("T-M02d", "WoS: Index Keywords", w1["Index Keywords"] == "Beta index",
                      f"got '{w1['Index Keywords']}'")
                check("T-M02e", "WoS: Cited by", w1["Cited by"] == "5",
                      f"got '{w1['Cited by']}'")
                check("T-M02f", "WoS: DOI", w1["DOI"] == "10.0002/beta-2021-a",
                      f"got '{w1['DOI']}'")
                check("T-M02g", "WoS: Document Type", w1["Document Type"] == "Article",
                      f"got '{w1['Document Type']}'")
                check("T-M02h", "WoS: Source", w1["Source"] == "WoS",
                      f"got '{w1['Source']}'")
                check("T-M02i", "WoS: duplicatedIn empty",
                      w1.get("duplicatedIn", "").strip() == "",
                      f"got '{w1.get('duplicatedIn', '')}'")
            else:
                check("T-M02", "WoS ref paper found", False, "EID WOS:test-beta-2021-a not found")

            # ── T-M03: Duplicate kept and marked ──
            print("\n--- Duplicate tests ---")
            d1 = find_row(papers, "DOI", "10.0000/dup001")
            if d1:
                check("T-M03a", "Dup kept: Source == WoS", d1["Source"] == "WoS",
                      f"got '{d1['Source']}'")
                check("T-M03b", "Dup kept: EID is WoS", d1["EID"] == "WOS:test-dup001",
                      f"got '{d1['EID']}'")
                check("T-M03c", "Dup kept: duplicatedIn has Scopus EID",
                      "2-s2.0-test-dup001" in d1.get("duplicatedIn", ""),
                      f"got '{d1.get('duplicatedIn', '')}'")
                # Cited by: average of 20 and 10 = 15
                check("T-M03d", "Dup kept: Cited by averaged",
                      d1["Cited by"] == "15",
                      f"got '{d1['Cited by']}'")
            else:
                check("T-M03", "Duplicate DOI 10.0000/dup001 found", False, "not found")

            # ── T-M04: Removed duplicate absent ──
            scopus_dup = find_row(papers, "EID", "2-s2.0-test-dup001")
            check("T-M04", "Removed Scopus duplicate absent", scopus_dup is None,
                  "Scopus EID still present" if scopus_dup else "")

            # ── T-M05: Duplicate count ──
            dup_count = sum(1 for p in papers if p.get("duplicatedIn", "").strip() != "")
            check("T-M05", "Rows with duplicatedIn == 2", dup_count == 2,
                  f"got {dup_count}")

            # ── T-M06: Country from Scopus ──
            print("\n--- Country/Institution tests ---")
            if s1:
                check("T-M06", "Country from Scopus: United States",
                      s1.get("country", "") == "United States",
                      f"got '{s1.get('country', '')}'")

            # ── T-M07: Country from WoS ──
            if w1:
                check("T-M07", "Country from WoS: Germany",
                      w1.get("country", "") == "Germany",
                      f"got '{w1.get('country', '')}'")

            # ── T-M08: Multiple countries ──
            gamma_2021 = find_row(papers, "EID", "2-s2.0-test-gamma-2021-scopus")
            if gamma_2021:
                expected_countries = "Brazil;United States"
                check("T-M08", "Multiple countries in one paper",
                      gamma_2021.get("country", "") == expected_countries,
                      f"got '{gamma_2021.get('country', '')}'")
            else:
                check("T-M08", "Gamma 2021 Scopus paper found", False, "not found")

            # ── T-M09: Institution from WoS ──
            if w1:
                check("T-M09a", "Institution from WoS: TU Berlin",
                      w1.get("institution", "") == "TU Berlin",
                      f"got '{w1.get('institution', '')}'")
                check("T-M09b", "institutionWithCountry from WoS",
                      w1.get("institutionWithCountry", "") == "TU Berlin, Germany",
                      f"got '{w1.get('institutionWithCountry', '')}'")

            # ── T-M10: Institution empty for Scopus ──
            if s1:
                check("T-M10a", "Institution empty for Scopus",
                      s1.get("institution", "") == "",
                      f"got '{s1.get('institution', '')}'")
                check("T-M10b", "institutionWithCountry empty for Scopus",
                      s1.get("institutionWithCountry", "") == "",
                      f"got '{s1.get('institutionWithCountry', '')}'")

            # ── T-M11: bothKeywords union ──
            print("\n--- Keywords tests ---")
            if s1:
                check("T-M11", "bothKeywords for Scopus paper",
                      s1.get("bothKeywords", "") == "Alpha;Alpha index",
                      f"got '{s1.get('bothKeywords', '')}'")

            # ── T-M12: bothKeywords dedup ──
            if gamma_2021:
                bk = gamma_2021.get("bothKeywords", "")
                gamma_count = bk.upper().split(";").count("GAMMA")
                check("T-M12", "bothKeywords dedup (Gamma not doubled)",
                      gamma_count <= 1,
                      f"got '{bk}' (Gamma appears {gamma_count} times)")

            # ── T-M13: Omitted types absent ──
            print("\n--- Document type tests ---")
            book_chapters = [p for p in papers if p.get("Document Type", "") == "Book Chapter"]
            check("T-M13", "No Book Chapter in output", len(book_chapters) == 0,
                  f"found {len(book_chapters)}")

            # ── T-M14: Valid document types ──
            valid_types = {"Article", "Conference Paper", "Review", "Proceedings Paper", "Article in Press"}
            all_valid = all(p.get("Document Type", "") in valid_types for p in papers)
            check("T-M14", "All papers have valid document type", all_valid)

            # ── T-M15: Source distribution ──
            scopus_count = sum(1 for p in papers if p.get("Source", "") == "Scopus")
            wos_count = sum(1 for p in papers if p.get("Source", "") == "WoS")
            # After dedup: 15 Scopus - 2 removed (Group D) = 13 Scopus, 13 WoS unchanged
            check("T-M15a", "Source: Scopus count == 13", scopus_count == 13,
                  f"got {scopus_count}")
            check("T-M15b", "Source: WoS count == 13", wos_count == 13,
                  f"got {wos_count}")

            # ── T-M16: Open Access normalization ──
            print("\n--- Open Access normalization tests ---")
            # Scopus Gold stays as Scopus format (SAVE_RESULTS_ON = SCOPUS_FIELDS)
            s_gold = find_row(papers, "EID", "2-s2.0-test-alpha-2020-a")
            if s_gold:
                check("T-M16a", "Scopus Gold OA preserved",
                      s_gold.get("Open Access", "") == "All Open Access; Gold Open Access",
                      f"got '{s_gold.get('Open Access', '')}'")

            # Scopus Green stays as Scopus format
            s_green = find_row(papers, "EID", "2-s2.0-test-alpha-2020-b")
            if s_green:
                check("T-M16b", "Scopus Green OA preserved",
                      s_green.get("Open Access", "") == "All Open Access; Green Open Access",
                      f"got '{s_green.get('Open Access', '')}'")

            # WoS "gold" normalized to Scopus format
            w_gold = find_row(papers, "EID", "WOS:test-beta-2021-a")
            if w_gold:
                check("T-M16c", "WoS gold -> Scopus Gold Open Access",
                      w_gold.get("Open Access", "") == "All Open Access; Gold Open Access",
                      f"got '{w_gold.get('Open Access', '')}'")

            # WoS "Green Submitted, hybrid" normalized to Scopus format
            w_multi = find_row(papers, "EID", "WOS:test-beta-2021-b")
            if w_multi:
                check("T-M16d", "WoS Green+hybrid -> Scopus format",
                      w_multi.get("Open Access", "") == "All Open Access; Green Open Access; Hybrid Gold Open Access",
                      f"got '{w_multi.get('Open Access', '')}'")

            # Empty OA stays empty
            s_empty = find_row(papers, "EID", "2-s2.0-test-alpha-2018-a")
            if s_empty:
                check("T-M16e", "Empty OA stays empty",
                      s_empty.get("Open Access", "").strip() == "",
                      f"got '{s_empty.get('Open Access', '')}'")

        # ── Stage 2: scientoPy analyses ──

        # T05–T07: authorKeywords default
        print("\n=== Stage 2: scientoPy authorKeywords ===")
        run_cmd([python, os.path.join(PROJECT_ROOT, "scientoPy.py"), "-c", "authorKeywords", "--noPlot"], cwd=work_dir)
        ak_path = os.path.join(work_dir, "results", "AuthorKeywords.csv")
        if os.path.isfile(ak_path):
            ak_rows = read_csv(ak_path)

            alpha_row = get_topic_row(ak_rows, "AuthorKeywords", "ALPHA")
            beta_row = get_topic_row(ak_rows, "AuthorKeywords", "BETA")
            gamma_row = get_topic_row(ak_rows, "AuthorKeywords", "GAMMA")
            delta_row = get_topic_row(ak_rows, "AuthorKeywords", "DELTA")

            check("T05a", "ALPHA total == 10",
                  alpha_row and int(alpha_row["Total"]) == 10,
                  f"got {alpha_row['Total']}" if alpha_row else "not found")
            check("T05b", "BETA total == 8",
                  beta_row and int(beta_row["Total"]) == 8,
                  f"got {beta_row['Total']}" if beta_row else "not found")
            check("T05c", "GAMMA total == 6",
                  gamma_row and int(gamma_row["Total"]) == 6,
                  f"got {gamma_row['Total']}" if gamma_row else "not found")
            check("T05d", "DELTA total == 2",
                  delta_row and int(delta_row["Total"]) == 2,
                  f"got {delta_row['Total']}" if delta_row else "not found")

            # T06: Year distribution for ALPHA
            if alpha_row:
                for y in [2018, 2019, 2020, 2021, 2022]:
                    val = alpha_row.get(str(y), "0")
                    check(f"T06-{y}", f"ALPHA {y} == 2",
                          int(float(val)) == 2, f"got {val}")

            # T07: EPSILON absent
            epsilon_row = get_topic_row(ak_rows, "AuthorKeywords", "EPSILON")
            check("T07", "EPSILON not in authorKeywords", epsilon_row is None)
        else:
            for tid in ["T05a", "T05b", "T05c", "T05d", "T06", "T07"]:
                check(tid, "AuthorKeywords.csv exists", False, "file not found")

        # T08: Country analysis
        print("\n=== Stage 2: country ===")
        run_cmd([python, os.path.join(PROJECT_ROOT, "scientoPy.py"), "-c", "country", "--noPlot"], cwd=work_dir)
        country_path = os.path.join(work_dir, "results", "Country.csv")
        if os.path.isfile(country_path):
            c_rows = read_csv(country_path)
            us_row = get_topic_row(c_rows, "Country", "UNITED STATES")
            de_row = get_topic_row(c_rows, "Country", "GERMANY")
            br_row = get_topic_row(c_rows, "Country", "BRAZIL")
            fr_row = get_topic_row(c_rows, "Country", "FRANCE")

            # 10 Alpha + 1 Gamma-2021 (multi-country: Brazil;United States) = 11
            check("T08a", "US total == 11",
                  us_row and int(us_row["Total"]) == 11,
                  f"got {us_row['Total']}" if us_row else "not found")
            check("T08b", "Germany total == 8",
                  de_row and int(de_row["Total"]) == 8,
                  f"got {de_row['Total']}" if de_row else "not found")
            check("T08c", "Brazil total == 6",
                  br_row and int(br_row["Total"]) == 6,
                  f"got {br_row['Total']}" if br_row else "not found")
            check("T08d", "France total == 2",
                  fr_row and int(fr_row["Total"]) == 2,
                  f"got {fr_row['Total']}" if fr_row else "not found")
        else:
            check("T08", "Country.csv exists", False, "file not found")

        # T09: Institution analysis
        print("\n=== Stage 2: institution ===")
        run_cmd([python, os.path.join(PROJECT_ROOT, "scientoPy.py"), "-c", "institution", "--noPlot"], cwd=work_dir)
        inst_path = os.path.join(work_dir, "results", "Institution.csv")
        if os.path.isfile(inst_path):
            i_rows = read_csv(inst_path)
            mit_row = get_topic_row(i_rows, "Institution", "MIT")
            tu_row = get_topic_row(i_rows, "Institution", "TU BERLIN")
            usp_row = get_topic_row(i_rows, "Institution", "USP")

            # Institution extraction is WoS-only in ScientoPy, so MIT (Scopus) won't appear
            # Only WoS institutions: TU BERLIN (8), USP (3 WoS gamma), Sorbonne (2 WoS dup)
            check("T09a", "TU BERLIN total == 8",
                  tu_row and int(tu_row["Total"]) == 8,
                  f"got {tu_row['Total']}" if tu_row else "not found")
            check("T09b", "USP total == 3",
                  usp_row and int(usp_row["Total"]) == 3,
                  f"got {usp_row['Total']}" if usp_row else "not found")
        else:
            check("T09", "Institution.csv exists", False, "file not found")

        # T10: Year range filter
        print("\n=== Stage 2: authorKeywords with year range ===")
        run_cmd([python, os.path.join(PROJECT_ROOT, "scientoPy.py"), "-c", "authorKeywords",
                 "--startYear", "2021", "--endYear", "2023", "--noPlot"], cwd=work_dir)
        if os.path.isfile(ak_path):
            ak_rows2 = read_csv(ak_path)
            alpha2 = get_topic_row(ak_rows2, "AuthorKeywords", "ALPHA")
            beta2 = get_topic_row(ak_rows2, "AuthorKeywords", "BETA")
            gamma2 = get_topic_row(ak_rows2, "AuthorKeywords", "GAMMA")

            check("T10a", "ALPHA in 2021-2023 == 4",
                  alpha2 and int(alpha2["Total"]) == 4,
                  f"got {alpha2['Total']}" if alpha2 else "not found")
            check("T10b", "BETA in 2021-2023 == 6",
                  beta2 and int(beta2["Total"]) == 6,
                  f"got {beta2['Total']}" if beta2 else "not found")
            check("T10c", "GAMMA in 2021-2023 == 6",
                  gamma2 and int(gamma2["Total"]) == 6,
                  f"got {gamma2['Total']}" if gamma2 else "not found")
        else:
            check("T10", "AuthorKeywords.csv exists (year range)", False, "file not found")

        # T11: Custom topic with hIndex
        print("\n=== Stage 2: custom topic Alpha ===")
        run_cmd([python, os.path.join(PROJECT_ROOT, "scientoPy.py"), "-c", "authorKeywords", "-t", "Alpha", "--noPlot"],
                cwd=work_dir)
        if os.path.isfile(ak_path):
            ak_rows3 = read_csv(ak_path)
            check("T11a", "Only 1 row for custom topic Alpha", len(ak_rows3) == 1,
                  f"got {len(ak_rows3)} rows")
            if ak_rows3:
                row = ak_rows3[0]
                check("T11b", "Alpha total == 10", int(row["Total"]) == 10,
                      f"got {row['Total']}")
                check("T11c", "Alpha hIndex == 10", int(row["hIndex"]) == 10,
                      f"got {row['hIndex']}")
        else:
            check("T11", "AuthorKeywords.csv exists (custom topic)", False, "file not found")

        # T12: Database source
        print("\n=== Stage 2: dataBase ===")
        run_cmd([python, os.path.join(PROJECT_ROOT, "scientoPy.py"), "-c", "dataBase", "--noPlot"], cwd=work_dir)
        db_path = os.path.join(work_dir, "results", "DataBase.csv")
        if os.path.isfile(db_path):
            db_rows = read_csv(db_path)
            scopus_r = get_topic_row(db_rows, "DataBase", "SCOPUS")
            wos_r = get_topic_row(db_rows, "DataBase", "WOS")

            # After dedup: 13 Scopus, 13 WoS
            check("T12a", "SCOPUS total == 13",
                  scopus_r and int(scopus_r["Total"]) == 13,
                  f"got {scopus_r['Total']}" if scopus_r else "not found")
            check("T12b", "WOS total == 13",
                  wos_r and int(wos_r["Total"]) == 13,
                  f"got {wos_r['Total']}" if wos_r else "not found")
        else:
            check("T12", "DataBase.csv exists", False, "file not found")

        # T13: Previous results chaining
        print("\n=== Stage 2: previous results chaining ===")
        # Step 1: filter country = United States
        run_cmd([python, os.path.join(PROJECT_ROOT, "scientoPy.py"), "-c", "country", "-t", "United States", "--noPlot"],
                cwd=work_dir)
        # Step 2: analyze authorKeywords from previous results
        run_cmd([python, os.path.join(PROJECT_ROOT, "scientoPy.py"), "-c", "authorKeywords", "-r", "--noPlot"],
                cwd=work_dir)
        if os.path.isfile(ak_path):
            ak_rows4 = read_csv(ak_path)
            # Only Alpha papers have country United States (plus gamma 2021 multi-country)
            alpha4 = get_topic_row(ak_rows4, "AuthorKeywords", "ALPHA")
            beta4 = get_topic_row(ak_rows4, "AuthorKeywords", "BETA")

            check("T13a", "Previous results: ALPHA present",
                  alpha4 is not None)
            if alpha4:
                check("T13b", "Previous results: ALPHA total == 10",
                      int(alpha4["Total"]) == 10,
                      f"got {alpha4['Total']}")
            check("T13c", "Previous results: BETA absent", beta4 is None,
                  f"BETA found with total {beta4['Total']}" if beta4 else "")
        else:
            check("T13", "AuthorKeywords.csv exists (chaining)", False, "file not found")

    finally:
        print(f"\nTest data preserved in: {work_dir}")

    # ── Summary ──
    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    if errors:
        print("\nFailures:")
        for e in errors:
            print(e)
    print(f"{'=' * 50}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
