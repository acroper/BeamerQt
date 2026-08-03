"""
Beamer QT
Copyright (C) 2024-2026  Jorge Guerrero - acroper@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
Shared "compile a Plot item to a raster preview" helper. Used both by
PlotEditorDialog's Preview button (while editing) and to store the inline
widget's preview once, at Accept time -- there's no lightweight native
renderer for pgfplots/tikz like EquationQT has for its own math markup, so
both cases go through an actual pdflatex compile.
"""

import os
import shutil
import subprocess
import tempfile

from PyQt6.QtGui import QPixmap, QImage

from . import csv_parser


# Session-scoped cache dir for stored preview PNGs (one per Plot item, named
# by its uuid). Mirrors itemImage's "reference a file path, load a QPixmap
# from it" approach: the compile only happens once, at Accept time, and
# every later Refresh() just re-reads this file instead of recompiling.
_PREVIEW_CACHE_DIR = None


def _preview_cache_dir():
    global _PREVIEW_CACHE_DIR
    if _PREVIEW_CACHE_DIR is None or not os.path.isdir(_PREVIEW_CACHE_DIR):
        _PREVIEW_CACHE_DIR = tempfile.mkdtemp(prefix="beamerQT_plotpreviews_")
    return _PREVIEW_CACHE_DIR


def compile_plot_to_pixmap(item, latex_body=None, dpi=110):
    """
    Compile a minimal beamer frame containing latex_body (or item.LatexCode
    if not given) into a PDF and rasterize its first page to a QPixmap.

    Returns None if there is nothing to compile or compilation fails.
    """
    if latex_body is None:
        latex_body = item.LatexCode

    if not latex_body or not latex_body.strip():
        return None

    latex_body = csv_parser.resolve_tags(
        latex_body, item.Series, item.CsvPath,
        item.CsvDelimiter, item.CsvDecimal, item.CsvHasHeader, item.Bins,
        xtick_step=getattr(item, "XTickStep", 0),
    )

    tempdir = tempfile.mkdtemp(prefix="beamerQT_plotpreview_")
    try:
        if item.CsvPath and os.path.exists(item.CsvPath):
            try:
                csv_parser.write_normalized_csv(
                    item.CsvPath, os.path.join(tempdir, item.CsvFilename()),
                    delimiter=item.CsvDelimiter, decimal=item.CsvDecimal,
                    has_header=item.CsvHasHeader,
                )
            except OSError:
                pass

        tex_path = os.path.join(tempdir, "preview.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write("\\documentclass{beamer}\n")
            with open("core/preamble.tex", "r", encoding="utf-8") as pf:
                f.write(pf.read())
            f.write("\n\\begin{document}\n\\begin{frame}\n")
            f.write(latex_body)
            f.write("\n\\end{frame}\n\\end{document}\n")

        for _ in range(2):
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "preview.tex"],
                cwd=tempdir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        pdf_path = os.path.join(tempdir, "preview.pdf")
        if not os.path.exists(pdf_path):
            return None

        import fitz
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=dpi)
        qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        doc.close()
        return pixmap
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


def compile_and_store_preview(item, latex_body=None, dpi=150):
    """
    Compile item's LaTeX (see compile_plot_to_pixmap) and save the rendered
    first page as a PNG under this session's preview cache dir, named by the
    item's uuid so it can be found again later.

    Returns the PNG's path on success, or "" on failure (nothing to compile,
    or the compile itself failed) -- callers should treat "" the same as "no
    preview yet".
    """
    pixmap = compile_plot_to_pixmap(item, latex_body=latex_body, dpi=dpi)
    if pixmap is None:
        return ""

    out_path = os.path.join(_preview_cache_dir(), f"plot_preview_{item.uuid}.png")
    if not pixmap.save(out_path, "PNG"):
        return ""
    return out_path
