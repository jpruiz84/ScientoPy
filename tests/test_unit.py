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

"""Unit tests for ScientoPy core functions."""

import os
import sys
import csv
import tempfile
import shutil

import pytest

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import globalVar
import paperUtils


class TestGlobalVarConstants:
    """Verify globalVar constants are defined correctly."""

    def test_version_format(self):
        parts = globalVar.SCIENTOPY_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_valid_criterion_not_empty(self):
        assert len(globalVar.validCriterion) > 0
        assert "authorKeywords" in globalVar.validCriterion

    def test_valid_graph_types(self):
        assert "bar_trends" in globalVar.validGrapTypes
        assert "word_cloud" in globalVar.validGrapTypes

    def test_colors_have_100_entries(self):
        assert len(globalVar.COLORS_TAB10) >= 100
        assert len(globalVar.COLORS_TAB20) >= 100

    def test_markers_have_enough_entries(self):
        assert len(globalVar.MARKERS) >= 100

    def test_default_years(self):
        assert globalVar.DEFAULT_START_YEAR == 1990
        assert globalVar.DEFAULT_END_YEAR > 2020


class TestSourcesStatics:
    """Test sourcesStatics function."""

    def _make_paper(self, doc_type, db):
        return {"documentType": doc_type, "dataBase": db}

    def test_counts_by_type(self):
        papers = [
            self._make_paper("Article", "Scopus"),
            self._make_paper("Article", "WoS"),
            self._make_paper("Review", "Scopus"),
        ]

        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["Source", "Conference Paper",
                                "Article", "Review", "Proceedings Paper",
                                "Article in Press", "Total"])

        paperUtils.sourcesStatics(papers, writer)
        output.seek(0)
        rows = list(csv.DictReader(output, fieldnames=["Source", "Conference Paper",
                                   "Article", "Review", "Proceedings Paper",
                                   "Article in Press", "Total"]))
        # Should produce 2 rows (WoS and Scopus)
        assert len(rows) == 2


class TestRemoveDuplicates:
    """Test the deduplication logic."""

    def _make_paper(self, title, author, year, doi="", eid="", db="Scopus", cited=0):
        return {
            "title": title,
            "author": author,
            "year": str(year),
            "doi": doi,
            "eid": eid,
            "dataBase": db,
            "citedBy": str(cited),
            "duplicatedIn": [],
            "documentType": "Article",
        }

    def test_no_duplicates(self):
        papers = [
            self._make_paper("Paper A", "Smith J.", 2020, eid="e1"),
            self._make_paper("Paper B", "Jones K.", 2021, eid="e2"),
        ]
        globalVar.OriginalTotalPapers = len(papers)
        globalVar.papersScopus = 2
        globalVar.papersWoS = 0
        globalVar.cancelProcess = False
        result = paperUtils.removeDuplicates(papers)
        assert len(result) == 2

    def test_title_author_duplicate(self):
        papers = [
            self._make_paper("Same Title", "Smith J.", 2020, eid="e1", db="WoS", cited=10),
            self._make_paper("Same Title", "Smith J.", 2020, eid="e2", db="Scopus", cited=8),
        ]
        globalVar.OriginalTotalPapers = len(papers)
        globalVar.papersScopus = 1
        globalVar.papersWoS = 1
        globalVar.cancelProcess = False
        result = paperUtils.removeDuplicates(papers)
        assert len(result) == 1

    def test_doi_duplicate(self):
        papers = [
            self._make_paper("Title A", "Smith J.", 2020, doi="10.1000/test", eid="e1", db="WoS", cited=5),
            self._make_paper("Title A", "Smith J.", 2020, doi="10.1000/test", eid="e2", db="Scopus", cited=3),
        ]
        globalVar.OriginalTotalPapers = len(papers)
        globalVar.papersScopus = 1
        globalVar.papersWoS = 1
        globalVar.cancelProcess = False
        result = paperUtils.removeDuplicates(papers)
        assert len(result) == 1

    def test_cancel_stops_dedup(self):
        papers = [
            self._make_paper("Paper %d" % i, "Author %d" % i, 2020, eid="e%d" % i)
            for i in range(10)
        ]
        globalVar.OriginalTotalPapers = len(papers)
        globalVar.papersScopus = 10
        globalVar.papersWoS = 0
        globalVar.cancelProcess = True
        result = paperUtils.removeDuplicates(papers)
        assert result == 0


