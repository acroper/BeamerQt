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

import importlib


class ContentItem(QtWidgets.QWidget):
    
    Activated = pyqtSignal()
    
    def __init__(self):
        
        super(ContentItem, self).__init__()
        
        uic.loadUi('gui/ContentItem.ui', self)
        
        self.ItemType = "Text"
        
        self.CurrentAction = ""
        
        self.SetActions()
        

    def SetActions(self):
        
        self.prevBtn.clicked.connect(lambda: self.SetOption("prev"))
        self.nextBtn.clicked.connect(lambda: self.SetOption("next"))
        self.deleteBtn.clicked.connect(lambda: self.SetOption("delete"))
        
    
    def SetOption(self, option):
        self.CurrentAction = option
        self.Activated.emit()
        
        
        
    
    def setItemType(self, itemtype):
        # search the itemtype
        
        typeloc = 'gui.ContentItems.'+itemtype+ ".ContentItem"+itemtype
        
        
        module = importlib.import_module(typeloc)
        my_class = getattr(module, "itemWidget" + itemtype )
        my_instance = my_class()
        
        self.Layout.addWidget(my_instance)
        
        

        

        
    
    
        
