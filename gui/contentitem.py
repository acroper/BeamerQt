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
from PyQt6.QtGui import QClipboard


import xml.etree.ElementTree as ET

from core.beamerBlock import *

import importlib


class ContentItem(QtWidgets.QWidget):
    
    Activated = pyqtSignal()
    
    def __init__(self):
        
        super(ContentItem, self).__init__()
        
        uic.loadUi('gui/ContentItem2.ui', self)
        
        self.ItemType = "Text"
        
        self.CurrentAction = ""
        
        self.InnerWidget = None
        
        self.SetActions()
        
        self.Alignment = "Default"
        
        self.Aligning = False
        

    def SetActions(self):
        
        self.prevBtn.clicked.connect(lambda: self.SetOption("prev"))
        self.nextBtn.clicked.connect(lambda: self.SetOption("next"))
        self.deleteBtn.clicked.connect(lambda: self.SetOption("delete"))
        
        self.AlignLeftBtn.clicked.connect(lambda: self.SetAlignment("Left"))
        self.AlignRightBtn.clicked.connect(lambda: self.SetAlignment("Right"))
        self.AlignCenterBtn.clicked.connect(lambda: self.SetAlignment("Center"))
        self.AlignDefaultBtn.clicked.connect(lambda: self.SetAlignment("Default"))
        
        toct = QWidgetAction(self)
        toct.setDefaultWidget(self.ButtonsWidget)
        self.opcButton.addAction(toct)
        
        
        
        
    def SetAlignment(self, option):
        self.Alignment = option
        
        if self.Aligning == False:
            self.CheckAlignment()
    
    
    def CheckAlignment(self):
        self.Aligning = True
        
        self.AlignCenterBtn.setChecked(False)
        self.AlignLeftBtn.setChecked(False)
        self.AlignRightBtn.setChecked(False)
        self.AlignDefaultBtn.setChecked(False)
        
        
        if self.Alignment == "Center":
            self.AlignCenterBtn.setChecked(True)
            self.opcButton.setIcon(self.AlignCenterBtn.icon())
        
        if self.Alignment == "Left":
            self.AlignLeftBtn.setChecked(True)
            self.opcButton.setIcon(self.AlignLeftBtn.icon())
        
        if self.Alignment == "Right":
            self.AlignRightBtn.setChecked(True)
            self.opcButton.setIcon(self.AlignRightBtn.icon())
        
        if self.Alignment == "Default":
            self.AlignDefaultBtn.setChecked(True)
            self.opcButton.setIcon(self.AlignDefaultBtn.icon())
        
        self.InnerWidget.GetInnerObject().Alignment = self.Alignment    
        
        self.Aligning = False
        
        
        
        

        
    
        
        
    
    def SetOption(self, option):
        self.CurrentAction = option
        self.Activated.emit()
        
        
        
    
    def setItemType(self, itemtype):
        # search the itemtype
        
        typeloc = 'gui.ContentItems.'+itemtype+ ".ContentItem"+itemtype
        
        
        module = importlib.import_module(typeloc)
        itemClass = getattr(module, "itemWidget" + itemtype )
        Item = itemClass()
        
        Item.ContentItem = self
        
        self.Layout.addWidget(Item)
        
        self.InnerWidget = Item
        
        
        
        
    def GetInnerObject(self):
        
        return self.InnerWidget.GetInnerObject()
    
    def SetInnerObject(self, obj):
        
        self.InnerWidget.SetInnerObject(obj)
        
        self.Alignment = self.InnerWidget.GetInnerObject().Alignment
        
        # print(self.Alignment)
        
        self.Aligning = False
        
        self.CheckAlignment()
        
        
        

        

        
    
    
        