class TestNormalizeOpenAccess:
    """Test Open Access normalization (takes a raw string, returns normalized)."""

    def test_scopus_gold(self):
        result = paperUtils.normalizeOpenAccess("All Open Access; Gold Open Access")
        assert "Gold" in result

    def test_scopus_green(self):
        result = paperUtils.normalizeOpenAccess("All Open Access; Green Open Access")
        assert "Green" in result

    def test_wos_gold(self):
        result = paperUtils.normalizeOpenAccess("gold")
        assert "Gold" in result

    def test_empty_string(self):
        result = paperUtils.normalizeOpenAccess("")
        assert result == ""

    def test_none_returns_empty(self):
        result = paperUtils.normalizeOpenAccess(None)
        assert result == ""


class TestScientoPyError:
    """Test that ScientoPyError is properly raised."""

    def test_import(self):
        from ScientoPyClass import ScientoPyError
        assert issubclass(ScientoPyError, Exception)

    def test_invalid_window_width(self):
        from ScientoPyClass import ScientoPyClass, ScientoPyError
        sp = ScientoPyClass()
        sp.windowWidth = 0
        with pytest.raises(ScientoPyError, match="windowWidth"):
            sp.scientoPy()

    def test_invalid_year_range(self):
        from ScientoPyClass import ScientoPyClass, ScientoPyError
        sp = ScientoPyClass()
        sp.startYear = 2025
        sp.endYear = 2020
        with pytest.raises(ScientoPyError, match="startYear"):
            sp.scientoPy()


def _paper(year, keywords, cited="0", title="T"):
    return {"year": str(year), "authorKeywords": keywords, "citedBy": cited, "title": title, "doi": ""}


