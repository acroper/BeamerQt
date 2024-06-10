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

import importlib


class BeamerBlock():
    
    
    def __init__(self):
        
        self.Title = ""
        
        self.nombre = ""
        
        self.Text = ""
        
        self.ColumnNumber = -1
        
        self.Expanded = False
        
        self.SubBlocks = []
        
        self.BlockType = "Normal"
        
        self.ColumnCount = 1
        
        


    def GetXMLContent(self):
        ContentXML = ET.Element('Block', id='block_'+self.nombre)
        BlockTitle = ET.SubElement(ContentXML, 'BlockTitle')
        BlockTitle.text = self.Title
        
        BlockText = ET.SubElement(ContentXML, 'BlockText')
        BlockText.text = self.Text
        
        BlockType = ET.SubElement(ContentXML, 'BlockType')
        BlockType.text = self.BlockType
        
        
        ColsCount = ET.SubElement(ContentXML, 'ColumnCount')
        ColsCount.text = str(self.ColumnCount)  
        
        
        for Elem in self.SubBlocks:
            blockElem = Elem.GetXMLContent()
            ContentXML.append(blockElem)
            
            
        
        
        self.ContentXML = ContentXML
        
        return ContentXML
    
    
    
    def ReadXMLContent(self, xblock):
        
        self.Title = xblock.findall('BlockTitle')[0].text
        self.Text = xblock.findall('BlockText')[0].text
        
        self.ColumnCount = int( xblock.findall('ColumnCount')[0].text  )  
        
        self.BlockType = xblock.findall('BlockType')[0].text
        
        self.SubBlocks.clear()
        
        for xmlWidget in xblock.findall('ItemWidget'):
            itemtype = xmlWidget.get('ItemType')
            
            Item = self.GetItemType(itemtype)
            Item.ReadXMLContent(xmlWidget)
            
            self.SubBlocks.append(Item)
            
            
            
    def GetItemType(self, itemtype):
        
        typeloc = 'gui.ContentItems.'+itemtype+ ".ContentItem"+itemtype
        
        module = importlib.import_module(typeloc)
        itemClass = getattr(module, "item" + itemtype )
        Item = itemClass()
        
        return Item
    
    
    def GenLatex(self):
        latexcontent = []
        
        # Add code to starting the block
        if self.BlockType == "Normal":
            latexcontent.append( "\\begin{block}{" + str(self.Title) + "}"  )
        
        if self.BlockType == "Example":
            latexcontent.append( "\\begin{exampleblock}{" + str(self.Title) + "}"  )
            
        
        if self.BlockType == "Alert":
            latexcontent.append( "\\begin{alertblock}{" + str(self.Title) + "}"  )
            
            
            
        
        for item in self.SubBlocks:
            
            itemlatex = item.GenLatex()
            latexcontent.extend(itemlatex)
        
            
        if self.BlockType == "Normal":
            latexcontent.append("\\end{block}")
            
        if self.BlockType == "Example":
            latexcontent.append("\\end{exampleblock}")
            
        
        if self.BlockType == "Alert":
            latexcontent.append("\\end{alertblock}")
            
            
            
            
        return latexcontent
            
            
            
        
        