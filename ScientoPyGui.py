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
    QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit, QSplitter,
    QDialog, QProgressBar, QFileDialog, QMessageBox,
    QMenuBar, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QStatusBar,
    QRadioButton, QButtonGroup, QGroupBox,
    QScrollArea, QToolButton, QFrame,
)
from PySide6.QtGui import (
    QPixmap, QIcon, QAction, QActionGroup, QPalette, QColor, QKeySequence, QShortcut,
    QDesktopServices,
)
from PySide6.QtCore import Qt, QTimer, QUrl

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
    "Cited by per year": "Citations divided by the years since the document was\n"
                         "published (the publication year counts as the first one)",
    "Source title": "Journal or conference where the document was published",
    "DOI": "Digital Object Identifier of the document",
    # Thematic map headers
    "Cluster": "Cluster number, the same as in the network map",
    "Label": "Item with more documents in the cluster",
    "Items": "Number of items in the cluster",
    "Occurrences": "Sum of the documents of every item in the cluster",
    "Documents": "Documents with at least one item of the cluster",
    "Avg. pub. year": "Average publication year of the cluster documents",
    "Callon centrality": "Relevance of the theme: strength of the links between the\n"
                         "cluster items and the items of the other clusters",
    "Callon density": "Development of the theme: strength of the links between\n"
                      "the items of the cluster, per item",
    "Centrality rank": "Position by centrality, 1 is the lowest (x axis of the map)",
    "Density rank": "Position by density, 1 is the lowest (y axis of the map)",
    "Theme": "Motor (central and developed), niche (developed, not central),\n"
             "basic (central, not developed) or emerging or declining theme",
    "Item labels": "Every item of the cluster, the ones with more documents first",
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

PROJECT_URL = "https://github.com/jpruiz84/ScientoPy"
CITATION = (
    "Ruiz-Rosero, J., Ramirez-Gonzalez, G., & Viveros-Delgado, J. (2019). "
    "Software survey: ScientoPy, a scientometric tool for topics trend analysis "
    "in scientific publications. Scientometrics, 121(2), 1165–1188. "
    "https://doi.org/10.1007/s11192-019-03213-w"
)

# Names shown in the lists. The values behind them are the names the
# scripts use (-c authorKeywords, -g bar_trends), also saved in the config.
CRITERION_LABELS = {
    "author": "Authors",
    "sourceTitle": "Sources (journals and conferences)",
    "subject": "Subject areas (WoS)",
    "authorKeywords": "Author keywords",
    "indexKeywords": "Index keywords",
    "abstract": "Abstract (custom topics)",
    "bothKeywords": "Author and index keywords",
    "documentType": "Document types",
    "dataBase": "Databases (Scopus, WoS)",
    "country": "Countries",
    "institution": "Institutions",
    "institutionWithCountry": "Institutions with country",
}

GRAPH_TYPE_LABELS = {
    "bar_trends": "Bars with trends",
    "bar": "Bars",
    "time_line": "Time line",
    "evolution": "Evolution",
    "word_cloud": "Word cloud",
    "world_map": "World map (countries)",
}

GRAPH_TYPE_TIPS = {
    "bar_trends": "Horizontal bars with the percentage of documents in the last years",
    "bar": "Horizontal bars with the total documents",
    "time_line": "Documents per year, one line per topic",
    "evolution": "Accumulative documents, and documents per year\n"
                 "against the percentage in the last years",
    "word_cloud": "Word cloud sized by the number of documents",
    "world_map": "World map shaded by the documents of each country",
}

COUNTING_LABELS = {"full": "Full", "fractional": "Fractional"}
COUNTING_TIPS = {
    "full": "Every co-occurrence counts 1",
    "fractional": "A document with n items gives each link 1/(n-1), so documents\n"
                  "with many authors or keywords weigh less",
}

THEME_AXES_LABELS = {"rank": "By rank", "value": "By value"}
THEME_AXES_TIPS = {
    "rank": "Place the themes by their centrality and density ranks,\n"
            "which spreads them evenly",
    "value": "Place the themes by their centrality and density values",
}

SYNONYMS_PLACEHOLDER = (
    "Names of the same topic, separated by commas. The first one names the group:\n"
    "internet of things, iot\n"
    "bluetooth low energy, ble"
)
SYNONYMS_TOOLTIP = (
    "Names of the same topic are counted as one, in any criterion: keyword\n"
    "variants and abbreviations, author names, institution names.\n"
    "One group per line, the names separated by commas. The first name of\n"
    "the group is the one shown in the results.\n"
    "The list is shared by the analysis, the network map and the thematic map."
)


def fill_combo(combo, values, labels, tips, current):
    """Fill a combo box with readable names; each item keeps its script name
    as data (combo.currentData())."""
    for value in values:
        combo.addItem(labels.get(value, value), value)
        tip = tips.get(value, "")
        tip = (tip + "\n" if tip else "") + "Name in the scripts: %s" % value
        combo.setItemData(combo.count() - 1, tip, Qt.ToolTipRole)
    set_combo(combo, current)


def set_combo(combo, value):
    index = combo.findData(value)
    if index >= 0:
        combo.setCurrentIndex(index)


def scrollable(widget, sections=()):
    """Put a panel in a scroll area, so a short window scrolls it instead of
    cutting it. sections are the collapsible sections inside the panel: the
    area is wide enough for them when they are open."""
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setFrameShape(QFrame.Shape.NoFrame)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    area.setWidget(widget)
    # Same background as the tab, not the one of a list
    widget.setAutoFillBackground(False)
    area.viewport().setAutoFillBackground(False)
    width = max([widget.minimumSizeHint().width()]
                + [section.body.minimumSizeHint().width() for section in sections])
    width += area.verticalScrollBar().sizeHint().width() + 12
    area.setMinimumWidth(width)
    area.setMaximumWidth(width + 110)
    return area


