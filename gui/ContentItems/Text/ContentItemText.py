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

import xml.etree.ElementTree as ET

from core.xmlutils import *


class itemWidgetText(QtWidgets.QWidget):
    
    def __init__(self):
        
        super(itemWidgetText, self).__init__()
        
        uic.loadUi('gui/ContentItems/Text/ItemText.ui', self)
        
        self.InnerObject = itemText()

        
        
    def GetInnerObject(self):
        self.InnerObject.Text = self.TextEditor.toPlainText()
        return self.InnerObject
    
    def SetInnerObject(self, inner):
        self.InnerObject = inner
        self.Refresh()
        
    def Refresh(self):
        self.TextEditor.setText(self.InnerObject.Text)
        

        
class itemText():
    
    def __init__(self):
        
        self.Type = "Text"
        
        self.Text = ""
        
        self.Alignment = "Left"
        
    
    def GetXMLContent(self):
        
        
        ContentXML = ET.Element('ItemWidget', ItemType='Text')
        
        ContentXML.text = self.Text
        
        Alignment = ET.SubElement(ContentXML, "Alignment")
        Alignment.text = self.Alignment
        
        
        
        return ContentXML
        
        
        
    def ReadXMLContent(self, xblock):
        
        xmlblock = xmlutils(xblock)
        
        self.Text = xblock.text
        
        self.Alignment = xmlblock.GetField("Alignment", "Left")
        
        
    def GenLatex(self):
        
        latexcontent = []
        
        outText = self.Text
        
        try:
            outText = self.Text.replace("\n", "\\"+"\\ \n")
        except:
            outText = " "
            
        # latexcontent.append(self.Text)
        latexcontent.append(outText)
        
        return latexcontent
        
        
    
        
        