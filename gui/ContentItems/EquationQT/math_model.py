# math_model.py
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

from PyQt6.QtGui import QFont, QFontMetrics, QPainter, QPen, QColor, QPainterPath
from PyQt6.QtCore import Qt

class MathElement:
    def __init__(self):
        self.parent = None; self.x = 0; self.y = 0; self.width = 0; self.height = 0; self.ascent = 0
    def layout(self, font: QFont): pass
    def draw(self, painter: QPainter, x, y): pass
    def to_latex(self) -> str: return ""
    def get_slots(self): return []

# --- SERIALIZATION HELPERS ---
def element_to_dict(element):
    if isinstance(element, MathChar):
        return {"type": "char", "char": element.char, "latex_command": element.latex_command}
    if isinstance(element, MathGroup):
        return {"type": "group", "inner": element_to_dict(element.inner)}
    if isinstance(element, MathRow):
        return {"type": "row", "items": [element_to_dict(it) for it in element.items]}
    if isinstance(element, MathFraction):
        return {"type": "fraction", "num": element_to_dict(element.num), "den": element_to_dict(element.den)}
    if isinstance(element, MathOperator):
        return {
            "type": "operator",
            "symbol": element.symbol_char,
            "top": element_to_dict(element.top),
            "bottom": element_to_dict(element.bottom),
        }
    if isinstance(element, MathScript):
        return {
            "type": "script",
            "base": element_to_dict(element.base),
            "sup": element_to_dict(element.sup) if element.sup else None,
            "sub": element_to_dict(element.sub) if element.sub else None,
        }
    if isinstance(element, MathRoot):
        return {"type": "root", "inner": element_to_dict(element.inner)}
    if isinstance(element, MathMatrix):
        return {
            "type": "matrix",
            "rows": element.rows,
            "cols": element.cols,
            "bracket_type": element.bracket_type,
            "cells": [[element_to_dict(c) for c in row] for row in element.cells],
        }
    raise ValueError(f"Unsupported element type: {type(element)}")


def element_from_dict(data, parent=None):
    etype = data.get("type")
    if etype == "char":
        el = MathChar(data.get("char", ""), latex_command=data.get("latex_command"))
        el.parent = parent
        return el
    if etype == "group":
        inner = element_from_dict(data.get("inner", {"type": "row", "items": []}), None)
        grp = MathGroup(inner)
        grp.parent = parent
        inner.parent = grp
        return grp
    if etype == "row":
        row = MathRow(parent)
        for item_data in data.get("items", []):
            item = element_from_dict(item_data, row)
            row.items.append(item)
        return row
    if etype == "fraction":
        frac = MathFraction()
        frac.parent = parent
        frac.num = element_from_dict(data.get("num", {"type": "row", "items": []}), frac)
        frac.den = element_from_dict(data.get("den", {"type": "row", "items": []}), frac)
        return frac
    if etype == "operator":
        op = MathOperator(data.get("symbol", ""))
        op.parent = parent
        op.top = element_from_dict(data.get("top", {"type": "row", "items": []}), op)
        op.bottom = element_from_dict(data.get("bottom", {"type": "row", "items": []}), op)
        return op
    if etype == "script":
        base = element_from_dict(data.get("base", {"type": "row", "items": []}), None)
        script = MathScript(base)
        script.parent = parent
        sup_data = data.get("sup")
        sub_data = data.get("sub")
        if sup_data:
            script.sup = element_from_dict(sup_data, script)
        if sub_data:
            script.sub = element_from_dict(sub_data, script)
        return script
    if etype == "root":
        root = MathRoot()
        root.parent = parent
        root.inner = element_from_dict(data.get("inner", {"type": "row", "items": []}), root)
        return root
    if etype == "matrix":
        rows = int(data.get("rows", 1))
        cols = int(data.get("cols", 1))
        bracket_type = data.get("bracket_type", "p")
        mat = MathMatrix(rows, cols, bracket_type=bracket_type)
        mat.parent = parent
        cells_data = data.get("cells", [])
        for r in range(rows):
            for c in range(cols):
                cell_data = None
                if r < len(cells_data) and c < len(cells_data[r]):
                    cell_data = cells_data[r][c]
                if cell_data:
                    mat.cells[r][c] = element_from_dict(cell_data, mat)
                else:
                    mat.cells[r][c] = MathRow(mat)
        return mat
    raise ValueError(f"Unsupported element dict: {data}")

class MathChar(MathElement):
    def __init__(self, char, latex_command=None):
        super().__init__(); self.char = char; self.latex_command = latex_command
    def layout(self, font: QFont):
        fm = QFontMetrics(font); self.width = fm.horizontalAdvance(self.char); self.height = fm.height(); self.ascent = fm.ascent()
    def draw(self, p: QPainter, x, y): p.drawText(int(x), int(y + self.ascent), self.char)
    def to_latex(self) -> str: return (self.latex_command + " ") if self.latex_command else self.char

