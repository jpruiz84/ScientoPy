# ScientoPy UI Modernization Specification

## 1. Overview

This document specifies the modernization of the ScientoPy graphical user interface, replacing the current Tkinter-based implementation with PySide6 (Qt 6), providing native cross-platform appearance, built-in high-DPI scaling, and light/dark theme support.

**Current version:** 2.1.6  
**Entry point:** `ScientoPyGui.py`

---

## 2. Current UI Analysis

### 2.1 Technology Stack

| Component | Current Technology |
|---|---|
| GUI framework | Tkinter (Python built-in) |
| Widget theme | ttk default theme |
| Image handling | Pillow (PIL) |
| Plots/graphs | Matplotlib (external windows) |
| Word clouds | wordcloud library |
| Layout | Mixed: `grid()` + `place()` with absolute coordinates |

### 2.2 Current Window Structure

- **Main window:** Fixed 853x480 pixels, non-resizable
- **Two tabs** via `ttk.Notebook`:
  - **Tab 1 - Pre-processing:** Logo splash, dataset folder selector, "Remove duplicated documents" checkbox, action buttons
  - **Tab 2 - Analysis:** Left-side form (criterion, graph type, year range, topics length, skip first, window width, checkboxes), right-side custom topics text area, bottom action buttons
- **Progress dialog:** Separate `Toplevel` popup (300x120 px) with label, progress bar, and cancel button
- **Plot windows:** Matplotlib figures open in separate OS windows via `plt.show()`

### 2.3 Current Limitations

| Issue | Details |
|---|---|
| **Fixed window size** | 853x480 px, non-resizable. Unusable on high-DPI (4K) displays where it appears tiny |
| **No DPI awareness** | All dimensions are hardcoded in pixels. No scaling for HiDPI monitors |
| **No theme support** | Background color detection is rudimentary (checkbox color only). No light/dark theme system |
| **Tkinter appearance** | Widgets look outdated and inconsistent across platforms (especially on macOS and Linux) |
| **Mixed layout strategy** | Combination of `grid()` and `place()` with absolute relx/rely coordinates makes the layout fragile |
| **External plot windows** | Matplotlib graphs open in separate unmanaged windows, disconnected from the main UI |
| **No responsive layout** | Widgets don't adapt to window resizing or different screen sizes |
| **Font scaling** | Hardcoded font size 10 does not adapt to system DPI settings |
| **Platform inconsistency** | Tkinter renders differently on Windows, macOS, and Linux (GTK vs Aqua vs Win32) |
| **Hardcoded plot dimensions** | Word cloud: 1960x1080 px, evolution: 800x500 px, default plots: 6.4x4.8 inches -- all fixed |

---

## 3. Target UI Framework: PySide6 (Qt 6)

### 3.1 Recommendation

Replace Tkinter with **PySide6**, the official Python bindings for Qt 6.

**Rationale:**
- **Best-in-class DPI scaling:** Qt 6 enables automatic high-DPI scaling by default (`AA_EnableHighDpiScaling`). Per-monitor DPI awareness works out of the box on Windows, macOS, and Linux with no manual intervention
- **Native appearance:** Qt widgets use platform-native styling (Windows 11 controls, macOS Aqua, GTK integration on Linux) for a professional look on every OS
- **Proven at scale:** Used by major desktop applications (Calibre, Spyder IDE, Anki, FreeCAD, QGIS)
- **Mature theme system:** Full QPalette-based theming with OS dark/light mode detection, plus Qt Style Sheets (QSS) for fine-grained customization
- **Rich widget set:** QTabWidget, QComboBox, QSpinBox, QProgressBar, QPlainTextEdit, QSplitter -- all map directly to ScientoPy's needs. QSpinBox provides integer input with built-in validation (no custom validation code needed)
- **Matplotlib integration:** `matplotlib.backends.backend_qtagg.FigureCanvasQTAgg` allows embedding plots directly inside the Qt window, or opening them in separate Qt-managed windows with consistent DPI handling
- **Signals & slots:** Clean, type-safe event model replacing Tkinter's command callbacks and variable traces
- **Threading:** `QThread` + signals provide a robust pattern for background processing with UI updates, replacing the current `threading.Thread` + `time.sleep` polling loop
- **License:** LGPLv3 (free for open-source projects like ScientoPy under MIT)
- **Active maintenance:** Developed by The Qt Company with regular releases tracking Qt 6.x

