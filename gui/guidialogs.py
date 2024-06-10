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



def openFileNameDialog(parent, location="", Filter = "All files (*.*)"):
    title = "Select a file"
    
    fileName = QFileDialog.getOpenFileName(parent, title, location, Filter)
    

    if fileName:
        return fileName[0]
    else:
        return ""

    
def saveFileNameDialog(parent, location="", Filter = "All files (*.*)"):
    title = "Select a file"
    
    fileName = QFileDialog.getSaveFileName(parent, title, location, Filter)

    if fileName:
        return fileName[0]
    else:
        return ""
    
def openFolderNameDialog(self, location):
    title = "Select a folder"
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    fileName = QFileDialog.getExistingDirectory(parent, title, location)
    if fileName:
        return fileName
    else:
        return "" 
