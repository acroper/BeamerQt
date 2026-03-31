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
import os

from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QPixmap, QImage, QIcon, QPainter, QPalette

from gui.ContentItems.EquationQT.EquationEditorDialog import EquationEditorDialog
from gui.ContentItems.EquationQT.math_editor import EquationEditor

import xml.etree.ElementTree as ET

from core.xmlutils import *


def render_latex_to_pixmap(latex_code):
    """Render LaTeX equation to QPixmap using EquationEditor."""
    if not latex_code.strip():
        return None

    print(f"Rendering LaTeX: {latex_code}")
    try:
        # Create off-screen equation editor
        editor = EquationEditor()
        editor.load_from_latex(latex_code)
        palette = editor.palette()
        
        # Layout the equation
        editor.root_row.layout(editor.font)
        
        # Set size based on equation bounds
        width = int(editor.root_row.width) + 20  # Add some padding
        height = int(editor.root_row.height) + 20
        print(f"Pixmap size: {width}x{height}")
        if width <= 20 or height <= 20:
            print("Empty equation")
            return None  # Empty equation
        
        # Create pixmap and render
        pixmap = QPixmap(width, height)
        pixmap.fill(palette.color(QPalette.ColorRole.Base))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(editor.font)
        painter.setPen(palette.color(QPalette.ColorRole.Text))
        
        # Center the equation vertically
        start_y = (height - editor.root_row.height) // 2
        editor.root_row.draw(painter, 10, start_y)
        painter.end()
        
        print("Rendering successful")
        return pixmap
    except Exception as e:
        print(f"Error rendering equation: {e}")
        return None


class itemWidgetEquationQT(QtWidgets.QWidget):

    def __init__(self):
        super(itemWidgetEquationQT, self).__init__()

        uic.loadUi('gui/ContentItems/EquationQT/ItemEquationQT.ui', self)

        self.InnerObject = itemEquationQT()

        self.previewButton.clicked.connect(self.showEquationDialog)
        
        self.Refresh()

    def showEquationDialog(self, event):
        dialog = EquationEditorDialog(self.InnerObject.Latex)
        dialog.equation_accepted.connect(self.on_equation_accepted)
        dialog.exec()

    def on_equation_accepted(self, latex):
        self.InnerObject.Latex = latex
        self.InnerObject.pixmap = None  # Clear cache
        self.Refresh()

    def GetInnerObject(self):
        return self.InnerObject

    def SetInnerObject(self, inner):
        self.InnerObject = inner
        self.Refresh()

    def Refresh(self):
        latex = self.InnerObject.Latex
        if latex.strip():
            # Use cached pixmap or generate new one
            if self.InnerObject.pixmap is None:
                self.InnerObject.pixmap = render_latex_to_pixmap(latex)
            
            if self.InnerObject.pixmap:
                # Scale to a larger size for better preview
                preview_size = QtCore.QSize(200, 150)  # Larger preview size
                scaled = self.InnerObject.pixmap.scaled(preview_size, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
                self.previewButton.setIcon(QIcon(scaled))
                self.previewButton.setIconSize(scaled.size())
                self.previewButton.setText("")
            else:
                self.previewButton.setText(f"LaTeX: {latex}")
                self.previewButton.setIcon(QIcon())
        else:
            self.previewButton.setText("Click to edit equation")
            self.previewButton.setIcon(QIcon())
            self.InnerObject.pixmap = None  # Clear cache


class itemEquationQT():

    def __init__(self):
        self.Type = "EquationQT"
        self.Latex = "y=x^2"
        self.Alignment = "Center"
        self.pixmap = None  # Cached pixmap

    def GetXMLContent(self):
        ContentXML = ET.Element('ItemWidget', ItemType='EquationQT')
        ContentXML.text = self.Latex
        Alignment = ET.SubElement(ContentXML, "Alignment")
        Alignment.text = self.Alignment
        return ContentXML

    def ReadXMLContent(self, xblock):
        xmlblock = xmlutils(xblock)
        self.Latex = xblock.text or ""
        self.Alignment = xmlblock.GetField("Alignment", "Center")
        
    def GenLatex(self):
        latex = []
        if self.Latex.strip():
            latex.append("\\[" + self.Latex + "\\]")
        return latex