class CollapsibleSection(QWidget):
    """A titled group of options that the user opens or closes."""

    def __init__(self, title, expanded=False, parent=None):
        super().__init__(parent)
        self.toggle = QToolButton()
        self.toggle.setText(title)
        self.toggle.setCheckable(True)
        self.toggle.setChecked(expanded)
        self.toggle.setAutoRaise(True)
        self.toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.toggle.toggled.connect(self._on_toggled)

        self.body = QWidget()
        self.body.setVisible(expanded)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self.toggle)
        layout.addWidget(self.body)

    def _on_toggled(self, expanded):
        self.toggle.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.body.setVisible(expanded)

    def isExpanded(self):
        return self.toggle.isChecked()


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
        "splitter_sizes": [300, 600],
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
        self._data_years = None  # (first, last) publication year of the dataset
        # Year ranges set by ScientoPy, not by the user: these can be replaced
        # when a dataset with other years is loaded
        self._auto_year_ranges = {(globalVar.DEFAULT_START_YEAR, globalVar.DEFAULT_END_YEAR)}
        saved_range = self.config.get("auto_year_range")
        if isinstance(saved_range, list) and len(saved_range) == 2:
            self._auto_year_ranges.add(tuple(saved_range))
        self._results_file = ""
        self._results_kind = ""
        self._documents_file = ""
        self._criterion_before_map = "country"
        self._updating_controls = False

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
        self.dataset_indicator = QLabel("")
        self.status_bar.addPermanentWidget(self.dataset_indicator)
        self._create_ext_results_tab()
        self._create_network_tab()
        self._create_export_tab()

        # Keyboard shortcuts: Ctrl+1 .. Ctrl+6 open the tabs. Ctrl+O, Ctrl+R
        # and Ctrl+Q belong to the File menu actions.
        for number in range(1, self.tabs.count() + 1):
            QShortcut(QKeySequence("Ctrl+%d" % number), self,
                      activated=lambda n=number: self.tabs.setCurrentIndex(n - 1))

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

        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Select dataset folder…", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(lambda: self.select_dataset())
        file_menu.addAction(open_action)

        run_action = QAction("Run the current tab", self)
        run_action.setShortcut(QKeySequence("Ctrl+R"))
        run_action.triggered.connect(lambda: self._run_current_tab())
        file_menu.addAction(run_action)

        file_menu.addSeparator()

        results_action = QAction("Open results folder", self)
        results_action.triggered.connect(lambda: self._open_path(globalVar.RESULTS_FOLDER))
        file_menu.addAction(results_action)

        graphs_action = QAction("Open graphs folder", self)
        graphs_action.triggered.connect(lambda: self._open_path(globalVar.GRAPHS_OUT_FOLDER))
        file_menu.addAction(graphs_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(lambda: self.close())
        file_menu.addAction(quit_action)

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

        help_menu = menu_bar.addMenu("Help")
        for title, filename in (
            ("User manual (graphical interface)", "ScientoPyGui_user_manual.pdf"),
            ("User manual (scripts)", "ScientoPy_user_manual.pdf"),
            ("Example paper", "example_paper.pdf"),
        ):
            action = QAction(title, self)
            action.triggered.connect(
                lambda checked=False, f=filename: self._open_path(asset_path(os.path.join("Manual", f))))
            help_menu.addAction(action)

        help_menu.addSeparator()

        shortcuts_action = QAction("Keyboard shortcuts", self)
        shortcuts_action.triggered.connect(lambda: self._show_shortcuts())
        help_menu.addAction(shortcuts_action)

        cite_action = QAction("How to cite ScientoPy", self)
        cite_action.triggered.connect(lambda: self._show_citation())
        help_menu.addAction(cite_action)

        website_action = QAction("ScientoPy website", self)
        website_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(PROJECT_URL)))
        help_menu.addAction(website_action)

        help_menu.addSeparator()

        about_action = QAction("About ScientoPy", self)
        about_action.triggered.connect(lambda: self._show_about())
        help_menu.addAction(about_action)

    def _open_path(self, path):
        """Open a file or a folder with the application the system uses for it."""
        if not path or not os.path.exists(path):
            QMessageBox.information(self, "Not found", "%s does not exist yet." % path)
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(path)))

    def _show_shortcuts(self):
        rows = [
            ("Ctrl+O", "Select the dataset folder"),
            ("Ctrl+R", "Run the current tab: preprocess, analysis, network map or export"),
            ("Ctrl+1 … Ctrl+%d" % self.tabs.count(), "Open a tab"),
            ("Ctrl+C", "Copy the selected cells of a table"),
            ("Ctrl+Q", "Quit"),
        ]
        html = "<table cellpadding='4'>" + "".join(
            "<tr><td><b>%s</b></td><td>%s</td></tr>" % row for row in rows) + "</table>"
        box = QMessageBox(self)
        box.setWindowTitle("Keyboard shortcuts")
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setText(html)
        box.exec()

    def _show_citation(self):
        box = QMessageBox(self)
        box.setWindowTitle("How to cite ScientoPy")
        box.setText("If you use ScientoPy in a paper, book or report, please cite:")
        box.setInformativeText(CITATION)
        box.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        copy_btn = box.addButton("Copy", QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Close)
        box.exec()
        if box.clickedButton() == copy_btn:
            QApplication.clipboard().setText(CITATION)
            self.status_bar.showMessage("Citation copied")

    def _show_about(self):
        QMessageBox.about(
            self, "About ScientoPy",
            "<h3>ScientoPy %s</h3>"
            "<p>Scientometric analysis of Scopus and Web of Science datasets: "
            "topic trends, maps and networks.</p>"
            "<p>Universidad del Cauca, Popayán, Colombia<br>MIT License</p>"
            "<p><a href='%s'>%s</a></p>" % (globalVar.SCIENTOPY_VERSION, PROJECT_URL, PROJECT_URL))

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
            # Options that do not apply are shown dimmed
            disabled = QPalette.ColorGroup.Disabled
            for role in (CR.WindowText, CR.Text, CR.ButtonText):
                palette.setColor(disabled, role, QColor(115, 115, 115))
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
        self.page_preprocess = page
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

        # What the other tabs will work on
        self.dataset_status_label = QLabel("")
        self.dataset_status_label.setAlignment(Qt.AlignCenter)
        self.dataset_status_label.setWordWrap(True)
        layout.addWidget(self.dataset_status_label)

        # Dataset folder row
        dataset_row = QHBoxLayout()
        dataset_row.addWidget(QLabel("Dataset folder:"))

        dataset_tip = (
            "Folder with the files downloaded from Scopus (.csv) and\n"
            "Web of Science (.txt). Sub-folders are read too.")
        self.dataset_entry = QLineEdit()
        self.dataset_entry.setPlaceholderText("Folder with the Scopus (.csv) and WoS (.txt) files")
        self.dataset_entry.setToolTip(dataset_tip)
        if self.config.get("last_dataset_folder"):
            self.dataset_entry.setText(self.config["last_dataset_folder"])
        dataset_row.addWidget(self.dataset_entry, stretch=1)

        browse_btn = QPushButton("Browse…")
        browse_btn.setToolTip(dataset_tip + "\nShortcut: Ctrl+O")
        browse_btn.clicked.connect(self.select_dataset)
        dataset_row.addWidget(browse_btn)

        layout.addLayout(dataset_row)

        # Bottom row: checkbox + buttons
        bottom_row = QHBoxLayout()

        self.chk_remove_dupl = QCheckBox("Remove duplicated documents")
        self.chk_remove_dupl.setChecked(self.config.get("remove_duplicates", True))
        self.chk_remove_dupl.setToolTip(
            "Keep one copy of the documents found in both Scopus and WoS\n"
            "(same DOI, or same title and first author).")
        bottom_row.addWidget(self.chk_remove_dupl)

        bottom_row.addStretch(1)

        run_preprocess_btn = QPushButton("Run preprocess")
        run_preprocess_btn.setDefault(True)
        run_preprocess_btn.setToolTip(
            "Read the dataset folder, remove the duplicated documents and\n"
            "save the dataset that the other tabs use.\nShortcut: Ctrl+R")
        run_preprocess_btn.clicked.connect(self.run_preprocess)
        bottom_row.addWidget(run_preprocess_btn)

        layout.addLayout(bottom_row)

    def _refresh_dataset_status(self):
        """Show the documents and the years of the preprocessed dataset."""
        path = os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_PARQUET)
        legacy = os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_NAME)
        self._data_years = None
        short = ""
        if os.path.isfile(path):
            try:
                import polars as pl
                column = pl.read_parquet(path, columns=["year"])["year"].to_list()
                years = [int(y) for y in column if y is not None and str(y).isdigit()]
                short = "{:,} documents".format(len(column))
                if years:
                    self._data_years = (min(years), max(years))
                    short += ", %d–%d" % self._data_years
                text = "Preprocessed dataset: %s (publication years)" % short if years \
                    else "Preprocessed dataset: %s" % short
            except Exception:
                text = "Preprocessed dataset found in %s" % path
        elif os.path.isfile(legacy):
            text = "Preprocessed dataset found in %s" % legacy
        else:
            text = ("No preprocessed dataset yet. Select the folder with your Scopus (.csv) "
                    "and WoS (.txt) files and click Run preprocess.")
        self.dataset_status_label.setText(text)
        self.dataset_indicator.setText(short)
        self.dataset_indicator.setToolTip("Preprocessed dataset: documents and publication years")

    def _default_year_range(self):
        """Year range for a new analysis: the default one, cut to the dataset years."""
        start, end = globalVar.DEFAULT_START_YEAR, globalVar.DEFAULT_END_YEAR
        if self._data_years:
            first, last = self._data_years
            if max(start, first) <= min(end, last):
                start, end = max(start, first), min(end, last)
        return start, end

    def _apply_year_defaults(self):
        """Fit the year ranges of the Analysis and Maps tabs to the dataset,
        unless the user chose a range that the dataset covers."""
        start, end = self._default_year_range()
        for spin_start, spin_end in ((self.spin_start_year, self.spin_end_year),
                                     (self.net_start_year, self.net_end_year)):
            current = (spin_start.value(), spin_end.value())
            outside = bool(self._data_years) and (
                current[1] < self._data_years[0] or current[0] > self._data_years[1])
            if current in self._auto_year_ranges or outside:
                spin_end.setValue(end)
                spin_start.setValue(start)
        self._auto_year_ranges.add((start, end))
        self.config["auto_year_range"] = [start, end]

    @staticmethod
    def _link_year_range(spin_start, spin_end):
        """Keep start year <= end year: moving one past the other drags it along."""
        for spin in (spin_start, spin_end):
            spin.setKeyboardTracking(False)
        spin_start.valueChanged.connect(
            lambda value: spin_end.setValue(value) if value > spin_end.value() else None)
        spin_end.valueChanged.connect(
            lambda value: spin_start.setValue(value) if value < spin_start.value() else None)

    def _update_previous_results_enabled(self):
        """Use previous results needs the documents of a previous analysis."""
        available = os.path.isfile(os.path.join(globalVar.RESULTS_FOLDER, globalVar.LAST_ANALYSIS_FILE))
        for checkbox, tip in (
            (self.chk_previous_results,
             "Analyze only the documents found by the last analysis.\n"
             "For example, first extract the documents of a country, then\n"
             "use previous results to find the top keywords of that country."),
            (self.net_previous,
             "Map only the documents found by the last analysis."),
        ):
            checkbox.setEnabled(available)
            if not available:
                checkbox.setChecked(False)
                tip += "\nNot available yet: run an analysis first."
            checkbox.setToolTip(tip)

    # ── Analysis Tab ──────────────────────────────────────────

    def _create_analysis_tab(self):
        page = QWidget()
        self.page_analysis = page
        self.tabs.addTab(page, "2. Analysis")
        page_layout = QVBoxLayout(page)

        # Splitter: left form | right text area
        splitter = QSplitter(Qt.Horizontal)
        self.analysis_splitter = splitter

        # Left panel: form
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 6, 0)

        form = QFormLayout()

        criterion_tips = {name: HEADER_TOOLTIPS.get(name, "") for name in globalVar.validCriterion}
        self.combo_criterion = QComboBox()
        fill_combo(self.combo_criterion, globalVar.validCriterion, CRITERION_LABELS,
                   criterion_tips, self.config.get("criterion", "authorKeywords"))
        self.combo_criterion.setToolTip(
            "Field of the documents to analyze.\n"
            "Hover an option of the list to see what it is.")
        form.addRow("Criterion:", self.combo_criterion)

        self.combo_graph_type = QComboBox()
        fill_combo(self.combo_graph_type, globalVar.validGrapTypes, GRAPH_TYPE_LABELS,
                   GRAPH_TYPE_TIPS, self.config.get("graph_type", "bar_trends"))
        self.combo_graph_type.setToolTip(
            "Graph drawn with the results.\n"
            "Hover an option of the list to see what it is.")
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
        self._link_year_range(self.spin_start_year, self.spin_end_year)

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
        left_layout.addWidget(self.chk_previous_results)

        self.chk_trend_analysis = QCheckBox("Trend analysis")
        self.chk_trend_analysis.setChecked(self.config.get("trend_analysis", False))
        self.chk_trend_analysis.setToolTip(
            "Find trending topics based on the highest Average Growth Rate (AGR).\n"
            "Extracts the top 200 topics, calculates AGR for the window period,\n"
            "and sorts them from highest to lowest AGR.")
        left_layout.addWidget(self.chk_trend_analysis)

        # Options used less often
        self.analysis_more = CollapsibleSection(
            "More options", expanded=self.config.get("more_options_open", False))
        more_form = QFormLayout(self.analysis_more.body)
        more_form.setContentsMargins(0, 0, 0, 0)

        self.edit_graph_title = QLineEdit(self.config.get("graph_title", ""))
        self.edit_graph_title.setPlaceholderText("No title")
        self.edit_graph_title.setToolTip("Title written above the graph.")
        more_form.addRow("Graph title:", self.edit_graph_title)

        size_row = QHBoxLayout()
        self.spin_plot_width = QDoubleSpinBox()
        self.spin_plot_height = QDoubleSpinBox()
        for spin, key, default in ((self.spin_plot_width, "plot_width", globalVar.DEFAULT_PLOT_WIDTH),
                                   (self.spin_plot_height, "plot_height", globalVar.DEFAULT_PLOT_HEIGHT)):
            spin.setRange(2.0, 40.0)
            spin.setDecimals(1)
            spin.setSingleStep(0.5)
            spin.setSuffix(" in")
            spin.setValue(self.config.get(key, default))
            spin.setToolTip(
                "Width and height of the graph in inches.\n"
                "For the bars, time line and world map graphs.")
        size_row.addWidget(self.spin_plot_width)
        size_row.addWidget(QLabel("×"))
        size_row.addWidget(self.spin_plot_height)
        more_form.addRow("Graph size:", size_row)

        self.chk_y_log = QCheckBox("Logarithmic scale")
        self.chk_y_log.setChecked(self.config.get("y_log", False))
        self.chk_y_log.setToolTip(
            "Logarithmic documents axis in the time line and evolution graphs,\n"
            "and logarithmic color scale in the world map, to see the topics\n"
            "or countries with few documents.")
        more_form.addRow(self.chk_y_log)

        self.chk_p_year = QCheckBox("Percentage per year")
        self.chk_p_year.setChecked(self.config.get("p_year", False))
        self.chk_p_year.setToolTip(
            "Time line graph: show each topic as a percentage of the\n"
            "documents published that year, instead of the number of documents.")
        more_form.addRow(self.chk_p_year)

        self.chk_agr_for_graph = QCheckBox("Growth rate (AGR) in evolution")
        self.chk_agr_for_graph.setChecked(self.config.get("agr_for_graph", False))
        self.chk_agr_for_graph.setToolTip(
            "Evolution graph: plot the Average Growth Rate (AGR) instead of\n"
            "the Average Documents per Year (ADY).")
        more_form.addRow(self.chk_agr_for_graph)

        self.chk_only_first = QCheckBox("Only the first author or country")
        self.chk_only_first.setChecked(self.config.get("only_first", False))
        self.chk_only_first.setToolTip(
            "Count only the first one of each document: the first author, or\n"
            "the country or the institution of the first author.\n"
            "For the authors, countries and institutions criteria.")
        more_form.addRow(self.chk_only_first)

        self.edit_filter = QLineEdit(self.config.get("filter", ""))
        self.edit_filter.setPlaceholderText("All countries")
        self.edit_filter.setToolTip(
            "Keep only the institutions of this country, for example Colombia.\n"
            "For the Institutions with country criterion.")
        more_form.addRow("Institutions of:", self.edit_filter)

        mask_row = QHBoxLayout()
        self.edit_word_cloud_mask = QLineEdit(self.config.get("word_cloud_mask", ""))
        self.edit_word_cloud_mask.setPlaceholderText("No mask")
        mask_tip = ("PNG image that gives its shape to the word cloud:\n"
                    "the words fill the areas that are not white.")
        self.edit_word_cloud_mask.setToolTip(mask_tip)
        mask_row.addWidget(self.edit_word_cloud_mask, stretch=1)
        self.btn_word_cloud_mask = QPushButton("Browse…")
        self.btn_word_cloud_mask.setToolTip(mask_tip)
        self.btn_word_cloud_mask.clicked.connect(self._browse_word_cloud_mask)
        mask_row.addWidget(self.btn_word_cloud_mask)
        more_form.addRow("Word cloud mask:", mask_row)

        left_layout.addWidget(self.analysis_more)
        left_layout.addStretch(1)

        # Right panel: custom topics and synonyms
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        topics_tip = (
            "Leave it empty to find the top topics of the criterion.\n"
            "To analyze your own topics, write one per line:\n"
            "  - commas group the names of one topic: internet of things, iot\n"
            "  - an asterisk matches any ending or beginning: smart*")
        topics_label = QLabel("Custom topics (leave empty to find the top topics):")
        topics_label.setToolTip(topics_tip)
        right_layout.addWidget(topics_label)

        self.custom_topics = QPlainTextEdit()
        self.custom_topics.setPlaceholderText(
            "One topic per line. Commas group the names of one topic, * is a wildcard:\n"
            "internet of things, iot\n"
            "indoor positioning, indoor localization\n"
            "smart*")
        self.custom_topics.setToolTip(topics_tip)
        right_layout.addWidget(self.custom_topics, stretch=3)

        self.analysis_synonyms = QPlainTextEdit()
        self.analysis_synonyms.setPlaceholderText(SYNONYMS_PLACEHOLDER)
        self.analysis_synonyms.setToolTip(SYNONYMS_TOOLTIP)
        # One list for the analysis and the maps. Older configurations kept two.
        saved = [self.config.get("synonyms", ""), self.config.get("net_synonyms", "")]
        lines = []
        for line in "\n".join(saved).splitlines():
            if line.strip() and line.strip() not in lines:
                lines.append(line.strip())
        self.analysis_synonyms.setPlainText("\n".join(lines))
        right_layout.addLayout(self._synonyms_header())
        right_layout.addWidget(self.analysis_synonyms, stretch=1)

        splitter.addWidget(scrollable(left_widget, [self.analysis_more]))
        splitter.addWidget(right_widget)

        # Restore splitter sizes
        try:
            sizes = self.config.get("splitter_sizes", [300, 600])
            splitter.setSizes(sizes)
        except Exception:
            splitter.setSizes([300, 600])

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

        top_cited_btn = QPushButton("Most cited documents")
        top_cited_btn.setToolTip(
            "List the most cited documents between Start Year and End Year.\n"
            "Topics length sets how many. With Use previous results, only\n"
            "the documents found by the last analysis are ranked.\n"
            "The table is saved as results/%s." % globalVar.TOP_CITED_FILE)
        top_cited_btn.clicked.connect(self.top_cited_run)
        btn_row.addWidget(top_cited_btn)

        clear_topics_btn = QPushButton("Clear topics")
        clear_topics_btn.setToolTip("Clear the Custom topics text area.")
        clear_topics_btn.clicked.connect(lambda: self.custom_topics.clear())
        btn_row.addWidget(clear_topics_btn)

        reset_btn = QPushButton("Reset defaults")
        reset_btn.setToolTip(
            "Reset the analysis parameters to their default values.\n"
            "The synonyms are kept.")
        reset_btn.clicked.connect(self._reset_analysis_defaults)
        btn_row.addWidget(reset_btn)

        btn_row.addStretch(1)

        run_btn = QPushButton("Run")
        run_btn.setDefault(True)
        run_btn.setToolTip("Run the analysis and draw the graph.\nShortcut: Ctrl+R")
        run_btn.clicked.connect(self.scientoPyRun)
        btn_row.addWidget(run_btn)

        page_layout.addLayout(btn_row)

        self.combo_criterion.currentIndexChanged.connect(self._update_analysis_controls)
        self.combo_graph_type.currentIndexChanged.connect(self._update_analysis_controls)
        self._update_analysis_controls()

    def _synonyms_header(self):
        """Label of a synonyms box with the button to load a thesaurus file."""
        row = QHBoxLayout()
        label = QLabel("Synonyms (one group per line):")
        label.setToolTip(SYNONYMS_TOOLTIP)
        row.addWidget(label, stretch=1)
        thesaurus_btn = QPushButton("Load thesaurus…")
        thesaurus_btn.setToolTip(
            "Add the synonyms of a VOSviewer thesaurus file (tab separated:\n"
            "label, replace by). Items with an empty 'replace by' go to the\n"
            "Exclude list of the maps tab.")
        thesaurus_btn.clicked.connect(self._load_thesaurus)
        row.addWidget(thesaurus_btn)
        return row

    def _browse_word_cloud_mask(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select the word cloud mask image",
            self.edit_word_cloud_mask.text() or "./",
            "PNG images (*.png);;All files (*.*)")
        if path:
            self.edit_word_cloud_mask.setText(path)

    def _update_analysis_controls(self, *_):
        """Enable the options that apply to the chosen criterion and graph."""
        if self._updating_controls:
            return
        self._updating_controls = True
        try:
            graph = self.combo_graph_type.currentData()

            # The world map only places countries
            if graph == "world_map":
                if self.combo_criterion.isEnabled():
                    self._criterion_before_map = self.combo_criterion.currentData()
                    self.combo_criterion.setEnabled(False)
                set_combo(self.combo_criterion, "country")
            elif not self.combo_criterion.isEnabled():
                self.combo_criterion.setEnabled(True)
                set_combo(self.combo_criterion, self._criterion_before_map)
            criterion = self.combo_criterion.currentData()

            self.chk_y_log.setEnabled(graph in ("time_line", "evolution", "world_map"))
            self.chk_p_year.setEnabled(graph == "time_line")
            self.chk_agr_for_graph.setEnabled(graph == "evolution")
            sized = graph in ("bar", "bar_trends", "time_line", "world_map")
            self.spin_plot_width.setEnabled(sized)
            self.spin_plot_height.setEnabled(sized)
            self.edit_word_cloud_mask.setEnabled(graph == "word_cloud")
            self.btn_word_cloud_mask.setEnabled(graph == "word_cloud")
            self.chk_only_first.setEnabled(
                criterion in ("author", "country", "institution", "institutionWithCountry"))
            self.edit_filter.setEnabled(criterion == "institutionWithCountry")
        finally:
            self._updating_controls = False

    # ── Results Tab ────────────────────────────────────────────

    def _create_results_tab(self):
        page = QWidget()
        self.page_results = page
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

        # Bottom bar: status label + buttons
        bottom_row = QHBoxLayout()

        self.results_status_label = QLabel("No results yet. Run preprocessing first.")
        self.results_status_label.setWordWrap(True)
        bottom_row.addWidget(self.results_status_label, stretch=1)

        self.results_open_btn = QPushButton("Open CSV")
        self.results_open_btn.setToolTip(
            "Open the file of this table with your spreadsheet application.")
        self.results_open_btn.setEnabled(False)
        self.results_open_btn.clicked.connect(lambda: self._open_path(self._results_file))
        bottom_row.addWidget(self.results_open_btn)

        copy_sel_btn = QPushButton("Copy Selection")
        copy_sel_btn.setToolTip("Copy the selected cells, with their headers.\nShortcut: Ctrl+C")
        copy_sel_btn.clicked.connect(self._copy_selected_cells)
        bottom_row.addWidget(copy_sel_btn)

        copy_all_btn = QPushButton("Copy All")
        copy_all_btn.setToolTip("Copy the whole table, to paste it in a spreadsheet or a document.")
        copy_all_btn.clicked.connect(self._copy_all_cells)
        bottom_row.addWidget(copy_all_btn)

        self.analyze_sel_btn = QPushButton("Analyze selection")
        self.analyze_sel_btn.setEnabled(False)
        self.analyze_sel_btn.clicked.connect(self._analyze_selection)
        bottom_row.addWidget(self.analyze_sel_btn)

        layout.addLayout(bottom_row)

        # Defer pre-loading so heavy modules are not imported before the window shows
        QTimer.singleShot(0, self._post_show_init)

    def _post_show_init(self):
        if os.path.exists(self.scientoPy.preprocessBriefFileName):
            self._load_results_table()
        self._refresh_dataset_status()
        self._apply_year_defaults()
        self._update_previous_results_enabled()
        self.status_bar.showMessage("Ready")

    def _load_results_table(self, filepath=None, kind="brief"):
        """Show a results CSV. kind is "brief" (preprocess report), "analysis"
        (topics of an analysis) or "themes" (thematic map)."""
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
        note = ""

        if kind == "analysis":
            # The years before the first document only hold zeros
            year_cols = [c for c, h in enumerate(headers) if len(h) == 4 and h.isdigit()]
            empty = []
            for c in year_cols[:-1]:
                if any(c < len(row) and row[c].strip() not in ("", "0", "0.0") for row in data):
                    break
                empty.append(c)
            if empty:
                drop = set(empty)
                note = ", from %s (the first year with documents)" % headers[empty[-1] + 1]
                headers = [h for c, h in enumerate(headers) if c not in drop]
                data = [[cell for c, cell in enumerate(row) if c not in drop] for row in data]

        self.results_table.setSortingEnabled(False)
        self.results_table.clearContents()

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
                    value = float(text)
                    # 36.66666666666667 -> 36.67 (the file keeps every decimal)
                    if "." in text and len(text.split(".")[1]) > 2 and "e" not in text.lower():
                        text = "%.2f" % value
                    item = NumericTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                except ValueError:
                    item = QTableWidgetItem(text)
                self.results_table.setItem(r, c, item)

        # The preprocess brief is a report with its own row order
        self.results_table.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        self.results_table.setSortingEnabled(kind != "brief")

        for col in range(len(headers)):
            self.results_table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )

        self.results_table.resizeRowsToContents()

        self._results_file = filepath
        self._results_kind = kind
        self.results_open_btn.setEnabled(True)
        self.analyze_sel_btn.setEnabled(kind == "analysis")
        self.analyze_sel_btn.setToolTip(
            "Copy the topic names from selected rows to the\n"
            "Custom topics field in the Analysis tab."
            if kind == "analysis" else
            "Available when the table shows the topics of an analysis.")
        title = {"brief": "Preprocess report", "analysis": "Analysis results",
                 "themes": "Thematic map themes"}.get(kind, "Results")
        self.results_status_label.setText("%s: %s%s" % (title, filepath, note))
        self.results_status_label.setToolTip(os.path.abspath(filepath))

    def _analyze_selection(self):
        """Copy topic names from selected rows to the Custom topics field."""
        if self._results_kind != "analysis":
            return
        selected_rows = sorted(set(idx.row() for idx in self.results_table.selectedIndexes()))
        if not selected_rows:
            self.status_bar.showMessage("No rows selected")
            return

        # The topic name is in column 1 (column 0 is "Pos.")
        topics = []
        for row in selected_rows:
            cell = self.results_table.item(row, 1)
            if cell and cell.text().strip():
                topics.append(cell.text().strip())

        if not topics:
            self.status_bar.showMessage("No topics found in selection")
            return

        self.custom_topics.setPlainText("\n".join(topics))
        self.tabs.setCurrentWidget(self.page_analysis)
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
        self.page_documents = page
        self.tabs.addTab(page, "4. Documents")
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

        self.ext_results_status_label = QLabel(
            "No documents yet. Run an analysis to list the documents of each topic, "
            "or use Most cited documents in the Analysis tab.")
        self.ext_results_status_label.setWordWrap(True)
        bottom_row.addWidget(self.ext_results_status_label, stretch=1)

        self.documents_open_btn = QPushButton("Open CSV")
        self.documents_open_btn.setEnabled(False)
        self.documents_open_btn.clicked.connect(lambda: self._open_path(self._documents_file))
        bottom_row.addWidget(self.documents_open_btn)

        copy_sel_btn = QPushButton("Copy Selection")
        copy_sel_btn.setToolTip("Copy the selected cells, with their headers.\nShortcut: Ctrl+C")
        copy_sel_btn.clicked.connect(self._copy_selected_ext_cells)
        bottom_row.addWidget(copy_sel_btn)

        copy_all_btn = QPushButton("Copy All")
        copy_all_btn.setToolTip("Copy the whole table, to paste it in a spreadsheet or a document.")
        copy_all_btn.clicked.connect(self._copy_all_ext_cells)
        bottom_row.addWidget(copy_all_btn)

        layout.addLayout(bottom_row)

    def _load_ext_results_table(self, filepath):
        """Load a documents CSV from disk (only used when the user
        exports or when -- in legacy flows -- such a file already exists)."""
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            return
        self._populate_ext_results(
            rows[0], rows[1:], description=os.path.basename(filepath), file_path=filepath
        )

    def _populate_ext_results_from_topics(self, topicResults, criterion):
        """Populate the Documents tab directly from the in-memory
        topicResults produced by the last analysis — no CSV round-trip."""
        import paperSave
        headers, data = paperSave.extendedResultsRows(topicResults, criterion)
        self._populate_ext_results(
            headers, data,
            description="documents of each topic of the last analysis "
                        "(not saved: use Extended results in the Export tab)"
        )

    def _populate_ext_results(self, headers, data, description="", file_path=None):
        """Show a table of documents. description says what the rows are and
        file_path is the CSV they were saved to, when there is one."""
        total = len(data)
        self._documents_file = file_path or ""
        self.documents_open_btn.setEnabled(bool(file_path))
        self.documents_open_btn.setToolTip(
            "Open the file of this table with your spreadsheet application."
            if file_path else
            "This table is not saved to a file. To save it, use\n"
            "Extended results in the Export tab.")

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
                        "Loading documents… %d / %d  (%d%%)"
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
                "%d rows: %s" % (total, description)
            )
        else:
            # Sensible interactive defaults without paying for content
            # measurement across every row.
            for col in range(len(headers)):
                self.ext_results_table.horizontalHeader().setSectionResizeMode(
                    col, QHeaderView.ResizeMode.Interactive
                )
            self.ext_results_status_label.setText(
                "%d rows: %s  "
                "(column auto-resize skipped for large tables — drag the "
                "header dividers to widen a column)"
                % (total, description)
            )

    # ── Export Tab ────────────────────────────────────────────

    def _create_export_tab(self):
        page = QWidget()
        self.page_export = page
        self.tabs.addTab(page, "6. Export")
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
        self.export_btn.setDefault(True)
        self.export_btn.clicked.connect(self._run_export)
        btn_row.addWidget(self.export_btn)
        layout.addLayout(btn_row)

        # Re-evaluate enabled state and default destination whenever the
        # source selection changes, so the path field suggests a sensible
        # default for each mode.
        self._src_group.buttonClicked.connect(self._update_export_enabled)
        self._update_export_enabled()

    # ── Network and Thematic Maps Tab ──────────────────────────

    def _create_network_tab(self):
        import networkAnalysis as na
        page = QWidget()
        self.page_maps = page
        self.tabs.addTab(page, "5. Network && Thematic Maps")
        page_layout = QVBoxLayout(page)

        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 6, 0)
        form = QFormLayout()

        criterion_tips = {
            "authorKeywords": "Keyword co-occurrence",
            "indexKeywords": "Keyword co-occurrence",
            "bothKeywords": "Keyword co-occurrence",
            "author": "Co-authorship",
            "country": "Collaboration between countries",
            "institution": "Collaboration between institutions",
            "institutionWithCountry": "Collaboration between institutions",
            "subject": "Subject area co-occurrence (WoS)",
        }
        self.net_criterion = QComboBox()
        fill_combo(self.net_criterion, globalVar.validNetworkCriterion, CRITERION_LABELS,
                   criterion_tips, self.config.get("net_criterion", "authorKeywords"))
        self.net_criterion.setToolTip(
            "Items of the maps. Two items are linked when they appear\n"
            "in the same document.")
        form.addRow("Criterion:", self.net_criterion)

        self.net_start_year = QSpinBox()
        self.net_start_year.setRange(1900, 2100)
        self.net_start_year.setValue(self.config.get("net_start_year", self.config.get("start_year", globalVar.DEFAULT_START_YEAR)))
        form.addRow("Start Year:", self.net_start_year)

        self.net_end_year = QSpinBox()
        self.net_end_year.setRange(1900, 2100)
        self.net_end_year.setValue(self.config.get("net_end_year", self.config.get("end_year", globalVar.DEFAULT_END_YEAR)))
        form.addRow("End Year:", self.net_end_year)
        self._link_year_range(self.net_start_year, self.net_end_year)

        self.net_length = QSpinBox()
        self.net_length.setRange(1, na.MAX_LENGTH)
        self.net_length.setValue(self.config.get("net_length", na.DEFAULT_LENGTH))
        self.net_length.setToolTip("Maximum number of items in the map, the top ones by occurrences.")
        form.addRow("Max items:", self.net_length)

        self.net_min_occ = QSpinBox()
        self.net_min_occ.setRange(1, 100000)
        self.net_min_occ.setValue(self.config.get("net_min_occurrences", na.DEFAULT_MIN_OCCURRENCES))
        self.net_min_occ.setToolTip("Minimum number of documents an item must appear in.")
        form.addRow("Min occurrences:", self.net_min_occ)

        self.net_skip_first = QSpinBox()
        self.net_skip_first.setRange(0, 1000)
        self.net_skip_first.setValue(self.config.get("net_skip_first", 0))
        self.net_skip_first.setToolTip(
            "Leave out the first N top items, for example the search\n"
            "terms that co-occur with everything.")
        form.addRow("Skip first:", self.net_skip_first)

        self.net_counting = QComboBox()
        fill_combo(self.net_counting, na.COUNTING_METHODS, COUNTING_LABELS, COUNTING_TIPS,
                   self.config.get("net_counting", na.DEFAULT_COUNTING))
        self.net_counting.setToolTip(
            "How a document counts for the links between its items.\n"
            "Hover an option of the list to see what it is.")
        form.addRow("Counting:", self.net_counting)

        self.net_resolution = QDoubleSpinBox()
        self.net_resolution.setRange(0.05, 20.0)
        self.net_resolution.setSingleStep(0.1)
        self.net_resolution.setDecimals(2)
        self.net_resolution.setValue(self.config.get("net_resolution", na.DEFAULT_RESOLUTION))
        self.net_resolution.setToolTip("Clustering resolution: higher values give more and smaller clusters.")
        form.addRow("Resolution:", self.net_resolution)

        self.net_min_cluster = QSpinBox()
        self.net_min_cluster.setRange(1, 1000)
        self.net_min_cluster.setValue(self.config.get("net_min_cluster_size", na.DEFAULT_MIN_CLUSTER_SIZE))
        self.net_min_cluster.setToolTip("Clusters with fewer items are merged into their most connected cluster.")
        form.addRow("Min cluster size:", self.net_min_cluster)

        left_layout.addLayout(form)

        self.net_previous = QCheckBox("Use previous results")
        self.net_previous.setChecked(self.config.get("net_previous_results", False))
        left_layout.addWidget(self.net_previous)

        # Options used less often
        self.net_more = CollapsibleSection(
            "More options", expanded=self.config.get("net_more_options_open", False))
        more_form = QFormLayout(self.net_more.body)
        more_form.setContentsMargins(0, 0, 0, 0)

        self.net_title = QLineEdit(self.config.get("net_title", ""))
        self.net_title.setPlaceholderText("No title")
        self.net_title.setToolTip("Title shown in the network map and above the thematic map.")
        more_form.addRow("Title:", self.net_title)

        self.net_min_link = QDoubleSpinBox()
        self.net_min_link.setRange(0.0, 100000.0)
        self.net_min_link.setDecimals(2)
        self.net_min_link.setSingleStep(1.0)
        self.net_min_link.setValue(self.config.get("net_min_link_strength", na.DEFAULT_MIN_LINK_STRENGTH))
        self.net_min_link.setToolTip(
            "Leave out the links weaker than this value, for example 2 to keep\n"
            "the pairs of items that appear together in at least 2 documents.\n"
            "0 keeps every link.")
        more_form.addRow("Min link strength:", self.net_min_link)

        self.net_cohesion = QDoubleSpinBox()
        self.net_cohesion.setRange(0.0, 5.0)
        self.net_cohesion.setDecimals(2)
        self.net_cohesion.setSingleStep(0.1)
        self.net_cohesion.setValue(self.config.get("net_cohesion", na.DEFAULT_COHESION))
        self.net_cohesion.setToolTip(
            "Network map: extra attraction between the items of a cluster, so\n"
            "each cluster reads as its own region. 0 is the plain VOS layout.")
        more_form.addRow("Cluster cohesion:", self.net_cohesion)

        self.theme_labels = QSpinBox()
        self.theme_labels.setRange(1, 10)
        self.theme_labels.setValue(self.config.get("theme_labels", na.DEFAULT_THEME_LABELS))
        self.theme_labels.setToolTip(
            "Thematic map: number of items written on each theme,\n"
            "the ones with more documents.")
        more_form.addRow("Labels per theme:", self.theme_labels)

        self.theme_axes = QComboBox()
        fill_combo(self.theme_axes, na.THEMATIC_AXES, THEME_AXES_LABELS, THEME_AXES_TIPS,
                   self.config.get("theme_axes", "rank"))
        self.theme_axes.setToolTip(
            "Thematic map: how the themes are placed.\n"
            "Hover an option of the list to see what it is.")
        more_form.addRow("Theme positions:", self.theme_axes)

        left_layout.addWidget(self.net_more)
        left_layout.addStretch(1)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.net_synonyms = QPlainTextEdit()
        # The same list as in the Analysis tab: both boxes edit one text
        self.net_synonyms.setDocument(self.analysis_synonyms.document())
        self.net_synonyms.setPlaceholderText(SYNONYMS_PLACEHOLDER)
        self.net_synonyms.setToolTip(SYNONYMS_TOOLTIP)
        right_layout.addLayout(self._synonyms_header())
        right_layout.addWidget(self.net_synonyms, stretch=3)
        exclude_label = QLabel("Exclude: one item per line:")
        exclude_tip = "Items left out of the maps, for example the terms used to search the dataset."
        exclude_label.setToolTip(exclude_tip)
        right_layout.addWidget(exclude_label)
        self.net_exclude = QPlainTextEdit()
        self.net_exclude.setToolTip(exclude_tip)
        self.net_exclude.setPlainText(self.config.get("net_exclude", ""))
        right_layout.addWidget(self.net_exclude, stretch=1)

        splitter.addWidget(scrollable(left_widget, [self.net_more]))
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 600])
        page_layout.addWidget(splitter, stretch=1)

        btn_row = QHBoxLayout()
        reset_btn = QPushButton("Reset defaults")
        reset_btn.setToolTip(
            "Reset the map parameters to their default values.\n"
            "The synonyms and the exclude list are kept.")
        reset_btn.clicked.connect(self._reset_network_defaults)
        btn_row.addWidget(reset_btn)
        btn_row.addStretch(1)

        open_btn = QPushButton("Open last network map")
        open_btn.setToolTip("Open the last network map of this criterion in the web browser.")
        open_btn.clicked.connect(self._open_network_map)
        btn_row.addWidget(open_btn)

        thematic_btn = QPushButton("Thematic map")
        thematic_btn.setToolTip(
            "Plot the thematic map (strategic diagram) of the same clusters:\n"
            "each cluster is a theme, placed by its centrality (relevance) and\n"
            "density (development) as a motor, niche, basic, or emerging or\n"
            "declining theme. The table is shown in the Results tab.")
        thematic_btn.clicked.connect(self.thematic_run)
        btn_row.addWidget(thematic_btn)

        run_btn = QPushButton("Network map")
        run_btn.setDefault(True)
        run_btn.setToolTip(
            "Build the co-occurrence network (VOSviewer style) and open the\n"
            "interactive 3D map in the web browser. Works offline.\nShortcut: Ctrl+R")
        run_btn.clicked.connect(self.network_run)
        btn_row.addWidget(run_btn)
        page_layout.addLayout(btn_row)

    def _reset_network_defaults(self):
        import networkAnalysis as na
        start, end = self._default_year_range()
        set_combo(self.net_criterion, "authorKeywords")
        self.net_end_year.setValue(end)
        self.net_start_year.setValue(start)
        self.net_length.setValue(na.DEFAULT_LENGTH)
        self.net_min_occ.setValue(na.DEFAULT_MIN_OCCURRENCES)
        self.net_skip_first.setValue(0)
        set_combo(self.net_counting, na.DEFAULT_COUNTING)
        self.net_resolution.setValue(na.DEFAULT_RESOLUTION)
        self.net_min_cluster.setValue(na.DEFAULT_MIN_CLUSTER_SIZE)
        self.net_previous.setChecked(False)
        self.net_title.clear()
        self.net_min_link.setValue(na.DEFAULT_MIN_LINK_STRENGTH)
        self.net_cohesion.setValue(na.DEFAULT_COHESION)
        self.theme_labels.setValue(na.DEFAULT_THEME_LABELS)
        set_combo(self.theme_axes, "rank")
        self.status_bar.showMessage("Map parameters reset to defaults")

    def _load_thesaurus(self):
        import networkAnalysis as na
        path, _ = QFileDialog.getOpenFileName(
            self, "Select a VOSviewer thesaurus file", "./",
            "Thesaurus files (*.txt *.tsv);;All files (*.*)")
        if not path:
            return
        groups = {}
        excluded = []
        for variant, canonical in na.parse_synonyms(path).items():
            if canonical:
                groups.setdefault(canonical, []).append(variant)
            else:
                excluded.append(variant)
        lines = [", ".join([c] + [v for v in vs if v != c.upper()]) for c, vs in groups.items()]
        if lines:
            self.net_synonyms.appendPlainText("\n".join(lines))
        if excluded:
            self.net_exclude.appendPlainText("\n".join(excluded))
        message = "Thesaurus loaded: %d synonym groups" % len(lines)
        if excluded:
            message += ", %d items added to the Exclude list of the maps tab" % len(excluded)
        self.status_bar.showMessage(message)

    def _network_html_path(self):
        criterion = self.net_criterion.currentData()
        return os.path.join(globalVar.GRAPHS_OUT_FOLDER, criterion[0].upper() + criterion[1:] + "_network.html")

    def _open_network_map(self):
        path = self._network_html_path()
        if os.path.exists(path):
            import pathlib
            webbrowser.open(pathlib.Path(os.path.abspath(path)).as_uri())
        else:
            QMessageBox.information(
                self, "Network map",
                "No network map yet for %s. Click Network map first."
                % self.net_criterion.currentText().lower())

    def _network_params(self):
        """Parameters of the maps tab that select items, links and clusters."""
        synonyms = ";".join(line.strip() for line in self.net_synonyms.toPlainText().splitlines() if line.strip())
        return dict(
            criterion=self.net_criterion.currentData(),
            start_year=self.net_start_year.value(),
            end_year=self.net_end_year.value(),
            length=self.net_length.value(),
            min_occurrences=self.net_min_occ.value(),
            skip_first=self.net_skip_first.value(),
            exclude=self.net_exclude.toPlainText().splitlines(),
            synonyms=synonyms,
            counting=self.net_counting.currentData(),
            min_link_strength=self.net_min_link.value(),
            resolution=self.net_resolution.value(),
            min_cluster_size=self.net_min_cluster.value(),
            previous_results=self.net_previous.isChecked(),
            title=self.net_title.text().strip(),
        )

    def _run_with_progress(self, task, what):
        """Run task() in a thread behind the progress dialog.

        Returns its result, or None when it was canceled or failed (the
        error is already shown). what names the task in the messages.
        """
        import networkAnalysis as na

        globalVar.cancelProcess = False
        globalVar.progressPer = 0
        self._thread_error = None
        result = []

        def run():
            try:
                result.append(task())
            except na.NetworkCanceled:
                pass
            except na.NetworkError as e:
                self._thread_error = str(e)
            except Exception as e:
                self._thread_error = "Unexpected error: %s" % e
            finally:
                globalVar.progressPer = 101  # closes the progress dialog

        t1 = threading.Thread(target=run)
        t1.start()
        ProgressDialog(self).exec()
        t1.join()

        if globalVar.cancelProcess:
            self.status_bar.showMessage("%s canceled" % what)
            return None
        if self._thread_error:
            self.status_bar.showMessage("%s failed" % what)
            QMessageBox.critical(self, "Error", self._thread_error)
            return None
        return result[0] if result else None

    def network_run(self):
        import pathlib
        import networkAnalysis as na

        if not self.net_previous.isChecked() and not os.path.exists(self.scientoPy.preprocessDatasetFile):
            QMessageBox.critical(self, "Error",
                                 "No preprocess input dataset, please run the preprocess first")
            return

        params = self._network_params()
        params["cohesion"] = self.net_cohesion.value()
        self.status_bar.showMessage("Building network map...")
        result = self._run_with_progress(lambda: na.generate_network_map(**params), "Network map")
        if result is None:
            return

        data, files = result
        self.status_bar.showMessage(
            "Network map \u2014 %d items, %d links, %d clusters \u2014 saved to %s"
            % (len(data["nodes"]), len(data["links"]), len(data["clusters"]), files["html"]))
        webbrowser.open(pathlib.Path(os.path.abspath(files["html"])).as_uri())

    def thematic_run(self):
        import types
        import matplotlib.pyplot as plt
        import graphUtils
        import networkAnalysis as na

        if not self.net_previous.isChecked() and not os.path.exists(self.scientoPy.preprocessDatasetFile):
            QMessageBox.critical(self, "Error",
                                 "No preprocess input dataset, please run the preprocess first")
            return

        params = self._network_params()
        self.status_bar.showMessage("Building thematic map...")
        result = self._run_with_progress(lambda: na.generate_thematic_map(**params), "Thematic map")
        if result is None:
            return

        data, themes, files = result
        self.status_bar.showMessage(
            "Thematic map \u2014 %d themes from %d items \u2014 saved to %s"
            % (len(themes), len(data["nodes"]), files["themes"]))

        apply_matplotlib_theme(QApplication.instance(), self.config.get("graph_appearance", "Same as UI"))
        self.scientoPy.closePlot()
        args = types.SimpleNamespace(
            criterion=params["criterion"], labels=self.theme_labels.value(),
            axes=self.theme_axes.currentData(),
            graphTitle=params["title"], savePlot="",
            plotWidth=globalVar.DEFAULT_PLOT_WIDTH, plotHeight=globalVar.DEFAULT_PLOT_HEIGHT)
        graphUtils.show_thematic_map(plt, themes, args, fromGui=True)
        QApplication.instance().processEvents()

        self._load_results_table(files["themes"], kind="themes")
        self.tabs.setCurrentWidget(self.page_results)

    def top_cited_run(self):
        import topCitedPapers

        previous = self.chk_previous_results.isChecked()
        if not previous and not os.path.exists(self.scientoPy.preprocessDatasetFile):
            QMessageBox.critical(self, "Error",
                                 "No preprocess input dataset, please run the preprocess first")
            return

        length = max(1, self.spin_topics_length.value())
        start_year = self.spin_start_year.value()
        end_year = self.spin_end_year.value()
        globalVar.progressText = "Finding the most cited documents"
        self.status_bar.showMessage("Finding the most cited documents...")
        result = self._run_with_progress(
            lambda: topCitedPapers.topCited(length, start_year, end_year, previous),
            "Most cited documents")
        if result is None:
            return

        headers, rows, path = result
        self._populate_ext_results(
            headers, rows, description="most cited documents, saved to %s" % path, file_path=path)
        self.status_bar.showMessage(
            "Most cited documents \u2014 %d documents \u2014 saved to %s" % (len(rows), path))
        self.tabs.setCurrentWidget(self.page_documents)

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
        self.export_btn.setToolTip(tip or "Shortcut: Ctrl+R")

        # The suggested destination follows the source, unless the user wrote one
        current = self.export_path_entry.text()
        if not current or current == getattr(self, "_export_auto_path", None):
            self._export_auto_path = self._default_export_path()
            self.export_path_entry.setText(self._export_auto_path)

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
        start, end = self._default_year_range()
        set_combo(self.combo_graph_type, "bar_trends")
        set_combo(self.combo_criterion, "authorKeywords")
        self.spin_end_year.setValue(end)
        self.spin_start_year.setValue(start)
        self.spin_topics_length.setValue(10)
        self.spin_skip_first.setValue(0)
        self.spin_window_width.setValue(2)
        self.chk_previous_results.setChecked(False)
        self.chk_trend_analysis.setChecked(False)
        self.edit_graph_title.clear()
        self.spin_plot_width.setValue(globalVar.DEFAULT_PLOT_WIDTH)
        self.spin_plot_height.setValue(globalVar.DEFAULT_PLOT_HEIGHT)
        self.chk_y_log.setChecked(False)
        self.chk_p_year.setChecked(False)
        self.chk_agr_for_graph.setChecked(False)
        self.chk_only_first.setChecked(False)
        self.edit_filter.clear()
        self.edit_word_cloud_mask.clear()
        self.custom_topics.clear()
        self.status_bar.showMessage("Analysis parameters reset to defaults")

    def _run_current_tab(self):
        """Ctrl+R handler: run the main action of the active tab."""
        page = self.tabs.currentWidget()
        if page is self.page_preprocess:
            self.run_preprocess()
        elif page is self.page_analysis:
            self.scientoPyRun()
        elif page is self.page_maps:
            self.network_run()
        elif page is self.page_export and self.export_btn.isEnabled():
            self._run_export()

    # ── Actions ───────────────────────────────────────────────

    def select_dataset(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select dataset folder")
        if dir_name:
            self.dataset_entry.setText(dir_name)
            self.config["last_dataset_folder"] = dir_name

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
            elif globalVar.totalPapers > 0:
                self.status_bar.showMessage(
                    "Preprocessing complete \u2014 %d papers" % globalVar.totalPapers)
                apply_matplotlib_theme(QApplication.instance(), self.config.get("graph_appearance", "Same as UI"))
                self.preprocess.graphBrief()
                self._load_results_table()
                self._update_export_enabled()
                self._refresh_dataset_status()
                self._apply_year_defaults()
                self.tabs.setCurrentWidget(self.page_results)
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

        criterion = self.combo_criterion.currentData()
        topics_text = self.custom_topics.toPlainText().strip()
        if criterion == "abstract" and not topics_text:
            QMessageBox.information(
                self, "Analysis",
                "The abstract criterion looks for your topics inside the abstracts, "
                "so it needs custom topics.\n\nWrite them in the Custom topics box, "
                "one per line, for example:\n    machine learning, deep learning\n    sensor*")
            self.custom_topics.setFocus()
            return

        mask = self.edit_word_cloud_mask.text().strip() if self.edit_word_cloud_mask.isEnabled() else ""
        if mask and not os.path.isfile(mask):
            QMessageBox.critical(self, "Error", "Word cloud mask image not found: %s" % mask)
            return

        self.scientoPy.closePlot()

        self.scientoPy.criterion = criterion
        self.scientoPy.graphType = self.combo_graph_type.currentData()
        # An option that does not apply to this criterion or graph is not used
        self.scientoPy.graphTitle = self.edit_graph_title.text().strip()
        self.scientoPy.yLog = self.chk_y_log.isEnabled() and self.chk_y_log.isChecked()
        self.scientoPy.pYear = self.chk_p_year.isEnabled() and self.chk_p_year.isChecked()
        self.scientoPy.agrForGraph = self.chk_agr_for_graph.isEnabled() and self.chk_agr_for_graph.isChecked()
        self.scientoPy.onlyFirst = self.chk_only_first.isEnabled() and self.chk_only_first.isChecked()
        self.scientoPy.filter = self.edit_filter.text().strip() if self.edit_filter.isEnabled() else ""
        self.scientoPy.wordCloudMask = mask
        if self.spin_plot_width.isEnabled():
            self.scientoPy.plotWidth = self.spin_plot_width.value()
            self.scientoPy.plotHeight = self.spin_plot_height.value()
        else:
            self.scientoPy.plotWidth = globalVar.DEFAULT_PLOT_WIDTH
            self.scientoPy.plotHeight = globalVar.DEFAULT_PLOT_HEIGHT
        self.scientoPy.startYear = self.spin_start_year.value()
        self.scientoPy.endYear = self.spin_end_year.value()
        self.scientoPy.length = self.spin_topics_length.value()
        self.scientoPy.skipFirst = self.spin_skip_first.value()
        self.scientoPy.windowWidth = self.spin_window_width.value()
        self.scientoPy.previousResults = self.chk_previous_results.isChecked()
        self.scientoPy.trend = self.chk_trend_analysis.isChecked()

        if topics_text:
            self.scientoPy.topics = topics_text.replace("\n", ";")
        else:
            self.scientoPy.topics = ''

        self.scientoPy.synonyms = ";".join(
            line.strip() for line in self.analysis_synonyms.toPlainText().splitlines() if line.strip())

        self._thread_error = None
        self.status_bar.showMessage("Running analysis...")

        def run_analysis():
            try:
                self.scientoPy.scientoPy()
            except ScientoPyError as e:
                self._thread_error = str(e)
            finally:
                # Closes the progress dialog, also when the analysis stops early
                globalVar.progressPer = 101

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
        if topic_count == 0:
            self.status_bar.showMessage("Analysis finished \u2014 no results found")
            QMessageBox.information(
                self, "Analysis",
                "No results found. Check the year range and the criterion.")
            return
        self.status_bar.showMessage(
            "Analysis complete \u2014 %d %s found" % (topic_count, "topic" if topic_count == 1 else "topics"))

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
            self._load_results_table(self.scientoPy.resultsFileName, kind="analysis")
        self._update_export_enabled()
        self._update_previous_results_enabled()
        if self.scientoPy.resultsFileName:
            self.tabs.setCurrentWidget(self.page_results)
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
        self.config["last_dataset_folder"] = self.dataset_entry.text().strip()
        self.config["remove_duplicates"] = self.chk_remove_dupl.isChecked()
        # With the world map the criterion list is locked on countries
        self.config["criterion"] = (self.combo_criterion.currentData() if self.combo_criterion.isEnabled()
                                    else self._criterion_before_map)
        self.config["graph_type"] = self.combo_graph_type.currentData()
        self.config["start_year"] = self.spin_start_year.value()
        self.config["end_year"] = self.spin_end_year.value()
        self.config["topics_length"] = self.spin_topics_length.value()
        self.config["skip_first"] = self.spin_skip_first.value()
        self.config["window_width"] = self.spin_window_width.value()
        self.config["previous_results"] = self.chk_previous_results.isChecked()
        self.config["trend_analysis"] = self.chk_trend_analysis.isChecked()
        self.config["synonyms"] = self.analysis_synonyms.toPlainText()
        self.config.pop("net_synonyms", None)   # one shared list now
        self.config["more_options_open"] = self.analysis_more.isExpanded()
        self.config["graph_title"] = self.edit_graph_title.text()
        self.config["plot_width"] = self.spin_plot_width.value()
        self.config["plot_height"] = self.spin_plot_height.value()
        self.config["y_log"] = self.chk_y_log.isChecked()
        self.config["p_year"] = self.chk_p_year.isChecked()
        self.config["agr_for_graph"] = self.chk_agr_for_graph.isChecked()
        self.config["only_first"] = self.chk_only_first.isChecked()
        self.config["filter"] = self.edit_filter.text()
        self.config["word_cloud_mask"] = self.edit_word_cloud_mask.text()
        # Save network map parameters
        self.config["net_criterion"] = self.net_criterion.currentData()
        self.config["net_start_year"] = self.net_start_year.value()
        self.config["net_end_year"] = self.net_end_year.value()
        self.config["net_length"] = self.net_length.value()
        self.config["net_min_occurrences"] = self.net_min_occ.value()
        self.config["net_skip_first"] = self.net_skip_first.value()
        self.config["net_counting"] = self.net_counting.currentData()
        self.config["net_resolution"] = self.net_resolution.value()
        self.config["net_min_cluster_size"] = self.net_min_cluster.value()
        self.config["net_previous_results"] = self.net_previous.isChecked()
        self.config["net_exclude"] = self.net_exclude.toPlainText()
        self.config["net_more_options_open"] = self.net_more.isExpanded()
        self.config["net_title"] = self.net_title.text()
        self.config["net_min_link_strength"] = self.net_min_link.value()
        self.config["net_cohesion"] = self.net_cohesion.value()
        self.config["theme_labels"] = self.theme_labels.value()
        self.config["theme_axes"] = self.theme_axes.currentData()
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
