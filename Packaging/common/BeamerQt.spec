# -*- mode: python ; coding: utf-8 -*-

from __future__ import annotations

import os

from PyInstaller.utils.hooks import collect_submodules


block_cipher = None
project_root = os.path.abspath(os.path.join(os.path.dirname(SPEC), "..", ".."))


def _data_tree(path: str) -> list[tuple[str, str]]:
    source_root = os.path.join(project_root, path)
    collected: list[tuple[str, str]] = []
    for current_root, _, files in os.walk(source_root):
        relative_root = os.path.relpath(current_root, project_root)
        for filename in files:
            collected.append((os.path.join(current_root, filename), relative_root))
    return collected


datas = [
    (os.path.join(project_root, "LICENSE"), "."),
    (os.path.join(project_root, "README.md"), "."),
    (os.path.join(project_root, "Release_Notes.md"), "."),
    (os.path.join(project_root, "core", "preamble.tex"), "core"),
]
datas += _data_tree("gui")
datas += _data_tree("templates")

hiddenimports = [
    "fitz",  # PyMuPDF
    "uuid",
    *collect_submodules("gui.ContentItems"),
]

is_windows = os.name == "nt"
icon_path = os.path.join(project_root, "icon.ico")
icon_file = icon_path if is_windows and os.path.exists(icon_path) else None


a = Analysis(
    [os.path.join(project_root, "main.py")],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name="BeamerQt",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
    exclude_binaries=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="BeamerQt",
)
