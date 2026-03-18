"""
Beamer QT
Copyright (C) 2024  Jorge Guerrero - acroper@gmail.com

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
import os

from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import *

import xml.etree.ElementTree as ET

from core.xmlutils import *


class itemWidgetTable(QtWidgets.QWidget):
    
    def __init__(self):
        
        super(itemWidgetTable, self).__init__()
        
        uic.loadUi('gui/ContentItems/Table/ItemTable.ui', self)
        
        self.InnerObject = itemTable()
        self.TableWidget.horizontalHeader().setVisible(True)
        
        self.AssignActions()

    
    def AssignActions(self):
        # Connect table cell changes
        self.TableWidget.itemChanged.connect(self.OnTableCellChanged)
        # Connect buttons for adding/removing rows and columns
        self.AddRowBtn.clicked.connect(self.AddRow)
        self.RemoveRowBtn.clicked.connect(self.RemoveRow)
        self.AddColBtn.clicked.connect(self.AddColumn)
        self.RemoveColBtn.clicked.connect(self.RemoveColumn)
        # Connect size mode combo box
        self.TableSizeCombo.currentTextChanged.connect(self.OnSizeModeChanged)
        # Connect header resize
        self.TableWidget.horizontalHeader().sectionResized.connect(self.OnColumnResized)

    def OnSizeModeChanged(self, mode):
        """Handle changes in the size mode combo box."""
        if self.InnerObject.SizeMode == mode:
            return
        self.InnerObject.SizeMode = mode
        # When changing mode, reset widths to default
        self.InnerObject.ColumnWidths = []
        self.Refresh()

    def OnColumnResized(self, logicalIndex, oldSize, newSize):
        """Update column width percentages when a column is resized in '%' mode."""
        if self.InnerObject.SizeMode != "%" or self.TableWidget.horizontalHeader().signalsBlocked():
            return

        cols = self.TableWidget.columnCount()
        if cols < 2:
            return

        header = self.TableWidget.horizontalHeader()
        header.blockSignals(True)

        delta = newSize - oldSize

        # Determine which column to adjust to keep the total width constant.
        neighborIndex = logicalIndex + 1
        if neighborIndex == cols:
            neighborIndex = logicalIndex - 1

        if 0 <= neighborIndex < cols:
            neighborWidth = self.TableWidget.columnWidth(neighborIndex)
            minWidth = 10 # A minimum width in pixels to prevent column from disappearing.
            
            if neighborWidth - delta >= minWidth:
                # We adjust the neighbor to keep the total width constant.
                self.TableWidget.setColumnWidth(neighborIndex, neighborWidth - delta)
            else:
                # The neighbor would become too small. We limit the resize.
                allowed_delta = neighborWidth - minWidth
                self.TableWidget.setColumnWidth(logicalIndex, oldSize + allowed_delta)
                self.TableWidget.setColumnWidth(neighborIndex, minWidth)

        # Now that the pixel widths are adjusted, recalculate percentages.
        total_width = sum(self.TableWidget.columnWidth(i) for i in range(cols))

        if total_width > 0:
            new_percentages = [(self.TableWidget.columnWidth(i) / total_width) * 100 for i in range(cols)]
            self.InnerObject.ColumnWidths = [f"{p:.1f}" for p in new_percentages]

            header_labels = [f"{p:.1f}%" for p in new_percentages]
            self.TableWidget.setHorizontalHeaderLabels(header_labels)
        
        header.blockSignals(False)

    def apply_percentage_widths(self):
        """Apply column widths based on stored percentages. Should be called after UI has settled."""
        if self.InnerObject.SizeMode != "%":
            return

        cols = self.TableWidget.columnCount()
        if not (cols > 0 and len(self.InnerObject.ColumnWidths) == cols):
            return

        total_width = self.TableWidget.viewport().width()
        if total_width <= 0:
            return  # Not visible or not laid out yet

        header = self.TableWidget.horizontalHeader()
        # Block signals to prevent OnColumnResized from firing and creating a loop
        header.blockSignals(True)
        
        # Distribute the total width according to percentages
        for i, width_str in enumerate(self.InnerObject.ColumnWidths):
            new_width = int(float(width_str) / 100.0 * total_width)
            self.TableWidget.setColumnWidth(i, new_width)
        
        header.blockSignals(False)

    def UpdateHeaderLabels(self):
        """Update horizontal header labels and resize mode based on the size mode."""
        mode = self.InnerObject.SizeMode
        cols = self.InnerObject.cols

        if cols == 0:
            return

        self.TableWidget.horizontalHeader().blockSignals(True)
        if mode == "Automatic":
            self.TableWidget.setHorizontalHeaderLabels([str(i + 1) for i in range(cols)])
            self.TableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        elif mode == "%":
            if len(self.InnerObject.ColumnWidths) != cols:
                percent = 100 / cols if cols > 0 else 0
                self.InnerObject.ColumnWidths = [f"{percent:.1f}" for _ in range(cols)]
            
            header_labels = [f"{w}%" for w in self.InnerObject.ColumnWidths]
            self.TableWidget.setHorizontalHeaderLabels(header_labels)
            self.TableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.TableWidget.horizontalHeader().blockSignals(False)

    def OnTableCellChanged(self, item):
        """Update inner object when a cell is edited"""
        if item is not None:
            row = self.TableWidget.row(item)
            col = self.TableWidget.column(item)
            self.InnerObject.SetValue(row, col, item.text())
        
    def AddRow(self):
        """Add a new row below the currently selected cell"""
        selected_row = self.TableWidget.currentRow()
        # If no row is selected, add at the end
        if selected_row < 0:
            insert_pos = self.TableWidget.rowCount()
        else:
            insert_pos = selected_row + 1
        
        self.TableWidget.insertRow(insert_pos)
        # Insert empty row into inner object at the correct position
        self.InnerObject.table.insert(insert_pos, ["" for _ in range(self.InnerObject.cols)])
        self.InnerObject.rows += 1
        
        # Populate new row with empty cells
        for col in range(self.TableWidget.columnCount()):
            item = QTableWidgetItem("")
            self.TableWidget.setItem(insert_pos, col, item)
    
    def RemoveRow(self):
        """Remove the row of the currently selected cell"""
        selected_row = self.TableWidget.currentRow()
        current_rows = self.TableWidget.rowCount()
        # Only remove if a row is selected and there is more than 1 row
        if selected_row >= 0 and current_rows > 1:
            self.TableWidget.removeRow(selected_row)
            # Update the inner object's data
            if selected_row < len(self.InnerObject.table):
                self.InnerObject.table.pop(selected_row)
                self.InnerObject.rows -= 1
    
    def AddColumn(self):
        """Add a new column to the right of the currently selected cell"""
        selected_col = self.TableWidget.currentColumn()
        # If no column is selected, add at the end
        if selected_col < 0:
            insert_pos = self.TableWidget.columnCount()
        else:
            insert_pos = selected_col + 1
        
        self.TableWidget.insertColumn(insert_pos)
        # Add empty cells to each row in the inner object at the correct position
        for row in self.InnerObject.table:
            row.insert(insert_pos, "")
        self.InnerObject.cols += 1
        
        # Populate new column with empty cells
        for row in range(self.TableWidget.rowCount()):
            item = QTableWidgetItem("")
            self.TableWidget.setItem(row, insert_pos, item)

        # Invalidate column widths to force recalculation
        if self.InnerObject.SizeMode == "%":
            self.InnerObject.ColumnWidths = []
        self.Refresh()
    
    def RemoveColumn(self):
        """Remove the column of the currently selected cell"""
        selected_col = self.TableWidget.currentColumn()
        current_cols = self.TableWidget.columnCount()
        # Only remove if a column is selected and there is more than 1 column
        if selected_col >= 0 and current_cols > 1:
            self.TableWidget.removeColumn(selected_col)
            # Update the inner object's data
            for row in self.InnerObject.table:
                if selected_col < len(row):
                    row.pop(selected_col)
            self.InnerObject.cols -= 1

            if self.InnerObject.SizeMode == "%":
                self.InnerObject.ColumnWidths = []
            self.Refresh()
        
    
    def GetInnerObject(self):
        """Extract table data from widget and update inner object"""
        rows = self.TableWidget.rowCount()
        cols = self.TableWidget.columnCount()
        
        # Clear and rebuild table data
        self.InnerObject.table = []
        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = self.TableWidget.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            self.InnerObject.table.append(row_data)
        
        self.InnerObject.rows = rows
        self.InnerObject.cols = cols

        self.InnerObject.SizeMode = self.TableSizeCombo.currentText()
        
        return self.InnerObject
    
    def SetInnerObject(self, inner):
        """Set the inner object and refresh the UI"""
        self.InnerObject = inner
        self.Refresh()
        
    def Refresh(self):
        """Refresh the table from the inner object"""
        # Block signals to avoid triggering change callbacks
        self.TableWidget.blockSignals(True)
        self.TableWidget.horizontalHeader().blockSignals(True)

        self.TableSizeCombo.setCurrentText(self.InnerObject.SizeMode)
        
        # Clear existing table
        self.TableWidget.setRowCount(0)
        self.TableWidget.setColumnCount(0)
        
        # Set up the table
        rows = self.InnerObject.rows
        cols = self.InnerObject.cols
        
        self.TableWidget.setRowCount(rows)
        self.TableWidget.setColumnCount(cols)
        
        # Populate the table
        for row in range(rows):
            for col in range(cols):
                if row < len(self.InnerObject.table) and col < len(self.InnerObject.table[row]):
                    value = self.InnerObject.table[row][col]
                else:
                    value = ""
                
                item = QTableWidgetItem(value)
                self.TableWidget.setItem(row, col, item)
        
        # Set up headers based on current mode
        self.TableWidget.horizontalHeader().setVisible(True)
        self.UpdateHeaderLabels()
        
        # Unblock signals
        self.TableWidget.blockSignals(False)
        self.TableWidget.horizontalHeader().blockSignals(False)
        
        # Defer width application to after the event loop processes layout changes
        if self.InnerObject.SizeMode == "%":
            QtCore.QTimer.singleShot(0, self.apply_percentage_widths)
            
    def resizeEvent(self, event):
        """Ensure columns resize proportionally when the widget is resized."""
        super().resizeEvent(event)
        if self.InnerObject.SizeMode == "%":
            QtCore.QTimer.singleShot(0, self.apply_percentage_widths)
        
class itemTable():
    
    def __init__(self):
        
        self.Type = "Table"
        
        # Initialize a 4x4 table with empty strings
        self.rows = 4
        self.cols = 4
        self.table = [["" for _ in range(4)] for _ in range(4)]
        
        self.SizeMode = "Automatic"
        self.ColumnWidths = []
        
        self.Alignment = "Center"
    
    def SetValue(self, row, col, value):
        """Set a value at the specified row and column"""
        if row < len(self.table) and col < len(self.table[row]):
            self.table[row][col] = value
    
    def AddRow(self):
        """Add a new row to the table"""
        self.table.append(["" for _ in range(self.cols)])
        self.rows += 1
    
    def RemoveRow(self):
        """Remove the last row from the table"""
        if self.rows > 1 and len(self.table) > 0:
            self.table.pop()
            self.rows -= 1
    
    def AddColumn(self):
        """Add a new column to the table"""
        for row in self.table:
            row.append("")
        self.cols += 1
    
    def RemoveColumn(self):
        """Remove the last column from the table"""
        if self.cols > 1:
            for row in self.table:
                if len(row) > 0:
                    row.pop()
            self.cols -= 1
        
    
    def GetXMLContent(self):
        
        ContentXML = ET.Element('ItemWidget', ItemType='Table')
        
        # Store table dimensions
        ContentXML.set('rows', str(self.rows))
        ContentXML.set('cols', str(self.cols))
        ContentXML.set('SizeMode', self.SizeMode)
        
        # Store column widths if mode is '%'
        if self.SizeMode == '%' and self.ColumnWidths:
            ContentXML.set('ColumnWidths', ",".join(map(str, self.ColumnWidths)))
        
        # Store table data as rows
        for row_idx, row_data in enumerate(self.table):
            row_elem = ET.SubElement(ContentXML, 'Row', index=str(row_idx))
            for col_idx, value in enumerate(row_data):
                cell_elem = ET.SubElement(row_elem, 'Cell', row=str(row_idx), col=str(col_idx))
                cell_elem.text = value if value else ""
        
        # Store alignment
        Alignment = ET.SubElement(ContentXML, "Alignment")
        Alignment.text = self.Alignment
        
        return ContentXML
        
        
        
    def ReadXMLContent(self, xblock):
        
        xmlblock = xmlutils(xblock)
        
        # Read dimensions
        self.rows = int(xblock.get('rows', '4'))
        self.cols = int(xblock.get('cols', '4'))
        self.SizeMode = xblock.get('SizeMode', 'Automatic')
        
        # Read column widths
        widths_str = xblock.get('ColumnWidths')
        if self.SizeMode == '%' and widths_str:
            self.ColumnWidths = widths_str.split(',')
        else:
            self.ColumnWidths = []
        
        # Initialize table
        self.table = [["" for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Read table data
        for row_elem in xblock.findall('Row'):
            row_idx = int(row_elem.get('index', '0'))
            for cell_elem in row_elem.findall('Cell'):
                col_idx = int(cell_elem.get('col', '0'))
                value = cell_elem.text if cell_elem.text else ""
                if row_idx < self.rows and col_idx < self.cols:
                    self.table[row_idx][col_idx] = value
        
        # Read alignment
        self.Alignment = xmlblock.GetField("Alignment", "Center")
        
            
    def GenLatex(self):
        """Generate LaTeX code for the table using tabular environment"""
        
        latexcontent = []
        
        # Create tabular environment with specified columns
        col_spec = "|" + "|".join(["c" for _ in range(self.cols)]) + "|"
        outText = "\\begin{tabular}{" + col_spec + "}\n"
        outText += "\\hline\n"
        
        for row_idx, row_data in enumerate(self.table):
            # Join cells with & and end row with \\
            row_text = " & ".join([str(cell) for cell in row_data])
            outText += row_text + " \\\\\n"
            outText += "\\hline\n"
        
        outText += "\\end{tabular}"
        
        latexcontent.append(outText)
        
        return latexcontent
    
    def escape_latex(self, text):
        """
        Escape special characters for LaTeX.
        """
        return text
        replacements = {
            '\\': r'\textbackslash{}',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text
