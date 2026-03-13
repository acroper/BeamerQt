# EquationEditorDialog.py
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

import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit,
    QFileDialog, QMessageBox, QInputDialog, QPushButton, QDialogButtonBox
)
from PyQt6.QtCore import pyqtSignal
from .symbol_palette import SymbolPalette
from .math_editor import EquationEditor

class EquationEditorDialog(QDialog):
    equation_accepted = pyqtSignal(str)  # Signal to emit the LaTeX when accepted

    def __init__(self, latex_text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("BeamerQT - Equation Editor")
        self.setGeometry(100, 100, 900, 600)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setLayout(layout)

        self.editor = EquationEditor()
        self.palette = SymbolPalette(self.editor)
        layout.addWidget(self.palette)
        layout.addWidget(self.editor, stretch=3)
        self.latex_display = QTextEdit()
        self.latex_display.setMaximumHeight(100)
        layout.addWidget(self.latex_display)

        controls = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh LaTeX")
        controls.addWidget(self.refresh_btn)
        controls.addStretch(1)
        layout.addLayout(controls)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.editor.equation_changed.connect(self._sync_latex_display)
        self.refresh_btn.clicked.connect(self._refresh_from_latex)

        if latex_text:
            self.editor.load_from_latex(latex_text)
        self.latex_display.setPlainText(self.editor.get_latex())

        self._setup_menu()

    def _setup_menu(self):
        # For dialog, perhaps add buttons or keep simple
        pass  # Remove menu for dialog

    def _new_file(self):
        self.editor.clear()

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open equation",
            "",
            "LaTeX (*.tex *.latex *.eq.tex *.txt);;All files (*)",
        )
        if not path:
            return
        try:
            self.editor.load_from_path(path)
        except Exception as exc:
            QMessageBox.critical(self, "Error opening", f"Could not open the file.\n{exc}")

    def _save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save equation",
            "",
            "LaTeX (*.tex *.latex *.eq.tex *.txt);;All files (*)",
        )
        if not path:
            return
        if not (path.endswith(".tex") or path.endswith(".latex") or path.endswith(".eq.tex") or path.endswith(".txt")):
            path = path + ".tex"
        try:
            self.editor.save_to_path(path)
        except Exception as exc:
            QMessageBox.critical(self, "Error saving", f"Could not save the file.\n{exc}")

    def _import_latex(self):
        text, ok = QInputDialog.getMultiLineText(
            self,
            "Import LaTeX",
            "Paste your LaTeX equation:",
            "",
        )
        if not ok or not text.strip():
            return
        try:
            self.editor.load_from_latex(text)
        except Exception as exc:
            QMessageBox.critical(self, "Error importing", f"Could not import LaTeX.\n{exc}")

    def accept(self):
        latex = self.editor.get_latex()
        self.equation_accepted.emit(latex)
        super().accept()

    def _sync_latex_display(self, latex_text):
        if not self.latex_display.hasFocus():
            self.latex_display.setPlainText(latex_text)

    def _refresh_from_latex(self):
        text = self.latex_display.toPlainText()
        if not text.strip():
            return
        try:
            self.editor.load_from_latex(text)
        except Exception as exc:
            QMessageBox.critical(self, "Error refreshing", f"Could not parse the LaTeX.\n{exc}")