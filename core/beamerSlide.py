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
        self.Columns = [[],[]]
        
        self.CurrentLayout = "layout_standard"
        
        self.Modified = False
        
        self.Preview = None
        
        self.LeftColumnProportion = 100
        


    def setPreview(self, pixmap):
        self.Preview = pixmap
        self.Modified = True


    def GetXMLContent(self):
        
        FrameXML = ET.Element('Frame', id='frame_0')
        
        TitleBar = ET.SubElement(FrameXML, 'TitleBar')
        TitleVisible = ET.SubElement(TitleBar, 'Visible')
        TitleVisible.text = str(self.TitleVisible)
        
        TitleBar.text = self.Title
        
        SubTitleBar = ET.SubElement(FrameXML, 'SubTitleBar')
        SubTitleBar.text = self.Subtitle
        
        FrameLayout = ET.SubElement(FrameXML, 'FrameLayout')
        FrameLayout.text = self.CurrentLayout
        
        ColumnXML0 = ET.SubElement(FrameXML, 'Column', id='0')
        ColumnXML1 = ET.SubElement(FrameXML, 'Column', id='1')
        
        ColXML = [ColumnXML0, ColumnXML1]
        
        for k in range(2):
            for block in self.Columns[k]:
                BlockElem = block.GetXMLContent()
                ColXML[k].append(BlockElem)
                
        
        # FrameXML.append(ColXML[0])
        # FrameXML.append(ColXML[1])
                
        
        # for block in self.Blocks:
        #     BlockElem = block.GetXMLContent()
        #     FrameXML.append(BlockElem)

       
        return FrameXML

    
    def ReadXMLContent(self, xblock):
        
        self.Title = xblock.findall('BlockTitle')[0].text
        self.Text = xblock.findall('BlockText')[0].text
        
        # Build the internal elements
        
        