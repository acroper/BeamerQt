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


class ConfiguratorWidget(QtWidgets.QWidget):
    
    def __init__(self):
        
        super(ConfiguratorWidget, self).__init__()
        
        uic.loadUi('gui/Configurator2.ui', self)
        
        self.SelectedBlock = None
        
        self.LoadActions()
                      
        # self.show()
        
    def ConnectFrame(self, NewFrame):
        self.CurrentFrame = NewFrame
        
        self.CurrentFrame.BlockSelected.connect(self.SelectBlock)
        
        
        # Actions for reposition the blocks. The signals will be sent to
        # the Frame directly
        self.Left.clicked.connect(self.CurrentFrame.MoveLeft)
        self.Right.clicked.connect(self.CurrentFrame.MoveRight)
        self.Up.clicked.connect(self.CurrentFrame.MoveUp)
        self.Down.clicked.connect(self.CurrentFrame.MoveDown)
        
        
        
    
    def SelectBlock(self):
        self.SelectedBlock = self.CurrentFrame.SelectedBlock
        
        self.toolBox.setCurrentIndex(2)
    
    
    def LoadActions(self):
        # Most actions are passed directly to the Frame object
        self.show_title.stateChanged.connect(self.titlechange)
        self.show_subtitle.stateChanged.connect(self.subtitlechange)
        
        self.layout_standard.toggled.connect(lambda: self.layoutchange("layout_standard"))
        self.layout_2cols.toggled.connect(lambda: self.layoutchange("layout_2cols"))
        self.layout_2rows.toggled.connect(lambda: self.layoutchange("layout_2rows"))
        self.layout_1col2rows.toggled.connect(lambda: self.layoutchange("layout_1col2rows"))
        self.layout_2rows1col.toggled.connect(lambda: self.layoutchange("layout_2rows1col"))
        self.layout_4blocks.toggled.connect(lambda: self.layoutchange("layout_4blocks"))
        self.layout_title.toggled.connect(lambda: self.layoutchange("layout_title"))
        
        
        
        
        
        
        
        
    def titlechange(self):
        self.CurrentFrame.config_title(self.show_title.isChecked())

        
    def subtitlechange(self):
        None
        
    def layoutchange(self, option):
        self.CurrentFrame.config_Layout(option)
        
    
    

