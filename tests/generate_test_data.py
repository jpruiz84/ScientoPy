#!/usr/bin/env python3

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

"""
Generates synthetic Scopus CSV and WoS TXT files with fully controlled content
for behavioral testing of ScientoPy.

See doc/behavioral_test_spec.md for the dataset design.
"""

import csv
import os


def generate(output_dir):
    """Generate test_scopus.csv and test_wos.txt in output_dir."""
    os.makedirs(output_dir, exist_ok=True)

    scopus_papers = []
    wos_papers = []

    # ── Group A: "Alpha" — 10 papers, Scopus only, 2018–2022 ──
    # OA values: 2020-A=Gold, 2020-B=Green, rest empty
    paper_idx = 0
    for year in [2018, 2019, 2020, 2021, 2022]:
        for suffix in ["A", "B"]:
            paper_idx += 1
            oa = ""
            if year == 2020 and suffix == "A":
                oa = "All Open Access; Gold Open Access"
            elif year == 2020 and suffix == "B":
                oa = "All Open Access; Green Open Access"
            scopus_papers.append({
                "Authors": "Smith, J.",
                "Title": f"Alpha Paper {year} {suffix}",
                "Year": str(year),
                "Source title": "Journal of Alpha",
                "Volume": "1",
                "Issue": "1",
                "Art. No.": "",
                "Page start": "1",
                "Page end": "10",
                "Cited by": "10",
                "DOI": f"10.0001/alpha-{year}-{suffix.lower()}",
                "Link": "",
                "Affiliations": "MIT, Cambridge, United States",
                "Authors with affiliations": "Smith, J., MIT, Cambridge, United States",
                "Abstract": f"Abstract for alpha paper {year} {suffix}",
                "Author Keywords": "Alpha",
                "Index Keywords": "Alpha index",
                "Document Type": "Article",
                "Open Access": oa,
                "Source": "Scopus",
                "EID": f"2-s2.0-test-alpha-{year}-{suffix.lower()}",
            })

    # ── Group B: "Beta" — 8 papers, WoS only, 2020–2023 ──
    # OA values: 2021-A=gold, 2021-B="Green Submitted, hybrid", rest empty
    for year in [2020, 2021, 2022, 2023]:
        for suffix in ["A", "B"]:
            oa = ""
            if year == 2021 and suffix == "A":
                oa = "gold"
            elif year == 2021 and suffix == "B":
                oa = "Green Submitted, hybrid"
            wos_papers.append({
                "PT": "J",
                "AU": "Muller, H.",
                "AF": "Muller, Hans",
                "TI": f"Beta Paper {year} {suffix}",
                "SO": "Journal of Beta",
                "LA": "English",
                "DT": "Article",
                "DE": "Beta",
                "ID": "Beta index",
                "AB": f"Abstract for beta paper {year} {suffix}",
                "C1": f"[Muller, Hans] TU Berlin, Berlin, Germany",
                "OA": oa,
                "Z9": "5",
                "PY": str(year),
                "DI": f"10.0002/beta-{year}-{suffix.lower()}",
                "SC": "Science",
                "UT": f"WOS:test-beta-{year}-{suffix.lower()}",
            })

    # ── Group C: "Gamma" — 6 papers, split 3 Scopus + 3 WoS, 2021–2023 ──
    # One Scopus and one WoS per year
    for year in [2021, 2022, 2023]:
        # Scopus version — use multi-country affiliation for 2021 paper (T-M08)
        if year == 2021:
            affiliations = "USP, Sao Paulo, Brazil; MIT, Cambridge, United States"
        else:
            affiliations = "USP, Sao Paulo, Brazil"

        # For T-M12: paper with year 2021 gets Index Keywords "Gamma; Extra keyword"
        if year == 2021:
            index_kw = "Gamma; Extra keyword"
        else:
            index_kw = ""

        scopus_papers.append({
            "Authors": "Silva, M.",
            "Title": f"Gamma Paper {year} Scopus",
            "Year": str(year),
            "Source title": "Journal of Gamma",
            "Volume": "2",
            "Issue": "1",
            "Art. No.": "",
            "Page start": "1",
            "Page end": "5",
            "Cited by": "2",
            "DOI": f"10.0003/gamma-{year}-scopus",
            "Link": "",
            "Affiliations": affiliations,
            "Authors with affiliations": f"Silva, M., {affiliations}",
            "Abstract": f"Abstract for gamma paper {year} scopus",
            "Author Keywords": "Gamma",
            "Index Keywords": index_kw,
            "Document Type": "Conference Paper",
            "Source": "Scopus",
            "EID": f"2-s2.0-test-gamma-{year}-scopus",
        })

        # WoS version
        wos_papers.append({
            "PT": "J",
            "AU": "Silva, M.",
            "AF": "Silva, Maria",
            "TI": f"Gamma Paper {year} WoS",
            "SO": "Conf of Gamma",
            "LA": "English",
            "DT": "Proceedings Paper",
            "DE": "Gamma",
            "ID": "",
            "AB": f"Abstract for gamma paper {year} wos",
            "C1": f"[Silva, Maria] USP, Sao Paulo, Brazil",
            "Z9": "2",
            "PY": str(year),
            "DI": f"10.0003/gamma-{year}-wos",
            "SC": "Science",
            "UT": f"WOS:test-gamma-{year}-wos",
        })

    # ── Group D: Duplicates — 2 Scopus + 2 WoS with same DOI ──
    for dup_num, year in [(1, 2022), (2, 2023)]:
        doi = f"10.0000/dup{dup_num:03d}"
        scopus_papers.append({
            "Authors": "Dupont, A.",
            "Title": f"Delta Duplicate Paper {year}",
            "Year": str(year),
            "Source title": "Journal of Delta",
            "Volume": "3",
            "Issue": "1",
            "Art. No.": "",
            "Page start": "1",
            "Page end": "8",
            "Cited by": "20",
            "DOI": doi,
            "Link": "",
            "Affiliations": "Sorbonne, Paris, France",
            "Authors with affiliations": "Dupont, A., Sorbonne, Paris, France",
            "Abstract": f"Abstract for delta duplicate {year}",
            "Author Keywords": "Delta",
            "Index Keywords": "",
            "Document Type": "Article",
            "Source": "Scopus",
            "EID": f"2-s2.0-test-dup{dup_num:03d}",
        })

        wos_papers.append({
            "PT": "J",
            "AU": "Dupont, A.",
            "AF": "Dupont, Antoine",
            "TI": f"Delta Duplicate Paper {year}",
            "SO": "Journal of Delta",
            "LA": "English",
            "DT": "Article",
            "DE": "Delta",
            "ID": "",
            "AB": f"Abstract for delta duplicate {year}",
            "C1": f"[Dupont, Antoine] Sorbonne, Paris, France",
            "Z9": "10",
            "PY": str(year),
            "DI": doi,
            "SC": "Science",
            "UT": f"WOS:test-dup{dup_num:03d}",
        })

    # ── Group E: Omitted document types — 2 Scopus papers ──
    for i in [1, 2]:
        scopus_papers.append({
            "Authors": "Omit, X.",
            "Title": f"Epsilon Paper {i}",
            "Year": "2022",
            "Source title": "Book of Epsilon",
            "Volume": "1",
            "Issue": "1",
            "Art. No.": "",
            "Page start": "1",
            "Page end": "20",
            "Cited by": "0",
            "DOI": f"10.9999/epsilon-{i}",
            "Link": "",
            "Affiliations": "Unknown Inst, Unknown City, Unknown Country",
            "Authors with affiliations": "",
            "Abstract": f"Abstract epsilon {i}",
            "Author Keywords": "Epsilon",
            "Index Keywords": "",
            "Document Type": "Book Chapter",
            "Source": "Scopus",
            "EID": f"2-s2.0-test-epsilon-{i}",
        })

    # ── Write Scopus CSV ──
    scopus_header = [
        "Authors", "Title", "Year", "Source title", "Volume", "Issue",
        "Art. No.", "Page start", "Page end", "Cited by", "DOI", "Link",
        "Affiliations", "Authors with affiliations", "Abstract",
        "Author Keywords", "Index Keywords", "Document Type",
        "Open Access", "Source", "EID",
    ]

    scopus_path = os.path.join(output_dir, "test_scopus.csv")
    with open(scopus_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=scopus_header, extrasaction="ignore")
        writer.writeheader()
        for paper in scopus_papers:
            writer.writerow(paper)

    # ── Write WoS TXT (tab-delimited) ──
    wos_header = [
        "PT", "AU", "AF", "TI", "SO", "LA", "DT", "DE", "ID", "AB",
        "C1", "OA", "Z9", "PY", "DI", "SC", "UT",
    ]

    wos_path = os.path.join(output_dir, "test_wos.txt")
    with open(wos_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=wos_header, delimiter="\t", extrasaction="ignore"
        )
        writer.writeheader()
        for paper in wos_papers:
            writer.writerow(paper)

    print(f"Generated {len(scopus_papers)} Scopus papers in {scopus_path}")
    print(f"Generated {len(wos_papers)} WoS papers in {wos_path}")
    return scopus_path, wos_path


if __name__ == "__main__":
    generate(os.path.join(os.path.dirname(__file__), "dataInTest"))
