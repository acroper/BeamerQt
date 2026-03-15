# math_editor.py
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

import json
from PyQt6.QtWidgets import (
    QWidget, QDialog, QFormLayout, QSpinBox, QDialogButtonBox, QComboBox,
    QApplication, QFrame, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QPainter, QFont, QPen, QColor
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from .math_model import (
    MathRow, MathChar, MathFraction, MathMatrix, MathOperator, MathRoot, MathScript, MathGroup,
    element_to_dict, element_from_dict
)
from .math_config import SYMBOLS, BLOCKS, MODIFIERS, SYMBOL_CATALOG, BLOCK_CATALOG


class LatexParser:
    def __init__(self, text: str):
        self.text = text or ""
        self.i = 0

    def parse(self):
        return self._parse_row(stop_chars=None)

    def _peek(self, n=0):
        idx = self.i + n
        return self.text[idx] if 0 <= idx < len(self.text) else ""

    def _advance(self, n=1):
        self.i += n

    def _consume_whitespace(self):
        while self._peek() and self._peek().isspace():
            self._advance(1)

    def _parse_row(self, stop_chars):
        row = MathRow()
        while self.i < len(self.text):
            ch = self._peek()
            if stop_chars and ch in stop_chars:
                break
            if ch == "{":
                self._advance(1)
                group_row = self._parse_row(stop_chars="}")
                if self._peek() == "}":
                    self._advance(1)
                group = MathGroup(group_row)
                group_row.parent = group
                row.insert(len(row.items), group)
                self._consume_scripts_for_last(row)
                continue
            if ch == "\\":
                cmd = self._parse_command()
                if cmd == "\\\\":
                    # row break marker (used in matrices)
                    row.insert(len(row.items), MathChar("\\"))
                    row.insert(len(row.items), MathChar("\\"))
                    continue
                if cmd == "\\begin":
                    env = self._parse_braced_text()
                    if env in ("matrix", "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix"):
                        mat = self._parse_matrix_env(env)
                        if mat:
                            row.insert(len(row.items), mat)
                            continue
                    # Unknown env: keep literal
                    self._insert_literal(row, f"\\begin{{{env}}}")
                    continue
                if cmd in SYMBOLS:
                    row.insert(len(row.items), MathChar(SYMBOLS[cmd], latex_command=cmd))
                    self._consume_scripts_for_last(row)
                    continue
                if cmd in BLOCKS:
                    block = self._parse_block(cmd)
                    if block:
                        row.insert(len(row.items), block)
                        self._consume_scripts_for_last(row)
                        continue
                # Unknown command: literal text
                self._insert_literal(row, cmd)
                self._consume_scripts_for_last(row)
                continue
            if ch in "^_":
                # Modifier without base -> treat as literal
                row.insert(len(row.items), MathChar(ch))
                self._advance(1)
                continue
            if ch.isspace():
                self._advance(1)
                continue
            # Normal character
            row.insert(len(row.items), MathChar(ch))
            self._advance(1)

            self._consume_scripts_for_last(row)

        return row

    def _parse_command(self):
        if self._peek() != "\\":
            return ""
        self._advance(1)
        if self._peek() == "\\":
            self._advance(1)
            return "\\\\"
        start = self.i
        while self._peek().isalpha():
            self._advance(1)
        if self.i == start and self._peek():
            self._advance(1)
            return "\\" + self.text[start:self.i]
        return "\\" + self.text[start:self.i]

    def _parse_braced_text(self):
        self._consume_whitespace()
        if self._peek() != "{":
            return ""
        self._advance(1)
        start = self.i
        depth = 1
        while self.i < len(self.text):
            ch = self._peek()
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    out = self.text[start:self.i]
                    self._advance(1)
                    return out
            self._advance(1)
        return self.text[start:self.i]

    def _parse_block(self, cmd):
        block_type = BLOCKS[cmd]["type"]
        if block_type == "fraction":
            num = self._parse_script_group()
            den = self._parse_script_group()
            if not num or not den:
                return None
            frac = MathFraction()
            frac.num = num; frac.num.parent = frac
            frac.den = den; frac.den.parent = frac
            return frac
        if block_type == "root":
            inner = self._parse_script_group()
            if not inner:
                return None
            root = MathRoot()
            root.inner = inner; root.inner.parent = root
            return root
        if block_type == "operator":
            op = MathOperator(BLOCKS[cmd]["symbol"])
            return op
        if block_type == "matrix":
            # \matrix{...} not supported; keep literal
            return None
        return None

    def _parse_script_group(self):
        self._consume_whitespace()
        if self._peek() == "{":
            self._advance(1)
            row = self._parse_row(stop_chars="}")
            if self._peek() == "}":
                self._advance(1)
            return row
        # Single element group
        if self._peek() == "\\":
            cmd = self._parse_command()
            row = MathRow()
            if cmd in SYMBOLS:
                row.insert(0, MathChar(SYMBOLS[cmd], latex_command=cmd))
            elif cmd in BLOCKS:
                block = self._parse_block(cmd)
                if block:
                    row.insert(0, block)
                else:
                    self._insert_literal(row, cmd)
            else:
                self._insert_literal(row, cmd)
            return row
        if self._peek():
            ch = self._peek()
            self._advance(1)
            row = MathRow()
            row.insert(0, MathChar(ch))
            return row
        return MathRow()

    def _apply_script(self, row, slot, script_row):
        if len(row.items) == 0:
            return
        base = row.items[-1]
        row.items.pop()
        if isinstance(base, MathScript):
            script = base
        else:
            script = MathScript(base)
        script.add_slot(slot)
        setattr(script, slot, script_row)
        script_row.parent = script
        row.insert(len(row.items), script)

    def _insert_literal(self, row, text):
        for ch in text:
            row.insert(len(row.items), MathChar(ch))

    def _consume_scripts_for_last(self, row):
        while self._peek() in ("^", "_"):
            mod = self._peek()
            self._advance(1)
            script_row = self._parse_script_group()
            if len(row.items) == 0:
                continue
            last = row.items[-1]
            if isinstance(last, MathOperator):
                if mod == "^":
                    last.top = script_row
                    script_row.parent = last
                else:
                    last.bottom = script_row
                    script_row.parent = last
            else:
                self._apply_script(row, "sup" if mod == "^" else "sub", script_row)

    def _parse_matrix_env(self, env):
        content = self._read_until_end_env(env)
        if content is None:
            return None
        bracket_map = {
            "matrix": "none",
            "pmatrix": "p",
            "bmatrix": "b",
            "Bmatrix": "B",
            "vmatrix": "v",
            "Vmatrix": "V",
        }
        rows = self._split_matrix(content)
        row_count = len(rows) if rows else 1
        col_count = max((len(r) for r in rows), default=1)
        mat = MathMatrix(row_count, col_count, bracket_type=bracket_map.get(env, "none"))
        for r in range(row_count):
            for c in range(col_count):
                cell_text = rows[r][c] if r < len(rows) and c < len(rows[r]) else ""
                cell_row = LatexParser(cell_text).parse()
                mat.cells[r][c] = cell_row
                cell_row.parent = mat
        return mat

    def _read_until_end_env(self, env):
        marker = f"\\end{{{env}}}"
        start = self.i
        idx = self.text.find(marker, start)
        if idx == -1:
            return None
        content = self.text[start:idx]
        self.i = idx + len(marker)
        return content

    def _split_matrix(self, content):
        rows = []
        current_row = []
        current_cell = []
        depth = 0
        i = 0
        while i < len(content):
            ch = content[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth = max(0, depth - 1)
            if depth == 0 and ch == "&":
                current_row.append("".join(current_cell).strip())
                current_cell = []
                i += 1
                continue
            if depth == 0 and ch == "\\" and i + 1 < len(content) and content[i + 1] == "\\":
                current_row.append("".join(current_cell).strip())
                rows.append(current_row)
                current_row = []
                current_cell = []
                i += 2
                continue
            current_cell.append(ch)
            i += 1
        if current_cell or current_row:
            current_row.append("".join(current_cell).strip())
            rows.append(current_row)
        return rows

class EquationEditor(QWidget):
    equation_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.font = QFont("Latin Modern Math", 24)
        if not self.font.exactMatch(): 
            self.font = QFont("Cambria Math", 24)

        self.root_row = MathRow()
        self.cursor_row = self.root_row
        self.cursor_index = 0

        self.cursor_visible = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.blink_cursor)
        self.timer.start(500)
        
        self.start_x = 50
        self.start_y = 0 

        # Selection state (row-local selection only)
        self.selection_anchor_row = None
        self.selection_anchor_index = None
        self.selection_row = None
        self.selection_start = None
        self.selection_end = None

        # Autocomplete state
        self.autocomplete_popup = None
        self.autocomplete_list = None
        self.autocomplete_prefix = ""
        self.autocomplete_matches = []

    def blink_cursor(self): 
        self.cursor_visible = not self.cursor_visible
        self.update()

    def get_latex(self): 
        return self.root_row.to_latex().strip()

    def to_dict(self):
        return element_to_dict(self.root_row)

    def load_from_dict(self, data):
        self.root_row = element_from_dict(data)
        self.cursor_row = self.root_row
        self.cursor_index = len(self.root_row.items)
        self.equation_changed.emit(self.get_latex())
        self.update()

    def load_from_latex(self, latex_text: str):
        parser = LatexParser((latex_text or "").strip())
        self.root_row = parser.parse()
        self.cursor_row = self.root_row
        self.cursor_index = len(self.root_row.items)
        self.equation_changed.emit(self.get_latex())
        self.update()

    def save_to_path(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.get_latex())

    def load_from_path(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
        # Treat file contents as LaTeX
        self.load_from_latex(data)

    def clear(self):
        self.root_row = MathRow()
        self.cursor_row = self.root_row
        self.cursor_index = 0
        self.equation_changed.emit(self.get_latex())
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(event.rect(), Qt.GlobalColor.white)
        p.setFont(self.font)
        
        self.root_row.layout(self.font)
        self.start_y = (self.height() - self.root_row.height) // 2
        self.root_row.draw(p, self.start_x, self.start_y)
        self.draw_selection(p)
        self.draw_cursor(p)

    def mousePressEvent(self, event):
        self.setFocus()
        self._hide_autocomplete()
        cx, cy = event.position().x(), event.position().y()
        
        def hit_test_recursive(row, row_x, row_y, px, py):
            if len(row.items) == 0: return row, 0
            
            for i, item in enumerate(row.items):
                item_x, item_y = row_x + item.x, row_y + item.y
                
                if item_x <= px <= item_x + item.width and item_y <= py <= item_y + item.height:
                    if isinstance(item, MathMatrix):
                        for r in range(item.rows):
                            for c in range(item.cols):
                                cell = item.cells[r][c]
                                cell_abs_x = item_x + cell.x
                                cell_abs_y = item_y + cell.y
                                if cell_abs_x <= px <= cell_abs_x + cell.width and cell_abs_y <= py <= cell_abs_y + cell.height:
                                    return hit_test_recursive(cell, cell_abs_x, cell_abs_y, px, py)
                    
                    slots = item.get_slots()
                    if slots:
                        for slot in slots:
                            slot_x, slot_y = item_x + slot.x, item_y + slot.y
                            if slot_x <= px <= slot_x + slot.width and slot_y <= py <= slot_y + slot.height:
                                return hit_test_recursive(slot, slot_x, slot_y, px, py)
                    
                    if px < item_x + item.width / 2: return row, i
                    else: return row, i + 1
            
            if px <= row_x: return row, 0
            return row, len(row.items)

        result = hit_test_recursive(self.root_row, self.start_x, self.start_y, cx, cy)
        if result:
            prev_row, prev_idx = self.cursor_row, self.cursor_index
            self.cursor_row, self.cursor_index = result
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if self.selection_anchor_row is None:
                    self.selection_anchor_row = prev_row
                    self.selection_anchor_index = prev_idx
                self._update_selection_from_anchor()
            else:
                self.clear_selection()
            self.update()

    def draw_cursor(self, p):
        if not self.cursor_visible: return
        cx, cy = self.start_x, self.start_y
        path = []; current = self.cursor_row
        
        while current and current != self.root_row:
            path.insert(0, current)
            parent = current.parent
            if parent and parent.parent and isinstance(parent.parent, MathRow): 
                parent = parent.parent
            current = parent
            
        for el in path: 
            cx += el.parent.x + el.x
            cy += el.parent.y + el.y
            
        for i in range(self.cursor_index): 
            cx += self.cursor_row.items[i].width
            
        p.setPen(QPen(QColor("blue"), 2))
        p.drawLine(int(cx), int(cy), int(cx), int(cy + self.cursor_row.height))

    def _row_abs_pos(self, row):
        x, y = self.start_x, self.start_y
        current = row
        while current and current != self.root_row:
            parent = current.parent
            if not parent:
                break
            if hasattr(parent, "x") and hasattr(parent, "y"):
                x += parent.x + current.x
                y += parent.y + current.y
            if hasattr(parent, "parent") and isinstance(parent.parent, MathRow):
                current = parent.parent
            else:
                current = parent.parent if hasattr(parent, "parent") else None
        return x, y

    def draw_selection(self, p):
        if not self.has_selection():
            return
        row, start, end = self._selection_range()
        if row is None:
            return
        row_x, row_y = self._row_abs_pos(row)
        if start == end:
            return
        start_x = row_x + (row.items[start].x if start < len(row.items) else row.width)
        end_x = row_x + (row.items[end - 1].x + row.items[end - 1].width if end > 0 else 0)
        if end == len(row.items):
            end_x = row_x + row.width
        sel_w = max(0, end_x - start_x)
        if sel_w <= 0:
            return
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(180, 215, 255, 120))
        p.drawRect(int(start_x), int(row_y), int(sel_w), int(row.height))
        p.restore()

    def has_selection(self):
        return (
            self.selection_row is not None
            and self.selection_start is not None
            and self.selection_end is not None
            and self.selection_start != self.selection_end
        )

    def _selection_range(self):
        if not self.has_selection():
            return None, None, None
        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)
        return self.selection_row, start, end

    def clear_selection(self):
        self.selection_anchor_row = None
        self.selection_anchor_index = None
        self.selection_row = None
        self.selection_start = None
        self.selection_end = None

    def _update_selection_from_anchor(self):
        if self.selection_anchor_row is None:
            return
        if self.selection_anchor_row != self.cursor_row:
            self.clear_selection()
            return
        self.selection_row = self.cursor_row
        self.selection_start = self.selection_anchor_index
        self.selection_end = self.cursor_index

    def check_and_expand_macro(self):
        text_before = "".join([item.char for item in self.cursor_row.items[:self.cursor_index] if isinstance(item, MathChar)])
        
        for cmd in {**SYMBOLS, **BLOCKS}:
            if text_before.endswith(cmd):
                idx = self.cursor_index - len(cmd)
                del self.cursor_row.items[idx:self.cursor_index]
                self.cursor_index = idx
                
                if cmd in SYMBOLS:
                    self.cursor_row.insert(idx, MathChar(SYMBOLS[cmd], latex_command=cmd))
                    self.cursor_index += 1
                
                elif cmd in BLOCKS:
                    config = BLOCKS[cmd]
                    block = None
                    
                    if config["type"] == "fraction": 
                        block = MathFraction()
                    elif config["type"] == "operator": 
                        block = MathOperator(config["symbol"])
                    elif config["type"] == "root": 
                        block = MathRoot()
                    elif config["type"] == "matrix":
                        # Diálogo de matriz con opción de paréntesis
                        dlg = QDialog(self)
                        dlg.setWindowTitle("Insertar Matriz")
                        layout = QFormLayout(dlg)
                        
                        rows = QSpinBox()
                        rows.setValue(2)
                        rows.setMinimum(1)
                        
                        cols = QSpinBox()
                        cols.setValue(2)
                        cols.setMinimum(1)
                        
                        bracket_combo = QComboBox()
                        bracket_combo.addItem("( ) Paréntesis", "p")
                        bracket_combo.addItem("[ ] Corchetes", "b")
                        bracket_combo.addItem("{ } Llaves", "B")
                        bracket_combo.addItem("| | Determinante", "v")
                        bracket_combo.addItem("‖ ‖ Norma", "V")
                        bracket_combo.addItem("Ninguno", "none")
                        
                        layout.addRow("Filas:", rows)
                        layout.addRow("Columnas:", cols)
                        layout.addRow("Envoltura:", bracket_combo)
                        
                        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
                        layout.addRow(btns)
                        btns.accepted.connect(dlg.accept)
                        btns.rejected.connect(dlg.reject)
                        
                        if dlg.exec():
                            selected_bracket = bracket_combo.currentData()
                            block = MathMatrix(rows.value(), cols.value(), bracket_type=selected_bracket)
                        else:
                            return False # Cancelado
                            
                    if block: 
                        self.cursor_row.insert(idx, block)
                        self.cursor_row = block.get_slots()[0]
                        self.cursor_index = 0
                return True
        return False

    def _get_cursor_pos(self):
        # Compute absolute cursor position for popup placement
        self.root_row.layout(self.font)
        cx, cy = self.start_x, self.start_y
        path = []
        current = self.cursor_row
        while current and current != self.root_row:
            path.insert(0, current)
            parent = current.parent
            if parent and parent.parent and isinstance(parent.parent, MathRow):
                parent = parent.parent
            current = parent
        for el in path:
            cx += el.parent.x + el.x
            cy += el.parent.y + el.y
        for i in range(self.cursor_index):
            cx += self.cursor_row.items[i].width
        return int(cx), int(cy)

    def _get_command_prefix(self):
        # Look backwards for contiguous \ + letters
        i = self.cursor_index - 1
        chars = []
        while i >= 0 and isinstance(self.cursor_row.items[i], MathChar):
            ch = self.cursor_row.items[i].char
            if ch.isalpha() or ch == "\\":
                chars.append(ch)
                if ch == "\\":
                    break
                i -= 1
                continue
            break
        if not chars:
            return ""
        prefix = "".join(reversed(chars))
        if not prefix.startswith("\\"):
            return ""
        return prefix

    def _get_autocomplete_matches(self, prefix):
        cmds = list({**SYMBOLS, **BLOCKS}.keys())
        return sorted([c for c in cmds if c.startswith(prefix)])

    def _command_display(self, cmd):
        if cmd in SYMBOLS:
            return SYMBOLS[cmd]
        if cmd in BLOCKS and BLOCKS[cmd]["type"] == "operator":
            return BLOCKS[cmd]["symbol"]
        # Look up UI catalogs for display glyphs
        for cat in (SYMBOL_CATALOG, BLOCK_CATALOG):
            for _group, items in cat.items():
                for glyph, c in items:
                    if c == cmd:
                        return glyph
        return ""

    def _show_autocomplete(self):
        prefix = self._get_command_prefix()
        if len(prefix) < 4:
            self._hide_autocomplete()
            return
        matches = self._get_autocomplete_matches(prefix)
        if not matches:
            self._hide_autocomplete()
            return
        self.autocomplete_prefix = prefix
        self.autocomplete_matches = matches[:12]
        if self.autocomplete_popup is None:
            self.autocomplete_popup = QFrame(self, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
            self.autocomplete_popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
            self.autocomplete_popup.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.autocomplete_list = QListWidget(self.autocomplete_popup)
            self.autocomplete_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.autocomplete_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.autocomplete_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.autocomplete_list.itemClicked.connect(self._on_autocomplete_clicked)
        self.autocomplete_list.clear()
        for cmd in self.autocomplete_matches:
            glyph = self._command_display(cmd)
            label = f"{glyph}  {cmd}" if glyph else cmd
            QListWidgetItem(label, self.autocomplete_list)
        self.autocomplete_list.setCurrentRow(0)
        self.autocomplete_list.adjustSize()
        self.autocomplete_popup.resize(self.autocomplete_list.sizeHint())
        x, y = self._get_cursor_pos()
        self.autocomplete_popup.move(self.mapToGlobal(QPoint(x, y + 20)))
        self.autocomplete_popup.show()
        self.setFocus()

    def _hide_autocomplete(self):
        if self.autocomplete_popup:
            self.autocomplete_popup.hide()
        self.autocomplete_prefix = ""
        self.autocomplete_matches = []

    def _accept_autocomplete(self, cmd):
        prefix = self.autocomplete_prefix or self._get_command_prefix()
        if not prefix:
            return
        # Remove typed prefix
        n = len(prefix)
        for _ in range(n):
            if self.cursor_index <= 0:
                break
            if not isinstance(self.cursor_row.items[self.cursor_index - 1], MathChar):
                break
            del self.cursor_row.items[self.cursor_index - 1]
            self.cursor_index -= 1
        # Insert full command and expand
        for ch in cmd:
            self.cursor_row.insert(self.cursor_index, MathChar(ch))
            self.cursor_index += 1
        self.check_and_expand_macro()
        self._hide_autocomplete()
        self.equation_changed.emit(self.get_latex())
        self.update()

    def _on_autocomplete_clicked(self, item):
        if item:
            self._accept_autocomplete(item.text())

    def handle_modifier(self, char):
        slot = MODIFIERS[char]["slot"]
        if self.cursor_index == 0: 
            base = MathRow()
        else: 
            base = self.cursor_row.items[self.cursor_index - 1]
            del self.cursor_row.items[self.cursor_index - 1]
            self.cursor_index -= 1
            
        script = base if isinstance(base, MathScript) else MathScript(base)
        script.add_slot(slot)
        self.cursor_row.insert(self.cursor_index, script)
        self.cursor_row = getattr(script, slot)
        self.cursor_index = len(self.cursor_row.items)

    def keyPressEvent(self, event):
        text = event.text()
        ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        shift = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        # Ignore pure modifier presses to avoid accidental edits
        if event.key() in (
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Meta,
        ):
            return

        if self.autocomplete_popup and self.autocomplete_popup.isVisible():
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab):
                if self.autocomplete_matches:
                    self._accept_autocomplete(self.autocomplete_matches[0])
                return
            if event.key() == Qt.Key.Key_Escape:
                self._hide_autocomplete()
                return

        if ctrl:
            self._hide_autocomplete()
            if event.key() == Qt.Key.Key_C:
                self.copy_selection()
                return
            if event.key() == Qt.Key.Key_X:
                self.cut_selection()
                return
            if event.key() == Qt.Key.Key_V:
                self.paste_clipboard()
                return
            if event.key() == Qt.Key.Key_A:
                self.selection_anchor_row = self.root_row
                self.selection_anchor_index = 0
                self.cursor_row = self.root_row
                self.cursor_index = len(self.root_row.items)
                self._update_selection_from_anchor()
                self.update()
                return
            return
        
        if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            self._hide_autocomplete()
            if shift:
                if self.selection_anchor_row is None:
                    self.selection_anchor_row = self.cursor_row
                    self.selection_anchor_index = self.cursor_index
                if event.key() == Qt.Key.Key_Left:
                    self.move_cursor_left()
                elif event.key() == Qt.Key.Key_Right:
                    self.move_cursor_right()
                elif event.key() == Qt.Key.Key_Up:
                    self.move_cursor_up()
                elif event.key() == Qt.Key.Key_Down:
                    self.move_cursor_down()
                self._update_selection_from_anchor()
            else:
                if event.key() == Qt.Key.Key_Left:
                    self.move_cursor_left()
                elif event.key() == Qt.Key.Key_Right:
                    self.move_cursor_right()
                elif event.key() == Qt.Key.Key_Up:
                    self.move_cursor_up()
                elif event.key() == Qt.Key.Key_Down:
                    self.move_cursor_down()
                self.clear_selection()
            self.equation_changed.emit(self.get_latex())
            self.update()
            return

        if self.has_selection() and event.key() == Qt.Key.Key_Backspace:
            self._hide_autocomplete()
            self.delete_selection()
            self.equation_changed.emit(self.get_latex())
            self.update()
            return

        if text == " ":
            # Only use space to expand macros; do not insert a space
            self.check_and_expand_macro()
            self._hide_autocomplete()
        elif text in MODIFIERS: 
            self._hide_autocomplete()
            self.handle_modifier(text)
        elif event.key() == Qt.Key.Key_Backspace:
            self._hide_autocomplete()
            if self.has_selection():
                self.delete_selection()
            elif self.cursor_index > 0: 
                del self.cursor_row.items[self.cursor_index - 1]
                self.cursor_index -= 1
            elif self.cursor_row.parent:
                parent_block = self.cursor_row.parent
                parent_row = parent_block.parent
                if parent_row:
                    idx = parent_row.items.index(parent_block)
                    del parent_row.items[idx]
                    self.cursor_row = parent_row
                    self.cursor_index = idx
        elif text.isprintable(): 
            if self.has_selection():
                self.delete_selection()
            self.cursor_row.insert(self.cursor_index, MathChar(text))
            self.cursor_index += 1
            if text.isalpha() or text == "\\":
                self._show_autocomplete()
            else:
                self._hide_autocomplete()
            
        self.equation_changed.emit(self.get_latex())
        self.update()

    def delete_selection(self):
        if not self.has_selection():
            return
        row, start, end = self._selection_range()
        del row.items[start:end]
        self.cursor_row = row
        self.cursor_index = start
        self.clear_selection()

    def copy_selection(self):
        if not self.has_selection():
            return
        row, start, end = self._selection_range()
        payload = {
            "format": "equation-selection-v1",
            "items": [element_to_dict(it) for it in row.items[start:end]],
        }
        QApplication.clipboard().setText(json.dumps(payload, ensure_ascii=False))

    def cut_selection(self):
        if not self.has_selection():
            return
        self.copy_selection()
        self.delete_selection()
        self.equation_changed.emit(self.get_latex())
        self.update()

    def paste_clipboard(self):
        text = QApplication.clipboard().text()
        if not text:
            return
        try:
            data = json.loads(text)
        except Exception:
            data = None
        if isinstance(data, dict) and data.get("format") == "equation-selection-v1":
            items = data.get("items", [])
            if self.has_selection():
                self.delete_selection()
            for item_data in items:
                el = element_from_dict(item_data, self.cursor_row)
                self.cursor_row.insert(self.cursor_index, el)
                self.cursor_index += 1
        else:
            if self.has_selection():
                self.delete_selection()
            if self._looks_like_latex(text):
                try:
                    row = LatexParser(text).parse()
                    self._insert_row_items(row)
                except Exception:
                    self._insert_plain_text(text)
            else:
                self._insert_plain_text(text)
        self.equation_changed.emit(self.get_latex())
        self.update()

    def _insert_row_items(self, row):
        for item in row.items:
            item.parent = self.cursor_row
            self.cursor_row.insert(self.cursor_index, item)
            self.cursor_index += 1

    def _insert_plain_text(self, text):
        for ch in text:
            if ch == "\n" or ch == "\r":
                ch = " "
            if ch.isspace():
                continue
            if not ch.isprintable():
                continue
            self.cursor_row.insert(self.cursor_index, MathChar(ch))
            self.cursor_index += 1

    def _looks_like_latex(self, text):
        triggers = ("\\", "^", "_", "{", "}", "\\begin")
        return any(t in text for t in triggers)

    # --- LÓGICA DE NAVEGACIÓN ---
    def _get_matrix_indices(self):
        if self.cursor_row.parent and isinstance(self.cursor_row.parent, MathMatrix):
            matrix = self.cursor_row.parent
            for r in range(matrix.rows):
                for c in range(matrix.cols):
                    if matrix.cells[r][c] == self.cursor_row:
                        return matrix, r, c
        return None, -1, -1

    def move_cursor_right(self):
        matrix, r, c = self._get_matrix_indices()
        if matrix and self.cursor_index == len(self.cursor_row.items): 
            if c < matrix.cols - 1: 
                self.cursor_row = matrix.cells[r][c+1]
                self.cursor_index = 0
            else: 
                parent_row = matrix.parent
                self.cursor_row = parent_row
                self.cursor_index = parent_row.items.index(matrix) + 1
            return

        # When inside a MathOperator placeholder, leaving it should go back to the main row
        if self.cursor_row.parent and isinstance(self.cursor_row.parent, MathOperator):
            operator = self.cursor_row.parent
            if self.cursor_index == len(self.cursor_row.items):
                parent_row = operator.parent
                if parent_row:
                    idx = parent_row.items.index(operator)
                    self.cursor_row = parent_row
                    self.cursor_index = idx + 1
                return

        if self.cursor_index < len(self.cursor_row.items): 
            next_item = self.cursor_row.items[self.cursor_index]
            # Treat complex symbols (e.g. sum/int) as a single object when moving left/right
            if isinstance(next_item, MathOperator):
                self.cursor_index += 1
            else:
                slots = next_item.get_slots()
                if slots: 
                    self.cursor_row = slots[0]
                    self.cursor_index = 0
                else: 
                    self.cursor_index += 1
            return

        if self.cursor_row.parent:
            parent_block = self.cursor_row.parent
            parent_row = parent_block.parent
            all_slots = parent_block.get_slots()
            try:
                current_slot_index = all_slots.index(self.cursor_row)
                if current_slot_index < len(all_slots) - 1:
                    self.cursor_row = all_slots[current_slot_index + 1]
                    self.cursor_index = 0
                    return
            except ValueError: pass
            if parent_row:
                self.cursor_row = parent_row
                self.cursor_index = parent_row.items.index(parent_block) + 1

    def move_cursor_left(self):
        matrix, r, c = self._get_matrix_indices()
        if matrix and self.cursor_index == 0: 
            if c > 0: 
                self.cursor_row = matrix.cells[r][c-1]
                self.cursor_index = len(self.cursor_row.items)
            else: 
                parent_row = matrix.parent
                self.cursor_row = parent_row
                self.cursor_index = parent_row.items.index(matrix)
            return

        # When inside a MathOperator placeholder, leaving it should go back to the main row
        if self.cursor_row.parent and isinstance(self.cursor_row.parent, MathOperator):
            operator = self.cursor_row.parent
            if self.cursor_index == 0:
                parent_row = operator.parent
                if parent_row:
                    idx = parent_row.items.index(operator)
                    self.cursor_row = parent_row
                    self.cursor_index = idx
                return

        if self.cursor_index > 0: 
            prev_item = self.cursor_row.items[self.cursor_index - 1]
            # Treat complex symbols (e.g. sum/int) as a single object when moving left/right
            if isinstance(prev_item, MathOperator):
                self.cursor_index -= 1
            else:
                slots = prev_item.get_slots()
                if slots: 
                    self.cursor_row = slots[-1]
                    self.cursor_index = len(self.cursor_row.items)
                else: 
                    self.cursor_index -= 1
            return

        if self.cursor_row.parent:
            parent_block = self.cursor_row.parent
            parent_row = parent_block.parent
            all_slots = parent_block.get_slots()
            try:
                current_slot_index = all_slots.index(self.cursor_row)
                if current_slot_index > 0:
                    self.cursor_row = all_slots[current_slot_index - 1]
                    self.cursor_index = len(self.cursor_row.items)
                    return
            except ValueError: pass
            if parent_row:
                self.cursor_row = parent_row
                self.cursor_index = parent_row.items.index(parent_block)

    def move_cursor_up(self):
        matrix, r, c = self._get_matrix_indices()
        if matrix:
            if r > 0: 
                self.cursor_row = matrix.cells[r-1][c]
                self.cursor_index = len(self.cursor_row.items)
            else: 
                parent_row = matrix.parent
                self.cursor_row = parent_row
                self.cursor_index = parent_row.items.index(matrix)
            return

        # When inside an operator placeholder, Up behaves like Right (move along the placeholder / exit it)
        if self.cursor_row.parent and isinstance(self.cursor_row.parent, MathOperator):
            operator = self.cursor_row.parent
            if self.cursor_row == operator.bottom:
                self.move_cursor_right()
                return

        # If we're just to the right of an operator, jump into its superscript slot
        if self.cursor_index > 0:
            prev_item = self.cursor_row.items[self.cursor_index - 1]
            if isinstance(prev_item, MathOperator) and prev_item.top:
                self.cursor_row = prev_item.top
                self.cursor_index = len(self.cursor_row.items)
                return

        if self.cursor_row.parent and isinstance(self.cursor_row.parent, MathFraction):
            if self.cursor_row == self.cursor_row.parent.den:
                self.cursor_row = self.cursor_row.parent.num
                self.cursor_index = len(self.cursor_row.items)

    def move_cursor_down(self):
        matrix, r, c = self._get_matrix_indices()
        if matrix:
            if r < matrix.rows - 1: 
                self.cursor_row = matrix.cells[r+1][c]
                self.cursor_index = len(self.cursor_row.items)
            else: 
                parent_row = matrix.parent
                self.cursor_row = parent_row
                self.cursor_index = parent_row.items.index(matrix) + 1
            return

        # When inside an operator placeholder, Down behaves like Right (move along the placeholder / exit it)
        if self.cursor_row.parent and isinstance(self.cursor_row.parent, MathOperator):
            self.move_cursor_right()
            return

        # If we're just to the right of an operator, jump into its subscript slot
        if self.cursor_index > 0:
            prev_item = self.cursor_row.items[self.cursor_index - 1]
            if isinstance(prev_item, MathOperator) and prev_item.bottom:
                self.cursor_row = prev_item.bottom
                self.cursor_index = len(self.cursor_row.items)
                return

        if self.cursor_row.parent and isinstance(self.cursor_row.parent, MathFraction):
            if self.cursor_row == self.cursor_row.parent.num:
                self.cursor_row = self.cursor_row.parent.den
                self.cursor_index = len(self.cursor_row.items)

