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


class BeamerSlide():
    
    
    def __init__(self):
        
        self.Title = ""
        self.Subtitle = ""
        self.TitleVisible = True
        self.nombre = ""
        
        self.Text = ""
        
        self.Blocks = []
        self.Columns = []
        
        


    def GetXMLContent(self):
        ContentXML = ET.Element('Block', id='block_'+self.nombre)
        BlockTitle = ET.SubElement(ContentXML, 'BlockTitle')
        BlockTitle.text = self.Title
        
        BlockText = ET.SubElement(ContentXML, 'BlockText')
        BlockText.text = self.Text
        
        self.ContentXML = ContentXML
        
        return ContentXML
    
    def ReadXMLContent(self, xblock):
        
        self.Title = xblock.findall('BlockTitle')[0].text
        self.Text = xblock.findall('BlockText')[0].text
        
        