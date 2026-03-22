# Pip installation (beamerqt)

This folder contains the packaging metadata to install BeamerQt via `pip` without adding build files to the repo root.

## Install (from this repo)

From the repo root:

```bash
python3 -m pip install ./Packaging/pip
```

Editable install (for development):

```bash
python3 -m pip install -e ./Packaging/pip
```

It installs a `beamerqt` command which runs the app.

## Build wheels/sdist

Linux/macOS:

```bash
./Packaging/pip/build.sh
```

Windows (PowerShell):

```powershell
Packaging\\pip\\build.ps1
```

Artifacts are placed in `Packaging/pip/dist/`.

## Notes

- External tools are still required for some features: `pdflatex` (TeX Live/MiKTeX) and `inkscape`.
- The installed package includes UI files, icons, and templates.

