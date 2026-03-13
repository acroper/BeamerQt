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
from PyQt6.QtGui import QPixmap, QImage, QIcon

from gui.ContentItems.EquationQT.EquationEditorDialog import EquationEditorDialog

import xml.etree.ElementTree as ET

from core.xmlutils import *


def render_latex_to_pixmap(latex_code, dpi=150):
    """Render LaTeX equation to QPixmap using pdflatex and PyMuPDF."""
    # Minimal: return None to show text instead
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
        self.Refresh()

    def GetInnerObject(self):
        return self.InnerObject

    def SetInnerObject(self, inner):
        self.InnerObject = inner
        self.Refresh()

    def Refresh(self):
        latex = self.InnerObject.Latex
        if latex.strip():
            pixmap = render_latex_to_pixmap(latex)
            if pixmap:
                # Scale to fit
                scaled = pixmap.scaled(self.previewButton.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
                self.previewButton.setIcon(QIcon(scaled))
                self.previewButton.setText("")
            else:
                self.previewButton.setText(f"LaTeX: {latex}")
                self.previewButton.setIcon(QIcon())
        else:
            self.previewButton.setText("y=x^2")
            self.previewButton.setIcon(QIcon())


class itemEquationQT():

    def __init__(self):
        self.Type = "EquationQT"
        self.Latex = "y=x^2"
        self.Alignment = "Center"

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