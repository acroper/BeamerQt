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

# from PyQt6.QtGui import QAction


from gui.slidewidget import *
from gui.configurator import *
from gui.slidebar import *

from gui.guidialogs import *

from core.beamerDocument import *

from gui.FrontMatter.frontmatterwidget import *

from gui.RecentFiles import *

from core.configFile import *

from gui.AboutWidget import *

from gui.ThemeEditorWindow import *


import xml.etree.ElementTree as ET
import tempfile




class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        
        super(MainWindow, self).__init__()

        uic.loadUi('gui/MainWindow.ui', self)
        
        self.Config = Config()
        
        self.ConfigStatusPanel()

        # Initialised in loadPanels()
        self.CurrentFrame = None
        self.UpdatingZoom = False
        
        # self.Documento = ET.Element('BeamerDoc')
        
        # Create Temporal Working directory
        
        self.WorkDirectory = tempfile.mkdtemp(prefix="beamerQT_")
        
        self.Document = beamerDocument(self.WorkDirectory)
        self.Document.Config = self.Config
        
        self.ThemeEditor = None
        
        self.setMenuActions()
        
        self.loadPanels()
        
        self.showMaximized()
        
        # Create timer for refresh previous
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.refreshPreviews)
        self.timer.start(4000)
        self.refreshPreviews()
        
        self.zoomValues = range(40,200,20)
        
        self.RecentFiles = RecentFiles( self.Config )
        
        self.ClipboardFrame = None
        
        self.UpdateRecentFiles()
        
    
    
    def ConfigStatusPanel(self):
        
        
        self.CentralPanel.removeWidget(self.ZoomPanel)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.statusBar.addPermanentWidget(self.ZoomPanel)
        
        

    def UpdateRecentFiles(self):
        RecentList = self.RecentFiles.RecentList.copy()
        
        RecentList.reverse()
        
        self.menuOpen_recent.clear()
        k = 1
        ListMenus = []
        for elem in RecentList:
            ListMenus.append( QAction( elem, self) )
            self.menuOpen_recent.addAction(ListMenus[-1])
            ListMenus[-1].triggered.connect(self.OpenRecent)
            
            # rfile = QAction(str(k)+". "+elem, self)
            # self.menuOpen_recent.addAction(rfile)
            # rfile.triggered.connect(lambda: self.OpenRecent( "Test " + str(k)  ))
            k+= 1
            
        
    
    def setMenuActions(self):
        # Assign actions for the GUI menu
        # File dropdown
        self.actionNew_File.triggered.connect(self.NewFile)
        self.actionNew_File.setShortcut("Ctrl+N")

        self.actionOpen_File.triggered.connect(self.Open)
        self.actionOpen_File.setShortcut("Ctrl+O")

        self.actionSave.triggered.connect(self.Save)
        self.actionSave.setShortcut("Ctrl+S")

        self.actionSave_as.triggered.connect(self.SaveAs)
        self.actionSave_as.setShortcut("Ctrl+Shift+S")

        self.actionGenerateLaTeX.triggered.connect(self.GenerateLatex)
        self.actionGenerateLaTeX.setShortcut("Ctrl+L")

        self.actionQuit.triggered.connect(self.closing)

        # View dropdown
        self.zoomInCtrl.clicked.connect(self.zoomIn)
        self.actionZoom_In.triggered.connect(self.zoomIn)
        # = is the same key on most keyboards as +
        # but does not need to press shift
        self.actionZoom_In.setShortcut("Ctrl+=")

        self.zoomOutCtrl.clicked.connect(self.zoomOut)
        self.actionZoom_Out.triggered.connect(self.zoomOut)
        self.actionZoom_Out.setShortcut("Ctrl+-")

        self.ZoomSlider.valueChanged.connect(self.ZoomSlideValue)

        self.actionLaTeX_Folder.triggered.connect(self.ShowLaTeXFolder)

        # Slide dropdown
        self.actionAdd_new_slide.triggered.connect(self.newSlide)
        self.actionDuplicate_slide.triggered.connect(self.duplicateSlide)

        self.actionReset_slide_number.triggered.connect(self.resetSlideNumber)

        # NOTE: is self.actionReorder_Slides missing here?
        # There is no corresponding function, so this may have been
        # deleted from code but not GUI

        self.actionCopy_Slide.triggered.connect(self.copySlide)
        self.actionCopy_Slide.setShortcut("Ctrl+C")

        self.actionPaste_Slide.triggered.connect(self.pasteSlide)
        self.actionPaste_Slide.setShortcut("Ctrl+V")

        self.actionDelete_Slide.triggered.connect(self.deleteSlide)
        self.actionDelete_Slide.setShortcut("backspace")

        self.actionFrontMatter.triggered.connect(self.ConfigFrontMatter)
        
        
        # Open Theme Editor
        self.actionOpen_Theme_Editor.triggered.connect(self.OpenThemeEditor)

        # About dropdown
        self.actionAbout.triggered.connect(self.ShowAboutDialog)
        

    def OpenThemeEditor(self):
        if self.ThemeEditor == None:
            self.ThemeEditor = ThemeEditorWindow()
            self.ThemeEditor.WorkDirectory = self.WorkDirectory
        else:
            self.ThemeEditor.hide()
            
        self.ThemeEditor.show()
        
    
    def ShowLaTeXFolder(self):
        self.Document.ShowLaTeXFolder()
            
        
       
    def ShowAboutDialog(self):
        about = AboutWidget()
        about.exec()
        
    
    def ConfigFrontMatter(self):
        fmw = FrontMatterWidget()
        
        fmw.SetFrontMatter(self.Document.FrontMatter)
        
        res = fmw.exec()
        
        if res:
            fmw.Save()
            
    
    
    
    def loadPanels(self):
        
        # Central panel
        
        self.InternalPanel = SlideWidget()
        self.CentralPanel.addWidget(self.InternalPanel)
        
        self.InternalPanel.UpdatedZoom.connect(self.zoomUpdate)
        
        
        self.CurrentFrame = self.InternalPanel.CurrentFrame
        
        # Left panel
        
        self.Slidebar = SlideBarWidget()
        self.LeftWidget.addWidget(self.Slidebar)
        
        self.Slidebar.ConnectFrame(self.CurrentFrame)
        
        context_menu = QMenu(self)
        
        context_menu.addAction(self.actionCopy_Slide)
        context_menu.addAction(self.actionPaste_Slide)
        context_menu.addAction(self.actionDelete_Slide)
        context_menu.addAction(self.actionDuplicate_slide)
        
        self.Slidebar.context_menu = context_menu
        
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
        
        self.Configurator.SetDocument(self.Document)
        
        self.Configurator.PrevThemeList.WorkDirectory = self.WorkDirectory
        
        
        
        
    def showOpenFile(self):
        
        # This should ask for saving file
        
        filename = openFileNameDialog(self, "", "BeamerQT files | *.bqt (*.bqt)")
        
        print("Selected file: " + filename)
        
        if filename != "":
            Document2 = beamerDocument(self.WorkDirectory)
            Document2.ReadXML(filename)
            
            self.Document = Document2
            
            self.CurrentFrame.ReadSlide(self.Document.Slides[0])
            
            self.Slidebar.SetDocument(self.Document)
            
            self.refreshPreviews()
            
    
    def NewFile(self):
        
        ### This should ask for saving changes

        Document2 = beamerDocument(self.WorkDirectory)

        self.Document = Document2

        self.Document.NewSlide()
        
        self.CurrentFrame.ReadSlide(self.Document.Slides[0])
        
        self.Slidebar.SetDocument(self.Document)
        
        self.refreshPreviews()    
    
    
    def openProject(self, filename):
        ### Restart the GUI and loads the new project
        
        # Opens the project file
        
        self.MainProject.readFile(filename)
        self.InternalPanel.LoadProject()
        
    def ZoomSlideValue(self):
        
        if self.UpdatingZoom == False:
            zoomFactor = self.ZoomSlider.value()
            self.InternalPanel.zoomVal(zoomFactor/100)
    
    def zoomIn(self):
        self.InternalPanel.zoom_in()
    
    def zoomOut(self):
        self.InternalPanel.zoom_out()
        
    def zoomUpdate(self):
        
        self.UpdatingZoom = True
        
        zoomFactor = int( self.InternalPanel.ZoomFactor*100 )
        
        self.zoomLabel.setText(str(zoomFactor) + "%")
        
        self.ZoomSlider.setValue(zoomFactor)
        
        self.UpdatingZoom = False
        
        
    
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
        nSlide = self.Document.NewSlide( self.Slidebar.SlidePos + 1 )
        
        self.CurrentFrame.ReadSlide(nSlide)

        self.refreshPreviews()
        
        self.Slidebar.selectNext()
        
    def duplicateSlide(self):
        # Temporal refresh slide
        xmldoc = self.CurrentFrame.BeamerSlide.GetXMLContent()
        
        nSlide = self.Document.NewSlide( self.Slidebar.SlidePos + 1 )
        
        nSlide.ReadXMLContent(xmldoc)


        self.CurrentFrame.ReadSlide(nSlide)
        
        self.refreshPreviews()
        
        self.Slidebar.selectNext()        
        
        
    def deleteSlide(self):
        
        pos  = min(self.Slidebar.SlidePos, len(self.Document.Slides)-1)
        
        print("Deleting slide in the position: ", pos)
        self.Document.Slides.pop(pos)
        
        if len(self.Document.Slides) == 0:
            self.Document.NewSlide(0)
        
        maxn = min( len(self.Document.Slides)-1, pos  ) 
        
        cSlide = self.Document.Slides[maxn]
        
        self.CurrentFrame.ReadSlide(cSlide)
        
        self.refreshPreviews()
        self.Slidebar.reSelect()
        
        
    
    def copySlide(self):
        self.ClipboardFrame = self.CurrentFrame.BeamerSlide.GetXMLContent()
        
    def pasteSlide(self):
        
        if self.ClipboardFrame == None:
            return
        
        xmldoc = self.ClipboardFrame
        
        nSlide = self.Document.NewSlide( self.Slidebar.SlidePos + 1 )
        
        nSlide.ReadXMLContent(xmldoc)

        self.CurrentFrame.ReadSlide(nSlide)
        
        self.refreshPreviews()
        
        self.Slidebar.selectNext()   

        
        
    
    def refreshPreviews(self):
        
        self.CurrentFrame.SaveSlide()
        self.Slidebar.RefreshSlides()
        
        # check for document message
        
        if self.Document.Status:
            self.statusBar.showMessage(self.Document.Message)
        else:
            self.statusBar.clearMessage()
        
        
        
    def resetSlideNumber(self):
        self.Slidebar.ResetSlideNumber()
        
        
    def Save(self):
        # Save contents to /tmp/BeamerQt.xml
        self.CurrentFrame.SaveSlide()
        # self.Document.SaveXML()
        self.Slidebar.ResetSlideNumber()
        
        self.Slidebar.reSelect()
        
        if self.Document.NewFile:
            # Create a new document
            self.SaveAs()
            # filename = saveFileNameDialog(self, "", "BeamerQT files | *.bqt (*.bqt)")
            # self.Document.WriteFile(filename)
            # self.RecentFiles.AppendFile(filename)
            # self.UpdateRecentFiles()
            
            # self.setWindowTitle("Beamer QT  - " + os.path.basename(filename))
        else:
            self.Document.WriteFile(self.Document.RealLocation)
            
            
            
    def SaveAs(self):

        # Create a new document
        filename = saveFileNameDialog(self, "", "BeamerQT files | *.bqt (*.bqt)")
        
        if (filename == ""):
            return
        
        if not filename.endswith(".bqt"):
            filename = filename + ".bqt"
        
        
        self.Document.WriteFile(filename)
        self.RecentFiles.AppendFile(filename)
        self.UpdateRecentFiles()
        
        self.setWindowTitle("Beamer QT  - " + os.path.basename(filename))
        
        
            

            
    def OpenRecent(self):
        sender = self.sender()  # QAction
        texto = sender.text()
        
        # print(texto)
        self.Open(texto)
        
        
        
        
    
    def Open(self, openfilename = False):
        
        
        
        if openfilename == False:
            filename = openFileNameDialog(self, "", "BeamerQT files | *.bqt (*.bqt)")
        
        else:
            filename = openfilename
            
        print(filename)
        
        
        print("Selected file: " + filename)
        
        if filename != "":
            Document2 = beamerDocument(self.WorkDirectory)
            
            Document2.Config = self.Config
            
            Document2.ReadFile(filename)
            
            self.Document = Document2
            
            print("From main window")
            for slide in self.Document.Slides:
                print(slide.Title)
            
            self.CurrentFrame.ReadSlide(self.Document.Slides[0])
            
            self.Slidebar.SetDocument(self.Document)
            
            self.Configurator.SetDocument(self.Document)
            
            self.refreshPreviews()  
            
            self.Slidebar.RefreshOpen()
            
            self.RecentFiles.AppendFile(filename)
            
            self.UpdateRecentFiles()
            
            self.setWindowTitle("Beamer QT  - " + os.path.basename(filename))
            
        
    def GenerateLatex(self):
        
        self.Slidebar.ResetSlideNumber()
        self.statusBar.showMessage("Generating LaTeX document... ")
        self.CurrentFrame.SaveSlide()
        self.Document.GenLaTeX()
        

        
        
        
        

