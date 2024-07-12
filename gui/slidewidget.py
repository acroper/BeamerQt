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
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import QAction
from gui.framewidget import *

class SlideWidget(QtWidgets.QWidget):
    
    UpdatedZoom = pyqtSignal()
    
    def __init__(self):
        
        super(SlideWidget, self).__init__()
        
        uic.loadUi('gui/SlideWidget.ui', self)
        
        self.ZoomFactor = 1
        
        self.createScene()
              
        self.show()
        
        self.ControlDown = False
        self.ReptitionControl = 0
        
        
    def createScene(self):
        self._scene = QtWidgets.QGraphicsScene(self)
        self._view = QtWidgets.QGraphicsView(self._scene)

        self.CurrentFrame = FrameWidget()
        
        # texto = QLabel("Test")
        
        self._scene.addWidget(self.CurrentFrame)
        self.CurrentFrame.show()
        # self._scene.addWidget(texto)

        self.layout.addWidget(self._view)
    
    
    def keyPressEvent(self, event):
        key = event.key()
        if key == 16777249:
            self.ControlDown = True
            
    def keyReleaseEvent(self, event):
        self.ControlDown = False
        self.ReptitionControl = 0
       

    def wheelEvent(self, event):
        
        if self.ControlDown:
            
            if self.ReptitionControl == 0:
                
                delta = event.angleDelta().y()
                
                if delta > 0:
                    self.zoom_in(0.05)
                else:
                    self.zoom_out(0.05)
            
            self.ReptitionControl += 1
            
            if self.ReptitionControl == 10:
                self.ReptitionControl = 0
            
            
            
            
    
    def zoomVal(self, target):
        
        scale = target/self.ZoomFactor
        
        self.ApplyZoom(scale)
    
    
    def zoom_in(self, inc = 0.2):
        
        # Lets try to increase in 10%
        target = self.ZoomFactor+inc
        scale = target/self.ZoomFactor
        
        if self.ZoomFactor > 1.8:
            scale = 1
  
        self.ApplyZoom(scale)

    
    def zoom_out(self, inc = 0.2):
        
        # Lets try to decrease in 10%
        target = self.ZoomFactor-inc
        
        scale = target/self.ZoomFactor
        
        if self.ZoomFactor <= 0.6:
            scale = 1
        
        self.ApplyZoom(scale)
        
        
    @QtCore.pyqtSlot()
    def ApplyZoom(self, scale):
        # self.ZoomFactor = round(self.ZoomFactor - 0.1 , 2)
        
        # if self.ZoomFactor < 0.2:
        #     self.ZoomFactor = 0.2
        self.ZoomFactor = self.ZoomFactor*scale
        
        rounded = round(self.ZoomFactor, 1)
        
        if abs( self.ZoomFactor - rounded ) < 0.01 :
            self.ZoomFactor = rounded
        
        
        
            
        # print(self.ZoomFactor)
        
        scale_tr = QtGui.QTransform()
        scale_tr.scale(scale, scale)

        tr = self._view.transform() * scale_tr
        self._view.setTransform(tr)
        
        self.UpdatedZoom.emit()
        

        
    

        
        
        