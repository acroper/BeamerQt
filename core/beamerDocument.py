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
            
        
        
    
    
    def GenLaTeX(self):
        None
    
    def ExportPDF(self, filename):
        None
    
    
    def WriteFile(self, filename):
        None
    
    def ReadFile(self, filename):
        None
        
