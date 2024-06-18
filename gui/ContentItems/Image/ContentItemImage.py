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
from PyQt6.QtGui import QPixmap, QIcon

from gui.ContentItems.Image.imagebrowse import *

from PyQt6.QtCore import pyqtSignal, QObject

import xml.etree.ElementTree as ET
import pathlib



class ImageWidget(QWidget):
    
    ImageClicked = pyqtSignal()
    
    def __init__(self, image_path, parent=None):
        super().__init__(parent)

        self.image_path = image_path
        self.image_label = QPushButton(self)
        
        # self.image_label.setText("Hello")
        self.max_image_size_percent = 0.5
        
        self.image_label.clicked.connect(self.showImageDLG)

        self.load_image()

        
    def showImageDLG(self):
        self.ImageClicked.emit()
        
    def load_pixmap(self, pixmap):
        self.image_label.setIcon(pixmap)

    def load_image(self):
        
        
        self.icon = QIcon(self.image_path)
        
        self.image_label.setIcon(self.icon)
        
        self.pixmap =QPixmap(self.image_path)
        # parent_size = self.parentWidget().parentWidget().size()
        
        # max_image_size = parent_size * self.max_image_size_percent
        max_image_size = QtCore.QSize(300,300)
        
        image_size = self.pixmap.size()
        
        scale_factor = min(max_image_size.width() / image_size.width(),
                          max_image_size.height() / image_size.height())
        
        self.image_label.setIconSize(image_size * scale_factor)
        
        # self.setFixedSize(image_size * scale_factor*1.1)
        
        
        
        
        
        # self.pixmap =QPixmap(self.image_path)  # Use walrus operator for concise assignment
        # self.image_label.setPixmap(self.pixmap)
        # self.adjust_size()
        # print("Image loaded")
     
        
    def adjust_size(self):
        """
        Adjusts the widget size to maintain the aspect ratio of the image 
        and limit the maximum size based on a percentage of the parent size.
        """
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Get the parent widget size
        parent_size = self.parentWidget().size()

        # Calculate the maximum allowed image size
        max_image_size = parent_size * self.max_image_size_percent

        # Load the image and get its actual size
        image_size = self.pixmap.size()

        # Calculate the scaling factor to fit within the maximum size while maintaining aspect ratio
        scale_factor = min(max_image_size.width() / image_size.width(),
                          max_image_size.height() / image_size.height())

        # Apply scaling to the image
        self.pixmap = self.pixmap.scaled(image_size * scale_factor, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(self.pixmap)

        # Set the widget size based on the scaled image
        self.setFixedSize(self.pixmap.size())



class itemWidgetImage(QtWidgets.QWidget):
    
    def __init__(self):
        
        super(itemWidgetImage, self).__init__()
        
        uic.loadUi('gui/ContentItems/Image/ItemImage.ui', self)
        
        self.InnerObject = itemImage()
        
        
        
        self.initialImage = os.path.join( pathlib.Path(__file__).parent.resolve() , 'add-image.png')
        
        # initialImage = "/tmp/ToPrint/IMG_20230212_123510.jpg"
        
        self.Image = ImageWidget(self.initialImage, self)
        
        self.layout.addWidget(self.Image)
        
        self.Image.show()
        
        self.Image.ImageClicked.connect(self.showImageDLG)
        
        

    def showImageDLG(self):
        print("Image clicked")
        ImgBrw = ImageBrowse()
        
        ImgBrw.SetImageItem(self.InnerObject)
        
        res = ImgBrw.exec()
        if res:
            self.InnerObject.image_path = ImgBrw.image_path
            self.InnerObject.Width = ImgBrw.percentage
            self.InnerObject.pixmap = None
            self.Refresh(True)

    def GetInnerObject(self):
        # self.InnerObject.Text = self.TextEditor.toPlainText()
        return self.InnerObject
    
    def SetInnerObject(self, inner):
        self.InnerObject = inner
        self.Refresh()
        
    
    def Refresh(self, forced = False):
        # self.TextEditor.setText(self.InnerObject.Text)
        if os.path.exists(self.InnerObject.image_path):
            self.Image.image_path = self.InnerObject.image_path
            
            
            if not forced and self.InnerObject.Pixmap != None:
                self.Image.load_pixmap(self.InnerObject.Pixmap)
            else:
                self.Image.load_image()
                self.InnerObject.Pixmap = self.Image.icon
        
        

        
class itemImage():
    
    # Once implemented, this module should store the files
    # inside the temporal folder 
    
    
    def __init__(self):
        
        self.Type = "Image"
        
        self.Text = ""
        
        self.image_path = ""
        
        self.Pixmap = None # Used to store the image, and not load it everytime
        
        self.Width = 50
     
        
    def GetXMLContent(self):
        ContentXML = ET.Element('ItemWidget', ItemType='Image')
        ContentXML.text = self.Text
        
        ImagePath = ET.SubElement(ContentXML, "ImagePath")
        ImagePath.text = self.image_path
        
        Width = ET.SubElement(ContentXML, "Width")
        Width.text = str(self.Width)
        
        
        return ContentXML

    
    def ReadXMLContent(self, xblock):
        self.Text = xblock.text    
        ImagePath = xblock.findall("ImagePath")[0]
        self.image_path = ImagePath.text
        
        try:
            Width = xblock.findall("Width")[0].text
            self.Width = int(Width)
        except:
            None
            
        
        
        
        
        
    def GenLatex(self):
        
        latexcontent = []
        
        if os.path.exists(self.image_path):
            widthText = 10
            width = round( widthText * self.Width / 100 , 1)
            # latexcontent.append("\\begin{center}")
            latexcontent.append("\\includegraphics[width="+str(width)+"cm]{" + self.image_path +"}")
            # latexcontent.append("\\end{center}")
        
        return latexcontent
            
        
        