class TestNetworkAnalysis:
    """Co-occurrence network: counting, clustering, layout and writers."""

    def test_cooccurrence_counts(self):
        import networkAnalysis as na
        papers = [_paper(2020, "A; B; C"), _paper(2021, "A; B"), _paper(2021, "a; D"), _paper(2019, "B")]
        data = na.build_network(papers, start_year=2019, end_year=2021, min_occurrences=1)
        labels = {n["label"].upper(): n for n in data["nodes"]}
        assert labels["A"]["occ"] == 3          # "A" and "a" are the same item
        assert labels["B"]["occ"] == 3
        links = {frozenset((data["nodes"][i]["label"].upper(), data["nodes"][j]["label"].upper())): w
                 for i, j, w in data["links"]}
        assert links[frozenset(("A", "B"))] == 2
        assert links[frozenset(("A", "C"))] == 1
        assert frozenset(("C", "D")) not in links
        assert labels["A"]["links"] == 3 and labels["A"]["tls"] == 4

    def test_fractional_counting(self):
        import networkAnalysis as na
        papers = [_paper(2020, "A; B; C"), _paper(2020, "A; B")]
        data = na.build_network(papers, start_year=2020, end_year=2020, min_occurrences=1,
                                counting="fractional")
        weights = {frozenset((data["nodes"][i]["label"], data["nodes"][j]["label"])): w
                   for i, j, w in data["links"]}
        assert weights[frozenset(("A", "B"))] == pytest.approx(1.5)   # 1/2 + 1/1
        assert weights[frozenset(("B", "C"))] == pytest.approx(0.5)

    def test_synonyms_and_exclude(self, tmp_path):
        import networkAnalysis as na
        papers = [_paper(2020, "IoT; BLE"), _paper(2020, "Internet of Things; Bluetooth Low Energy; Noise")]
        data = na.build_network(papers, start_year=2020, end_year=2020, min_occurrences=1,
                                synonyms="Internet of Things, iot; Bluetooth Low Energy, ble",
                                exclude=["noise"])
        assert sorted(n["label"] for n in data["nodes"]) == ["Bluetooth Low Energy", "Internet of Things"]
        assert data["links"][0][2] == 2
        thesaurus = tmp_path / "thesaurus.txt"
        thesaurus.write_text("label\treplace by\nIoT\tInternet of Things\nnoise\t\n", encoding="utf-8")
        assert na.parse_synonyms(str(thesaurus)) == {"IOT": "Internet of Things", "NOISE": ""}

    def test_clusters_split_two_groups(self):
        import networkAnalysis as na
        # two 4-cliques joined by one weak edge
        rows, cols, weights = [], [], []
        for group in ([0, 1, 2, 3], [4, 5, 6, 7]):
            for a in group:
                for b in group:
                    if a < b:
                        rows.append(a); cols.append(b); weights.append(5.0)
        rows.append(3); cols.append(4); weights.append(0.2)
        membership = na.cluster_network(8, rows, cols, weights, resolution=1.0, min_cluster_size=1)
        assert len(set(membership[:4])) == 1 and len(set(membership[4:])) == 1
        assert membership[0] != membership[4]

    def test_small_clusters_are_merged(self):
        import networkAnalysis as na
        import numpy as np
        membership = np.array([0, 0, 0, 1, 2])
        merged = na._merge_small_clusters(membership, np.array([0, 2]), np.array([3, 4]),
                                          np.array([1.0, 1.0]), min_size=3)
        assert merged.tolist() == [0, 0, 0, 0, 0]

    def test_layout_is_finite_and_normalized(self):
        import networkAnalysis as na
        import numpy as np
        rng = np.random.default_rng(1)
        S = rng.random((30, 30))
        S = (S + S.T) / 2
        np.fill_diagonal(S, 0)
        S[29, :] = S[:, 29] = 0           # an unconnected item must stay on the map
        X = na._fit_unit_radius(na.vos_layout(S, dim=3, iterations=60))
        assert X.shape == (30, 3) and np.isfinite(X).all()
        assert np.sqrt((X * X).sum(1)).max() <= 1.35 + 1e-9

    def test_writers(self, tmp_path):
        import networkAnalysis as na
        import xml.etree.ElementTree as ET
        papers = [_paper(2020, "A; B; C", cited="4"), _paper(2021, "A; B")]
        data = na.build_network(papers, start_year=2020, end_year=2021, min_occurrences=1)
        na.write_vosviewer_map(data, str(tmp_path / "map.txt"))
        na.write_vosviewer_network(data, str(tmp_path / "net.txt"))
        na.write_gexf(data, str(tmp_path / "net.gexf"))
        lines = (tmp_path / "map.txt").read_text(encoding="utf-8").splitlines()
        assert lines[0].startswith("id\tlabel\tx\ty\tcluster")
        assert len(lines) == 1 + len(data["nodes"])
        assert len((tmp_path / "net.txt").read_text().splitlines()) == len(data["links"])
        root = ET.parse(str(tmp_path / "net.gexf")).getroot()
        assert len(root.findall(".//{http://gexf.net/1.3}node")) == len(data["nodes"])

    def test_html_embeds_safe_json(self, tmp_path):
        import networkAnalysis as na
        papers = [_paper(2020, "</script><b>x; B")]
        data = na.build_network(papers, start_year=2020, end_year=2020, min_occurrences=1)
        path = tmp_path / "map.html"
        na.write_html(data, str(path))
        html = path.read_text(encoding="utf-8")
        assert "</script><b>" not in html
        assert "__SP_DATA__" not in html and "/*__SP_SCRIPT__*/" not in html

    def test_invalid_parameters(self):
        import networkAnalysis as na
        with pytest.raises(na.NetworkError, match="not valid"):
            na.build_network([], criterion="abstract")
        with pytest.raises(na.NetworkError, match="startYear"):
            na.build_network([], start_year=2025, end_year=2020)
        with pytest.raises(na.NetworkError, match="No papers"):
            na.build_network([_paper(2000, "A")], start_year=2020, end_year=2021)


def _full_paper(year, keywords, cited="0", title="T", country="", eid=None):
    """A paper with the fields the analysis and the result tables read."""
    return {
        "year": str(year), "authorKeywords": keywords, "citedBy": cited, "title": title,
        "country": country, "eid": eid or title, "author": "Doe, J.", "sourceTitle": "Journal",
        "documentType": "Article", "doi": "", "abstract": "", "bothKeywords": keywords,
        "duplicatedIn": [], "dataBase": "Scopus",
    }


class _AnalysisArgs:
    """Attributes scientoPy.py passes to ScientoPyClass.scientoPy()."""

    def __init__(self, **overrides):
        self.criterion = "authorKeywords"
        self.graphType = "bar"
        self.length = 10
        self.skipFirst = 0
        self.topics = ""
        self.startYear = 2018
        self.endYear = 2022
        self.savePlot = ""
        self.noPlot = True
        self.agrForGraph = False
        self.wordCloudMask = ""
        self.windowWidth = 2
        self.previousResults = False
        self.onlyFirst = False
        self.graphTitle = ""
        self.pYear = False
        self.plotWidth = 6.4
        self.plotHeight = 4.8
        self.trend = False
        self.yLog = False
        self.filter = ""
        self.saveExtended = False
        self.synonyms = ""
        for name, value in overrides.items():
            setattr(self, name, value)


