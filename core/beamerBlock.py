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

import json

from core.xmlutils import *


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
        
        self.TableMode = True
        
        self.BlockWidth = 100 # percentage
        
        self.DebugMode = False
        
        self.ColumnProportions = [100, 100, 100, 100]
        
        # for interpolation of column size
        self.mval = [1.16, 1.17, 1.16]
        self.bval = [-1.8, -2.4, -2.8]
        
        


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
        
        ColsProp = ET.SubElement(ContentXML, 'ColumnProportions')
        ColsProp.text = str(self.ColumnProportions)
        
        
        for Elem in self.SubBlocks:
            blockElem = Elem.GetXMLContent()
            ContentXML.append(blockElem)
            
            
        
        
        self.ContentXML = ContentXML
        
        return ContentXML
    
    
    
    def ReadXMLContent(self, xblock):
        
        xmlblock = xmlutils(xblock)
        
        self.Title = xblock.findall('BlockTitle')[0].text
        self.Text = xblock.findall('BlockText')[0].text
        
        self.ColumnCount = int( xblock.findall('ColumnCount')[0].text  )  
        
        self.BlockType = xblock.findall('BlockType')[0].text
        
        ColProportions = xmlblock.GetField('ColumnProportions', '[100,100,100,100]')
        
        self.ColumnProportions = json.loads(ColProportions)
        
        
        
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
    
    
    def GenLatex(self, arg = None):
        latexcontent = []
        
        if self.Title == None:
            self.Title = ""
        
        # Add code to starting the block
        if self.BlockType == "Normal":
            latexcontent.append( "\\begin{block}{" + str(self.Title) + "}"  )
        
        if self.BlockType == "Example":
            latexcontent.append( "\\begin{exampleblock}{" + str(self.Title) + "}"  )
            
        
        if self.BlockType == "Alert":
            latexcontent.append( "\\begin{alertblock}{" + str(self.Title) + "}"  )
            
        
        ## Create table mode
        ## Create tabular letters
        k = 0    
        
        if len(self.SubBlocks) > 1:
            self.TableMode = True
        else:
            self.TableMode = False
            
       
        # if self.TableMode:
            
        #     latexcontent.append("\\setlength\\tabcolsep{0pt}")
        #     latexcontent.append("\\begin{tabular}{lllll}")
        
        LastCol = 0
        
        for item in self.SubBlocks:
            
            # recalculate width
            
            colsize = 10*self.BlockWidth/100
            
            divisions = min(len(self.SubBlocks),self.ColumnCount)
            
            if divisions > 1:
                colsize = colsize*self.mval[divisions-2]+self.bval[divisions-2]
                
           

            
            SBSize = self.BlockWidth/divisions
            SBSize = (self.ColumnProportions[LastCol]*colsize/divisions)/100 # cm
            SBSize = round((self.ColumnProportions[LastCol]//divisions)/100, 2)
            
            # self.TableMode = False
            if self.TableMode:
                latexcontent.append("{\\fboxsep 0pt%")
            ### Need to recalculate the formula, since it is not that linear!
            
            item.MaxItemSize = SBSize
            
            
            LastCol += 1
        
            if LastCol == self.ColumnCount:
                LastCol = 0
            
            
            
            if self.DebugMode and self.TableMode:
                latexcontent.append("\\fbox{%")
                
            if self.TableMode:
                # latexcontent.append("\\begin{minipage}[b]{"+str(SBSize)+"\linewidth}")
                # latexcontent.append("\\begin{minipage}[t]{0.33\linewidth}")
                latexcontent.append("\\begin{minipage}[c]{"+str(SBSize)+"\\linewidth}%")
                
            
            # Alignment
            if item.Alignment == "Left":
                latexcontent.append("\\begin{flushleft}")
            if item.Alignment == "Right":
                latexcontent.append("\\begin{flushright}")
            if item.Alignment == "Center":
                latexcontent.append("\\begin{center}")
            
            itemlatex = item.GenLatex()
            latexcontent.extend(itemlatex)
            
            
            # end Alignment
            
            if item.Alignment == "Left":
                latexcontent.append("\\end{flushleft}")
            if item.Alignment == "Right":
                latexcontent.append("\\end{flushright}")
            if item.Alignment == "Center":
                latexcontent.append("\\end{center}")
            
            
            
            if self.TableMode:
                latexcontent.append("\\end{minipage}}%")
                # latexcontent.append("}%")
                
            
            if self.DebugMode and self.TableMode:
                latexcontent.append("}%")
            
            # if self.TableMode:
            #     latexcontent.append(" & ")
            k += 1
            
            if k == self.ColumnCount:
                # if self.TableMode:
                #     latexcontent.append("\\tabularnewline")
                # else:
                latexcontent.append("\\"+"\\")
 
            
        # if self.TableMode:
        #     latexcontent.append("\\end{tabular}")
        
            
        if self.BlockType == "Normal":
            latexcontent.append("\\end{block}")
            
        if self.BlockType == "Example":
            latexcontent.append("\\end{exampleblock}")
            
        
        if self.BlockType == "Alert":
            latexcontent.append("\\end{alertblock}")
            
            
            
            
        return latexcontent
            
            
            
        
        