**Alternative considered:** CustomTkinter was initially evaluated as a drop-in Tkinter replacement. While it requires less refactoring, its DPI auto-scaling is unreliable across platforms, its widget set is limited (no native spinbox, no splitter), and it depends on a community project with less long-term stability than Qt.

### 3.2 New Dependencies

```
PySide6>=6.6.0
```

PySide6 bundles Qt 6 binaries (~80 MB installed). No additional sub-packages are needed -- `PySide6-Essentials` is sufficient if install size is a concern.

**Retained dependencies:** Pillow (for image preprocessing only), matplotlib, wordcloud, numpy, pandas, scipy, unidecode

**No longer needed:** `tkinter` (stdlib, but no longer imported)

---

## 4. Functional Specification

### 4.1 Window and Layout

| Property | Current | New |
|---|---|---|
| Default size | 853x480 (fixed) | 1000x600 (minimum), resizable |
| Minimum size | N/A | 853x480 |
| Resizable | No | Yes (both axes) |
| Layout engine | Mixed grid/place | `QVBoxLayout` / `QHBoxLayout` / `QGridLayout` / `QSplitter` |
| DPI handling | None | Qt 6 automatic high-DPI scaling (per-monitor aware) |

The window must resize gracefully. Use a `QSplitter` between the left form panel and the right custom topics area in the Analysis tab so the user can drag to adjust proportions. Form controls on the left should maintain their natural width via `QSizePolicy.Fixed` or `QSizePolicy.Preferred`.

### 4.2 Theme Support

| Feature | Specification |
|---|---|
| Modes | Light, Dark, System (follow OS) |
| Default | System |
| Switching | Menu bar: View > Appearance > Light / Dark / System |
| Styling method | `QPalette` for color scheme + optional QSS overrides for fine-tuning |
| OS detection | Use `QStyleHints.colorScheme()` (Qt 6.5+) to detect OS dark/light mode |
| Persistence | Save preference to a config file (e.g., `scientopy_config.json`) |

**Dark palette implementation:**

```python
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

def apply_dark_palette(app: QApplication):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(43, 43, 43))
    palette.setColor(QPalette.WindowText, QColor(204, 204, 204))
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
    palette.setColor(QPalette.ToolTipBase, QColor(43, 43, 43))
    palette.setColor(QPalette.ToolTipText, QColor(204, 204, 204))
    palette.setColor(QPalette.Text, QColor(204, 204, 204))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(204, 204, 204))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
```

Remove the current manual background color detection logic (`bg_color_rgb`, `bg_color_avg`, `cb_square_color`).

### 4.3 DPI and Scaling

| Feature | Specification |
|---|---|
| Auto DPI detection | Qt 6 handles this natively -- no application code required |
| Per-monitor DPI | Supported automatically on Windows 10+, macOS, and Wayland |
| Manual override | Optional: `QApplication.setHighDpiScaleFactorRoundingPolicy()` or environment variable `QT_SCALE_FACTOR=1.5` |
| Widget scaling | All Qt widgets scale automatically with the platform DPI |
| Plot DPI | Read screen DPI via `QScreen.logicalDotsPerInch()` and pass to matplotlib `figure(dpi=...)` |

On a 4K monitor (3840x2160) at 200% system scaling, the window and all widgets appear at the same physical size as on a 1920x1080 monitor at 100%. No manual intervention required.

### 4.4 Tab Structure

Maintain the existing two-tab structure using `QTabWidget`:

**Tab 1 - Pre-processing:**
- ScientoPy logo (centered, responsive to window size via `QLabel` + `QPixmap` with `scaled()` and `Qt.KeepAspectRatio`)
- Version and institution info (`QLabel`, centered)
- Dataset folder: label + `QLineEdit` + "Browse" `QPushButton` (in a `QHBoxLayout`, line edit expands)
- "Remove duplicated documents" `QCheckBox`
- Action buttons row: "Run preprocess", "Open preprocess brief" (in a `QHBoxLayout`, right-aligned)

