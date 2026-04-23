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

import sys
import threading

# ── Startup splash ────────────────────────────────────────────────────────────
# Appears before any heavy import (PySide6, matplotlib, polars, …) using only
# tkinter (stdlib) so the user gets immediate feedback in < 0.2 s.
_splash_done = threading.Event()

def _run_splash():
    try:
        import tkinter as tk
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes('-topmost', True)
        root.configure(bg='#1a3a5c')
        w, h = 320, 90
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
        tk.Label(root, text="ScientoPy", fg='white', bg='#1a3a5c',
                 font=('Helvetica', 22, 'bold')).pack(expand=True)
        tk.Label(root, text="Loading...", fg='#aaaacc', bg='#1a3a5c',
                 font=('Helvetica', 11)).pack(pady=(0, 12))
        root.update()
        while not _splash_done.wait(timeout=0.05):
            try:
                root.update()
            except Exception:
                break
        root.destroy()
    except Exception:
        pass

_splash_thread = threading.Thread(target=_run_splash, daemon=True)
_splash_thread.start()
# ─────────────────────────────────────────────────────────────────────────────

import os
import json
import csv
import webbrowser

import matplotlib
matplotlib.use('QtAgg')

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QComboBox, QSpinBox, QPlainTextEdit, QSplitter,
    QDialog, QProgressBar, QFileDialog, QMessageBox,
    QMenuBar, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QStatusBar,
    QRadioButton, QButtonGroup, QGroupBox,
)
from PySide6.QtGui import QPixmap, QIcon, QAction, QActionGroup, QPalette, QColor, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QTimer

import globalVar

