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
        self.ShortTitle = ""
        
        self.Subtitle = ""
        
        self.Author = ""
        self.ShortAuthor = ""
        
        self.Logo = None
        
        self.Background = None
        
        self.LogoPath = ""
        
        self.BackgroundPath = ""
        
        self.Options = ""
        
        self.Preamble = ""
        
        self.AspectRatio = "43"
        
        self.ShowSectionPage = "False"
        
        self.ShowSectionOutline = "False"
        
        self.OutlineTitle = ""
        
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
        
        xmlblock.SetField('ShortTitle', self.ShortTitle)
        xmlblock.SetField('ShortAuthor', self.ShortAuthor)
        
        xmlblock.SetField('AspectRatio', self.AspectRatio)
        
        xmlblock.SetField('ShowSectionPage', self.ShowSectionPage)
        xmlblock.SetField('ShowSectionOutline', self.ShowSectionOutline)
        xmlblock.SetField('OutlineTitle', self.OutlineTitle)
        
        self.ContentXML = ContentXML
        
        return ContentXML
    
    
    def ReadXMLContent(self, xblock):
        
        # self.Title = xblock.findall('Title')[0].text
        # self.Subtitle = xblock.findall('Subtitle')[0].text
        # self.Author = xblock.findall('Author')[0].text
        # self.Options = xblock.findall('Options')[0].text
        
        xmlblock = xmlutils(xblock)
        
        self.Title = xmlblock.GetField('Title', '')
        self.ShortTitle = xmlblock.GetField('ShortTitle', '')
        self.Subtitle = xmlblock.GetField('Subtitle', '')
        self.Author = xmlblock.GetField('Author', '')
        self.ShortAuthor = xmlblock.GetField('ShortAuthor', '')
        self.Options = xmlblock.GetField('Options', '')
        
        self.Preamble = xmlblock.GetField('Preamble', '')
        self.LogoPath = xmlblock.GetField('LogoPath', '')
        self.BackgroundPath =  xmlblock.GetField('BackgroundPath', '')
        
        self.AspectRatio =  xmlblock.GetField('AspectRatio', '43')
        
        self.ShowSectionPage =  xmlblock.GetField('ShowSectionPage', '')
        self.ShowSectionOutline =  xmlblock.GetField('ShowSectionOutline', '')
        self.OutlineTitle =  xmlblock.GetField('OutlineTitle', '')
        
        self.Logo.ReadXMLContent(xblock.findall('ItemWidget')[0])
        self.Background.ReadXMLContent(xblock.findall('ItemWidget')[1])
        
    
    def GenLaTeXOptions(self):
        latexcontent = "\\documentclass[english" #  ", aspectratio=169]{beamer}"
        if self.AspectRatio == "169":
            latexcontent = latexcontent + ", aspectratio=169"
        
        latexcontent = latexcontent + "]{beamer}\n"
        
        return latexcontent

        
        
    def GenLaTeX(self):
        latexcontent = []
        
        # latexcontent.append(self.Preamble)
        
        latexcontent.append("\\title["+self.ShortTitle+"]{" + self.Title + "}")
        
        latexcontent.append("\\subtitle{" + self.Subtitle + "}")
        
        latexcontent.append("\\author["+self.ShortAuthor+"]{" + self.Author + "}")
        
        # latexcontent.append("\\makebeamertitle")
        
        # Sections
        
        sectionCode = []
        
        if self.ShowSectionPage == "True":
            spage = "\\begin{frame} \n  \\sectionText{\\secname} \n \\end{frame}"
            sectionCode.append(spage)
            
        if self.ShowSectionOutline == "True":
            spage = "\\frame<beamer>{ \n \\frametitle{"+self.OutlineTitle+"}     \\tableofcontents[currentsection,currentsubsection]  }"
            sectionCode.append(spage)
        
        if len(sectionCode) > 0:
            latexcontent.append( "\\AtBeginSection[]{" )
            latexcontent.extend(sectionCode)
            latexcontent.append("}")
            
        
        
        
        
        
        
        
        return latexcontent
        
        
        
        
        