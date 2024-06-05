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

import subprocess

from core.beamerSlide import *


class beamerDocument():
    
    def __init__(self, Path):
        
        # Define a path inside the given Path. It is expected to be
        # a temporary folder.
        
        self.DocLocation =  tempfile.mkdtemp(prefix= Path+"/" )
        
        # Store everything in DocLocation
        
        
        self.Slides = []
        
    
    def NewSlide(self, Location=-1):
        
        newslide = BeamerSlide()
        if Location == -1 or Location >= len(self.Slides):
            self.Slides.append(newslide)
        else:
            self.Slides.insert(Location, newslide)
            
        return newslide
    
    
        
    def RemoveSlide(self, Location):
        if len(self.Slides) > Location:
            return self.Slides.pop(Location)
        else:
            return None
                
        
    def InsertSlide(self, Slide, Location=-1):
        
        if Location == -1 or Location >= len(self.Slides):
            self.Slides.append(Slide)
        else:
            self.Slides.insert(Location, Slide)
            
    
    def SaveXML (self):
        
        Documento = ET.Element('BeamerDoc')
        
        for slide in self.Slides:
            Documento.append(slide.GetXMLContent())
            
        tree = ET.ElementTree(Documento)
        ET.indent(tree, '  ')
        
        tree.write(self.DocLocation+"/BeamerQt.xml", encoding="utf-8", xml_declaration=True)
        
        
    def ReadXML(self, xmlDocument):
        print('Opening XML file')
        tree = ET.parse(xmlDocument)
        root = tree.getroot()
        
        for subslide in root:
            newslide = self.NewSlide()
            newslide.ReadXMLContent(subslide)
            
   
    
    def WriteFile(self, filename):
        None
    
    def ReadFile(self, filename):
        None
        
        
    def GenLaTeX(self):
        
        
        # Create LaTeX folder
        latexfolder = os.path.join(self.DocLocation, "LaTeX")
        
        os.makedirs(latexfolder, exist_ok=True)
        
        filename = os.path.join(latexfolder, "output.tex")
        # outputfile = open( os.path.join(self.DocLocation, "Output.tex"), 'w' )
        
        
        outputfile = open(filename, 'w' )
        
        
        preamble = open(  os.path.join( os.path.dirname(__file__) , "preamble.tex" ), 'r').readlines()
           
        outputfile.writelines(preamble)
        
        
        for slide in self.Slides:
            latexcontent = slide.GenLaTeX()
            
            for line in latexcontent:
                outputfile.write(line)
                outputfile.write('\n')
            
        
        outputfile.write("\end{document}")
        
        outputfile.close()
        
        self.ExportPDF(latexfolder)
        
        
        
        
    def ExportPDF(self, latexfolder):
        
        current_working_directory = os.getcwd()
        
        os.chdir(latexfolder)
    
        subprocess.call("pdflatex output.tex", shell=True) 
        
        subprocess.call(('xdg-open', 'output.pdf'))
        
        os.chdir(current_working_directory)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
