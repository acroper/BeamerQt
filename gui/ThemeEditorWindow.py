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
import base64

from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize

from core.template import *

from gui.PreviewPDF import *

from xml.dom import minidom

class ThemeEditorWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        
        super(ThemeEditorWindow, self).__init__()
        
        self.incorporated_files = []

        uic.loadUi('gui/ThemeEditorWindow.ui', self)
        
        self.WorkDirectory = None
        
        self.InnerTemplate = None
        
        self.current_file_path = None
        
        self.editable_file = None
        
        self.tabWidget.setCurrentIndex(0)
        
        self.tabWidget.setTabEnabled(2, False)
        
        self.tabWidget.setStyleSheet("QTabBar::tab::disabled { width: 0; height: 0; margin: 0.5; padding: 0; border: none; }")
        
        
        self.PrevWindow = PreviewPDF()
        
        self.PreviewLayout.addWidget(self.PrevWindow)
        
        self.ReviewCount = 0
        
        
        self.setFunctions()
        
        self.removePreviewFile()
        
    
    def removePreviewFile(self):
        # delete file
        previewfile = os.path.join("templates","Previews", "preview.pdf") 
        if os.path.exists( previewfile ):
            try:
                os.remove(previewfile)
            except:
                None
        
    def setFunctions(self):
        
        self.AddFileButton.clicked.connect(self.add_file)
        
        self.RemoveSelectedButton.clicked.connect(self.remove_file)
        
        self.actionOpen.triggered.connect(self.open_xml_file)
        
        self.actionSave.triggered.connect(self.save_xml_file)
        
        self.actionSave_As.triggered.connect(self.save_xml_file_as)
        
        self.actionApply_this_theme.triggered.connect(self.apply_theme)
        
        ## Selection of file on the file list
        
        self.lw_files.itemDoubleClicked.connect(self.editfile)
        
        # self.SaveAttachedButton.clicked.connect(self.save_attached)
        
        self.RevertButton.clicked.connect(self.revert_attached)
        
        self.PreviewButton.clicked.connect(self.ShowPreview)
        
        
    def ShowPreview(self):
        
        print("Generating previews")
        
        self.save_params()
        
        self.InnerTemplate.JustPreview = True
        
        self.InnerTemplate.GenPreviewFile(self.WorkDirectory)
        
        
        if self.ReviewCount == 0 or self.ReviewCount == 10:
            self.ReviewCount = 0
            QtCore.QTimer.singleShot(1000, self.ReviewPreview)
        
        self.ReviewCount = 0
        

        
        

    def ReviewPreview(self):
        
        print("Attempting preview...")

        
        self.InnerTemplate.PreviewPDF = None
        pdfpath = self.InnerTemplate.GetPreviewPDF()
        
        
        self.PrevWindow.ShowPDF(pdfpath)
        
        self.ReviewCount += 1
        
        if self.ReviewCount > 10:
            return
        
        QtCore.QTimer.singleShot(5000, self.ReviewPreview)
        

            
        

        
    def revert_attached(self):
        if self.editable_file != None:
            self.editable_file['content'] = self.editable_file['original']
            self.editableFile_Text.setPlainText(self.editable_file['content'])
        
        
    def save_attached(self):
        
        if self.editable_file != None:
            self.editable_file['content'] = self.editableFile_Text.toPlainText()
        
        
        
    def editfile(self, item):
        
        self.save_attached()
        
        # Find file
        filename = item.text().split(' ')[0]
        
        # Remove from internal list
        # self.incorporated_files = [f for f in self.incorporated_files if f['filename'] != filename_to_remove]
        
        k = 0
        for nitem in self.incorporated_files:
            f = nitem['filename']
            if f == filename:
                # self.incorporated_files.pop(k)
                kfile = nitem
                
                if kfile["type"] == "text":
                    
                    self.tabWidget.setTabEnabled(2, True)
                    
                    self.editable_file = kfile
                    self.editableFile_Text.setPlainText(self.editable_file["content"])
                    
                    self.tabWidget.setCurrentIndex(2)
                    
                    self.tabWidget.setTabText(2, filename)
                    
            
            k+= 1

        
    def apply_theme(self):
        None
            
    def add_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Incorporate File", "", "All Files (*)")
        if not file_path:
            return

        filename = os.path.basename(file_path)
        
        # Check if filename already exists
        if any(f['filename'] == filename for f in self.incorporated_files):
            QMessageBox.warning(self, "Warning", f"A file named '{filename}' is already incorporated.")
            return

        try:
            # Try to read as text first
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            file_type = 'text'
        except UnicodeDecodeError:
            # If it fails, read as binary
            with open(file_path, 'rb') as f:
                binary_content = f.read()
            # Encode binary content to a Base64 string
            content = base64.b64encode(binary_content).decode('ascii')
            file_type = 'binary'

        self.incorporated_files.append({
            'filename': filename,
            'type': file_type,
            'content': content,
            'original': content
        })
        self.lw_files.addItem(f"{filename} ({file_type})")
        

        
    def remove_file(self):
        selected_item = self.lw_files.currentItem()
        if not selected_item:
            return
        
        # Filename is the first part of the list item text, e.g., "logo.png (binary)"
        filename_to_remove = selected_item.text().split(' ')[0]
        
        # Remove from internal list
        # self.incorporated_files = [f for f in self.incorporated_files if f['filename'] != filename_to_remove]
        
        k = 0
        for item in self.incorporated_files:
            f = item['filename']
            if f == filename_to_remove:
                self.incorporated_files.pop(k)
                
            k+= 1
            
        
        
        # Remove from QListWidget
        self.lw_files.takeItem(self.lw_files.row(selected_item))
        
        
    def open_xml_file(self):
        
        
        
        
        # searchpath = os.path.join(  os.path.dirname(os.path.dirname( os.path.abspath(__file__))), "templates")
        # print(searchpath)
        
        path, _ = QFileDialog.getOpenFileName(self, "Open Template File", "templates", "XML Files (*.xml)")
        if path:
            try:
                
                self.lw_files.clear()
                
                # self.load_from_xml(path)
                self.current_file_path = path
                self.setWindowTitle(f"Beamer/LaTeX Template Editor - {os.path.basename(path)}")
                
                self.InnerTemplate = BeamerTemplate()
                self.InnerTemplate.ReadXMLFile(self.current_file_path)
                print("Template readed")
                
                self.BaseName.setText(self.InnerTemplate.UseTheme)
                
                self.ThemeName.setText(self.InnerTemplate.Name)
                
                self.SourceCodeText.setPlainText(self.InnerTemplate.CustomCode)
                
                self.incorporated_files = self.InnerTemplate.incorporated_files
                
                self.tabWidget.setCurrentIndex(0)
                
                self.tabWidget.setTabEnabled(2, False)
                
                self.editable_file = None
                

                
                for file_el in self.incorporated_files:
                    filename = file_el["filename"]
                    file_type = file_el["type"]
                    file_el ['original'] = file_el['content']
                    self.lw_files.addItem(f"{filename} ({file_type})")
                    
                
                self.removePreviewFile()
                self.ReviewPreview()
                

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load XML file.\nError: {e}")


    def save_params(self):
        if self.InnerTemplate == None:
            self.InnerTemplate = BeamerTemplate()
        
        self.InnerTemplate.CustomCode = self.SourceCodeText.toPlainText()
        self.InnerTemplate.UseTheme = self.BaseName.text()
        
        self.InnerTemplate.Name = self.ThemeName.text()
        

    def save_xml_file(self):
        if self.current_file_path != None:
            self.save_to_xml(self.current_file_path)
        else:
            self.save_xml_file_as()

    def save_xml_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Template File As", "", "XML Files (*.xml)")
        if path:
            self.save_to_xml(path)
            self.current_file_path = path
            self.setWindowTitle(f"Beamer/LaTeX Template Editor - {os.path.basename(path)}")        
            
    def save_to_xml(self, filepath):
        
        self.save_params()
        
        TemplateXML = self.InnerTemplate.GenXMLContent()
        # Pretty print XML
        xml_str = minidom.parseString(ET.tostring(TemplateXML)).toprettyxml(indent="   ")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_str)
            
        QMessageBox.information(self, "Success", f"Template saved to {filepath}")
        
        
        
        
