#!/usr/bin/env python3
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
