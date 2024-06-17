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
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import *

import xml.etree.ElementTree as ET
import pathlib

from gui.guidialogs import *


class ImageBrowse(QtWidgets.QDialog):
    
    def __init__(self):
        
        super(ImageBrowse, self).__init__()
        
        uic.loadUi('gui/ContentItems/Image/ImageBrowse.ui', self)
        
        self.percentage = 50
        self.SizeSlider.valueChanged.connect(self.UpdatePercentage)
        
        self.BrowseButton.clicked.connect(self.BrowseImage)
        
        self.ImageItem = None
        
       

    def SetImageItem(self, imageitem):
        self.ImageItem = imageitem
        self.image_path = self.ImageItem.image_path
        
        self.percentage = self.ImageItem.Width
        self.SizeSlider.setValue(self.percentage)
        
        
        if os.path.exists(self.image_path):
            self.PathText.setText(self.image_path)
            self.LoadImage()
        
        
        
        
        
        
    def UpdatePercentage(self):
        self.percentage = self.SizeSlider.value()
        self.SizeLabel.setText( str(self.percentage) + "%"  )
        
        
    def BrowseImage(self):
        filename = openFileNameDialog(self, "", "Supported Imagen files (*.png, *.jpg, *.jpeg)")
                
        if os.path.exists(filename):
            # assign image to the elements
            self.image_path = filename
            self.LoadImage()
            
            self.PathText.setText(filename)
            
    def LoadImage(self):
        
        self.pixmap =QPixmap(self.image_path)
        
        image_size = self.pixmap.size()
        
        max_image_size = self.size() * 0.8
        
        scale_factor = min(max_image_size.width() / image_size.width(),
                          max_image_size.height() / image_size.height())
        
        self.pixmap = self.pixmap.scaled(image_size * scale_factor, Qt.AspectRatioMode.KeepAspectRatio)
        
        self.image_label.setPixmap(self.pixmap)
        
        
        
        
        

        

        
    
        
            