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
import xml.etree.ElementTree as ET
import tempfile
import zipfile
import shutil
import platform

import subprocess

import threading
import time

from core.beamerSlide import *

from core.frontMatter import *

from core.template import *

class beamerDocument():
    
    def __init__(self, Path):
        
        # Define a path inside the given Path. It is expected to be
        # a temporary folder.
        
        self.DocLocation =  tempfile.mkdtemp(prefix= Path+"/" )
        
        # Store everything in DocLocation
        
        
        self.NewFile = True
        self.RealLocation =  ""
        
        self.Template = BeamerTemplate()
        
        self.FrontMatter = frontMatter()
        
        self.CreateFolders()
        
        self.Slides = []
        
        self.ExportCounts = 0
        
        self.Status = False
        
        self.Message = ""
        
        self.Config = None
        
    
    def ReIndexSlides(self):
        k = 0
        for slide in self.Slides:
            slide.Number = k
            k += 1
    
    def NewSlide(self, Location=-1):
        
        newslide = BeamerSlide()
        
        newslide.Document = self
        
        if Location == -1:
            self.Slides.append(newslide)
        else:
            self.Slides.insert(Location, newslide)

        self.ReIndexSlides()
        
        return newslide
    
    
        
    def RemoveSlide(self, Location):
        if len(self.Slides) > Location:
            return self.Slides.pop(Location)
        else:
            return None
        
        self.ReIndexSlides()
                
        
    def InsertSlide(self, Slide, Location=-1):
        
        Slide.Document = self
        
        if Location == -1 or Location >= len(self.Slides):
            self.Slides.append(Slide)
        else:
            self.Slides.insert(Location, Slide)
            
        self.ReIndexSlides()
            
    
    def SaveXML (self):
        
        Documento = ET.Element('BeamerDoc')
        
        BT = self.Template.GetXMLContent()
        Documento.append(BT)
        
        FM = self.FrontMatter.GetXMLContent()
        Documento.append(FM)
        
        for slide in self.Slides:
            Documento.append(slide.GetXMLContent())
            slide.savePreview()
            
        tree = ET.ElementTree(Documento)
        ET.indent(tree, '  ')
        
        tree.write( os.path.join(self.docfolder, "BeamerQt.xml"), encoding="utf-8", xml_declaration=True)
        
        
    def ReadXML(self, xmlDocument):
        print('Opening XML file')
        tree = ET.parse(xmlDocument)
        root = tree.getroot()
        
        BT = root.findall('Template')[0]
        self.Template.ReadXMLContent(BT)
        
        FM = root.findall('FrontMatter')[0]
        
        self.FrontMatter.ReadXMLContent(FM)
        
        
        for subslide in root.findall('Frame'):
            newslide = self.NewSlide()
            newslide.ReadXMLContent(subslide)
            
            print(newslide.Title)
            
   
    
    def WriteFile(self, filename):
        self.RealLocation = filename
        
        self.SaveXML()
        
        #Now compress the whole Doc folder
        
        current_working_directory = os.getcwd()
        # os.chdir(self.DocLocation)
        
        tmpfile = os.path.join(self.DocLocation, "beamerqt")
        
        # subprocess.call("zip -r ../beamerqt.bqt * ", shell=True)
        shutil.make_archive( tmpfile  , 'zip', self.docfolder)
        
        shutil.copy(tmpfile+".zip", filename)
        
        # os.chdir(current_working_directory)
        
        self.NewFile = False
        
    
    def ReadFile(self, filename):
        self.RealLocation = filename
        self.NewFile = False

        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(self.docfolder)
        
        print("Extracted file in :" + self.docfolder)
            
        self.ReadXML( os.path.join(self.docfolder, "BeamerQt.xml"  )    )
        
        print("After read")
        for slide in self.Slides:
            print(slide.Title)
        
        
        
        
    def CreateFolders(self):
        
        self.latexfolder = os.path.join(self.DocLocation, "LaTeX")
        os.makedirs(self.latexfolder, exist_ok=True)
        
        self.docfolder = os.path.join(self.DocLocation, "Doc")
        os.makedirs(self.docfolder, exist_ok=True)
        
        self.mediafolder = os.path.join(self.docfolder, "Media")
        os.makedirs(self.mediafolder, exist_ok=True)
        
        self.slidesprev = os.path.join(self.mediafolder, "SlidesPrev")
        os.makedirs(self.slidesprev, exist_ok=True)
        
        
    
    def WriteLines(self, lines, outputfile):
        
        for line in lines:
            try:
                outputfile.write(line)
                outputfile.write('\n')
            except:
                None
        
    
    def ShowLaTeXFolder(self):
        LocalSystem = platform.system() 
        
        if LocalSystem == "Windows":
            os.startfile(self.latexfolder)
        else:
            subprocess.call(('xdg-open', self.latexfolder))
        
    
    def GenLaTeX(self):
        self.Status = True
        self.Message = "Generating LaTeX..."
        x = threading.Thread(target=self.GenLaTeXThread, args=(self,))
        x.start()
        
    def GenLaTeXThread(self, arg):
        
        filename = os.path.join(self.latexfolder, "output.tex")
        # outputfile = open( os.path.join(self.DocLocation, "Output.tex"), 'w' )
        
        
        outputfile = open(filename, 'w' )
        
        
        preamble = open(  os.path.join( os.path.dirname(__file__) , "preamble.tex" ), 'r').readlines()
           
        outputfile.writelines(preamble)
        self.WriteLines([self.FrontMatter.Preamble], outputfile)
        
        # add template
        latexcontent = self.Template.GenLaTeX()
        self.WriteLines(latexcontent, outputfile)  
        
        
        
        # add front matter
        latexcontent = self.FrontMatter.GenLaTeX()
        self.WriteLines(latexcontent, outputfile)

        
        for slide in self.Slides:
            latexcontent = slide.GenLaTeX()
            self.WriteLines(latexcontent, outputfile)
            
        
        outputfile.write("\\end{document}")
        
        outputfile.close()
        
        self.ExportPDF()
        
        
        
        
    def ExportPDF(self):
        
        self.Message = "Generating PDF document..."
        
        LocalSystem = platform.system() 
        
        current_working_directory = os.getcwd()
        
        os.chdir(self.latexfolder)

    
        subprocess.call("pdflatex -interaction=nonstopmode output.tex", shell=True) 
        
        
        if self.ExportCounts == 0:
            # some processes need pdflatex to run twice!
            subprocess.call("pdflatex -interaction=nonstopmode output.tex", shell=True) 
        
        self.ExportCounts += 1
        
        
        if LocalSystem == "Windows":
            os.startfile('output.pdf')
        else:
            subprocess.call(('xdg-open', 'output.pdf'))
        
        
        self.Status = True
        
        if os.path.exists('output.pdf'):
            self.Message = "Document generated"
            copylocation = self.RealLocation.replace("bqt", "")+"pdf" 
            shutil.copy( os.path.join(self.latexfolder, 'output.pdf')  , copylocation)
            print("Exported file to: " + copylocation)
        else:
            self.Message = "Error generating PDF document"
        
        os.chdir(current_working_directory)
        
        
        
        time.sleep(10)
        self.Status = False
        self.Message = ""
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
