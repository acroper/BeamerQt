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
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize

from core.template import *

from gui.PreviewPDF import *


class ThemePreview(QtWidgets.QWidget):
    
    Selected = pyqtSignal()
    
    def __init__(self):
        
        super(ThemePreview, self).__init__()
        
        uic.loadUi('gui/ThemePreview.ui', self)
        
        self.List = []
        
        self.ItemsWithoutPreview = []
        
        self.WorkDirectory = None
        
  
        self.ThemeList.setIconSize(QSize(90, 90))

        self.model = QStandardItemModel()
        self.ThemeList.setModel(self.model)
        
        self.PrevWindow = PreviewPDF()
        
        self.PreviewLayout.addWidget(self.PrevWindow)
        # self.verticalLayout.addWidget(self.ThemeList)
        
        self.ThemeList.clicked.connect(self.ChangeSelection)
        
        self.genPDFButton.clicked.connect(self.genPDFPreview)
        
        self.SelectedTheme = None
        
        self.ProcessingReview = False
        
        QtCore.QTimer.singleShot(1000, self.reviewPreviews)


    def reviewPreviews(self):
        
        print("\n############# Starting review of Previews #################")
        
        print("Size:")
        print(len(self.ItemsWithoutPreview))
        
        if len (self.ItemsWithoutPreview) == 0:
            return

        item = self.ItemsWithoutPreview[0]
        template = item.Template
        
        if self.ProcessingReview:
            # Already asked to generate the PDF
            print("Getting preview PDF")
            print(template.Name)
            
            template.PreviewPDF = None
            
            path = template.GetPreviewPDF()
            
            print(path)
            
            if template.ValidPDF:
                item.setIcon(QIcon(template.Preview))
                self.ItemsWithoutPreview.pop(0)
                self.ProcessingReview = False
                print("Pass")
            else:
                print("Didn't pass")
        
        else:
            print("Starting other slide")
            template.GenPreviewFile(self.WorkDirectory)
            self.ProcessingReview = True
        
        QtCore.QTimer.singleShot(1000, self.reviewPreviews)
                
                
            
            
        
        

        
    
    def genPDFPreview(self):
        if self.SelectedTheme == None:
            return
        self.SelectedTheme.GenPreviewFile(self.WorkDirectory)
    
        
    def ChangeSelection(self):
        index = self.ThemeList.selectionModel().selectedIndexes()[0]
        item = self.model.itemFromIndex(index)
        template = item.Template
        
        self.SelectedTheme = template
        
        pdfpath = template.GetPreviewPDF()
        template.GetPreview()
        item.setIcon(QIcon(template.Preview))
        
        print("Changing icon:")
        print(template.Preview)
        
        self.PrevWindow.ShowPDF(pdfpath)
        
        self.Selected.emit()
        
        



    def RefreshThemeList(self):
        
        # check in template folder
        filelist = os.listdir("templates")
        
        filelist.sort()
        
        
        for file in filelist:
            if file.endswith("xml"):
                filename = os.path.join("templates", file  )
                
                if os.path.exists(filename):
                    
                    # print("Opening file " + filename)

                    templ = BeamerTemplate()
                    templ.ReadXMLFile( filename )
                    templ.GetPreview()
                    
                    self.List.append(templ)
                    self.AddItemList(templ)
                    

    def AddItemList(self, templ):
        item = QStandardItem()
        
        templ.GetPreviewPDF()
        
        # print(templ.Preview)
        
        item.setIcon(QIcon(templ.Preview))
        
        item.setText(templ.Name)
        
        item.Template = templ
        
        
        
        if templ.ValidIcon == False:
            self.ItemsWithoutPreview.append(item)
        
        self.model.appendRow(item)
        

        
    
    

        
        
        
    
    
        
    
    

