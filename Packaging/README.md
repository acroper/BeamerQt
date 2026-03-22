# Packaging / Redistribution

BeamerQt is a Python + PyQt6 desktop app. The simplest way to redistribute it to end users is to bundle Python + dependencies into a native app per platform.

## Recommended approach (end-user apps)

**Tool:** PyInstaller (build on each target OS)

Why: PyQt6 bundles well with PyInstaller, and you can ship a single folder app per OS.

### 1) Runtime dependencies (still external)

BeamerQt calls external tools for LaTeX and SVG conversion:

- `pdflatex` (MiKTeX on Windows, TeX Live on Linux/macOS)
- `inkscape` (SVG → PDF conversion)

You usually *do not* bundle these inside your app (huge), but instead:

- Document them as prerequisites for users
- Add a startup “dependency check” dialog (optional improvement)

### 2) Build (Windows)

From a venv:

```powershell
python -m pip install -r Packaging/requirements.txt -r Packaging/requirements-build.txt
pyinstaller Packaging/common/BeamerQt.spec --noconfirm --clean --distpath Packaging/Windows/dist --workpath Packaging/Windows/build --specpath Packaging/Windows
```

Or run:

```powershell
Packaging\\Windows\\build.ps1
```

Output: `Packaging/Windows/dist/BeamerQt/`

### 3) Build (Linux/macOS)

```bash
python3 -m pip install -r Packaging/requirements.txt -r Packaging/requirements-build.txt
pyinstaller Packaging/common/BeamerQt.spec --noconfirm --clean --distpath Packaging/Linux/dist --workpath Packaging/Linux/build --specpath Packaging/Linux
```

Or:

```bash
./Packaging/Linux/build.sh
```

Output: `Packaging/Linux/dist/BeamerQt/`

### 3b) Build (Linux AppImage)

This creates an AppDir from the PyInstaller output and then runs `appimagetool`.

```bash
./Packaging/Linux/build-appimage.sh
```

Requirements:

- `appimagetool` in PATH, or set `APPIMAGETOOL=/path/to/appimagetool`

### 4) Turn it into a “proper installer”

- Windows: wrap `dist/BeamerQt/` with Inno Setup or NSIS
- macOS: create a `.app` + `.dmg` and (optionally) codesign/notarize
- Linux: AppImage (or Flatpak/Snap, if you want sandboxing and stores)

## Alternative approach (developer install)

For Linux power users, you can also offer a source install:

```bash
pip install pyqt6 pymupdf
python3 main.py
```

This is not as user-friendly as a bundled app, but it’s easy to maintain.
