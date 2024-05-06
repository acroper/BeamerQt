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
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QMimeData
from PyQt6.QtGui import QDrag, QPixmap


class SlideBarWidget(QtWidgets.QWidget):
    
    def __init__(self):
        
        super(SlideBarWidget, self).__init__()
        
        uic.loadUi('gui/Slidebar.ui', self)
        
        self.setAcceptDrops(True)
        
        self.SlideList = []
                      
        # self.show()
    
    def setSelected(self):
        for slide in self.SlideList:
            slide.unSelected()
            
        slidesel = self.sender()
        slidesel.setSelected()
        
        self.CurrentFrame.ReadSlide(slidesel.Slide)
        
        
    def dragEnterEvent(self, e):
        e.accept()
        
    def dropEvent(self, e):
        pos = e.position()
        widget = e.source()

        for n in range(self.SlidePanel.count()):
            # Get the widget at each index in turn.
            w = self.SlidePanel.itemAt(n).widget()
            if pos.y() < w.y() + w.size().width() // 2:
                # We didn't drag past this widget.
                # insert to the left of it.
                break
        else:
            # We aren't on the left hand side of any widget,
            # so we're at the end. Increment 1 to insert after.
            n += 1
        
        self.SlidePanel.removeWidget(widget)
        self.SlideList.remove(widget)

        
        self.SlidePanel.insertWidget(n, widget)
        self.SlideList.insert(n, widget)

        e.accept()
    
    def ConnectFrame(self, NewFrame):
        self.CurrentFrame = NewFrame
        
        slidePrev = SlidePrev()
        
        slidePrev.setNumber(1)
        
        slidePrev.setInnerFrame(NewFrame)
        self.SlideList.append(slidePrev)
        self.SlidePanel.insertWidget( len(self.SlidePanel) -1,   slidePrev)
        
        slidePrev.Selected.connect(self.setSelected)
        slidePrev.setSelected()
        
        
        
    def RefreshSlides(self, Slides):
        # Restore previews
        # Test with one slide by now
        # if len(Slides) > len(self.SlideList):
        
        ### Need to improve this part    
        for k in range( len(self.SlideList), len(Slides) ):
            slidePrev = SlidePrev()
            slidePrev.setInnerFrame(self.CurrentFrame)
            self.SlideList.append(slidePrev)
            self.SlidePanel.insertWidget( len(self.SlidePanel) -1,   slidePrev)
            slidePrev.setNumber(len(self.SlideList))
            
            slidePrev.Selected.connect(self.setSelected)
            

        for k in range(len(self.SlideList)):
            self.SlideList[k].refresh(Slides[k])
            
            
    def ResetSlideNumber(self):
        # Resets the slide numbers:
        k = 1
        for slide in self.SlideList:
            slide.setNumber(k)
            k += 1
            
      
        
        
            
            


class SlidePrev(QtWidgets.QWidget):
    
    Selected = pyqtSignal()
    
    def __init__(self):
        
        super(SlidePrev, self).__init__()
        
        uic.loadUi('gui/SlidePrev.ui', self)
        
        self.Number = 1
        
        self.Slide = None
        
        
        
        
    def setInnerFrame(self, NewFrame):
        self.InnerFrame = NewFrame
        
    def refresh(self, slide):
        self.LabelPix.setPixmap(slide.Preview)
        self.Slide = slide
        
    def setNumber(self, number):
        self.slideNumber.setText(str(number))
        self.Number = number
        
        
    def setSelected(self):
        self.frame.setStyleSheet('background-color: rgb(181, 181, 181)')
    
    
    def unSelected(self):
        self.frame.setStyleSheet('background-color: rgb(255, 255, 255)')
    
        
    def mouseReleaseEvent(self, event):
        self.ClickSelected = True
        self.Selected.emit()
        
    
    def mouseMoveEvent(self, e):

        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(Qt.DropAction.MoveAction)
    
        
    
        
    
        
    
    

