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
Reusable "compile LaTeX and show the result" panel. Feed it a LaTeX snippet
(wrapped in a minimal beamer frame) or a complete standalone .tex file, call
Compile(), and it runs pdflatex in a background thread -- keeping the rest
of the UI responsive -- then displays the resulting PDF, with Prev/Next page
navigation if it has more than one page. Meant to be dropped into any dialog
that wants a compile-and-preview panel (the Plot editor, the FrontMatter
editor, ...) without depending on anything specific to either one.

Self-contained by design: only depends on gui.ImageScale (already used
elsewhere for the same "scale a pixmap to its container" job) and
core/preamble.tex (read by path, not imported).
"""

import os
import shutil
import subprocess
import tempfile

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

from gui.ImageScale import ImageScale


class _CompileWorker(QThread):
    """Runs pdflatex (twice) on a .tex file already sitting in workdir,
    off the GUI thread. Emits the resulting PDF's path, or "" on failure."""

    finished_ = pyqtSignal(str)

    def __init__(self, workdir, tex_filename, parent=None):
        super().__init__(parent)
        self.workdir = workdir
        self.tex_filename = tex_filename

    def run(self):
        pdf_path = ""
        try:
            for _ in range(2):
                subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", self.tex_filename],
                    cwd=self.workdir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            candidate = os.path.join(
                self.workdir, os.path.splitext(self.tex_filename)[0] + ".pdf"
            )
            if os.path.exists(candidate):
                pdf_path = candidate
        except OSError:
            pdf_path = ""
        self.finished_.emit(pdf_path)