def _run_analysis(papers, monkeypatch, tmp_path, **overrides):
    """Run ScientoPyClass.scientoPy() on in-memory papers. The result files
    go to tmp_path, not to the project folders."""
    from ScientoPyClass import ScientoPyClass
    monkeypatch.chdir(tmp_path)
    sp = ScientoPyClass()
    sp.papersDict = papers            # already loaded: nothing is read from disk
    sp.lastPreviousResults = False
    sp.scientoPy(_AnalysisArgs(**overrides))
    return sp


class TestSynonyms:
    """Topic names merged by --synonyms and documents counted once per topic."""

    def test_paper_items_merge_synonyms(self):
        from ScientoPyClass import ScientoPyClass
        synonyms = {"IOT": "Internet of Things", "INTERNET OF THINGS": "Internet of Things", "NOISE": ""}
        paper = {"authorKeywords": "IoT; Internet of things; BLE; noise; ; ble"}
        assert ScientoPyClass._paperItems(paper, "authorKeywords", synonyms) == ["Internet of Things", "BLE"]
        assert ScientoPyClass._paperItems(paper, "authorKeywords", {}) == \
            ["IoT", "Internet of things", "BLE", "noise"]

    def test_synonyms_merge_top_topics(self, monkeypatch, tmp_path):
        papers = [_full_paper(2020, "IoT; Internet of Things", cited="3", title="A"),
                  _full_paper(2021, "Internet of Things; BLE", title="B"),
                  _full_paper(2021, "iot", title="C")]
        sp = _run_analysis(papers, monkeypatch, tmp_path,
                           synonyms="Internet of Things, IoT")
        totals = {t["name"]: t["PapersTotal"] for t in sp.topicResults}
        assert totals == {"Internet of Things": 3, "BLE": 1}

    def test_document_counts_once_per_grouped_topic(self, monkeypatch, tmp_path):
        # Paper A has two names of the same custom topic: it is one document
        papers = [_full_paper(2020, "IoT; Internet of Things", cited="3", title="A"),
                  _full_paper(2021, "Internet of Things", cited="1", title="B")]
        sp = _run_analysis(papers, monkeypatch, tmp_path, topics="Internet of Things, IoT")
        topic = sp.topicResults[0]
        assert topic["PapersTotal"] == 2
        assert topic["CitedByTotal"] == 4
        assert len(topic["papers"]) == 2
        assert sorted(x.upper() for x in topic["topicsFound"]) == ["INTERNET OF THINGS", "IOT"]

    def test_wildcard_topic_counts_documents(self, monkeypatch, tmp_path):
        papers = [_full_paper(2020, "device; devices; device management", title="A")]
        sp = _run_analysis(papers, monkeypatch, tmp_path, topics="device*")
        assert sp.topicResults[0]["PapersTotal"] == 1


