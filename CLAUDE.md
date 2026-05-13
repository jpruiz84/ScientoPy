# CLAUDE.md

Project guidance for Claude Code when working in this repository.

## Releasing a new version

The version number lives in **four** places. All must be kept in sync, otherwise the GUI, the Python package metadata, and the Windows EXE properties will disagree.

### 1. Bump the version number

Update **all four** of these files (search for the current version, e.g. `3.1.2`, and replace with the new one, e.g. `3.1.3`):

| File | Line(s) | What to change |
|---|---|---|
| `globalVar.py` | ~103 | `SCIENTOPY_VERSION = "X.Y.Z"` — runtime version shown in the GUI |
| `pyproject.toml` | ~7 | `version = "X.Y.Z"` — Python package metadata |
| `version_info.py` | ~28-29 | `filevers=(X, Y, Z, 0)` and `prodvers=(X, Y, Z, 0)` — Windows EXE binary metadata (tuple form) |
| `version_info.py` | ~45, ~50 | `StringStruct(u'FileVersion', u'X.Y.Z')` and `StringStruct(u'ProductVersion', u'X.Y.Z')` — Windows EXE string metadata |

> Quick check that nothing was missed:
> ```bash
> grep -rn "OLD_VERSION" --include="*.py" --include="*.toml" .
> ```
> Should return zero hits (excluding `doc/release_notes/`).

### 2. Create the release notes

Create a new file `doc/release_notes/vX.Y.Z.md` following the existing format (`doc/release_notes/v3.1.0.md` and `v3.1.2.md` are good templates).

Suggested structure:

```markdown
# ScientoPy vX.Y.Z — Release Notes

## Highlights

One short paragraph describing the headline change.

## <Section per category>

- bullet points...

---

**Full changelog:** [`vPREV...vX.Y.Z`](https://github.com/jpruiz84/ScientoPy/compare/vPREV...vX.Y.Z)
```

Common section headings used in past releases:
- `Performance`
- `Bug Fixes`
- `New Features`
- `Code Signing (Windows)`
- `Infrastructure`

Keep wording user-facing — describe what changed and why it matters to someone running the app, not implementation details.

### 3. Commit, tag, push

```bash
git add globalVar.py pyproject.toml version_info.py doc/release_notes/vX.Y.Z.md
git commit -m "Bump version to X.Y.Z and add release notes"
git push origin master

git tag vX.Y.Z
git push origin vX.Y.Z
```

The `v*` tag push triggers `.github/workflows/build-release.yml`, which:
1. Runs unit + behavioral tests on Linux, macOS, and Windows.
2. Builds PyInstaller bundles for Linux x64, macOS arm64, and Windows x64.
3. Submits the Windows artifact to SignPath for Authenticode signing (only on `v*` tags).
4. Publishes a GitHub Release with all three platform artifacts.

### 4. Verify the release

After the workflow finishes:

- Check the **Actions** tab → all jobs green.
- Open the new release at **Releases** → confirm three assets attached (`ScientoPy-windows-x64.zip`, `ScientoPy-linux-x64.tar.gz`, `ScientoPy-macos-arm64.zip`).
- Download `ScientoPy-windows-x64.zip` → extract → on Windows, right-click `ScientoPyGui.exe` → **Properties** → **Digital Signatures**: signature must be **Valid** with the correct publisher.
- Optional PowerShell check:
  ```powershell
  Get-AuthenticodeSignature .\ScientoPyGui.exe | Format-List
  ```

## SignPath secrets

The Windows signing job needs these GitHub repository secrets:
- `SIGNPATH_API_TOKEN`
- `SIGNPATH_ORGANIZATION_ID`
- `SIGNPATH_PROJECT_SLUG`
- `SIGNPATH_ARTIFACT_CONFIG_SLUG`
- `SIGNPATH_SIGNING_POLICY_SLUG`

A helper script for updating them lives at `sandbox/update-signpath-secrets.sh` (gitignored).

The artifact configuration is at `.signpath/artifact-configuration.xml` — defines which files inside the ZIP get signed.
