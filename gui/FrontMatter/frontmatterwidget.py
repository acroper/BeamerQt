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
from gui.LatexPreviewWidget import *
from core.beamerDocument import beamerDocument



class FrontMatterWidget(QtWidgets.QDialog):
    
    Selected = pyqtSignal()
    
    def __init__(self):
        
        super(FrontMatterWidget, self).__init__()
        
        uic.loadUi('gui/FrontMatter/FrontMatterWidget.ui', self)
        
        self.FrontMatter = frontMatter()
        self.latexPreview = LatexPreviewWidget(self)
        QVBoxLayout(self.previewFrame).addWidget(self.latexPreview)

        self.RefreshButton.clicked.connect(self.onPreview)
        self.Document = None
        self.prevDocument = None
        self._previewDir = None
        
        
    
    def SetFrontMatter(self, document):

        self.Document = document
        self.FrontMatter = self.Document.FrontMatter
        self.LoadElements()

        self.prevDocument = beamerDocument(self.Document.latexpreviewfolder)
        self.prevDocument.Template = self.Document.Template

        subslide = self.prevDocument.NewSlide()
        subslide.GetFromXML("gui/FrontMatter/preview.xml")

        # beamerDocument.Current = document   # restore original document

        # Adding virtual sections

        


    def onPreview(self):
        prevFrontMatter = frontMatter()

        # save configuration to the prevFrontMatter
        self.Save(prevFrontMatter)
        self.prevDocument.FrontMatter = prevFrontMatter

        tex_path = self.prevDocument.WriteLaTeX()

        self.latexPreview.SetTexFile(tex_path)
        self.latexPreview.Compile()

           
        

        
    
    def LoadElements(self):
        self.Title.setText(self.FrontMatter.Title)
        self.ShortTitle.setText(self.FrontMatter.ShortTitle)
        
        self.Subtitle.setText(self.FrontMatter.Subtitle)
        self.Authors.setPlainText(self.FrontMatter.Author)
        self.ShortAuthor.setText(self.FrontMatter.ShortAuthor)
        # self.Options.setPlainText(self.FrontMatter.Options)
        
        self.preambleText.setPlainText(self.FrontMatter.Preamble)
        
        self.Logo.setText(self.FrontMatter.LogoPath)
        self.Background.setText(self.FrontMatter.BackgroundPath)
        
        self.OutlineTitle.setText(self.FrontMatter.OutlineTitle)
        
        if self.FrontMatter.ShowSectionPage == "True":
            self.ShowSectionPage.setChecked(True)
            
        if self.FrontMatter.ShowSectionOutline == "True":
            self.ShowSectionOutline.setChecked(True)
        
        if self.FrontMatter.AspectRatio == "169":
            self.Aspect169.setChecked(True)

        if self.FrontMatter.EquationStyle == "Normal":
            self.EquationNormal.setChecked(True)
        elif self.FrontMatter.EquationStyle == "Professional":
            self.EquationPro.setChecked(True)

    def Save(self, FrontMatter = None):
        if FrontMatter == None:
            FrontMatter = self.FrontMatter

        FrontMatter.Title = self.Title.text()
        FrontMatter.ShortTitle = self.ShortTitle.text()
        FrontMatter.Subtitle = self.Subtitle.text()
        FrontMatter.Author = self.Authors.toPlainText()
        FrontMatter.ShortAuthor = self.ShortAuthor.text()
        # assign the logo locations
        # assign the background locations
        
        # self.FrontMatter.Options = self.Options.toPlainText()
        
        FrontMatter.Preamble = self.preambleText.toPlainText()
        
        FrontMatter.LogoPath = self.Logo.text()
        FrontMatter.BackgroundPath = self.Background.text()
        
        FrontMatter.OutlineTitle = self.OutlineTitle.text()
        
        if self.Aspect169.isChecked():
            FrontMatter.AspectRatio = "169"
        else:
            FrontMatter.AspectRatio = "43"
        
        if self.EquationNormal.isChecked():
            FrontMatter.EquationStyle = "Normal"   
        elif self.EquationPro.isChecked():
            FrontMatter.EquationStyle = "Professional"

        if self.ShowSectionPage.isChecked():
            FrontMatter.ShowSectionPage = "True"
        else:
            FrontMatter.ShowSectionPage = "False"
            
        if self.ShowSectionOutline.isChecked():
            FrontMatter.ShowSectionOutline = "True"
        else:
            FrontMatter.ShowSectionOutline = "False"
            
        
        # print(self.FrontMatter.Preamble)
        
        
        
        
        
        
