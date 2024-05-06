"""
Beamer QT
Copyright (C) 2024  Mosquera Lab - Montana State University

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
    
    def __init__(self):
        
        super(SlideWidget, self).__init__()
        
        uic.loadUi('gui/SlideWidget.ui', self)
        
        self.ZoomFactor = 1
        
        self.createScene()
              
        self.show()
        
        
    def createScene(self):
        self._scene = QtWidgets.QGraphicsScene(self)
        self._view = QtWidgets.QGraphicsView(self._scene)

        self.CurrentFrame = FrameWidget()
        
        # texto = QLabel("Test")
        
        self._scene.addWidget(self.CurrentFrame)
        self.CurrentFrame.show()
        # self._scene.addWidget(texto)

        self.layout.addWidget(self._view)
    
        
    
    def zoom_in(self):
        
        # Lets try to increase in 10%
        target = self.ZoomFactor+0.2
        scale = target/self.ZoomFactor
        
        if self.ZoomFactor > 8:
            scale = 1
        
        
        
        self.ApplyZoom(scale)

    
    def zoom_out(self):
        
        # Lets try to decrease in 10%
        target = self.ZoomFactor-0.2
        
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
            
        print(self.ZoomFactor)
        
        scale_tr = QtGui.QTransform()
        scale_tr.scale(scale, scale)

        tr = self._view.transform() * scale_tr
        self._view.setTransform(tr)
        

        
    

        
        
        