# ScientoPy Distribution Specification

## 1. Overview

This document specifies the plan to build and distribute ScientoPy as standalone executables for three platforms using GitHub Actions CI/CD:

| Platform | Architecture | Artifact |
|---|---|---|
| Windows 11 | x86_64 | `ScientoPy-windows-x64.zip` |
| Ubuntu 22.04+ | x86_64 | `ScientoPy-linux-x64.tar.gz` |
| macOS 14+ | ARM64 (Apple Silicon) | `ScientoPy-macos-arm64.zip` |

**Tool:** PyInstaller (already used for the current Windows build)
**CI/CD:** GitHub Actions with a matrix build across the three platforms
**Trigger:** Manual dispatch + automatic on version tag push (`v*`)

---

## 2. Current State

| Item | Status |
|---|---|
| Windows PyInstaller spec | Exists (`winBuildScientoPyGui.spec`), hardcoded paths |
| Linux/macOS builds | None |
| GitHub Actions | None |
| `pyproject.toml` / `setup.py` | None |
| Entry point | `ScientoPyGui.py` (GUI), `scientoPy.py` / `preProcess.py` / `generateBibtex.py` (CLI) |

### Runtime Data Files

These must be bundled with the executable:

| Path | Description |
|---|---|
| `scientopy_logo.png` | Application logo |
| `scientopy_icon.png` | Window icon (Linux) |
| `scientopy_icon.ico` | Window icon (Windows) |
| `wordcloudFiles/` | Word cloud font and support files |
| `dataInExample/` | Example Scopus/WoS dataset |
| `Manual/` | PDF user manual |
| `latexExample/` | Example LaTeX document + Makefile |

---

## 3. PyInstaller Configuration

### 3.1 Cross-Platform Spec File

Replace the Windows-only `winBuildScientoPyGui.spec` with a single `ScientoPyGui.spec` that works on all platforms:

```python
# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# Icon is platform-dependent
icon_file = 'scientopy_icon.ico' if sys.platform == 'win32' else 'scientopy_icon.png'

a = Analysis(
    ['ScientoPyGui.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        ('wordcloudFiles/*', 'wordcloud'),
        ('Manual/*.pdf', 'Manual'),
        ('dataInExample/*', 'dataInExample'),
        ('latexExample/*', 'latexExample'),
        ('scientopy_icon.ico', '.'),
        ('scientopy_icon.png', '.'),
        ('scientopy_logo.png', '.'),
    ],
    hiddenimports=[
        'scipy.spatial.transform._rotation_groups',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter'],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ScientoPyGui',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=icon_file,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ScientoPyGui',
)
```

Key changes from the current spec:
- `pathex` uses `os.getcwd()` instead of hardcoded Windows path
- `excludes=['tkinter']` since we migrated to PySide6
- `console=False` to hide the terminal window on launch
- Platform-dependent icon selection
- `Manual/*.pdf` glob instead of `Manual/*` to avoid bundling LaTeX source

### 3.2 CLI Scripts

The CLI scripts (`scientoPy.py`, `preProcess.py`, `generateBibtex.py`) are bundled alongside the GUI directory. They are Python scripts the user runs from the command line and do not need to be compiled into separate executables. They are included via the `datas` list or shipped as-is in the release ZIP.

To include them, add to `datas`:

```python
('scientoPy.py', '.'),
('preProcess.py', '.'),
('generateBibtex.py', '.'),
('ScientoPyClass.py', '.'),
('PreProcessClass.py', '.'),
('globalVar.py', '.'),
('graphUtils.py', '.'),
('paperUtils.py', '.'),
('paperSave.py', '.'),
```

---

## 4. GitHub Actions Workflow