def asset_path(filename):
    """Resolve asset path for both PyInstaller bundle and source mode."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)

CONFIG_FILE = "scientopy_config.json"

HEADER_TOOLTIPS = {
    # Analysis results headers
    "Pos.": "Position in the ranking",
    "Total": "Total number of documents",
    "AGR": "Average Growth Rate: average difference between documents\n"
           "published in one year and the previous year, inside a time frame.\n"
           "AGR = \u03a3(Pi - Pi-1) / (Ye - Ys + 1)",
    "ADY": "Average Documents per Year: average number of documents\n"
           "published inside a time frame for a specific topic.\n"
           "ADY = \u03a3Pi / (Ye - Ys + 1)",
    "PDLY": "Percentage of Documents in Last Years: percentage of the ADY\n"
            "relative to the total number of documents for a specific topic.\n"
            "PDLY = (\u03a3Pi / ((Ye - Ys + 1) * TND)) * 100%",
    "hIndex": "h-index: a topic has index h if h of its documents have\n"
              "been cited at least h times",
    # Preprocess brief headers
    "Info": "Description of the preprocessing statistic",
    "Number": "Count of documents",
    "Percentage": "Relative percentage",
    "Source": "Database source (WoS or Scopus)",
    # Extended results headers
    "Cited by": "Number of citations received by the document",
    "EID": "Document unique identifier (from WoS or Scopus)",
    "EID2": "Secondary document identifier",
    "Year": "Publication year of the document",
    "Title": "Title of the document",
    "Document type": "Type of document (Conference Paper, Article, Review, etc.)",
    "Authors": "Document authors list",
    "Author keywords": "Keywords assigned by the document authors",
    "Both keywords": "Author keywords and index keywords combined",
    # Criterion headers (both original and capitalized CSV column names)
    "author": "Authors last name and first name initial",
    "Author": "Authors last name and first name initial",
    "sourceTitle": "Journal name",
    "SourceTitle": "Journal name",
    "subject": "Research area (only from WoS documents)",
    "Subject": "Research area (only from WoS documents)",
    "abstract": "Document's abstract",
    "Abstract": "Document's abstract",
    "authorKeywords": "Author's keywords",
    "AuthorKeywords": "Author's keywords",
    "indexKeywords": "Keywords generated by the index. From WoS {Keyword Plus},\n"
                     "and from Scopus {Indexed keywords}",
    "IndexKeywords": "Keywords generated by the index. From WoS {Keyword Plus},\n"
                     "and from Scopus {Indexed keywords}",
    "bothKeywords": "AuthorKeywords and indexKeywords combined",
    "BothKeywords": "AuthorKeywords and indexKeywords combined",
    "documentType": "Type of document",
    "DocumentType": "Type of document",
    "dataBase": "Database where the document was extracted (WoS or Scopus)",
    "DataBase": "Database where the document was extracted (WoS or Scopus)",
    "country": "Country extracted from authors affiliations",
    "Country": "Country extracted from authors affiliations",
    "institution": "Institution extracted from authors affiliations\n"
                   "(only from WoS documents)",
    "Institution": "Institution extracted from authors affiliations\n"
                   "(only from WoS documents)",
    "institutionWithCountry": "Institution with country extracted from\n"
                              "authors affiliations",
    "InstitutionWithCountry": "Institution with country extracted from\n"
                              "authors affiliations",
}

DARK_MATPLOTLIB_STYLE = {
    'figure.facecolor': '#2b2b2b',
    'axes.facecolor': '#2b2b2b',
    'axes.edgecolor': '#cccccc',
    'axes.labelcolor': '#cccccc',
    'text.color': '#cccccc',
    'xtick.color': '#cccccc',
    'ytick.color': '#cccccc',
    'grid.color': '#555555',
}


def load_config():
    defaults = {
        "appearance_mode": "System",
        "graph_appearance": "Light",
        "last_dataset_folder": "",
        "window_geometry": "1000x600",
        "splitter_sizes": [280, 600],
        "criterion": "authorKeywords",
        "graph_type": "bar_trends",
        "start_year": globalVar.DEFAULT_START_YEAR,
        "end_year": globalVar.DEFAULT_END_YEAR,
        "topics_length": 10,
        "skip_first": 0,
        "window_width": 2,
        "previous_results": False,
        "trend_analysis": False,
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
            defaults.update(saved)
        except Exception:
            pass
    return defaults


def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception:
        pass


def is_dark_mode(app):
    palette = app.palette()
    bg = palette.color(QPalette.ColorRole.Window)
    return bg.lightnessF() < 0.5


def apply_matplotlib_theme(app, graph_mode="Same as UI"):
    if graph_mode == "Dark":
        matplotlib.rcParams.update(DARK_MATPLOTLIB_STYLE)
    elif graph_mode == "Light":
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        matplotlib.rcParams['figure.dpi'] = 100
    else:  # "Same as UI"
        if is_dark_mode(app):
            matplotlib.rcParams.update(DARK_MATPLOTLIB_STYLE)
        else:
            matplotlib.rcParams.update(matplotlib.rcParamsDefault)
            matplotlib.rcParams['figure.dpi'] = 100


class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except ValueError:
            return super().__lt__(other)


class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)
        self.setFixedSize(350, 140)
        self.setWindowTitle("Progress")

        layout = QVBoxLayout(self)

        self.label = QLabel("Starting...")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel)
        layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)

    def update_progress(self):
        self.label.setText(globalVar.progressText)
        val = min(globalVar.progressPer, 100)
        self.progress_bar.setValue(val)
        if globalVar.progressPer >= 101 or globalVar.cancelProcess:
            self.timer.stop()
            self.accept()

    def on_cancel(self):
        globalVar.cancelProcess = True
        print("Canceled")
        self.timer.stop()
        self.reject()


class ScientoPyGui(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = load_config()
        self._scientoPy = None   # lazy-initialized on first use
        self._preprocess = None  # lazy-initialized on first use

        self.setWindowTitle("ScientoPy")
        self.setMinimumSize(853, 480)

        # Parse saved geometry
        try:
            w, h = self.config["window_geometry"].split("x")
            self.resize(int(w), int(h))
        except Exception:
            self.resize(1000, 600)

        # Window icon
        icon_path = asset_path("scientopy_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Menu bar
        self._create_menu_bar()

        # Central widget with tabs
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(4, 4, 4, 4)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self._create_preprocess_tab()
        self._create_analysis_tab()
        self._create_results_tab()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("ScientoPy loading...")
        self._create_ext_results_tab()
        self._create_export_tab()

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+O"), self, activated=self.select_dataset)
        QShortcut(QKeySequence("Ctrl+R"), self, activated=self._run_current_tab)
        QShortcut(QKeySequence("Ctrl+1"), self, activated=lambda: self.tabs.setCurrentIndex(0))
        QShortcut(QKeySequence("Ctrl+2"), self, activated=lambda: self.tabs.setCurrentIndex(1))
        QShortcut(QKeySequence("Ctrl+3"), self, activated=lambda: self.tabs.setCurrentIndex(2))
        QShortcut(QKeySequence("Ctrl+4"), self, activated=lambda: self.tabs.setCurrentIndex(3))
        QShortcut(QKeySequence("Ctrl+5"), self, activated=lambda: self.tabs.setCurrentIndex(4))

        # Apply saved appearance
        self._apply_appearance(self.config.get("appearance_mode", "System"))

    # ── Lazy-loaded heavy dependencies ───────────────────────

    @property
    def scientoPy(self):
        if self._scientoPy is None:
            from ScientoPyClass import ScientoPyClass
            self._scientoPy = ScientoPyClass(from_gui=True)
        return self._scientoPy

    @property
    def preprocess(self):
        if self._preprocess is None:
            from PreProcessClass import PreProcessClass
            self._preprocess = PreProcessClass(from_gui=True)
        return self._preprocess

    # ── Menu Bar ──────────────────────────────────────────────

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        view_menu = menu_bar.addMenu("View")

        appearance_menu = view_menu.addMenu("Appearance")
        self.appearance_group = QActionGroup(self)
        self.appearance_group.setExclusive(True)
        for mode in ("System", "Light", "Dark"):
            action = QAction(mode, self, checkable=True)
            if mode == self.config.get("appearance_mode", "System"):
                action.setChecked(True)
            action.triggered.connect(lambda checked, m=mode: self._apply_appearance(m))
            self.appearance_group.addAction(action)
            appearance_menu.addAction(action)

        graph_appearance_menu = view_menu.addMenu("Graph appearance")
        self.graph_appearance_group = QActionGroup(self)
        self.graph_appearance_group.setExclusive(True)
        for mode in ("Same as UI", "Light", "Dark"):
            action = QAction(mode, self, checkable=True)
            if mode == self.config.get("graph_appearance", "Same as UI"):
                action.setChecked(True)
            action.triggered.connect(lambda checked, m=mode: self._apply_graph_appearance(m))
            self.graph_appearance_group.addAction(action)
            graph_appearance_menu.addAction(action)

    def _apply_appearance(self, mode):
        app = QApplication.instance()
        self.config["appearance_mode"] = mode

        if mode == "System":
            app.setStyleSheet("")
            app.setPalette(app.style().standardPalette())
        elif mode == "Light":
            app.setStyleSheet("")
            app.setPalette(app.style().standardPalette())
        elif mode == "Dark":
            app.setStyleSheet("")
            palette = QPalette()
            CR = QPalette.ColorRole
            palette.setColor(CR.Window, QColor(43, 43, 43))
            palette.setColor(CR.WindowText, QColor(204, 204, 204))
            palette.setColor(CR.Base, QColor(30, 30, 30))
            palette.setColor(CR.AlternateBase, QColor(50, 50, 50))
            palette.setColor(CR.ToolTipBase, QColor(43, 43, 43))
            palette.setColor(CR.ToolTipText, QColor(204, 204, 204))
            palette.setColor(CR.Text, QColor(204, 204, 204))
            palette.setColor(CR.Button, QColor(53, 53, 53))
            palette.setColor(CR.ButtonText, QColor(204, 204, 204))
            palette.setColor(CR.BrightText, QColor(255, 0, 0))
            palette.setColor(CR.Link, QColor(42, 130, 218))
            palette.setColor(CR.Highlight, QColor(42, 130, 218))
            palette.setColor(CR.HighlightedText, QColor(0, 0, 0))
            palette.setColor(CR.PlaceholderText, QColor(130, 130, 130))
            app.setPalette(palette)

        # Update matplotlib theme
        apply_matplotlib_theme(app, self.config.get("graph_appearance", "Same as UI"))

        # Update logo if we have both variants
        self._update_logo()

    def _apply_graph_appearance(self, mode):
        self.config["graph_appearance"] = mode
        apply_matplotlib_theme(QApplication.instance(), mode)

    def _update_logo(self):
        if not hasattr(self, 'logo_label'):
            return
        app = QApplication.instance()
        dark = is_dark_mode(app)
        dark_logo = asset_path("scientopy_logo_dark.png")
        light_logo = asset_path("scientopy_logo.png")
        logo_path = dark_logo if dark and os.path.exists(dark_logo) else light_logo
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled = pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled)

    # ── Pre-processing Tab ────────────────────────────────────

    def _create_preprocess_tab(self):
        page = QWidget()
        self.tabs.addTab(page, "1. Pre-processing")
        layout = QVBoxLayout(page)

        # Logo area (centered, stretches)
        logo_container = QVBoxLayout()
        logo_container.addStretch(1)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_file = asset_path("scientopy_logo.png")
        if os.path.exists(logo_file):
            pixmap = QPixmap(logo_file)
            scaled = pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
        logo_container.addWidget(self.logo_label)

        version_label = QLabel(
            "Universidad del Cauca, Popayán, Colombia\n"
            "MIT License\n"
            "Version %s" % globalVar.SCIENTOPY_VERSION
        )
        version_label.setAlignment(Qt.AlignCenter)
        logo_container.addWidget(version_label)
        logo_container.addStretch(1)

        layout.addLayout(logo_container, stretch=1)

        # Dataset folder row
        dataset_row = QHBoxLayout()
        dataset_row.addWidget(QLabel("Dataset folder:"))

        self.dataset_entry = QLineEdit()
        if self.config.get("last_dataset_folder"):
            self.dataset_entry.setText(self.config["last_dataset_folder"])
        dataset_row.addWidget(self.dataset_entry, stretch=1)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.select_dataset)
        dataset_row.addWidget(browse_btn)

        layout.addLayout(dataset_row)

        # Bottom row: checkbox + buttons
        bottom_row = QHBoxLayout()

        self.chk_remove_dupl = QCheckBox("Remove duplicated documents")
        self.chk_remove_dupl.setChecked(True)
        bottom_row.addWidget(self.chk_remove_dupl)

        bottom_row.addStretch(1)

        run_preprocess_btn = QPushButton("Run preprocess")
        run_preprocess_btn.clicked.connect(self.run_preprocess)
        bottom_row.addWidget(run_preprocess_btn)

        layout.addLayout(bottom_row)

    # ── Analysis Tab ──────────────────────────────────────────

    def _create_analysis_tab(self):
        page = QWidget()
        self.tabs.addTab(page, "2. Analysis")
        page_layout = QVBoxLayout(page)

        # Splitter: left form | right text area
        splitter = QSplitter(Qt.Horizontal)
        self.analysis_splitter = splitter

        # Left panel: form
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        form = QFormLayout()

        self.combo_criterion = QComboBox()
        self.combo_criterion.addItems(globalVar.validCriterion)
        saved_criterion = self.config.get("criterion", "authorKeywords")
        idx = globalVar.validCriterion.index(saved_criterion) if saved_criterion in globalVar.validCriterion else 3
        self.combo_criterion.setCurrentIndex(idx)
        self.combo_criterion.setToolTip(
            "Field to analyze: author, sourceTitle, authorKeywords,\n"
            "indexKeywords, bothKeywords, abstract, documentType,\n"
            "dataBase, country, institution, institutionWithCountry")
        form.addRow("Criterion:", self.combo_criterion)

        self.combo_graph_type = QComboBox()
        self.combo_graph_type.addItems(globalVar.validGrapTypes)
        saved_graph = self.config.get("graph_type", "bar_trends")
        gidx = globalVar.validGrapTypes.index(saved_graph) if saved_graph in globalVar.validGrapTypes else 0
        self.combo_graph_type.setCurrentIndex(gidx)
        self.combo_graph_type.setToolTip(
            "Visualization type:\n"
            "bar_trends - Horizontal bars with percentage in last years\n"
            "bar - Horizontal bars with total documents\n"
            "time_line - Documents per year line plot\n"
            "evolution - Accumulative documents + AGR vs PDLY scatter\n"
            "word_cloud - Word cloud sized by document count")
        form.addRow("Graph type:", self.combo_graph_type)

        self.spin_start_year = QSpinBox()
        self.spin_start_year.setRange(1900, 2100)
        self.spin_start_year.setValue(self.config.get("start_year", globalVar.DEFAULT_START_YEAR))
        self.spin_start_year.setToolTip(
            "Start year for the analysis range.\n"
            "Papers published before this year are excluded.")
        form.addRow("Start Year:", self.spin_start_year)

        self.spin_end_year = QSpinBox()
        self.spin_end_year.setRange(1900, 2100)
        self.spin_end_year.setValue(self.config.get("end_year", globalVar.DEFAULT_END_YEAR))
        self.spin_end_year.setToolTip(
            "End year for the analysis range.\n"
            "Papers published after this year are excluded.")
        form.addRow("End Year:", self.spin_end_year)

        self.spin_topics_length = QSpinBox()
        self.spin_topics_length.setRange(0, 1000)
        self.spin_topics_length.setValue(self.config.get("topics_length", 10))
        self.spin_topics_length.setToolTip(
            "Number of top topics to extract and display.\n"
            "Default: 10")
        form.addRow("Topics length:", self.spin_topics_length)

        self.spin_skip_first = QSpinBox()
        self.spin_skip_first.setRange(0, 1000)
        self.spin_skip_first.setValue(self.config.get("skip_first", 0))
        self.spin_skip_first.setToolTip(
            "Skip the first N topics from the results.\n"
            "Useful to filter dominant topics that overshadow others.\n"
            "Default: 0")
        form.addRow("Skip first:", self.spin_skip_first)

        self.spin_window_width = QSpinBox()
        self.spin_window_width.setRange(1, 100)
        self.spin_window_width.setValue(self.config.get("window_width", 2))
        self.spin_window_width.setToolTip(
            "Window width in years for AGR, ADY, and PDLY calculation.\n"
            "Start year for indicators: Ys = EndYear - (WindowWidth + 1)\n"
            "Default: 2")
        form.addRow("Window (years):", self.spin_window_width)

        left_layout.addLayout(form)

        self.chk_previous_results = QCheckBox("Use previous results")
        self.chk_previous_results.setChecked(self.config.get("previous_results", False))
        self.chk_previous_results.setToolTip(
            "Analyze based on the output documents from the last run.\n"
            "For example, first extract papers from a country, then\n"
            "use previous results to find top keywords within that subset.")
        left_layout.addWidget(self.chk_previous_results)

        self.chk_trend_analysis = QCheckBox("Trend analysis")
        self.chk_trend_analysis.setChecked(self.config.get("trend_analysis", False))
        self.chk_trend_analysis.setToolTip(
            "Find trending topics based on the highest Average Growth Rate (AGR).\n"
            "Extracts the top 200 topics, calculates AGR for the window period,\n"
            "and sorts them from highest to lowest AGR.")
        left_layout.addWidget(self.chk_trend_analysis)

        left_layout.addStretch(1)

        left_widget.setMinimumWidth(250)
        left_widget.setMaximumWidth(350)

        # Right panel: custom topics
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_layout.addWidget(QLabel("Custom topics:"))

        self.custom_topics = QPlainTextEdit()
        right_layout.addWidget(self.custom_topics, stretch=1)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # Restore splitter sizes
        try:
            sizes = self.config.get("splitter_sizes", [280, 600])
            splitter.setSizes(sizes)
        except Exception:
            splitter.setSizes([280, 600])

        page_layout.addWidget(splitter, stretch=1)

        # Bottom button bar
        btn_row = QHBoxLayout()

        bibtex_btn = QPushButton("Generate BibTeX")
        bibtex_btn.setToolTip(
            "Generate a BibTeX bibliography file from a LaTeX document.\n"
            "Select a .tex file that uses paper EIDs as \\cite{} keys.\n"
            "The .bib file is created next to the input file.")
        bibtex_btn.clicked.connect(self.generate_bibtex)
        btn_row.addWidget(bibtex_btn)

        clear_topics_btn = QPushButton("Clear topics")
        clear_topics_btn.setToolTip("Clear the Custom topics text area.")
        clear_topics_btn.clicked.connect(lambda: self.custom_topics.clear())
        btn_row.addWidget(clear_topics_btn)

        reset_btn = QPushButton("Reset defaults")
        reset_btn.setToolTip("Reset all analysis parameters to their default values.")
        reset_btn.clicked.connect(self._reset_analysis_defaults)
        btn_row.addWidget(reset_btn)

        btn_row.addStretch(1)

        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self.scientoPyRun)
        btn_row.addWidget(run_btn)

        page_layout.addLayout(btn_row)

    # ── Results Tab ────────────────────────────────────────────

    def _create_results_tab(self):
        page = QWidget()
        self.tabs.addTab(page, "3. Results")
        layout = QVBoxLayout(page)

        self.results_table = QTableWidget()
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.results_table.setSortingEnabled(True)
        layout.addWidget(self.results_table)

        # Ctrl+C to copy selected cells
        copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self.results_table)
        copy_shortcut.activated.connect(self._copy_selected_cells)

        # Bottom bar: status label + copy buttons
        bottom_row = QHBoxLayout()

        self.results_status_label = QLabel("No results yet. Run preprocessing first.")
        bottom_row.addWidget(self.results_status_label, stretch=1)

        copy_sel_btn = QPushButton("Copy Selection")
        copy_sel_btn.clicked.connect(self._copy_selected_cells)
        bottom_row.addWidget(copy_sel_btn)

        copy_all_btn = QPushButton("Copy All")
        copy_all_btn.clicked.connect(self._copy_all_cells)
        bottom_row.addWidget(copy_all_btn)

        analyze_sel_btn = QPushButton("Analyze selection")
        analyze_sel_btn.setToolTip(
            "Copy the topic names from selected rows to the\n"
            "Custom topics field in the Analysis tab.")
        analyze_sel_btn.clicked.connect(self._analyze_selection)
        bottom_row.addWidget(analyze_sel_btn)

        layout.addLayout(bottom_row)

        # Defer pre-loading so heavy modules are not imported before the window shows
        QTimer.singleShot(0, self._post_show_init)

    def _post_show_init(self):
        if os.path.exists(self.scientoPy.preprocessBriefFileName):
            self._load_results_table()
        self.status_bar.showMessage("Ready")

    def _load_results_table(self, filepath=None):
        if filepath is None:
            filepath = self.scientoPy.preprocessBriefFileName
        if not os.path.exists(filepath):
            return

        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            return

        headers = rows[0]
        data = rows[1:]

        self.results_table.setSortingEnabled(False)

        self.results_table.setColumnCount(len(headers))
        self.results_table.setRowCount(len(data))
        self.results_table.setHorizontalHeaderLabels(headers)

        for c, header in enumerate(headers):
            item = self.results_table.horizontalHeaderItem(c)
            if item:
                item.setToolTip(self._get_header_tooltip(header))

        for r, row in enumerate(data):
            for c, cell in enumerate(row):
                text = cell.strip()
                try:
                    float(text)
                    item = NumericTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                except ValueError:
                    item = QTableWidgetItem(text)
                self.results_table.setItem(r, c, item)

        self.results_table.setSortingEnabled(True)

        for col in range(len(headers)):
            self.results_table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )

        self.results_table.resizeRowsToContents()
        self.results_status_label.setText(
            "Showing results from: %s" % os.path.basename(filepath)
        )

    def _analyze_selection(self):
        """Copy topic names from selected rows to the Custom topics field."""
        selected_rows = sorted(set(idx.row() for idx in self.results_table.selectedIndexes()))
        if not selected_rows:
            self.status_bar.showMessage("No rows selected")
            return

        # The topic name is in column 1 (column 0 is "Pos.")
        # But if the table is showing preprocess brief, column 1 may not be topics.
        # Detect: if header of col 1 matches a criterion name, it's analysis results.
        header_item = self.results_table.horizontalHeaderItem(1)
        if not header_item:
            return

        topics = []
        for row in selected_rows:
            cell = self.results_table.item(row, 1)
            if cell and cell.text().strip():
                topics.append(cell.text().strip())

        if not topics:
            self.status_bar.showMessage("No topics found in selection")
            return

        self.custom_topics.setPlainText("\n".join(topics))
        self.tabs.setCurrentIndex(1)  # Switch to Analysis tab
        self.status_bar.showMessage(
            "%d topic(s) copied to Custom topics" % len(topics))

    @staticmethod
    def _get_header_tooltip(header):
        tip = HEADER_TOOLTIPS.get(header, "")
        if not tip and header.startswith("Topic "):
            criterion = header[len("Topic "):]
            tip = HEADER_TOOLTIPS.get(criterion, "")
            if tip:
                tip = "Topic: " + tip
        return tip

    # ── Extended Results Tab ─────────────────────────────────

    def _create_ext_results_tab(self):
        page = QWidget()
        self.tabs.addTab(page, "4. Extended Results")
        layout = QVBoxLayout(page)

        self.ext_results_table = QTableWidget()
        self.ext_results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.ext_results_table.setAlternatingRowColors(True)
        self.ext_results_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.ext_results_table.setSortingEnabled(True)
        layout.addWidget(self.ext_results_table)

        copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self.ext_results_table)
        copy_shortcut.activated.connect(self._copy_selected_ext_cells)

        bottom_row = QHBoxLayout()

        self.ext_results_status_label = QLabel("No extended results yet. Run analysis first.")
        bottom_row.addWidget(self.ext_results_status_label, stretch=1)

        copy_sel_btn = QPushButton("Copy Selection")
        copy_sel_btn.clicked.connect(self._copy_selected_ext_cells)
        bottom_row.addWidget(copy_sel_btn)

        copy_all_btn = QPushButton("Copy All")
        copy_all_btn.clicked.connect(self._copy_all_ext_cells)
        bottom_row.addWidget(copy_all_btn)

        layout.addLayout(bottom_row)

    def _load_ext_results_table(self, filepath):
        """Load an Extended Results CSV from disk (only used when the user
        exports or when -- in legacy flows -- such a file already exists)."""
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            return
        self._populate_ext_results(
            rows[0], rows[1:], source_label=os.path.basename(filepath)
        )

    def _populate_ext_results_from_topics(self, topicResults, criterion):
        """Populate the Extended Results tab directly from the in-memory
        topicResults produced by the last analysis — no CSV round-trip."""
        import paperSave
        headers, data = paperSave.extendedResultsRows(topicResults, criterion)
        self._populate_ext_results(
            headers, data, source_label="last analysis (in memory)"
        )

    def _populate_ext_results(self, headers, data, source_label=""):
        total = len(data)

        self.ext_results_table.setSortingEnabled(False)
        self.ext_results_table.clearContents()

        self.ext_results_table.setColumnCount(len(headers))
        self.ext_results_table.setRowCount(total)
        self.ext_results_table.setHorizontalHeaderLabels(headers)

        for c, header in enumerate(headers):
            item = self.ext_results_table.horizontalHeaderItem(c)
            if item:
                item.setToolTip(self._get_header_tooltip(header))

        # Large-table handling: on the AI-scale corpus the extended-results
        # CSV can run to 100 k+ rows. Blindly calling setItem 14 × 100 k
        # times followed by per-column ResizeToContents + resizeRowsToContents
        # (both O(rows × cols)) freezes the main thread long enough for
        # Wayland to pop a "Not Responding" dialog. We mitigate with two
        # techniques: (1) chunked loading with processEvents() every N rows
        # so the UI stays responsive and a progress label updates, and
        # (2) skipping the expensive resize-to-contents passes above a row
        # threshold — users can drag header dividers on the rare column
        # that needs widening.
        CHUNK = 2000
        RESIZE_LIMIT = 3000
        app = QApplication.instance()
        self.ext_results_table.setUpdatesEnabled(False)

        try:
            for r, row in enumerate(data):
                for c, cell in enumerate(row):
                    text = cell.strip()
                    try:
                        float(text)
                        item = NumericTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    except ValueError:
                        item = QTableWidgetItem(text)
                    self.ext_results_table.setItem(r, c, item)
                if total > CHUNK and r and r % CHUNK == 0:
                    # Temporarily re-enable updates so the user sees the new
                    # chunk render, pump events, then disable again for the
                    # next batch.
                    self.ext_results_table.setUpdatesEnabled(True)
                    self.ext_results_status_label.setText(
                        "Loading extended results… %d / %d  (%d%%)"
                        % (r, total, int(100 * r / total))
                    )
                    app.processEvents()
                    self.ext_results_table.setUpdatesEnabled(False)
        finally:
            self.ext_results_table.setUpdatesEnabled(True)

        self.ext_results_table.setSortingEnabled(True)

        if total <= RESIZE_LIMIT:
            for col in range(len(headers)):
                self.ext_results_table.horizontalHeader().setSectionResizeMode(
                    col, QHeaderView.ResizeMode.ResizeToContents
                )
            self.ext_results_table.resizeRowsToContents()
            self.ext_results_status_label.setText(
                "Showing %d extended results from %s" % (total, source_label)
            )
        else:
            # Sensible interactive defaults without paying for content
            # measurement across every row.
            for col in range(len(headers)):
                self.ext_results_table.horizontalHeader().setSectionResizeMode(
                    col, QHeaderView.ResizeMode.Interactive
                )
            self.ext_results_status_label.setText(
                "Showing %d extended results from %s  "
                "(column auto-resize skipped for large tables — drag the "
                "header dividers to widen a column)"
                % (total, source_label)
            )

    # ── Export Tab ────────────────────────────────────────────

    def _create_export_tab(self):
        page = QWidget()
        self.tabs.addTab(page, "5. Export")
        layout = QVBoxLayout(page)

        # Source
        src_group = QGroupBox("Source")
        src_layout = QVBoxLayout(src_group)
        self.rb_src_preprocessed = QRadioButton(
            "Preprocessed corpus (dataPre/papersPreprocessed.parquet)")
        self.rb_src_preprocessed.setToolTip(
            "Export the full deduplicated corpus as a single CSV.")
        self.rb_src_results = QRadioButton(
            "Last analysis results (results/*.csv)")
        self.rb_src_results.setToolTip(
            "Copy the CSVs produced by the last analysis run into the\n"
            "chosen destination folder.")
        self.rb_src_extended = QRadioButton(
            "Extended results (last analysis, per-document)")
        self.rb_src_extended.setToolTip(
            "Write the detailed per-document extended-results CSV for the\n"
            "last analysis still in memory. This file is no longer produced\n"
            "automatically because it can be very large on big corpora.")
        self.rb_src_preprocessed.setChecked(True)
        self._src_group = QButtonGroup(self)
        self._src_group.addButton(self.rb_src_preprocessed)
        self._src_group.addButton(self.rb_src_results)
        self._src_group.addButton(self.rb_src_extended)
        src_layout.addWidget(self.rb_src_preprocessed)
        src_layout.addWidget(self.rb_src_results)
        src_layout.addWidget(self.rb_src_extended)
        layout.addWidget(src_group)

        # Format
        fmt_group = QGroupBox("Format")
        fmt_layout = QVBoxLayout(fmt_group)
        self.rb_fmt_scopus = QRadioButton("Scopus fields")
        self.rb_fmt_wos = QRadioButton("WoS fields")
        self.rb_fmt_scopus.setChecked(True)
        self._fmt_group = QButtonGroup(self)
        self._fmt_group.addButton(self.rb_fmt_scopus)
        self._fmt_group.addButton(self.rb_fmt_wos)
        fmt_layout.addWidget(self.rb_fmt_scopus)
        fmt_layout.addWidget(self.rb_fmt_wos)
        layout.addWidget(fmt_group)

        # Destination
        dest_group = QGroupBox("Destination")
        dest_layout = QHBoxLayout(dest_group)
        self.export_path_entry = QLineEdit()
        self.export_path_entry.setPlaceholderText(
            "e.g., export/papersPreprocessed.csv  (or a folder for 'results')")
        dest_layout.addWidget(self.export_path_entry, stretch=1)
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_export_path)
        dest_layout.addWidget(browse_btn)
        layout.addWidget(dest_group)

        layout.addStretch(1)

        # Bottom row
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self._run_export)
        btn_row.addWidget(self.export_btn)
        layout.addLayout(btn_row)

        # Re-evaluate enabled state and default destination whenever the
        # source selection changes, so the path field suggests a sensible
        # default for each mode.
        self._src_group.buttonClicked.connect(self._update_export_enabled)
        self._update_export_enabled()

    def _default_export_path(self):
        if self.rb_src_preprocessed.isChecked():
            return os.path.join("export", globalVar.OUTPUT_FILE_NAME)
        if self.rb_src_extended.isChecked():
            criterion = getattr(self.scientoPy, "criterion", "analysis")
            crit = criterion[0].upper() + criterion[1:] if criterion else "analysis"
            return os.path.join("export", crit + "_extended.csv")
        return os.path.join("export", "results")

    def _browse_export_path(self):
        if self.rb_src_results.isChecked():
            path = QFileDialog.getExistingDirectory(
                self, "Select destination folder",
                self.export_path_entry.text() or self._default_export_path(),
            )
        else:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save CSV as",
                self.export_path_entry.text() or self._default_export_path(),
                "CSV files (*.csv);;All files (*.*)",
            )
        if path:
            self.export_path_entry.setText(path)

    def _update_export_enabled(self, *_):
        # The Format group only applies to the preprocessed-corpus path.
        fmt_applies = self.rb_src_preprocessed.isChecked()
        for rb in (self.rb_fmt_scopus, self.rb_fmt_wos):
            rb.setEnabled(fmt_applies)

        # Disabled whenever the chosen source has no data to export.
        if self.rb_src_preprocessed.isChecked():
            parquet = os.path.join(
                globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_PARQUET
            )
            legacy = os.path.join(
                globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_NAME
            )
            enabled = os.path.isfile(parquet) or os.path.isfile(legacy)
            tip = "" if enabled else "No preprocessed corpus found. Run Preprocess first."
        elif self.rb_src_results.isChecked():
            results_dir = globalVar.RESULTS_FOLDER
            enabled = os.path.isdir(results_dir) and any(
                f.lower().endswith(".csv")
                and f != globalVar.LAST_ANALYSIS_FILE
                for f in os.listdir(results_dir)
            )
            tip = "" if enabled else "No results CSVs found. Run an analysis first."
        else:  # extended
            enabled = bool(self._scientoPy and getattr(self._scientoPy, "topicResults", []))
            tip = ("" if enabled else
                   "Run an analysis in this session before exporting extended results.")
        self.export_btn.setEnabled(enabled)
        self.export_btn.setToolTip(tip)

        if not self.export_path_entry.text():
            self.export_path_entry.setText(self._default_export_path())

    def _run_export(self):
        if self.rb_src_preprocessed.isChecked():
            source = "preprocessed"
        elif self.rb_src_results.isChecked():
            source = "results"
        else:
            source = "extended"
        fmt = "scopus" if self.rb_fmt_scopus.isChecked() else "wos"
        output = self.export_path_entry.text().strip() or None

        # Reset progress state and run the export on a worker thread so the
        # GUI stays responsive and the ProgressDialog can poll progressText /
        # progressPer in real time (banner on entry, percentage while the
        # CSV is being written).
        globalVar.cancelProcess = False
        globalVar.progressPer = 0
        globalVar.progressText = "Starting export…"

        self._export_result = None
        self._export_error = None

        # Snapshot the in-memory analysis state (the worker thread runs off
        # the main thread; grabbing references here keeps things simple).
        topics = list(getattr(self.scientoPy, "topicResults", []) or [])
        criterion = getattr(self.scientoPy, "criterion", "analysis")

        def run_export():
            try:
                if source == "extended":
                    import paperSave
                    out = output or os.path.join(
                        "export",
                        (criterion[0].upper() + criterion[1:] if criterion else "analysis")
                        + "_extended.csv",
                    )
                    globalVar.progressText = "Writing extended results"
                    self._export_result = paperSave.saveExtendedResults(
                        topics, criterion, "", outPath=out,
                    )
                else:
                    import exportPapers
                    self._export_result = exportPapers.export(source, fmt, output)
            except FileNotFoundError as e:
                self._export_error = ("missing", str(e))
            except Exception as e:
                self._export_error = ("failed", str(e))
            finally:
                # Make absolutely sure the ProgressDialog closes even if the
                # export raised before reaching the finally block in export().
                globalVar.progressPer = 101

        self.status_bar.showMessage("Exporting…")
        t = threading.Thread(target=run_export)
        t.start()
        dialog = ProgressDialog(self)
        dialog.exec()
        t.join()

        if self._export_error is not None:
            kind, msg = self._export_error
            title = "Export failed" if kind == "failed" else "Export failed"
            QMessageBox.critical(self, title, msg if kind == "missing"
                                 else "Unexpected error: %s" % msg)
            self.status_bar.showMessage("Export failed")
            return

        written = self._export_result
        abs_path = os.path.abspath(written)
        self.status_bar.showMessage("Exported to %s" % abs_path)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Export complete")
        msg.setText("Export finished successfully.")
        msg.setInformativeText(
            '<a href="file://%s">%s</a>' % (abs_path, abs_path)
        )
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        open_btn = msg.addButton("Open", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Ok)
        msg.exec()
        if msg.clickedButton() == open_btn:
            webbrowser.open(
                abs_path if os.path.isdir(abs_path) else os.path.dirname(abs_path)
            )

    # ── Copy Helpers ──────────────────────────────────────────

    @staticmethod
    def _copy_selected_from(table):
        selection = table.selectedIndexes()
        if not selection:
            return

        rows_dict = {}
        for idx in selection:
            rows_dict.setdefault(idx.row(), {})[idx.column()] = idx.data() or ""

        min_col = min(c for cols in rows_dict.values() for c in cols)
        max_col = max(c for cols in rows_dict.values() for c in cols)

        lines = []
        headers = []
        for c in range(min_col, max_col + 1):
            item = table.horizontalHeaderItem(c)
            headers.append(item.text() if item else "")
        lines.append("\t".join(headers))

        for r in sorted(rows_dict):
            cells = []
            for c in range(min_col, max_col + 1):
                cells.append(rows_dict[r].get(c, ""))
            lines.append("\t".join(cells))

        QApplication.clipboard().setText("\n".join(lines))

    @staticmethod
    def _copy_all_from(table):
        if table.rowCount() == 0:
            return

        lines = []
        headers = []
        for c in range(table.columnCount()):
            item = table.horizontalHeaderItem(c)
            headers.append(item.text() if item else "")
        lines.append("\t".join(headers))

        for r in range(table.rowCount()):
            cells = []
            for c in range(table.columnCount()):
                item = table.item(r, c)
                cells.append(item.text() if item else "")
            lines.append("\t".join(cells))

        QApplication.clipboard().setText("\n".join(lines))

    def _copy_selected_cells(self):
        self._copy_selected_from(self.results_table)

    def _copy_all_cells(self):
        self._copy_all_from(self.results_table)

    def _copy_selected_ext_cells(self):
        self._copy_selected_from(self.ext_results_table)

    def _copy_all_ext_cells(self):
        self._copy_all_from(self.ext_results_table)

    def _reset_analysis_defaults(self):
        """Reset all analysis parameters to their default values."""
        self.combo_criterion.setCurrentIndex(
            globalVar.validCriterion.index("authorKeywords"))
        self.combo_graph_type.setCurrentIndex(
            globalVar.validGrapTypes.index("bar_trends"))
        self.spin_start_year.setValue(globalVar.DEFAULT_START_YEAR)
        self.spin_end_year.setValue(globalVar.DEFAULT_END_YEAR)
        self.spin_topics_length.setValue(10)
        self.spin_skip_first.setValue(0)
        self.spin_window_width.setValue(2)
        self.chk_previous_results.setChecked(False)
        self.chk_trend_analysis.setChecked(False)
        self.custom_topics.clear()
        self.status_bar.showMessage("Analysis parameters reset to defaults")

    def _run_current_tab(self):
        """Ctrl+R handler: run preprocess or analysis depending on active tab."""
        idx = self.tabs.currentIndex()
        if idx == 0:
            self.run_preprocess()
        elif idx == 1:
            self.scientoPyRun()

    # ── Actions ───────────────────────────────────────────────

    def select_dataset(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select dataset folder")
        if dir_name:
            self.dataset_entry.setText(dir_name)
            self.config["last_dataset_folder"] = dir_name

    def open_results(self):
        if os.path.exists(self.scientoPy.resultsFileName):
            webbrowser.open(self.scientoPy.resultsFileName)
        else:
            QMessageBox.critical(self, "Error", "No results found, please run the analysis first")

    def open_ext_results(self):
        if os.path.exists(self.scientoPy.extResultsFileName):
            webbrowser.open(self.scientoPy.extResultsFileName)
        else:
            QMessageBox.critical(self, "Error", "No extended results found, please run the analysis first")

    def open_preprocess_brief(self):
        if os.path.exists(self.scientoPy.preprocessBriefFileName):
            webbrowser.open(self.scientoPy.preprocessBriefFileName)
        else:
            QMessageBox.critical(self, "Error", "No preprocess brief found, please run the preprocess first")

    def run_preprocess(self):
        dataset_path = self.dataset_entry.text()
        if not dataset_path:
            QMessageBox.critical(self, "Error", "No dataset folder defined")
            return

        if not os.path.isdir(dataset_path):
            QMessageBox.critical(self, "Error", "Dataset folder not found: %s" % dataset_path)
            return

        # Validate folder contains CSV or TXT files (recursively).
        has_data_files = False
        for _root, _dirs, names in os.walk(dataset_path):
            if any(n.lower().endswith(('.csv', '.txt')) for n in names):
                has_data_files = True
                break
        if not has_data_files:
            QMessageBox.critical(self, "Error",
                                 "No CSV or TXT files found under: %s\n"
                                 "Ensure the folder (or any sub-folder) contains\n"
                                 "Scopus CSV or WoS TXT export files." % dataset_path)
            return

        try:
            self.preprocess.dataInFolder = dataset_path
            self.preprocess.noRemDupl = not self.chk_remove_dupl.isChecked()

            globalVar.cancelProcess = False
            globalVar.progressPer = 0

            self.status_bar.showMessage("Preprocessing dataset...")

            t1 = threading.Thread(target=self.preprocess.preprocess)
            t1.start()

            dialog = ProgressDialog(self)
            dialog.exec()

            t1.join()

            if globalVar.cancelProcess:
                self.status_bar.showMessage("Preprocessing canceled")
                QMessageBox.critical(self, "Error", "Preprocessing canceled")
            elif globalVar.totalPapers > 0:
                self.status_bar.showMessage(
                    "Preprocessing complete \u2014 %d papers" % globalVar.totalPapers)
                apply_matplotlib_theme(QApplication.instance(), self.config.get("graph_appearance", "Same as UI"))
                self.preprocess.graphBrief()
                self._load_results_table()
                self._update_export_enabled()
                self.tabs.setCurrentIndex(2)  # Switch to Results tab
            elif globalVar.totalPapers == 0:
                self.status_bar.showMessage("Preprocessing failed: no valid files")
                QMessageBox.critical(self, "Error",
                                     "No valid dataset files found in: %s\n"
                                     "Ensure the folder contains Scopus CSV or WoS TXT export files." % dataset_path)
        except FileNotFoundError:
            self.status_bar.showMessage("Error: folder not found")
            QMessageBox.critical(self, "Error", "Dataset folder not found: %s" % dataset_path)
        except PermissionError:
            self.status_bar.showMessage("Error: permission denied")
            QMessageBox.critical(self, "Error", "Permission denied accessing: %s" % dataset_path)
        except Exception as e:
            self.status_bar.showMessage("Error: preprocessing failed")
            QMessageBox.critical(self, "Error", "Preprocessing failed: %s" % str(e))

    def scientoPyRun(self):
        from ScientoPyClass import ScientoPyError
        globalVar.cancelProcess = False
        globalVar.progressPer = 0

        if not os.path.exists(self.scientoPy.preprocessDatasetFile):
            QMessageBox.critical(self, "Error",
                                 "No preprocess input dataset, please run the preprocess first")
            return

        self.scientoPy.closePlot()

        self.scientoPy.criterion = self.combo_criterion.currentText()
        self.scientoPy.graphType = self.combo_graph_type.currentText()
        self.scientoPy.startYear = self.spin_start_year.value()
        self.scientoPy.endYear = self.spin_end_year.value()
        self.scientoPy.length = self.spin_topics_length.value()
        self.scientoPy.skipFirst = self.spin_skip_first.value()
        self.scientoPy.windowWidth = self.spin_window_width.value()
        self.scientoPy.previousResults = self.chk_previous_results.isChecked()
        self.scientoPy.trend = self.chk_trend_analysis.isChecked()

        topics_text = self.custom_topics.toPlainText().strip()
        if topics_text:
            self.scientoPy.topics = topics_text.replace("\n", ";")
        else:
            self.scientoPy.topics = ''

        self._thread_error = None
        self.status_bar.showMessage("Running analysis...")

        def run_analysis():
            try:
                self.scientoPy.scientoPy()
            except ScientoPyError as e:
                self._thread_error = str(e)

        t1 = threading.Thread(target=run_analysis)
        t1.start()

        dialog = ProgressDialog(self)
        dialog.exec()

        t1.join()

        if globalVar.cancelProcess:
            self.status_bar.showMessage("Analysis canceled")
            return

        if self._thread_error:
            self.status_bar.showMessage("Analysis failed")
            QMessageBox.critical(self, "Error", self._thread_error)
            return

        topic_count = len(self.scientoPy.topicResults)
        self.status_bar.showMessage(
            "Analysis complete \u2014 %d topics found" % topic_count)

        apply_matplotlib_theme(QApplication.instance(), self.config.get("graph_appearance", "Same as UI"))

        if self.scientoPy.graphType == "word_cloud":
            globalVar.progressText = "Generating word cloud..."
            globalVar.progressPer = 0
            globalVar.cancelProcess = False

            def _compute_wc():
                self.scientoPy.computeWordCloud()
                globalVar.progressPer = 101

            t_wc = threading.Thread(target=_compute_wc)
            t_wc.start()
            ProgressDialog(self).exec()
            t_wc.join()

        self.scientoPy.plotResults()

        # plotResults() calls plt.show(block=False), which queues Qt paint
        # events for the new figure window. If we immediately start
        # populating the extended-results table (can be 10 k+ rows with
        # per-column ResizeToContents), Qt can't run those paint events
        # until our heavy loop returns — the figure stays blank for ~5 s.
        # Pump events once so the window appears, then defer the heavy
        # table load to the next event-loop tick.
        app = QApplication.instance()
        app.processEvents()

        # Results table is small (<= 200 rows); load it now.
        if self.scientoPy.resultsFileName:
            self._load_results_table(self.scientoPy.resultsFileName)
        self._update_export_enabled()
        if self.scientoPy.resultsFileName:
            self.tabs.setCurrentIndex(2)  # Switch to Results tab
        app.processEvents()

        # Extended results can be very large — defer so the plot paints
        # and the Results tab is interactive before we block the UI again.
        # Populate from the in-memory topicResults (no disk round-trip;
        # the CSV is only written on-demand via the Export tab / --saveExtended).
        topics = list(self.scientoPy.topicResults)
        criterion = self.scientoPy.criterion
        if topics:
            QTimer.singleShot(
                0,
                lambda t=topics, c=criterion: self._populate_ext_results_from_topics(t, c),
            )

    def generate_bibtex(self):
        if not os.path.exists(self.scientoPy.preprocessDatasetFile):
            QMessageBox.critical(self, "Error",
                                 "No preprocess input dataset, please run the preprocess first")
            return

        latex_file, _ = QFileDialog.getOpenFileName(
            self, "Select the LaTeX file", "./",
            "LaTeX files (*.tex);;All files (*.*)"
        )
        if not latex_file:
            return

        from generateBibtex import generateBibtex
        out_file = generateBibtex(latex_file)
        self.status_bar.showMessage("BibTeX generated: %s" % os.path.basename(out_file))
        abs_path = os.path.abspath(out_file)

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("BibTeX Generated")
        msg.setText("BibTeX file created successfully.")
        msg.setInformativeText(
            '<a href="file://%s">%s</a>' % (abs_path, abs_path)
        )
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        open_btn = msg.addButton("Open File", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Ok)
        msg.exec()

        if msg.clickedButton() == open_btn:
            webbrowser.open(abs_path)

    # ── Close / Save Config ───────────────────────────────────

    def closeEvent(self, event):
        self.config["window_geometry"] = "%dx%d" % (self.width(), self.height())
        if hasattr(self, 'analysis_splitter'):
            self.config["splitter_sizes"] = self.analysis_splitter.sizes()
        # Save analysis parameters
        self.config["criterion"] = self.combo_criterion.currentText()
        self.config["graph_type"] = self.combo_graph_type.currentText()
        self.config["start_year"] = self.spin_start_year.value()
        self.config["end_year"] = self.spin_end_year.value()
        self.config["topics_length"] = self.spin_topics_length.value()
        self.config["skip_first"] = self.spin_skip_first.value()
        self.config["window_width"] = self.spin_window_width.value()
        self.config["previous_results"] = self.chk_previous_results.isChecked()
        self.config["trend_analysis"] = self.chk_trend_analysis.isChecked()
        save_config(self.config)
        event.accept()


def runGui():
    app = QApplication(sys.argv)
    app.setApplicationName("ScientoPy")

    window = ScientoPyGui()

    _splash_done.set()
    _splash_thread.join(timeout=0.5)

    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    runGui()
