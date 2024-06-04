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
from gui.contentitem import *


class ContentWidget(QtWidgets.QWidget):
    
    Selected = pyqtSignal()
    
    def __init__(self):
        
        super(ContentWidget, self).__init__()
        
        uic.loadUi('gui/ContentWidget.ui', self)
        
        self.nombre = "None"
        
        self.ClickSelected = False
        
        self.ColumnNumber = -1
        
        self.WidgetList = []
        
        # self.WidgetList.append(self.blockText)
        
        self.SetActions()
        
        self.Block = BeamerBlock()
        
        self.moveDirection = ""
        
        self.AddWidgetItem("Text")
        
       

        
    
    def SetActions(self):
        self.mUp.clicked.connect(lambda: self.setMoveBlock("up"))
        self.mDown.clicked.connect(lambda: self.setMoveBlock("down"))
        self.mLeft.clicked.connect(lambda: self.setMoveBlock("left"))
        self.mRight.clicked.connect(lambda: self.setMoveBlock("right"))
        
        self.addTextButton.clicked.connect(lambda: self.AddWidgetItem("Text"))
        
        self.addImageButton.clicked.connect(lambda: self.AddWidgetItem("Image"))
        
        self.maxCols.valueChanged.connect(self.RefreshItemList)
        
    

    
    
    def AddWidgetItem(self, itemtype):
        # add a content item
        
        cItem = ContentItem()
        self.WidgetList.append(cItem)
        cItem.setItemType(itemtype)
        cItem.Activated.connect(self.ActivatedItem)
        
        self.RefreshItemList()
        
        return cItem
        
    
    def RefreshItemList(self):
        # Remove all items from the gridlayout, and relocate them
        for i in reversed(range(self.gridLayout.count())):
            tmpwidget = self.gridLayout.itemAt(i)
            self.gridLayout.removeItem(tmpwidget)
            # tmpwidget.widget().hide()
            
        maxcols = self.maxCols.value()
        
        LastCol = 0
        LastRow = 0
        
        for cItem in self.WidgetList:
        
            if LastCol == maxcols:
                LastCol = 0
                LastRow += 1
            self.gridLayout.addWidget(cItem, LastRow, LastCol)
            
            LastCol += 1
        
        
        
    
    
    def ActivatedItem(self):
        selected = self.sender()
        action = selected.CurrentAction
        selected.CurrentAction = "" # Delete action
        
        index = self.WidgetList.index(selected)
        
        if action == "delete":
            self.WidgetList.pop(index)
            
            if len(self.WidgetList) == 0:  # failsafe
                self.AddWidgetItem("Text")
            
            
            self.RefreshItemList()
            
        
        if action == "prev" and index > 0:
            self.WidgetList.pop(index)
            self.WidgetList.insert(index-1, selected)
            self.RefreshItemList()
            
        if action == "next" and index < len(self.WidgetList) :
            self.WidgetList.pop(index)
            self.WidgetList.insert(index+1,selected)
            self.RefreshItemList()
            
        print(action)
            
        
        
        
    
    
    def setMoveBlock(self, direction):
        self.moveDirection = direction
        
        self.ClickSelected = True
        self.Selected.emit()
        
    
    
    def ReadBlock(self, outBlock):
        self.Block = outBlock
        
        self.blockTitle.setText(self.Block.Title)
        
        # self.blockText.setPlainText(self.Block.Text)
        
        self.ColumnNumber = self.Block.ColumnNumber
        
        self.nombre = self.Block.nombre
                
        self.maxCols.setValue(self.Block.ColumnCount)
        
        self.WidgetList.clear()
        
        for subblock in self.Block.SubBlocks:
          
            itemtype = subblock.Type
            cItem = self.AddWidgetItem(itemtype)
            cItem.SetInnerObject(subblock)
               
                
        
    
    def UpdateBlock(self):
        self.Block.Title = self.blockTitle.text()
        # self.Block.Text = self.blockText.toPlainText()
        self.Block.ColumnNumber = self.ColumnNumber
        
        self.Block.ColumnCount = self.maxCols.value()
        
        self.Block.SubBlocks.clear()
        
        
        
        for subblock in self.WidgetList:
            self.Block.SubBlocks.append( subblock.GetInnerObject() )
            
    
    
    
    def GetXMLContent(self):
        ContentXML = ET.Element('Block', id='block_'+self.nombre)
        BlockTitle = ET.SubElement(ContentXML, 'BlockTitle')
        BlockTitle.text = self.blockTitle.text()
        
        ColsCount = ET.SubElement(ContentXML, 'ColumnCount')
        ColsCount.text = str(self.maxCols.value())  
        
        
        # BlockText = ET.SubElement(ContentXML, 'BlockText')
        # BlockText.text = self.blockText.toPlainText()
        
        
        
        return ContentXML
    
    def ReadXMLContent(self, xblock):
        
        self.blockTitle.setText( xblock.findall('BlockTitle')[0].text  ) 
        self.maxCols.setValue( int( xblock.findall('ColumnCount')[0].text  )  )
        


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
        
