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

from gui.DualSlider import *

from core.xmlutils import *


class ContentWidget(QtWidgets.QWidget):
    
    Selected = pyqtSignal()
    
    SetDelete = pyqtSignal()
    
    def __init__(self):
        
        super(ContentWidget, self).__init__()
        
        uic.loadUi('gui/ContentWidget.ui', self)
        
        self.nombre = "None"
        
        self.ClickSelected = False
        
        self.ColumnNumber = -1
        
        self.GUIWaiting = 0
        
        self.WidgetList = []
        
        # self.WidgetList.append(self.blockText)
        
        self.BarSlider = DualSlider()
        self.FrameBarLayout.addWidget(self.BarSlider)
        self.ColumnProportions = [100, 100, 100, 100]
        self.BarSlider.Minimum = 10
        self.BarSlider.Maximum = 90
        self.BarSlider.NextRounding = 1
        self.BarSlider.LabelPosition = "Right"
        
        self.SetActions()
        
        self.Block = BeamerBlock()
        
        self.moveDirection = ""
        
        self.BlockType = "Normal"
        
        self.AddWidgetItem("RTF")
        
        self.maxCols.setValue(2)
        
        self.updateColors()
        
        
        
        
        
        
        
       

        
    
    def SetActions(self):
        self.mUp.clicked.connect(lambda: self.setMoveBlock("up"))
        self.mDown.clicked.connect(lambda: self.setMoveBlock("down"))
        self.mLeft.clicked.connect(lambda: self.setMoveBlock("left"))
        self.mRight.clicked.connect(lambda: self.setMoveBlock("right"))
        
        self.addTextButton.clicked.connect(lambda: self.AddWidgetItem("Text"))
        
        self.addImageButton.clicked.connect(lambda: self.AddWidgetItem("Image"))
        
        self.addRTF.clicked.connect(lambda: self.AddWidgetItem("RTF"))
        
        self.maxCols.valueChanged.connect(self.RefreshItemList)
        
        self.BlockNormal.clicked.connect(lambda: self.SetBlockType("Normal"))
        
        self.BlockExample.clicked.connect(lambda: self.SetBlockType("Example"))
        
        self.BlockAlert.clicked.connect(lambda: self.SetBlockType("Alert"))
        
        self.BlockSimple.clicked.connect(lambda: self.SetBlockType("Simple"))
        
        self.deleteBlockBtn.clicked.connect(self.DeleteBlock)
        
        self.BarSlider.ValueUpdated.connect(self.BarSliderUpdated)
        
        self.BarSlider.Released.connect(self.BarSliderReleased)
        
    

    def DeleteBlock(self):
        print("Deleting block")
        self.SetDelete.emit()
    
    def SetBlockType(self, blocktype):
        self.BlockType = blocktype
        self.updateColors()
        
        
    def updateColors(self):
        
        # update intensity
        low = 230
        high = 255
        
        if os.name != 'posix':
            low = 190
        
        
        blocktype = self.BlockType
        
        if blocktype == "Simple":
            self.setStyleSheet('border-color: rgb(0, 0, 0); \nbackground-color: rgb({}, {} ,{} );'.format(high, high, high)   )
        if blocktype == "Normal":    
            self.setStyleSheet('border-color: rgb(0, 0, 0); \nbackground-color: rgb({}, {} ,{} );'.format(low, low, high)   )
        if blocktype == "Alert":    
            self.setStyleSheet('border-color: rgb(0, 0, 0); \nbackground-color: rgb({}, {} ,{} );'.format(high, low, low)   )
        if blocktype == "Example":    
            self.setStyleSheet('border-color: rgb(0, 0, 0); \nbackground-color: rgb({}, {} ,{} );'.format(low, high, low)   )
    
    
    
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
        
        self.UpdateDualSlider()
        
    
    def FixProportions(self):
        
        controls = min(self.maxCols.value(), len(self.WidgetList))
        #Column proportions must be equal to 100*controls
        Total = 0
        
        # print("Before", self.ColumnProportions)
        
        for k in range(controls ):
            Total = Total + self.ColumnProportions[k]
        
        diff = 100*controls - Total
        
        if diff > 100:
            self.ColumnProportions[k] -= diff
        else:
            self.ColumnProportions[k] += diff
            
            
        # print("After", self.ColumnProportions)
        # print(diff)
    
    
    def updateColumnSize(self):
        
        self.FixProportions()
        
        controls = min(self.maxCols.value(), len(self.WidgetList))
        
        self.TotalSize = self.width()
        LastCol = 0
        
        maxcols = self.maxCols.value()
        # print("--------")
        
        for cItem in self.WidgetList:
            
            proportion = self.ColumnProportions[LastCol]/controls
            
            cItem.setMinimumWidth(int(  proportion*self.TotalSize/100 ) )
            cItem.setMaximumWidth(int(  proportion*self.TotalSize/100 ) )
            
            # print(proportion, LastCol)
            
            LastCol += 1
        
            if LastCol == maxcols:
                LastCol = 0
        
        self.Block.ColumnProportions = self.ColumnProportions
            
            
        
    
        
    def UpdateDualSlider(self):
        controls = min(self.maxCols.value(), len(self.WidgetList))
        self.BarSlider.setSliders(controls - 1)
        
        # Initial values, next, I need to assign them from a list
        values = []
        current = 0
        for cproportion in self.ColumnProportions:
            current = cproportion+current
            values.append(current/controls)
            
        # print(values)
        self.BarSlider.UpdateValues( values  )
        
        
    def BarSliderReleased(self):
        self.GUIWaiting = 0
        # print("Released!")
    
    
    def BarSliderUpdated(self):
        # take the values from BarSlider
        values = [self.BarSlider.value1, self.BarSlider.value2, self.BarSlider.value3]
        
        controls = min(self.maxCols.value(), len(self.WidgetList))
        
        proportions = []
        
        current = 0
        
        for val in values:
            cproportion = (val - current)*controls
            current = val
            proportions.append(cproportion)
            
        
        
        remain = (100-val)*controls
        proportions.append(remain)
            
        self.ColumnProportions = proportions
        
        # Wait 10 repetitions before resizing the columns
        
        if self.GUIWaiting == 0:
            self.updateColumnSize()
        
        self.GUIWaiting+= 1
        
        if self.GUIWaiting == 10:
            self.GUIWaiting = 0
        
            
        
        
        
    
    
    def ActivatedItem(self):
        selected = self.sender()
        action = selected.CurrentAction
        selected.CurrentAction = "" # Delete action
        
        index = self.WidgetList.index(selected)
        
        if action == "delete":
            self.WidgetList.pop(index)

            if len(self.WidgetList) == 0:  # failsafe
                self.AddWidgetItem("Text")
                
            selected.hide()
            
            selected.deleteLater()
            
            
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
        
        self.ColumnProportions = self.Block.ColumnProportions
        
        self.nombre = self.Block.nombre
                
        self.maxCols.setValue(self.Block.ColumnCount)
        
        self.WidgetList.clear()
        
        self.BlockType = self.Block.BlockType
        
        # update the marker
        if self.BlockType == "Normal":
            self.BlockNormal.setChecked(True)
            
        if self.BlockType == "Example":
            self.BlockExample.setChecked(True)
            
        if self.BlockType == "Alert":
            self.BlockAlert.setChecked(True)
            
        if self.BlockType == "Simple":
            self.BlockSimple.setChecked(True)
        
        self.updateColors()
        
        for subblock in self.Block.SubBlocks:
          
            itemtype = subblock.Type
            cItem = self.AddWidgetItem(itemtype)
            cItem.SetInnerObject(subblock)
               
                
        
    
    def UpdateBlock(self):
        self.Block.Title = self.blockTitle.text()
        # self.Block.Text = self.blockText.toPlainText()
        self.Block.ColumnNumber = self.ColumnNumber
        
        self.Block.ColumnCount = self.maxCols.value()
        
        self.FixProportions()
        
        self.Block.ColumnProportions = self.ColumnProportions
        
        self.Block.SubBlocks.clear()
        
        self.Block.BlockType = self.BlockType
        
        
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
        return
        self.frame.setLineWidth(3)

    
    def unSelected(self):
        return
        self.frame.setLineWidth(1)
        
                      
        # self.show()
    def setContentName(self, text):
        self.nombre = text
        self.content_name.setText(text)
        