class MathGroup(MathElement):
    def __init__(self, inner=None):
        super().__init__()
        self.inner = inner if inner else MathRow(self)
        self.inner.parent = self

    def get_slots(self):
        return [self.inner]

    def layout(self, font: QFont):
        self.inner.layout(font)
        self.width = self.inner.width
        self.height = self.inner.height
        self.ascent = self.inner.ascent
        self.inner.x = 0
        self.inner.y = 0

    def draw(self, p: QPainter, x, y):
        self.inner.draw(p, x + self.inner.x, y + self.inner.y)

    def to_latex(self) -> str:
        return "{" + self.inner.to_latex() + "}"

class MathRow(MathElement):
    def __init__(self, parent_element=None):
        super().__init__(); self.parent = parent_element; self.items = []
    def insert(self, index, element): element.parent = self; self.items.insert(index, element)
    def layout(self, font: QFont):
        fm = QFontMetrics(font)
        if len(self.items) == 0: self.width = 16; self.height = fm.height(); self.ascent = fm.ascent(); return
        self.width = 0; self.ascent = 0; descent = 0
        for item in self.items:
            item.layout(font)
            if item.ascent > self.ascent: self.ascent = item.ascent
            if (item.height - item.ascent) > descent: descent = item.height - item.ascent
        self.height = self.ascent + descent
        current_x = 0
        for item in self.items: item.x = current_x; item.y = self.ascent - item.ascent; current_x += item.width
        self.width = current_x
    def draw(self, p: QPainter, x, y):
        if len(self.items) == 0:
            pen = QPen(QColor(180, 180, 180), 1, Qt.PenStyle.DashLine)
            p.setPen(pen); p.drawRect(int(x), int(y), int(self.width), int(self.height)); p.setPen(QPen(Qt.GlobalColor.black, 1)); return
        for item in self.items: item.draw(p, x + item.x, y + item.y)
    def to_latex(self) -> str: return "".join(item.to_latex() for item in self.items)

class MathFraction(MathElement):
    def __init__(self):
        super().__init__(); self.num = MathRow(self); self.den = MathRow(self); self.padding = 4
    def get_slots(self): return [self.num, self.den]
    def layout(self, font: QFont):
        self.num.layout(font); self.den.layout(font); self.width = max(self.num.width, self.den.width) + 8
        self.num.x = (self.width - self.num.width)/2; self.num.y = self.padding
        line_y = self.num.y + self.num.height + self.padding
        self.den.x = (self.width - self.den.width)/2; self.den.y = line_y + self.padding
        self.height = self.den.y + self.den.height + self.padding; self.ascent = line_y
    def draw(self, p, x, y):
        self.num.draw(p, x + self.num.x, y + self.num.y); self.den.draw(p, x + self.den.x, y + self.den.y)
        p.drawLine(int(x), int(y + self.ascent), int(x + self.width), int(y + self.ascent))
    def to_latex(self): return f"\\frac{{{self.num.to_latex()}}}{{{self.den.to_latex()}}}"

class MathOperator(MathElement):
    def __init__(self, symbol):
        super().__init__(); self.symbol_char = symbol; self.top = MathRow(self); self.bottom = MathRow(self)
    def get_slots(self): return [self.top, self.bottom]
    def layout(self, font):
        bf = QFont(font); bf.setPointSize(int(font.pointSize()*1.5)); fm = QFontMetrics(bf)
        self.sym_w = fm.horizontalAdvance(self.symbol_char); self.sym_h = fm.height(); self.sym_asc = fm.ascent()
        sf = QFont(font); sf.setPointSize(int(font.pointSize()*0.7))
        self.top.layout(sf); self.bottom.layout(sf); self.width = max(self.top.width, self.bottom.width, self.sym_w) + 4
        self.top.x = (self.width - self.top.width)/2; self.top.y = 0
        self.bottom.x = (self.width - self.bottom.width)/2; self.bottom.y = self.top.height + self.sym_h + 2
        self.height = self.bottom.y + self.bottom.height; self.ascent = self.top.height + self.sym_asc
    def draw(self, p, x, y):
        font_orig = p.font()
        sf = QFont(font_orig); sf.setPointSize(int(font_orig.pointSize()*0.7)); p.setFont(sf)
        self.top.draw(p, x + self.top.x, y + self.top.y); self.bottom.draw(p, x + self.bottom.x, y + self.bottom.y)
        bf = QFont(font_orig); bf.setPointSize(int(font_orig.pointSize()*1.5)); p.setFont(bf)
        p.drawText(int(x + (self.width - self.sym_w)/2), int(y + self.top.height + self.sym_asc), self.symbol_char)
        p.setFont(font_orig)
    def to_latex(self): return f"\\sum_{{{self.bottom.to_latex()}}}^{{{self.top.to_latex()}}}"

