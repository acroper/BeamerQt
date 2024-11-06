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
from core.beamerBlock import *

from core.xmlutils import *


class frontMatter:
    
    def __init__(self):
        self.Title = ""
        
        self.Subtitle = ""
        
        self.Author = ""
        
        self.Logo = None
        
        self.Background = None
        
        self.LogoPath = ""
        
        self.BackgroundPath = ""
        
        self.Options = ""
        
        self.Preamble = ""
        
        self.getImageObjects()
        
        
    def getImageObjects(self):
        
        bb = BeamerBlock()
        
        self.Logo = bb.GetItemType("Image")
        self.Background = bb.GetItemType("Image")
        
        
    def GetXMLContent(self):
        ContentXML = ET.Element('FrontMatter')
        xmlblock = xmlutils(ContentXML)
        
        Title = ET.SubElement(ContentXML, 'Title')
        Title.text = self.Title
        
        Subtitle = ET.SubElement(ContentXML, 'Subtitle')
        Subtitle.text = self.Subtitle
        
        Author = ET.SubElement(ContentXML, 'Author')
        Author.text = self.Author
        
        Options = ET.SubElement(ContentXML, 'Options')
        Options.text = self.Options
        
        Logo = self.Logo.GetXMLContent()
        ContentXML.append(Logo)
        
        Background = self.Background.GetXMLContent()
        ContentXML.append(Background)
        
        xmlblock.SetField('Preamble', self.Preamble)
        xmlblock.SetField('LogoPath', self.LogoPath)
        xmlblock.SetField('BackgroundPath', self.BackgroundPath)
        
        
        self.ContentXML = ContentXML
        
        return ContentXML
    
    
    def ReadXMLContent(self, xblock):
        
        # self.Title = xblock.findall('Title')[0].text
        # self.Subtitle = xblock.findall('Subtitle')[0].text
        # self.Author = xblock.findall('Author')[0].text
        # self.Options = xblock.findall('Options')[0].text
        
        xmlblock = xmlutils(xblock)
        
        self.Title = xmlblock.GetField('Title', '')
        self.Subtitle = xmlblock.GetField('Subtitle', '')
        self.Author = xmlblock.GetField('Author', '')
        self.Options = xmlblock.GetField('Options', '')
        
        self.Preamble = xmlblock.GetField('Preamble', '')
        self.LogoPath = xmlblock.GetField('LogoPath', '')
        self.BackgroundPath =  xmlblock.GetField('BackgroundPath', '')
        
        
        self.Logo.ReadXMLContent(xblock.findall('ItemWidget')[0])
        self.Background.ReadXMLContent(xblock.findall('ItemWidget')[1])
        
        
    def GenLaTeX(self):
        latexcontent = []
        
        # latexcontent.append(self.Preamble)
        
        latexcontent.append("\\title{" + self.Title + "}")
        
        latexcontent.append("\\subtitle{" + self.Subtitle + "}")
        
        latexcontent.append("\\author{" + self.Author + "}")
        
        latexcontent.append("\\makebeamertitle")
        
        
        return latexcontent
        
        
        
        
        