### 4.1 Workflow File: `.github/workflows/build-release.yml`

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: windows-latest
            platform: windows-x64
            artifact_ext: zip
          - os: ubuntu-22.04
            platform: linux-x64
            artifact_ext: tar.gz
          - os: macos-14
            platform: macos-arm64
            artifact_ext: zip

    runs-on: ${{ matrix.os }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller

      # Linux: install system libraries for Qt
      - name: Install Linux Qt dependencies
        if: runner.os == 'Linux'
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            libgl1-mesa-glx \
            libegl1 \
            libxkbcommon0 \
            libdbus-1-3 \
            libxcb-cursor0 \
            libxcb-icccm4 \
            libxcb-keysyms1 \
            libxcb-shape0

      - name: Build with PyInstaller
        run: pyinstaller ScientoPyGui.spec --noconfirm

      - name: Package artifact (Windows)
        if: runner.os == 'Windows'
        shell: pwsh
        run: |
          Compress-Archive -Path dist/ScientoPyGui/* `
            -DestinationPath ScientoPy-${{ matrix.platform }}.zip

      - name: Package artifact (Linux)
        if: runner.os == 'Linux'
        run: |
          tar -czf ScientoPy-${{ matrix.platform }}.tar.gz \
            -C dist ScientoPyGui

      - name: Package artifact (macOS)
        if: runner.os == 'macOS'
        run: |
          cd dist && zip -r ../ScientoPy-${{ matrix.platform }}.zip ScientoPyGui

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: ScientoPy-${{ matrix.platform }}
          path: ScientoPy-${{ matrix.platform }}.${{ matrix.artifact_ext }}

  release:
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')

    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v4
        with:
          path: artifacts

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: artifacts/**/*
          generate_release_notes: true
```

### 4.2 Matrix Details

| Runner | OS | Python | Architecture | Notes |
|---|---|---|---|---|
| `windows-latest` | Windows Server 2022 | 3.11 | x86_64 | Produces `.exe` + DLLs |
| `ubuntu-22.04` | Ubuntu 22.04 LTS | 3.11 | x86_64 | Needs Qt system libraries |
| `macos-14` | macOS 14 Sonoma | 3.11 | ARM64 (M1/M2/M3) | Native Apple Silicon build |

### 4.3 Trigger Modes

1. **Tag push:** Push a tag like `v2.2.0` to trigger build + automatic GitHub Release with all three platform artifacts attached
2. **Manual dispatch:** Click "Run workflow" in the Actions tab for testing without creating a release

---

## 5. Release Artifacts

Each platform artifact contains a directory `ScientoPyGui/` with:

```
ScientoPyGui/
├── ScientoPyGui              # Executable (or ScientoPyGui.exe on Windows)
├── scientopy_logo.png
├── scientopy_icon.png
├── scientopy_icon.ico
├── dataInExample/
│   ├── scopus*.csv
│   └── savedrecs*.txt
├── Manual/
│   └── *.pdf
├── latexExample/
│   ├── article_example.tex
│   ├── Makefile
│   └── article_example_bibliography.bib
├── wordcloud/
│   └── (font files + wordcloud support)
└── (Qt libraries and Python runtime bundled by PyInstaller)
```

### 5.1 Artifact Sizes (Estimated)

| Platform | Estimated Size |
|---|---|
| Windows x64 | ~150-200 MB (compressed) |
| Linux x64 | ~120-170 MB (compressed) |
| macOS ARM64 | ~130-180 MB (compressed) |

PySide6/Qt is the largest component (~80 MB uncompressed). The example dataset adds ~50 MB.

---

## 6. Platform-Specific Considerations

### 6.1 Windows

- Icon: `scientopy_icon.ico` embedded in the `.exe`
- No installer (`.msi` / `.exe` installer) -- distribute as a ZIP that users extract and run
- Future enhancement: Create an NSIS or WiX installer for Start Menu shortcuts

### 6.2 Linux

- Requires OpenGL and X11/Wayland libraries at runtime (bundled by PyInstaller for most)
- Distribute as `.tar.gz` -- users extract and run `./ScientoPyGui`
- The executable may need `chmod +x` after extraction
- Future enhancement: AppImage or Flatpak for wider compatibility

### 6.3 macOS (Apple Silicon)

- `macos-14` runner provides native ARM64 builds (no Rosetta)
- macOS may block unsigned executables with Gatekeeper
- Users must right-click > Open or run `xattr -cr ScientoPyGui/` to clear quarantine
- Future enhancement: Code sign with an Apple Developer certificate and notarize for seamless launch
- Future enhancement: Create a `.dmg` disk image with drag-to-Applications layout

---

## 7. Version Management

The release version should come from the git tag. Update `globalVar.py` before tagging:

```bash
# 1. Update version in globalVar.py
# SCIENTOPY_VERSION = "2.2.0"

# 2. Commit the version bump
git commit -am "Bump version to 2.2.0"

# 3. Tag and push
git tag v2.2.0
git push origin master --tags
```

The tag push triggers the GitHub Actions workflow, which builds all three platforms and creates a GitHub Release with the artifacts.

---

## 8. Testing the Build

### 8.1 Local Testing

Test PyInstaller locally before pushing:

```bash
pip install pyinstaller
pyinstaller ScientoPyGui.spec --noconfirm
cd dist/ScientoPyGui
./ScientoPyGui  # or ScientoPyGui.exe on Windows
```

Verify:
- Application launches and shows the main window
- Pre-processing tab: logo visible, browse button opens file dialog
- Analysis tab: all controls populated with defaults
- Results tab: loads existing data if present
- Theme switching works (View > Appearance)
- Matplotlib plots open correctly

### 8.2 CI Testing

The GitHub Actions workflow can be tested via manual dispatch (`workflow_dispatch`) without creating a release. Download the artifacts from the Actions run summary and test on each platform.

---

## 9. Implementation Steps

### Phase 1: PyInstaller Spec (Day 1)

1. Create `ScientoPyGui.spec` (cross-platform, replacing `winBuildScientoPyGui.spec`)
2. Test locally on the current development machine (Linux)
3. Verify the bundled application launches and all features work

### Phase 2: GitHub Actions (Day 1-2)

1. Create `.github/workflows/build-release.yml`
2. Push to a feature branch and trigger a manual dispatch
3. Download and test artifacts from all three platforms
4. Fix any platform-specific issues (missing libraries, paths, etc.)

### Phase 3: First Release (Day 2-3)

1. Update `globalVar.py` with the new version
2. Update `README.md` installation instructions to reference GitHub Releases
3. Tag and push `v2.2.0`
4. Verify the GitHub Release is created with all three artifacts
5. Test the release artifacts on Windows, Ubuntu, and macOS

### Phase 4: Enhancements (Future)

1. Add code signing for macOS (Apple Developer certificate + notarization)
2. Create Windows installer (NSIS or WiX)
3. Create Linux AppImage for broader compatibility
4. Add auto-update check in the GUI
5. Reduce artifact size by excluding `dataInExample/` (provide as separate download)

---

## 10. Files to Create or Modify

| File | Action | Description |
|---|---|---|
| `ScientoPyGui.spec` | Create | Cross-platform PyInstaller spec |
| `.github/workflows/build-release.yml` | Create | CI/CD workflow |
| `winBuildScientoPyGui.spec` | Delete | Replaced by cross-platform spec |
| `README.md` | Modify | Add download links to GitHub Releases |
| `globalVar.py` | Modify | Bump version for release |
| `.gitignore` | Modify | Add `dist/`, `build/`, `*.spec.bak` |
