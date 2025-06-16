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

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtGui import QPixmap, QImage, QIcon



class PrevWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.Previews = []
        
        # self.resize(100, 100)
        self.child1 = QLabel(self)
        # self.child1.setStyleSheet("background-color:red;border-radius:15px;")
        self.child1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.child1.resize(200, 80)
        self.child1.resize(self.size())
        
        self.child2 = QLabel(self)
        # self.child2.setStyleSheet("background-color:blue;border-radius:15px;")
        self.child2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.child2.resize(200, 80)
        
        self.CurrentObject = self.child2
        
        self.AnimInterval = 1000
        
        # self.StartAnimation()
        
    def StartAnimation(self):
        
        if self.CurrentObject == self.child1:
            self.CurrentObject = self.child2
        else:
            self.CurrentObject = self.child1
        
        self.CurrentObject.raise_()
        
        self.CurrentObject.setPixmap(self.Previews[self.Current])
        
        self.anim = QPropertyAnimation(self.CurrentObject, b"pos")
        self.anim.finished.connect(self.RestartAnimation)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim.setStartValue(QPoint(300,0))
        self.anim.setEndValue(QPoint(10, 0))
        self.anim.setDuration(500)
        self.anim.start()
        
    
    def RestartAnimation(self):
        
        self.Current += 1
        
        if self.Current == self.Total:
            self.Current = 0
            self.AnimInterval += 1000

        QtCore.QTimer.singleShot(self.AnimInterval, self.StartAnimation)

            
        
    def Initialize(self):
        
        self.Total = len(self.Previews)
        self.Current = 0
        
        self.AnimInterval = 1000
        
        self.StartAnimation()
        
    def ResizeTo(self, widget):
        # Resize to the size of the largest object
        self.child1.resize(200, widget.size().height())
        self.child2.resize(200, widget.size().height())
        None




class PreviewPDF(QtWidgets.QWidget):
    
    def __init__(self):
        
        super(PreviewPDF, self).__init__()
        uic.loadUi('gui/PreviewPDF.ui', self)
        
        self.image_prev = PrevWindow()
        
        self.FrameLayout.addWidget(self.image_prev)
        
        self.image_prev.ResizeTo(self)
        
        self.Previews = []
        
        # self.FrameView.setCentralWidget(self.image_prev)
        
    
    
    def ShowPDF(self, file_path):
        
        import fitz  # PyMuPDF

        print("Opening pdf:")
        
        try:
            self.pdf_document = fitz.open(file_path)
            self.total_pages = self.pdf_document.page_count
            self.LoadPreviews()

        except Exception as e:
            self.pdf_document = None
            print("Error")
            print(e)

            
    def LoadPreviews(self):
        
        
        if not self.pdf_document:
            return
        
        self.Previews.clear()
        
        for currentpage in range(self.total_pages):
            page = self.pdf_document.load_page(currentpage)
            # Render page to a pixmap (an image)
            # Higher DPI gives better quality
            pix = page.get_pixmap(dpi=40)

            # Convert the PyMuPDF Pixmap to a QImage
            image_format = QImage.Format.Format_RGB888
            qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, image_format)

            # Convert the QImage to a QPixmap and set it on the label
            pixmap = QPixmap.fromImage(qimage)
            
            self.Previews.append(pixmap)
            
        
        print("Finalizing previews")
        
        self.image_prev.Previews = self.Previews
        
        self.image_prev.Initialize()
        
        
    
        
    
        
    
    

