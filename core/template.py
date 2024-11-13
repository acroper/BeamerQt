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


class BeamerTemplate:
    
    def __init__(self):
        
        self.Name = "Warsaw"
        
        self.Preview = None
        
        self.UseTheme = ""
        
        self.CustomCode = ""
        
        
    def GetXMLContent(self):
        
        # Right now, just saving the template name
        # Future versions, it will copy the code of the
        # template to the file, so it will more portable
        TemplateXML = ET.Element('Template')
        TemplateXML.text = self.Name
        
        return TemplateXML
        
        
    def ReadXMLFile(self, file):
        tree = ET.parse(file)
        root = tree.getroot()[0]
        self.ReadXMLContent(root)
    
    
    def ReadXMLContent(self, xblock):
        self.SetTemplate( xblock.text )
        
        
        
    def SetTemplate(self, name):
        self.Name = name
        
        # try to reach the template file
        tempfile = os.path.join("templates", self.Name.lower()+".xml")
        
        
        tree = ET.parse(tempfile)
        
        self.UseTheme = tree.findall('UseTheme')[0].text
        self.CustomCode = tree.findall('CustomCode')[0].text
        
        
        
    
    def GetPreview(self):
        # Try to generate a preview
        None
    
    
    def GenLaTeX(self):
        latexcontent = []
        
        if self.UseTheme != "":
            latexcontent.append("\\usetheme{"+self.UseTheme+"}")
            
        if self.CustomCode != "":
            latexcontent.append(self.CustomCode)
            
            
        # latexcontent.append("\\begin{document}")
        
        
        return latexcontent
        
        
        
        
        