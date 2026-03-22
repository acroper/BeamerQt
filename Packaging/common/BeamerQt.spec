# -*- mode: python ; coding: utf-8 -*-

from __future__ import annotations

import os

from PyInstaller.building.datastruct import Tree


block_cipher = None


def _tree(path: str) -> Tree:
    return Tree(path, prefix=path)


datas = [
    _tree("gui"),
    _tree("templates"),
    ("LICENSE", "."),
    ("README.md", "."),
    ("Release_Notes.md", "."),
]

hiddenimports = [
    "fitz",  # PyMuPDF
]

is_windows = os.name == "nt"
icon_file = "icon.ico" if is_windows and os.path.exists("icon.ico") else None


a = Analysis(
    ["main.py"],
    pathex=[os.path.abspath(".")],
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
    a.binaries,
    a.zipfiles,
    a.datas,
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
