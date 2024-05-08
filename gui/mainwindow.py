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

from gui.slidewidget import *
from gui.configurator import *
from gui.slidebar import *

from core.beamerDocument import *


import xml.etree.ElementTree as ET
import tempfile




class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        
        super(MainWindow, self).__init__()

        uic.loadUi('gui/MainWindow.ui', self)
               
        self.CurrentFrame = None
        
        # self.Documento = ET.Element('BeamerDoc')
        
        self.Slides = []
        
        self.CurrentSlide = None
        
        # Create Temporal Working directory
        
        self.WorkDirectory = tempfile.mkdtemp(prefix="beamerQT_")
        
        self.Document = beamerDocument(self.WorkDirectory)
        
        
        self.setMenuActions()
        
        self.loadPanels()
        
        self.showMaximized()
        
        # Create timer for refresh previous
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.refreshPreviews)
        self.timer.start(20000)
        self.refreshPreviews()
        
        
        
        
    
    def setMenuActions(self):
        # Assign actions for the GUI menu

        # close
        self.actionQuit.triggered.connect(self.closing)
        self.actionOpen_File.triggered.connect(self.showOpenFile)
        
        self.actionSave.triggered.connect(self.Save)
        
        self.actionZoom_In.triggered.connect(self.zoomIn)
        self.actionZoom_Out.triggered.connect(self.zoomOut)
        self.actionAdd_new_slide.triggered.connect(self.newSlide)
        self.actionReset_slide_number.triggered.connect(self.resetSlideNumber)
        
        
       
    
    
    def loadPanels(self):
        
        # Central panel
        
        self.InternalPanel = SlideWidget()
        self.CentralPanel.addWidget(self.InternalPanel)
        
        self.CurrentFrame = self.InternalPanel.CurrentFrame
        
        # Left panel
        
        self.Slidebar = SlideBarWidget()
        self.LeftWidget.addWidget(self.Slidebar)
        
        self.Slidebar.ConnectFrame(self.CurrentFrame)
        
        
        # Initial slide
        
        ## TODO: Replace this code for the new beamerSlide code
        self.CurrentSlide = Slide()
        self.Slides.append(self.CurrentSlide)
        self.CurrentFrame.ReadSlideOld(self.CurrentSlide)
        
        
        # Create new slide for the document
        self.Document.NewSlide()
        self.Slidebar.SetDocument(self.Document)
        self.CurrentFrame.ReadSlide(self.Document.Slides[0])
        
        
        
        
        
        # self.InternalPanel = ProcessListWidget()
        # self.CentralPanel.addWidget(self.InternalPanel)
        
        # # Assign mainproject
        # self.InternalPanel.MainProject = self.MainProject
        
        # Right panel
        self.Configurator = ConfiguratorWidget()
        self.RightWidget.addWidget(self.Configurator)
        
        self.Configurator.ConnectFrame(self.CurrentFrame)
        
        
    def showOpenFile(self):
        
        filename = openFileNameDialog(self, "", "Project files | *.txt (*.txt)")
        
        if filename != "":
            self.openProject(filename)
            
        
    
        
    
    def openProject(self, filename):
        ### Restart the GUI and loads the new project
        
        # Opens the project file
        
        self.MainProject.readFile(filename)
        self.InternalPanel.LoadProject()
        
        
    
    def zoomIn(self):
        self.InternalPanel.zoom_in()
    
    def zoomOut(self):
        self.InternalPanel.zoom_out()
    
    ### Check how to improve to ask to save the file
    def closeEvent(self, event):
        print("Closing")
        QApplication.instance().quit()
        
    def closing(self):
        # First ask about to quit
        print("Quitting...")
        QApplication.instance().quit()
        
        
    def newSlide(self):
        # Temporal refresh slide
        newSlide = Slide()
        
        nSlide = self.Document.NewSlide( self.Slidebar.SlidePos + 1 )
        
        
        
        self.Slides.append(newSlide)
        
        
        
        # self.CurrentFrame.ReadSlideOld(newSlide)
        
        self.CurrentFrame.ReadSlide(nSlide)
        
        # self.CurrentSlide = newSlide
        
        # self.CurrentFrame.ReadSlide()
        
        
        
        self.refreshPreviews()
        
        self.Slidebar.selectNext()
        
        
        
        
        
    def refreshPreviews(self):
        self.CurrentFrame.SaveSlide()
        self.Slidebar.RefreshSlides(self.Slides)
        
        
        
        
    def resetSlideNumber(self):
        self.Slidebar.ResetSlideNumber()
        
        
    def Save(self):
        # Save contents to /tmp/BeamerQt.xml
        Documento = ET.Element('BeamerDoc')
        
        for slide in self.Slides:
            Documento.append(slide.FrameXML)
            
        tree = ET.ElementTree(Documento)
        ET.indent(tree, '  ')
        
        # DocLocation =  tempfile.mkdtemp(prefix= self.WorkDirectory+"/" )  
        DocLocation = self.WorkDirectory

        tree.write(DocLocation+"/BeamerQt.xml", encoding="utf-8", xml_declaration=True)
        
        
        
        

