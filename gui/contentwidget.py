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

from core.beamerBlock import *


class ContentWidget(QtWidgets.QWidget):
    
    Selected = pyqtSignal()
    
    def __init__(self):
        
        super(ContentWidget, self).__init__()
        
        uic.loadUi('gui/ContentWidget.ui', self)
        
        self.nombre = "None"
        
        self.ClickSelected = False
        
        self.ColumnNumber = -1
        
        self.Block = BeamerBlock()

        
    
    def ReadBlock(self, outBlock):
        self.Block = outBlock
        
        self.blockTitle.setText(self.Block.Title)
        
        self.blockText.setPlainText(self.Block.Text)
        
        self.ColumnNumber = self.Block.ColumnNumber
        
        self.nombre = self.Block.nombre
        
    
    def UpdateBlock(self):
        self.Block.Title = self.blockTitle.text()
        self.Block.Text = self.blockText.toPlainText()
        self.Block.ColumnNumber = self.ColumnNumber
    
    
    
    def GetXMLContent(self):
        ContentXML = ET.Element('Block', id='block_'+self.nombre)
        BlockTitle = ET.SubElement(ContentXML, 'BlockTitle')
        BlockTitle.text = self.blockTitle.text()
        
        BlockText = ET.SubElement(ContentXML, 'BlockText')
        BlockText.text = self.blockText.toPlainText()
        
        return ContentXML
    
    def ReadXMLContent(self, xblock):
        
        self.blockTitle.setText( xblock.findall('BlockTitle')[0].text  ) 
        self.blockText.setPlainText( xblock.findall('BlockText')[0].text  )
        


    def mousePressEvent(self, event):
        print("Selected " + self.nombre)
        self.ClickSelected = True
        self.Selected.emit()
        
    
    
    def setSelected(self):
        self.frame.setLineWidth(3)

    
    def unSelected(self):
        self.frame.setLineWidth(1)
        
                      
        # self.show()
    def setContentName(self, text):
        self.nombre = text
        self.content_name.setText(text)
        