**Tab 2 - Analysis:**
- **Left panel** (fixed width ~280px, `QFormLayout`):
  - Criterion: `QComboBox` (dropdown)
  - Graph type: `QComboBox` (dropdown)
  - Start Year: `QSpinBox` (range 1900-2100, built-in integer validation and up/down arrows)
  - End Year: `QSpinBox` (range 1900-2100, built-in integer validation and up/down arrows)
  - Topics length: `QSpinBox` (range 0-1000)
  - Skip first: `QSpinBox` (range 0-1000)
  - Window (years): `QSpinBox` (range 1-100)
  - "Use previous results" `QCheckBox`
  - "Trend analysis" `QCheckBox`
- **Right panel** (expandable, separated by `QSplitter`):
  - "Custom topics" `QLabel`
  - `QPlainTextEdit` (multi-line, scrollable, expands with window)
- **Bottom bar** (full width, `QHBoxLayout`):
  - Left-aligned: "Open results table", "Open extended results", "Generate BibTeX"
  - Spacer (`QSpacerItem` with `QSizePolicy.Expanding`)
  - Right-aligned: "Run"

### 4.5 Progress Dialog

Replace the `Toplevel` popup with a `QDialog`:

- Size: 350x140 (logical pixels, scaled automatically by Qt DPI)
- Centered over the main window via `dialog.move()` relative to parent geometry
- `QProgressBar` (determinate mode, range 0-100)
- Status label (`QLabel`)
- "Cancel" button (`QPushButton`)
- **Modal behavior:** `dialog.setWindowModality(Qt.WindowModal)` disables the main window while progress is active
- **Update mechanism:** Use a `QTimer` (100ms interval) to poll `globalVar.progressPer` and `globalVar.progressText`, replacing the current `while` loop with `time.sleep`. This keeps the Qt event loop responsive without blocking.

### 4.6 Plot Display

Matplotlib plots continue to open in separate windows, but use the Qt backend for consistent behavior:

```python
import matplotlib
matplotlib.use('QtAgg')  # Use Qt backend instead of default TkAgg
```

| Improvement | Details |
|---|---|
| Qt backend | `matplotlib.use('QtAgg')` -- plot windows are Qt-managed, inherit DPI scaling and theme |
| DPI awareness | Read DPI via `QScreen.logicalDotsPerInch()` and set `matplotlib.rcParams['figure.dpi']` |
| Theme-aware plots | Detect current theme mode; apply `plt.style.use('default')` for light or a dark stylesheet for dark mode |
| Consistent sizing | Calculate figure size in inches from desired pixel size divided by actual screen DPI |
| Font scaling | Scale matplotlib font sizes proportionally to the system DPI scaling factor |

**Optional future enhancement:** Embed plots directly in the main window using `FigureCanvasQTAgg` inside a `QWidget`, eliminating separate windows entirely.

**Dark mode matplotlib style overrides** (when dark theme is active):
```python
{
    'figure.facecolor': '#2b2b2b',
    'axes.facecolor': '#2b2b2b',
    'axes.edgecolor': '#cccccc',
    'axes.labelcolor': '#cccccc',
    'text.color': '#cccccc',
    'xtick.color': '#cccccc',
    'ytick.color': '#cccccc',
    'grid.color': '#555555',
}
```

The word cloud background should also adapt: white for light theme, `#2b2b2b` for dark theme.

---

## 5. Widget Mapping

Detailed mapping from current Tkinter widgets to PySide6 replacements:

| Current (Tkinter) | New (PySide6) | Notes |
|---|---|---|
| `Tk()` | `QMainWindow` | Main window (with menu bar support) |
| `ttk.Notebook` | `QTabWidget` | Tab container with native styling |
| `Frame` | `QWidget` + layout | Container with `QVBoxLayout` / `QHBoxLayout` / `QGridLayout` |
| `Label` | `QLabel` | Text and image labels |
| `Entry` | `QLineEdit` | Single-line text input |
| `Spinbox` | `QSpinBox` | Integer input with built-in validation, range, and arrows |
| `Button` | `QPushButton` | Action buttons |
| `Checkbutton` + `BooleanVar` | `QCheckBox` | Boolean toggles (use `isChecked()` / `setChecked()`) |
| `ttk.Combobox` | `QComboBox` | Dropdown selectors |
| `scrolledtext.ScrolledText` | `QPlainTextEdit` | Multi-line text area (built-in scrollbar) |
| `ttk.Progressbar` | `QProgressBar` | Progress indicator |
| `Toplevel` | `QDialog` | Modal popup windows |
| `PIL.ImageTk.PhotoImage` | `QPixmap` / `QIcon` | Image handling with automatic DPI scaling |
| `BooleanVar` / `StringVar` / `DoubleVar` | Direct widget methods | No variable wrappers needed; use `widget.value()`, `widget.text()`, etc. |
| `filedialog.askdirectory` | `QFileDialog.getExistingDirectory` | Native OS directory picker |
| `filedialog.askopenfilename` | `QFileDialog.getOpenFileName` | Native OS file picker |
| `messagebox.showinfo` | `QMessageBox.information` | Info dialogs |
| `messagebox.showinfo("Error", ...)` | `QMessageBox.critical` | Error dialogs (shows correct icon) |
| `grid()` / `place()` | `QGridLayout` / `QHBoxLayout` / `QVBoxLayout` | Layout managers |

---

## 6. Layout Specification

### 6.1 Main Window Structure

```
QMainWindow
├── QMenuBar
│   └── View > Appearance > [Light | Dark | System]
└── Central Widget (QWidget)
    └── QVBoxLayout
        └── QTabWidget
            ├── Tab 1: "1. Pre-processing"
            └── Tab 2: "2. Analysis"
```

### 6.2 Pre-processing Tab

```
QWidget with QVBoxLayout
├── QVBoxLayout (stretch=1, centered)
│   ├── QLabel [ScientoPy Logo - QPixmap, centered]
│   └── QLabel [Universidad del Cauca, ..., MIT License, Version X.X.X]
├── QHBoxLayout
│   ├── QLabel ["Dataset folder:"]
│   ├── QLineEdit [expanding]
│   └── QPushButton ["Browse"]
└── QHBoxLayout
    ├── QCheckBox ["Remove duplicated documents"]
    ├── Spacer (expanding)
    ├── QPushButton ["Open preprocess brief"]
    └── QPushButton ["Run preprocess"]
```

### 6.3 Analysis Tab

```
QWidget with QVBoxLayout
├── QSplitter (horizontal)
│   ├── Left Panel (QWidget, fixed ~280px)
│   │   └── QFormLayout
│   │       ├── "Criterion:"      → QComboBox
│   │       ├── "Graph type:"     → QComboBox
│   │       ├── "Start Year:"     → QSpinBox (1900-2100)
│   │       ├── "End Year:"       → QSpinBox (1900-2100)
│   │       ├── "Topics length:"  → QSpinBox (0-1000)
│   │       ├── "Skip first:"     → QSpinBox (0-1000)
│   │       ├── "Window (years):" → QSpinBox (1-100)
│   │       ├── QCheckBox ["Use previous results"]
│   │       └── QCheckBox ["Trend analysis"]
│   └── Right Panel (QWidget, expanding)
│       └── QVBoxLayout
│           ├── QLabel ["Custom topics:"]
│           └── QPlainTextEdit [expanding, scrollable]
└── QHBoxLayout (bottom bar)
    ├── QPushButton ["Open results table"]
    ├── QPushButton ["Open extended results"]
    ├── QPushButton ["Generate BibTeX"]
    ├── Spacer (expanding)
    └── QPushButton ["Run"]
```

---

## 7. Threading and Progress

### 7.1 Current Model (to be replaced)

The current implementation uses a `while` loop with `time.sleep(0.1)` that blocks the Tkinter event loop in a fragile way:

```python
# CURRENT -- do not replicate
while globalVar.progressPer != 101:
    label_text.set(globalVar.progressText)
    popup.update()
    time.sleep(0.1)
    progress_var.set(globalVar.progressPer)
```

### 7.2 New Model: QTimer-based Polling

Since the backend classes (`ScientoPyClass`, `PreProcessClass`) communicate progress via global variables (`globalVar.progressPer`, `globalVar.progressText`), the simplest migration path is to poll with a `QTimer`:

