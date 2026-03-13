# symbol_palette.py
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

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMenu
from .math_config import SYMBOL_CATALOG, BLOCK_CATALOG
from .math_model import MathChar

class SymbolPalette(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.layout = QHBoxLayout(self)
        
        self.all_catalogs = {**SYMBOL_CATALOG, **BLOCK_CATALOG}
        
        for cat, items in self.all_catalogs.items():
            btn = QPushButton(f"{items[0][0]} {cat}")
            menu = QMenu(self)
            for char, cmd in items:
                action = menu.addAction(f"{char} {cmd}")
                action.triggered.connect(lambda checked, c=cmd: self.insert_command(c))
            btn.setMenu(menu)
            self.layout.addWidget(btn)

    def insert_command(self, cmd):
        # 1. Insertar el comando en la fila, letra por letra
        for char in cmd:
            self.editor.cursor_row.insert(self.editor.cursor_index, MathChar(char))
            self.editor.cursor_index += 1
        
        # 2. Intentar expandir el macro INMEDIATAMENTE (sin insertar espacio)
        expanded = self.editor.check_and_expand_macro()
        
        # Si por alguna razón el comando no era un macro conocido, dejamos un espacio
        if not expanded:
            self.editor.cursor_row.insert(self.editor.cursor_index, MathChar(" "))
            self.editor.cursor_index += 1
            
        # 3. Forzar la actualización visual y la generación de LaTeX
        self.editor.equation_changed.emit(self.editor.get_latex())
        self.editor.update()
        self.editor.setFocus()