class LatexPreviewWidget(QWidget):
    """
    Compile-and-preview panel. Typical use:

        preview = LatexPreviewWidget(self)
        someLayout.addWidget(preview)
        ...
        preview.SetLatexBody(my_latex_snippet)
        preview.Compile()

    The host dialog should call preview.Cleanup() from its own closeEvent/
    done() handler -- an embedded child widget's own closeEvent never fires,
    so nothing else removes the scratch temp folder this creates.
    """

    compileStarted = pyqtSignal()
    compileFinished = pyqtSignal(bool)  # True on success

    def __init__(self, parent=None):
        super().__init__(parent)

        self._workdir = None
        self._worker = None
        self._pendingRecompile = False

        self._pdfDoc = None
        self._pageCount = 0
        self._currentPage = 0

        self._latexBody = ""
        self._extraPreamble = ""
        self._texFile = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.imageView = ImageScale(self)
        self.imageView.setMinimumHeight(120)
        layout.addWidget(self.imageView, 1)

        self.statusLabel = QLabel("")
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.statusLabel.setVisible(False)
        layout.addWidget(self.statusLabel)

        navRow = QHBoxLayout()
        self.prevButton = QPushButton("< Prev")
        self.pageLabel = QLabel("")
        self.pageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.nextButton = QPushButton("Next >")
        navRow.addWidget(self.prevButton)
        navRow.addWidget(self.pageLabel, 1)
        navRow.addWidget(self.nextButton)
        layout.addLayout(navRow)
        self._setNavVisible(False)

        self.prevButton.clicked.connect(self._goPrevPage)
        self.nextButton.clicked.connect(self._goNextPage)

    # ---------- public API ----------

    def SetLatexBody(self, latex_body, extra_preamble=""):
        """
        Set a LaTeX snippet to compile inside a minimal beamer frame (real
        core/preamble.tex + an optional bit of extra preamble code, e.g. a
        FrontMatter's custom preamble). Call Compile() to actually run it.
        """
        self._latexBody = latex_body or ""
        self._extraPreamble = extra_preamble or ""
        self._texFile = ""

    def SetTexFile(self, path):
        """Set an existing, complete .tex file to compile as-is."""
        self._texFile = path or ""
        self._latexBody = ""

    def Compile(self):
        """
        Compile whatever was last set, asynchronously -- returns immediately.
        Safe to call again while a previous compile is still running: the
        new request is simply deferred until the current one finishes,
        so only the latest requested state ever actually gets shown.
        """
        if self._worker is not None and self._worker.isRunning():
            self._pendingRecompile = True
            return
        self._pendingRecompile = False

        if not self._latexBody.strip() and not self._texFile.strip():
            return

        self._cleanupWorkdir()
        self._workdir = tempfile.mkdtemp(prefix="beamerQT_latexpreview_")

        if self._texFile:
            tex_filename = os.path.basename(self._texFile)
            try:
                shutil.copy(self._texFile, os.path.join(self._workdir, tex_filename))
            except OSError:
                self._onCompileFinished("")
                return
        else:
            tex_filename = "preview.tex"
            tex_path = os.path.join(self._workdir, tex_filename)
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write("\\documentclass{beamer}\n")
                with open("core/preamble.tex", "r", encoding="utf-8") as pf:
                    f.write(pf.read())
                if self._extraPreamble.strip():
                    f.write("\n" + self._extraPreamble + "\n")
                f.write("\n\\begin{document}\n\\begin{frame}\n")
                f.write(self._latexBody)
                f.write("\n\\end{frame}\n\\end{document}\n")

        self._setBusy(True)
        self.compileStarted.emit()

        self._worker = _CompileWorker(self._workdir, tex_filename, self)
        self._worker.finished_.connect(self._onCompileFinished)
        self._worker.start()

    def Cleanup(self):
        """Remove the scratch temp folder and close the open PDF, if any.
        Call this from the host dialog's own close handling."""
        if self._pdfDoc is not None:
            self._pdfDoc.close()
            self._pdfDoc = None
        self._cleanupWorkdir()

    # ---------- internals ----------

    def _onCompileFinished(self, pdf_path):
        self._setBusy(False)

        if not pdf_path:
            self.statusLabel.setText("LaTeX compilation failed.")
            self.statusLabel.setVisible(True)
            self.imageView.setPixmap(QPixmap())
            if self._pdfDoc is not None:
                self._pdfDoc.close()
            self._pdfDoc = None
            self._pageCount = 0
            self._setNavVisible(False)
            self.compileFinished.emit(False)
        else:
            import fitz
            if self._pdfDoc is not None:
                self._pdfDoc.close()
            self._pdfDoc = fitz.open(pdf_path)
            self._pageCount = self._pdfDoc.page_count
            self.statusLabel.setVisible(False)
            self._showPage(0)
            self._setNavVisible(self._pageCount > 1)
            self.compileFinished.emit(True)

        if self._pendingRecompile:
            self._pendingRecompile = False
            self.Compile()

    def _showPage(self, index):
        if not self._pdfDoc or not (0 <= index < self._pageCount):
            return
        self._currentPage = index
        page = self._pdfDoc.load_page(index)
        pix = page.get_pixmap(dpi=110)
        qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        self.imageView.setPixmap(QPixmap.fromImage(qimage))
        self.pageLabel.setText(f"Page {index + 1} of {self._pageCount}")
        self.prevButton.setEnabled(index > 0)
        self.nextButton.setEnabled(index < self._pageCount - 1)

    def _goPrevPage(self):
        self._showPage(self._currentPage - 1)

    def _goNextPage(self):
        self._showPage(self._currentPage + 1)

    def _setNavVisible(self, visible):
        self.prevButton.setVisible(visible)
        self.nextButton.setVisible(visible)
        self.pageLabel.setVisible(visible)

    def _setBusy(self, busy):
        self.prevButton.setEnabled(not busy and self._currentPage > 0)
        self.nextButton.setEnabled(not busy and self._currentPage < self._pageCount - 1)
        if busy:
            self.statusLabel.setText("Compiling...")
            self.statusLabel.setVisible(True)

    def _cleanupWorkdir(self):
        if self._workdir and os.path.isdir(self._workdir):
            shutil.rmtree(self._workdir, ignore_errors=True)
        self._workdir = None