```python
class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)
        self.setFixedSize(350, 140)
        self.setWindowTitle("Progress")

        layout = QVBoxLayout(self)
        self.label = QLabel("Starting...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel)

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # 100ms interval

    def update_progress(self):
        self.label.setText(globalVar.progressText)
        self.progress_bar.setValue(globalVar.progressPer)
        if globalVar.progressPer >= 101 or globalVar.cancelProcess:
            self.timer.stop()
            self.accept()

    def on_cancel(self):
        globalVar.cancelProcess = True
        self.timer.stop()
        self.reject()
```

### 7.3 Future Improvement (Optional)

For a cleaner architecture, refactor the backend to emit Qt signals instead of writing to global variables. This is not required for the initial migration.

---

## 8. Image Assets

### 8.1 Logo

The current `scientopy_logo.png` should be loaded via `QPixmap` and displayed in a `QLabel`:

```python
pixmap = QPixmap("scientopy_logo.png")
logo_label = QLabel()
logo_label.setPixmap(pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
logo_label.setAlignment(Qt.AlignCenter)
```

Qt automatically handles HiDPI scaling for `QPixmap`. For best results on Retina/HiDPI displays, provide a `@2x` variant (`scientopy_logo@2x.png`) and Qt will select it automatically.

**Recommendation:** Create a dark-mode variant of the logo (`scientopy_logo_dark.png`) with lighter colors. Switch between them when the theme changes.

### 8.2 Window Icon

```python
app.setWindowIcon(QIcon("scientopy_icon.png"))
```

For best native integration, provide platform-specific icon formats:
- macOS: `.icns` file
- Windows: `.ico` file
- Linux: `.png` (works natively)

---

## 9. Configuration Persistence

Add a JSON configuration file (`scientopy_config.json`) stored alongside the application:

```json
{
    "appearance_mode": "System",
    "ui_scaling": 1.0,
    "last_dataset_folder": "",
    "window_geometry": "1000x600",
    "splitter_sizes": [280, 600]
}
```

Load on startup with `QSettings` or plain JSON, save on exit via `QMainWindow.closeEvent()`. This replaces the need for users to reconfigure preferences each session.

---

## 10. Behavioral Requirements

### 10.1 Preserved Behavior

The following must work identically to the current implementation:

1. **Pre-processing workflow:** Select dataset folder, toggle duplicate removal, run preprocess, view brief
2. **Analysis workflow:** Select criterion/graph type, set year range and parameters, enter custom topics, run analysis, view results
3. **Threading model:** Heavy processing in background threads; progress updates in main thread; cancel support via `globalVar.cancelProcess`
4. **File operations:** Directory picker for dataset selection, file picker for LaTeX file selection
5. **External file opening:** `webbrowser.open()` for CSV/TSV results (or `QDesktopServices.openUrl()`)
6. **BibTeX generation:** Select LaTeX file, generate and open BibTeX
7. **Matplotlib plot output:** All 5 graph types (bar_trends, bar, time_line, evolution, word_cloud) rendered via matplotlib
8. **Console output:** Print statements remain for CLI logging

### 10.2 Changed Behavior

| Behavior | Current | New |
|---|---|---|
| Window resizing | Disabled | Enabled with minimum size constraints |
| Year input | Spinbox (Tkinter, allows any text) | `QSpinBox` (enforced integer range, up/down arrows) |
| Error dialogs | `messagebox.showinfo` (always titled "Error") | `QMessageBox.critical` for errors (correct icon and title) |
| Progress dialog | Non-modal, polled via `while`/`sleep` | Modal `QDialog` with `QTimer`-based polling (event loop stays responsive) |
| Theme | OS default only | User-selectable light/dark/system via menu bar |
| Plot backend | TkAgg (Tkinter-based) | QtAgg (Qt-based, consistent DPI and theming) |
| File dialogs | Tkinter `filedialog` | Qt `QFileDialog` (native OS dialogs) |

### 10.3 Input Validation

`QSpinBox` provides built-in integer validation with range enforcement:

- **Year fields:** Range 1900-2100, default `globalVar.DEFAULT_START_YEAR` / `globalVar.DEFAULT_END_YEAR`
- **Topics length:** Range 0-1000, default 10
- **Skip first:** Range 0-1000, default 0
- **Window (years):** Range 1-100, default 2

No custom validation code is needed -- `QSpinBox` rejects non-integer input and clamps to the specified range automatically.

---

## 11. Migration Strategy

