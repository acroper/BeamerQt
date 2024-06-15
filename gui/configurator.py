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



from PyQt6 import QtWidgets, uic, QtCore, QtGui
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, QObject

from core.template import *


class ConfiguratorWidget(QtWidgets.QWidget):
    
    def __init__(self):
        
        super(ConfiguratorWidget, self).__init__()
        
        uic.loadUi('gui/Configurator.ui', self)
        
        self.SelectedBlock = None
        
        self.LeftColumnValue = 100
        
        self.ThemeList = []
        
        self.LoadActions()
        
        self.RefreshThemeList()
        
        self.Document = None
        
        
                      
        # self.show()
        
        
    def SetDocument(self, documento):
        self.Document = documento
        
        # Check template
        tempName = self.Document.Template.Name
        
        self.themeBox.setCurrentText(tempName)
        
    
    def UpdateTheme(self):
        
        index = self.themeBox.currentIndex()
        self.Document.Template = self.ThemeList[index]
        
        
        
    
    def RefreshThemeList(self):
        
        # check in template folder
        filelist = os.listdir("templates")
        for file in filelist:
            if file.endswith("xml"):
                filename = os.path.join("templates", file  )
                
                if os.path.exists(filename):
                    
                    print("Opening file " + filename)
                    
                
                    templ = BeamerTemplate()
                    templ.ReadXMLFile( filename )
                    self.themeBox.addItem(templ.Name)
                    self.ThemeList.append(templ)
                    
        
        self.themeBox.currentIndexChanged.connect(self.UpdateTheme)
            
            
        
    
    def ConnectFrame(self, NewFrame):
        self.CurrentFrame = NewFrame
        
        self.CurrentFrame.BlockSelected.connect(self.SelectBlock)
        
        self.CurrentFrame.Updated.connect(self.Refresh)
        
        
        # Actions for reposition the blocks. The signals will be sent to
        # the Frame directly
        self.Left.clicked.connect(self.CurrentFrame.MoveLeft)
        self.Right.clicked.connect(self.CurrentFrame.MoveRight)
        self.Up.clicked.connect(self.CurrentFrame.MoveUp)
        self.Down.clicked.connect(self.CurrentFrame.MoveDown)
        
        
        
    
    def SelectBlock(self):
        self.SelectedBlock = self.CurrentFrame.SelectedBlock
        self.blockLayout.setVisible(True)
        
        # self.toolBox.setCurrentIndex(2)
    def UnSelectBlock(self):
        self.blockLayout.setVisible(False)
    
    
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
        self.layout_restore.toggled.connect(self.restoreLayout)
        
        self.LeftColumnSize.valueChanged.connect(self.UpdateLeftColumn)
        # self.RightColumnSize.valueChanged.connect(self.UpdateRightColumn)
        
        
        
    
    def UpdateLeftColumn(self):
                
        self.LeftColumnValue = self.LeftColumnSize.value()
        self.RightColumnText.setText( str(100-self.LeftColumnValue)  )
        # self.RightColumnSize.setValue(100-self.LeftColumnValue)
        
        
        if self.CurrentFrame.LeftColumnProportion != self.LeftColumnValue:
            self.CurrentFrame.LeftColumnProportion = self.LeftColumnValue
            self.CurrentFrame.updateColumnSize()


    def UpdateRightColumn(self):
        
        self.LeftColumnValue = 100 - self.RightColumnSize.value()
        self.LeftColumnSize.setValue(self.LeftColumnValue)   
        self.CurrentFrame.LeftColumnProportion = self.LeftColumnValue
        # self.CurrentFrame.updateColumnSize()

        
    
    
    
    def restoreLayout(self):
        if self.CurrentFrame.Updating == False and self.layout_restore.isChecked() :
            button = QMessageBox.question(self, "Reset layout", "This will remove all blocks. \n\nContinue?")
            if button == QMessageBox.StandardButton.Yes:
                self.layoutchange("layout_restore")
            
            self.Refresh()
    
        
    def titlechange(self):
        self.CurrentFrame.config_title(self.show_title.isChecked())

        
    def subtitlechange(self):
        None
        
    def layoutchange(self, option):
        self.CurrentFrame.config_Layout(option)
        
    def Refresh(self):
        # recheck the layout button
        
        self.CurrentFrame.Updating = True
        
        layoutstyle = self.CurrentFrame.CurrentLayout
        
        if layoutstyle == "layout_standard":
            self.layout_standard.setChecked(True)
            
        if layoutstyle == "layout_2cols":
            self.layout_2cols.setChecked(True)
            
        if layoutstyle == "layout_2rows":
            self.layout_2rows.setChecked(True)
            
        if layoutstyle == "layout_1col2rows":
            self.layout_1col2rows.setChecked(True)
            
        if layoutstyle == "layout_2rows1col":
            self.layout_2rows1col.setChecked(True)
            
        if layoutstyle == "layout_4blocks":
            self.layout_4blocks.setChecked(True)
        
        if layoutstyle == "layout_title":
            self.layout_title.setChecked(True)
            
        if layoutstyle == "Custom":
            self.layout_restore.setChecked(True)
            # self.layout_restore.setChecked(False)
            
        self.CurrentFrame.Updating = False
        
        self.UnSelectBlock()
        
        self.LeftColumnSize.setValue(self.CurrentFrame.LeftColumnProportion)
        
        
    

        
        
            
            
        
        
        
    
    