class TestWorldMap:
    """Country outlines, name matching, projection and the world map graph."""

    def test_country_names_are_matched(self):
        import worldMap
        countries = worldMap.load_countries()

        def name_of(text):
            index = worldMap.find_country(text)
            return countries[index]["name"] if index is not None else None

        assert name_of("United States") == "United States"
        assert name_of("USA") == "United States"
        assert name_of("Peoples R China") == "China"
        assert name_of("Russian Federation") == "Russian Federation"
        assert name_of("Viet Nam") == "Vietnam"
        assert name_of("Côte d'Ivoire") == "Ivory Coast"
        assert name_of("Singapore") == "Singapore"       # only in the detailed outlines
        assert name_of("Not A Country") is None

    def test_outlines_are_valid(self):
        import worldMap
        countries = worldMap.load_countries()
        assert len(countries) > 200
        names = [worldMap.normalize_name(c["name"]) for c in countries]
        assert len(names) == len(set(names))
        for country in countries:
            assert country["polygons"], country["name"]
            for ring in country["polygons"]:
                assert len(ring) >= 4
                assert all(-180 <= lon <= 180 and -90 <= lat <= 90 for lon, lat in ring)

    def test_match_countries_adds_up_names_of_one_country(self):
        import worldMap
        matched, not_found = worldMap.match_countries({"USA": 3, "United States": 4, "Atlantis": 2})
        assert matched == {worldMap.find_country("United States"): 7}
        assert not_found == ["Atlantis"]

    def test_robinson_projection(self):
        import numpy as np
        import worldMap
        x, y = worldMap.robinson([0, 180, -180, 0, 0], [0, 0, 0, 90, -90])
        assert x[0] == 0 and y[0] == 0
        assert x[1] == pytest.approx(0.8487 * np.pi) and x[2] == pytest.approx(-x[1])
        assert y[3] == pytest.approx(1.3523) and y[4] == pytest.approx(-1.3523)
        # Parallels get shorter towards the poles
        assert worldMap.robinson(180, 60)[0] < worldMap.robinson(180, 0)[0]

    def test_world_map_plot(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.collections import PolyCollection
        import graphUtils
        args = _AnalysisArgs(criterion="country", graphType="world_map")
        plt.figure()
        not_found = graphUtils.plot_world_map(
            plt, {"United States": 11, "GERMANY": 8, "Nowhere": 5, "Atlantis": 9}, args)
        assert not_found == ["Atlantis", "Nowhere"]      # more documents first
        shapes = [c for c in plt.gca().collections if isinstance(c, PolyCollection)]
        assert len(shapes) == 1 and len(shapes[0].get_paths()) > 200
        plt.close()

    def test_world_map_needs_country_criterion(self):
        from ScientoPyClass import ScientoPyClass, ScientoPyError
        sp = ScientoPyClass()
        sp.graphType = "world_map"
        sp.criterion = "authorKeywords"
        with pytest.raises(ScientoPyError, match="country"):
            sp.scientoPy()

    def test_world_map_counts_every_country(self, monkeypatch, tmp_path):
        papers = [_full_paper(2020, "A", country="United States;Brazil", title="A"),
                  _full_paper(2021, "A", country="United States", title="B"),
                  _full_paper(2021, "A", country="France", title="C")]
        sp = _run_analysis(papers, monkeypatch, tmp_path, criterion="country",
                           graphType="world_map", length=1)
        assert len(sp.topicResults) == 1                  # the table has the top one
        assert sp.worldMapCounts(_AnalysisArgs(length=1)) == \
            {"UNITED STATES": 2, "BRAZIL": 1, "FRANCE": 1}
        assert sp.worldMapCounts(_AnalysisArgs(skipFirst=1)) == {"BRAZIL": 1, "FRANCE": 1}


class TestThematicMap:
    """Callon centrality and density of the clusters, and the map plot."""

    @staticmethod
    def _two_themes():
        import networkAnalysis as na
        # Theme 1: A, B, C always together (4 documents). Theme 2: D, E (2 documents),
        # and one document links C with D. F is alone.
        papers = [_paper(2020, "A; B; C")] * 4 + [_paper(2021, "D; E")] * 2 \
            + [_paper(2021, "C; D"), _paper(2021, "F")]
        return na.build_network(papers, start_year=2020, end_year=2021, min_occurrences=1,
                                min_cluster_size=1, layout=False)

    def test_centrality_and_density(self):
        import networkAnalysis as na
        data = self._two_themes()
        themes = {tuple(sorted(t["items"])): t for t in na.thematic_map(data)}
        assert set(themes) == {("A", "B", "C"), ("D", "E")}       # F has no links
        big, small = themes[("A", "B", "C")], themes[("D", "E")]
        # e(C,D) = 1^2 / (5 * 3)
        assert big["centrality"] == pytest.approx(10 / 15, abs=1e-4)
        assert small["centrality"] == pytest.approx(10 / 15, abs=1e-4)
        # e(A,B) = 16/16, e(A,C) = e(B,C) = 16/20; over 3 items
        assert big["density"] == pytest.approx(100 * (1 + 0.8 + 0.8) / 3, abs=1e-3)
        # e(D,E) = 4 / (3 * 2); over 2 items
        assert small["density"] == pytest.approx(100 * (4 / 6) / 2, abs=1e-3)
        assert big["rankDensity"] > small["rankDensity"]
        assert big["theme"] == na.THEME_MOTOR
        assert small["theme"] == na.THEME_BASIC       # as central, less developed

    def test_no_layout_keeps_clusters(self):
        import networkAnalysis as na
        papers = [_paper(2020, "A; B; C")] * 3 + [_paper(2021, "D; E")] * 2
        with_layout = na.build_network(papers, start_year=2020, end_year=2021, min_occurrences=1)
        without = na.build_network(papers, start_year=2020, end_year=2021, min_occurrences=1,
                                   layout=False)
        assert [n["c"] for n in with_layout["nodes"]] == [n["c"] for n in without["nodes"]]
        assert all(n["p2"] == [0.0, 0.0] for n in without["nodes"])

    def test_clusters_csv(self, tmp_path):
        import csv
        import networkAnalysis as na
        data = self._two_themes()
        na.write_clusters_csv(data, str(tmp_path / "clusters.csv"))
        na.write_clusters_csv(data, str(tmp_path / "themes.csv"), only_themes=True)
        with open(tmp_path / "clusters.csv", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        # Inside a cluster, the items with more documents go first (C has 5)
        assert [row["Item labels"] for row in rows] == ["C; A; B", "D; E", "F"]
        assert rows[0]["Theme"] == na.THEME_MOTOR and rows[2]["Theme"] == ""
        assert rows[2]["Callon centrality"] == ""
        with open(tmp_path / "themes.csv", encoding="utf-8") as f:
            assert len(list(csv.DictReader(f))) == 2

    def test_thematic_map_plot_separates_labels(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import graphUtils
        import networkAnalysis as na
        # Six themes on the same spot: every label starts on top of the others
        themes = [{"cluster": k + 1, "items": ["keyword %d a" % k, "keyword %d b" % k],
                   "occ": 10 + k, "centrality": 1.0, "density": 1.0,
                   "rankCentrality": 3.5, "rankDensity": 3.5, "theme": na.THEME_MOTOR}
                  for k in range(6)]
        args = _AnalysisArgs(labels=2, axes="rank")
        plt.figure()
        graphUtils.plot_thematic_map(plt, themes, args)
        plt.tight_layout()
        ax = plt.gca()
        graphUtils.separate_theme_labels(ax)
        fig = ax.figure
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        boxes = [t.get_window_extent(renderer) for t in ax.texts
                 if t.get_gid() == graphUtils.THEME_LABEL_GID]
        assert len(boxes) == 6
        frame = ax.get_window_extent(renderer)
        for a in range(len(boxes)):
            assert frame.x0 - 1 <= boxes[a].x0 and boxes[a].x1 <= frame.x1 + 1
            for b in range(a + 1, len(boxes)):
                assert not boxes[a].overlaps(boxes[b]), (a, b)
        plt.close()


class TestTopCited:
    """Most cited documents table."""

    def test_ranking_and_year_range(self):
        import paperSave
        papers = [_full_paper(2019, "A", cited="5", title="Old"),
                  _full_paper(2021, "A", cited="50", title="Most"),
                  _full_paper(2020, "A", cited="5", title="Tie later"),
                  _full_paper(2022, "A", cited="", title="No count"),
                  _full_paper("n/a", "A", cited="99", title="No year")]
        headers, rows = paperSave.topCitedRows(papers, length=3, currentYear=2025)
        col = {name: k for k, name in enumerate(headers)}
        assert [row[col["Title"]] for row in rows] == ["Most", "Old", "Tie later"]
        assert [row[col["Pos."]] for row in rows] == ["1", "2", "3"]
        assert rows[0][col["Cited by per year"]] == "10.00"     # 50 / (2025 - 2021 + 1)
        headers, rows = paperSave.topCitedRows(papers, length=10, startYear=2020, endYear=2022,
                                               currentYear=2025)
        assert [row[col["Title"]] for row in rows] == ["Most", "Tie later", "No count"]
        assert rows[2][col["Cited by"]] == "0"

    def test_save(self, tmp_path):
        import csv
        import paperSave
        headers, rows = paperSave.topCitedRows([_full_paper(2020, "A", cited="7", title="One, two")],
                                               currentYear=2020)
        path = paperSave.saveTopCited(headers, rows, str(tmp_path / "out" / "top.csv"))
        with open(path, encoding="utf-8") as f:
            saved = list(csv.DictReader(f))
        assert saved[0]["Title"] == "One, two" and saved[0]["Cited by per year"] == "7.00"
