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
import shutil

import base64

import xml.etree.ElementTree as ET


class BeamerTemplate:
    
    def __init__(self):
        
        self.Name = "Warsaw"
        
        self.ValidPDF = None
        
        self.ValidIcon = False
        
        self.Preview = None
        
        self.PreviewPDF = None
        
        self.UseTheme = ""
        
        self.CustomCode = ""
        
        self.incorporated_files = []
        
        self.OutputDirectory = ""
        
        
    def GetXMLContent(self):
        
        # Right now, just saving the template name
        # Future versions, it will copy the code of the
        # template to the file, so it will more portable
        TemplateXML = ET.Element('Template')
        TemplateXML.text = self.Name
        
        return TemplateXML
    
    
    def GenXMLContent(self):
        
        TemplateXML = ET.Element('Template')
        TemplateXML.text = self.Name
        
        ET.SubElement(TemplateXML, 'Name').text = self.Name
        
        ET.SubElement(TemplateXML, 'UseTheme').text = self.UseTheme
        ET.SubElement(TemplateXML, 'CustomCode').text = self.CustomCode
        
        
        files_el = ET.SubElement(TemplateXML, "incorporatedFiles")
        for file_data in self.incorporated_files:
            file_el = ET.SubElement(files_el, "file")
            ET.SubElement(file_el, "filename").text = file_data['filename']
            ET.SubElement(file_el, "type").text = file_data['type']
            ET.SubElement(file_el, "content").text = file_data['content']
            
        
        return TemplateXML

    
        
    def ReadXMLFile(self, file):
        tree = ET.parse(file)
        root = tree.getroot()
        self.ReadXMLContent(root)
    
    
    # def ReadXMLContent(self, xblock):
    #     self.SetTemplate( xblock.text )
        
        
    def ReadXMLContent(self, xblock):
        
        try:
            # self.Name = xblock[0].text
            
            if xblock.find('Name') != None:
                self.Name = xblock.find('Name').text
            else:
                self.Name = xblock[0].text
                
            
            self.UseTheme = xblock.findall('UseTheme')[0].text
            self.CustomCode = xblock.findall('CustomCode')[0].text
            
            files_el = xblock.find("incorporatedFiles")
            
            if files_el is not None:
                for file_el in files_el.findall("file"):
                    filename = file_el.find("filename").text
                    file_type = file_el.find("type").text
                    content = file_el.find("content").text
                    self.incorporated_files.append({
                        'filename': filename,
                        'type': file_type,
                        'content': content
                    })
                
        
        except:
            ### Keep compatibility with previous template format
            self.SetTemplate( xblock.text )
                
        
        

        
    def SetTemplate(self, name):
        self.Name = name
        
        # try to reach the template file
        tempfile = os.path.join("templates", self.Name.lower()+".xml")
        
        tree = ET.parse(tempfile)
        
        self.Name = tree.findall('Name')[0].text
        self.UseTheme = tree.findall('UseTheme')[0].text
        self.CustomCode = tree.findall('CustomCode')[0].text
        
        
        
    
    def GetPreview(self):
        
        if self.ValidIcon:
            return
        # Try to generate a preview
        iconpath = os.path.join( os.path.join("templates", "Previews"), self.Name.lower()+".png" ) 
        
        if os.path.exists(iconpath):
            self.Preview = iconpath
            self.ValidIcon = True
        else:
            # self.Preview = "/tmp/notfound.png"
            self.Preview = os.path.join( os.path.join("templates", "gen"), "notfound.png" ) 
            

    
    def GetPreviewPDF(self):
        #try to compile the example file and generate it
        
        # print("Getting preview...")
        
        
        if self.PreviewPDF != None:
            return self.PreviewPDF
        
        # Try to generate a preview
        pdfpath = os.path.join( os.path.join("templates", "Previews"), self.Name.lower()+".pdf" ) 

        if os.path.exists(pdfpath):
            self.PreviewPDF = pdfpath
            self.ValidPDF = True
        else:
            self.PreviewPDF = os.path.join( os.path.join("templates", "gen"), "notfound.pdf" ) 

        
        if self.ValidIcon == False and self.ValidPDF:
            self.GeneratePreviewPNG()
            
        return self.PreviewPDF


    def GeneratePreviewPNG(self):
        import fitz  # PyMuPDF
        from PyQt6.QtGui import QPixmap, QImage, QIcon
        
        
        
        pdf_document = fitz.open(self.PreviewPDF)
        page = pdf_document.load_page(1)
        pix = page.get_pixmap(dpi=40)
        image_format = QImage.Format.Format_RGB888
        qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, image_format)
        iconpath = os.path.join( os.path.join("templates", "Previews"), self.Name.lower()+".png" ) 
        qimage.save(iconpath)
        
        
        

    def GenPreviewFile(self, WorkDirectory):
        import core.beamerDocument as beamdoc
        import time
        
        if WorkDirectory == None:
            return
        
        basefile = os.path.abspath(os.path.join( os.path.join("templates", "gen"), "PreviewFile.bqt" ) )
        previewfile = os.path.abspath(os.path.join( os.path.join("templates", "Previews"), self.Name.lower()+".bqt" ) )
        
        
        shutil.copy(basefile, previewfile)
        
        tmpfolder = os.path.join( WorkDirectory, "temp")
        
        print("Using the folder:")
        print(tmpfolder)
        try:
            os.mkdir( tmpfolder )
        except:
            None
        
        TestDoc = beamdoc.beamerDocument(tmpfolder)
        
        TestDoc.ReadFile(previewfile)
        
        TestDoc.ShowPreview = False
        
        TestDoc.Template = self
        
        TestDoc.GenLaTeX()
        
        self.ValidIcon = False
        
        self.Preview = None
        self.PreviewPDF = None
        
        
        
        
        
    
    def GenLaTeX(self):
        latexcontent = []
        
        if self.UseTheme != "":
            latexcontent.append("\\usetheme{"+self.UseTheme+"}")
            
        if self.CustomCode != "":
            latexcontent.append(self.CustomCode)
            
            
        # latexcontent.append("\\begin{document}")
        
        self.ExtractFiles()
        
        
        return latexcontent

    
    def ExtractFiles(self):

        folder_path = self.OutputDirectory
        if not folder_path:
            return

        try:
            for file_data in self.incorporated_files:
                out_path = os.path.join(folder_path, file_data['filename'])
                if file_data['type'] == 'text':
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(file_data['content'])
                elif file_data['type'] == 'binary':
                    # Decode the Base64 string back to bytes
                    binary_content = base64.b64decode(file_data['content'])
                    with open(out_path, 'wb') as f:
                        f.write(binary_content)

        except Exception as e:
            None
        
        
        
        
        