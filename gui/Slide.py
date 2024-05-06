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



from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QMimeData
from PyQt6.QtGui import QDrag, QPixmap

import xml.etree.ElementTree as ET


class Slide:
    
    def __init__(self):
        
        self.Preview = None
        
        self.Blocks = []
        self.Columns = []
        
        self.CurrentLayout = "layout_standard"
        
        self.Modified = False
        
        self.FrameXML = ET.Element('Frame', id='frame_0', visible='True')
        
    def setPreview(self, pixmap):
        self.Preview = pixmap
        self.Modified = True
        
        
    
        
    
        
    
    
