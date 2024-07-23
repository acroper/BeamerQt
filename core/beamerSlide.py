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
        
        self.TitleMode = "Normal"
        
        self.LeftColumnProportion = 100
        
        self.Document = None
        
        self.Number = -1
        


    def setPreview(self, pixmap):
        self.Preview = pixmap
        self.Modified = True
        
    def savePreview(self):
        if self.Preview != None and self.Document != None and self.Number != -1:
            slidename = os.path.join(self.Document.slidesprev, "Slide_"+str(self.Number)+".png")
            print("Saving slide prev at: " + slidename)
            self.Preview.save(slidename, "PNG", 0)
        

    def GetXMLContent(self):
        
        FrameXML = ET.Element('Frame', id='frame_0')
        
        TitleBar = ET.SubElement(FrameXML, 'TitleBar')
        TitleVisible = ET.SubElement(TitleBar, 'Visible')
        TitleVisible.text = str(self.TitleVisible)
        
        TitleBar.text = self.Title
        
        SubTitleBar = ET.SubElement(FrameXML, 'SubTitleBar')
        SubTitleBar.text = self.Subtitle
        
        TitleMode = ET.SubElement(FrameXML, 'TitleMode')
        TitleMode.text = self.TitleMode
        
        
        FrameLayout = ET.SubElement(FrameXML, 'FrameLayout')
        FrameLayout.text = self.CurrentLayout
        
        # colAttributes={"id":"0", "Proportion":str(self.LeftColumnProportion)}
        
        ColumnProportion = ET.SubElement(FrameXML, 'ColumnProportion')
        ColumnProportion.text = str(self.LeftColumnProportion)
        
        
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
        
        self.Title = xblock.findall('TitleBar')[0].text
        self.Subtitle = xblock.findall('SubTitleBar')[0].text
        
        self.CurrentLayout =  xblock.findall('FrameLayout')[0].text
        
        self.LeftColumnProportion = int( xblock.findall('ColumnProportion')[0].text )
        
        self.TitleMode = xblock.findall('TitleMode')[0].text
        
        columns = xblock.findall('Column')
        
        k = 0

        for column in columns:
            # get the blocks
            for xmlblock in column.findall('Block'):

                block = BeamerBlock()   
                block.ReadXMLContent(xmlblock)
                
                self.Columns[k].append(block)
            
            k += 1


        # Build the internal elements
        
    def GenLaTeX(self):
        latexcontent = []
        
        if self.TitleMode == "Section":
            latexcontent.append("\\section{" + self.Title + "}")
        
        if self.TitleMode == "Subsection":
            latexcontent.append("\\subsection{" + self.Title + "}")
        
        
        latexcontent.append("\\begin{frame}{" + self.Title + "}")
        
        useColumns = False
        
        if len(self.Columns[1]) > 0:
            useColumns = True
            # Add something to start the column environment
            latexcontent.append("\\begin{columns}[t]")
            
            framesize = 10
            
            leftcol = round (self.LeftColumnProportion*10/100) 
            rightcol = framesize - leftcol
            
            columnsizes = [leftcol, rightcol ]
            
            
        k = 0
        
        for column in self.Columns:
            
            # Add code to starting column
            if useColumns:
                latexcontent.append("\\column{"+str(columnsizes[k])+"cm}")
            
            for block in column:
                blockLatex = block.GenLatex()
                latexcontent.extend(blockLatex)
                
                print("Adding block content: ")
                print(blockLatex)
                
            k += 1
            # Add code to ending column
            
        # Add code to ending column environment
        if useColumns:
            latexcontent.append("\\end{columns}")
            
        
            
        latexcontent.append("\\end{frame}")
        
        
        return latexcontent
        
        