class MathScript(MathElement):
    def __init__(self, base):
        super().__init__(); self.base = base; self.base.parent = self; self.sup = None; self.sub = None
    def get_slots(self): return [s for s in [self.sup, self.sub] if s]
    def add_slot(self, slot_type):
        if slot_type=="sup" and not self.sup: self.sup = MathRow(self)
        if slot_type=="sub" and not self.sub: self.sub = MathRow(self)
    def layout(self, font):
        self.base.layout(font); sfont = QFont(font); sfont.setPointSize(int(font.pointSize()*0.7))
        sup_w, sup_h, sub_w, sub_h = 0,0,0,0
        if self.sup: self.sup.layout(sfont); sup_w = self.sup.width; sup_h = self.sup.height
        if self.sub: self.sub.layout(sfont); sub_w = self.sub.width; sub_h = self.sub.height
        self.width = self.base.width + max(sup_w, sub_w); self.height = self.base.height + sup_h//2 + sub_h//2
        self.ascent = self.base.ascent + sup_h//2
    def draw(self, p, x, y):
        font_orig = p.font()
        self.base.draw(p, x, y + (self.ascent - self.base.ascent));
        sfont = QFont(font_orig); sfont.setPointSize(int(font_orig.pointSize()*0.7)); p.setFont(sfont)
        if self.sup: self.sup.draw(p, x + self.base.width, y)
        if self.sub: self.sub.draw(p, x + self.base.width, y + self.height - self.sub.height)
        p.setFont(font_orig)
    def to_latex(self): return f"{self.base.to_latex()}" + (f"^{{{self.sup.to_latex()}}}" if self.sup else "") + (f"_{{{self.sub.to_latex()}}}" if self.sub else "")

class MathRoot(MathElement):
    def __init__(self):
        super().__init__(); self.inner = MathRow(self)
    def get_slots(self): return [self.inner]
    def layout(self, font):
        self.inner.layout(font); self.width = self.inner.width + 20; self.height = self.inner.height + 10; self.ascent = self.inner.ascent + 5
        self.inner.x = 16; self.inner.y = 5
    def draw(self, p, x, y):
        self.inner.draw(p, x + self.inner.x, y + self.inner.y)
        path = QPainterPath(); path.moveTo(x+2, y+self.height-5); path.lineTo(x+6, y+self.height); path.lineTo(x+14, y+2); path.lineTo(x+self.width, y+2); p.drawPath(path)
    def to_latex(self): return f"\\sqrt{{{self.inner.to_latex()}}}"

# --- AQUÍ ESTÁ LA NUEVA CLASE MATHMATRIX ACTUALIZADA ---
class MathMatrix(MathElement):
    def __init__(self, rows, cols, bracket_type="p"):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.bracket_type = bracket_type # "p", "b", "B", "v", "V", "none"
        self.cells = [[MathRow(self) for _ in range(cols)] for _ in range(rows)]
        self.brackets = {
            "p": ("(", ")"), "b": ("[", "]"), "B": ("{", "}"),
            "v": ("|", "|"), "V": ("‖", "‖"), "none": ("", "")
        }

    def get_slots(self): 
        return [cell for row in self.cells for cell in row]

    def layout(self, font: QFont):
        for r in range(self.rows):
            for c in range(self.cols): 
                self.cells[r][c].layout(font)
        
        col_w = [max([self.cells[r][c].width for r in range(self.rows)]) for c in range(self.cols)]
        row_h = [max([self.cells[r][c].height for c in range(self.cols)]) for r in range(self.rows)]
        
        padding = 10
        bracket_space = 20 if self.bracket_type != "none" else 0
        
        self.width = sum(col_w) + (self.cols + 1) * padding + bracket_space
        self.height = sum(row_h) + (self.rows + 1) * padding
        self.ascent = self.height / 2
        
        y_pos = padding
        for r in range(self.rows):
            x_pos = (10 if self.bracket_type != "none" else 0) + padding
            for c in range(self.cols):
                self.cells[r][c].x = x_pos
                self.cells[r][c].y = y_pos
                x_pos += col_w[c] + padding
            y_pos += row_h[r] + padding

    def draw(self, p, x, y):
        for r in range(self.rows):
            for c in range(self.cols): 
                self.cells[r][c].draw(p, x + self.cells[r][c].x, y + self.cells[r][c].y)
                
        left, right = self.brackets[self.bracket_type]
        if left and right:
            # Dibujamos los paréntesis centrados (convertido a int para evitar el error de C++)
            p.drawText(int(x), int(y + self.height/2 + p.fontMetrics().ascent()/3), left)
            p.drawText(int(x + self.width - 15), int(y + self.height/2 + p.fontMetrics().ascent()/3), right)

    def to_latex(self):
        env_map = {
            "p": "pmatrix", "b": "bmatrix", "B": "Bmatrix", 
            "v": "vmatrix", "V": "Vmatrix", "none": "matrix"
        }
        env = env_map[self.bracket_type]
        rows_latex = []
        for r in range(self.rows):
            rows_latex.append(" & ".join([c.to_latex() for c in self.cells[r]]))
        return f"\\begin{{{env}}}\n" + " \\\\\n".join(rows_latex) + f"\n\\end{{{env}}}"
