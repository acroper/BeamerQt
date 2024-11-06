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


from core.frontMatter import *




class FrontMatterWidget(QtWidgets.QDialog):
    
    Selected = pyqtSignal()
    
    def __init__(self):
        
        super(FrontMatterWidget, self).__init__()
        
        uic.loadUi('gui/FrontMatter/FrontMatterWidget.ui', self)
        
        self.FrontMatter = frontMatter()
        
    
    def SetFrontMatter(self, front):
        
        self.FrontMatter = front
        self.LoadElements()
    
    
    def LoadElements(self):
        self.Title.setText(self.FrontMatter.Title)
        self.Subtitle.setText(self.FrontMatter.Subtitle)
        self.Authors.setPlainText(self.FrontMatter.Author)
        self.Options.setPlainText(self.FrontMatter.Options)
        
        self.preambleText.setPlainText(self.FrontMatter.Preamble)
        
        self.Logo.setText(self.FrontMatter.LogoPath)
        self.Background.setText(self.FrontMatter.BackgroundPath)
        
        
    def Save(self):
        self.FrontMatter.Title = self.Title.text()
        self.FrontMatter.Subtitle = self.Subtitle.text()
        self.FrontMatter.Author = self.Authors.toPlainText()
        
        # assign the logo locations
        # assign the background locations
        
        self.FrontMatter.Options = self.Options.toPlainText()
        
        self.FrontMatter.Preamble = self.preambleText.toPlainText()
        
        self.FrontMatter.LogoPath = self.Logo.text()
        self.FrontMatter.BackgroundPath = self.Background.text()
        
        # print(self.FrontMatter.Preamble)
        
        
        
        
        
        