### Phase 1: Framework Swap (Minimal Changes)

1. Add `PySide6>=6.6.0` to `requirements.txt`
2. Replace all Tkinter imports with PySide6 equivalents in `ScientoPyGui.py`
3. Create `QMainWindow` with `QTabWidget` containing the two tabs
4. Rebuild the Pre-processing tab layout with `QVBoxLayout` / `QHBoxLayout`
5. Rebuild the Analysis tab layout with `QSplitter` + `QFormLayout` + `QPlainTextEdit`
6. Replace progress dialog with `QDialog` + `QTimer`
7. Set matplotlib backend to `QtAgg`
8. Enable window resizing with `setMinimumSize(853, 480)`
9. Verify all existing functionality works identically

### Phase 2: Theme and DPI

1. Add menu bar with View > Appearance > Light / Dark / System
2. Implement `QPalette`-based dark theme
3. Detect OS dark mode via `QStyleHints.colorScheme()`
4. Create dark-mode logo variant
5. Apply theme-aware matplotlib styles for plots
6. Read screen DPI via `QScreen.logicalDotsPerInch()` for matplotlib figures
7. Add configuration persistence (`scientopy_config.json`)

### Phase 3: Layout Polish

1. Fine-tune splitter proportions and padding for responsive resizing
2. Save/restore window geometry and splitter sizes in config
3. Test at 100%, 125%, 150%, 200% scaling on all platforms
4. Test on 1080p, 1440p, and 4K displays
5. Test on Windows 10/11, macOS 12+, Ubuntu 22.04+

---

## 12. Testing Requirements

### 12.1 Platform Matrix

| Platform | Resolution | Scale | Theme |
|---|---|---|---|
| Windows 11 | 1920x1080 | 100% | Light |
| Windows 11 | 3840x2160 | 150% | Dark |
| Windows 11 | 3840x2160 | 200% | System |
| macOS 14+ | Retina (2x) | Default | Light |
| macOS 14+ | Retina (2x) | Default | Dark |
| Ubuntu 22.04+ | 1920x1080 | 100% | Light (Adwaita) |
| Ubuntu 22.04+ | 3840x2160 | 200% | Dark (Adwaita-dark) |

### 12.2 Functional Tests

1. Pre-processing tab: select dataset, run preprocess, open brief
2. Analysis tab: run all 5 graph types with default settings
3. Custom topics: enter multi-line topics with semicolons, run analysis
4. Asterisk wildcard: enter `device*`, verify expanded results
5. Use previous results: run analysis, check "Use previous results", run again
6. Trend analysis: enable trend analysis, verify output
7. Generate BibTeX: select LaTeX file, verify output
8. Cancel operation: start preprocess, cancel mid-operation
9. Window resize: resize to minimum, maximize, restore -- verify layout integrity
10. Splitter drag: adjust left/right panel proportions, verify no clipping
11. Theme switch: switch between Light/Dark/System via menu, verify all widgets update
12. DPI: test on a HiDPI display, verify no tiny/blurry widgets

### 12.3 Visual Checks

- All text is readable in both light and dark themes
- Logo is visible and properly scaled in both themes
- Buttons have consistent sizing and alignment
- Dropdown menus are readable and properly positioned
- Progress bar is visible and updates smoothly
- Matplotlib plots use appropriate colors for the active theme
- No widget clipping or overlap at minimum window size
- No excessive whitespace at maximized window size
- Spinbox arrows are visible and functional
- Splitter handle is visible and draggable

---

## 13. Files to Modify

| File | Changes |
|---|---|
| `ScientoPyGui.py` | Complete rewrite of UI layer using PySide6; backend calls unchanged |
| `requirements.txt` | Add `PySide6>=6.6.0` |
| `globalVar.py` | No changes required |
| `ScientoPyClass.py` | Set matplotlib backend to `QtAgg`; add theme-aware matplotlib style application in `plotResults()` |
| `PreProcessClass.py` | Add theme-aware matplotlib style in `graphBrief()` / `grapPreprocess()` |
| `graphUtils.py` | Add functions for DPI-aware figure creation and theme-aware color selection |
| `scientopy_config.json` | New file -- user preferences |
| `scientopy_logo_dark.png` | New file -- dark mode logo variant |
