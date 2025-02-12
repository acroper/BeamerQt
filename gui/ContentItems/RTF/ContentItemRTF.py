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



from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import *

from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QToolBar, QFileDialog, QComboBox
from PyQt6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextListFormat, QAction


import xml.etree.ElementTree as ET

from core.xmlutils import *


class itemWidgetRTF(QtWidgets.QWidget):
    
    def __init__(self):
        
        super(itemWidgetRTF, self).__init__()
        
        uic.loadUi('gui/ContentItems/RTF/ItemRTF.ui', self)
        
        self.InnerObject = itemRTF()
        
        self.AssignActions()

    
    def AssignActions(self):
        self.bold_action.clicked.connect(self.toggle_bold)
        self.italic_action.clicked.connect(self.toggle_italic)
        self.bullet_list_action.clicked.connect(self.toggle_bullet_list)
        self.numbered_list_action.clicked.connect(self.toggle_numbered_list)
        
    
        
    def GetInnerObject(self):
        # self.InnerObject.Text = self.TextEditor.toPlainText()
        # self.InnerObject.RTF = self.TextEditor.document()
        self.InnerObject.RTF.setMarkdown( self.TextEditor.toMarkdown() )
        
        return self.InnerObject
    
    def SetInnerObject(self, inner):
        self.InnerObject = inner
        self.Refresh()
        
    def Refresh(self):
        # self.TextEditor.setText(self.InnerObject.Text)
        # self.TextEditor.setDocument(self.InnerObject.RTF)
        
        self.TextEditor.setMarkdown(self.InnerObject.RTF.toMarkdown())

        
        
    def clearFormat(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Normal)
        fmt.setFontItalic(False)
        
        self.TextEditor.setCurrentCharFormat(fmt)
        
    
    # -----------------------------------------------------------------------------
    # This source code was created with assistance from ChatGPT (OpenAI o3-mini-high).
    # -----------------------------------------------------------------------------
    # Functions 
    # toggle_bold
    # toggle_italic
    # toggle_bullet_list
    # toggle_numbered_list
    # change_font_size 
   
    def toggle_bold(self):
        cursor = self.TextEditor.textCursor()
        fmt = QTextCharFormat()
        current_format = cursor.charFormat()
        # Toggle bold: if already bold, remove it; otherwise, apply bold.
        if current_format.fontWeight() == QFont.Weight.Bold:
            fmt.setFontWeight(QFont.Weight.Normal)
        else:
            fmt.setFontWeight(QFont.Weight.Bold)
        cursor.mergeCharFormat(fmt)
        if not cursor.hasSelection():
            self.TextEditor.setCurrentCharFormat(fmt)
        
        self.TextEditor.setFocus()
        

    def toggle_italic(self):
        cursor = self.TextEditor.textCursor()
        fmt = QTextCharFormat()
        current_format = cursor.charFormat()
        fmt.setFontItalic(not current_format.fontItalic())
        cursor.mergeCharFormat(fmt)
        if not cursor.hasSelection():
            self.TextEditor.setCurrentCharFormat(fmt)
        
        self.TextEditor.setFocus()

    def toggle_bullet_list(self):
        cursor = self.TextEditor.textCursor()
        block = cursor.block()
        current_list = block.textList()
        cursor.beginEditBlock()
        if current_list and current_list.format().style() == QTextListFormat.Style.ListDisc:
            # Remove list formatting.
            block_format = cursor.blockFormat()
            block_format.setObjectIndex(-1)
            cursor.setBlockFormat(block_format)
        else:
            # Apply bullet list formatting.
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.Style.ListDisc)
            cursor.createList(list_format)
        cursor.endEditBlock()
        
        self.TextEditor.setFocus()

    def toggle_numbered_list(self):
        cursor = self.TextEditor.textCursor()
        block = cursor.block()
        current_list = block.textList()
        cursor.beginEditBlock()
        if current_list and current_list.format().style() == QTextListFormat.Style.ListDecimal:
            block_format = cursor.blockFormat()
            block_format.setObjectIndex(-1)
            cursor.setBlockFormat(block_format)
        else:
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.Style.ListDecimal)
            cursor.createList(list_format)
        cursor.endEditBlock()
        
        self.TextEditor.setFocus()

    # def change_font_size(self):
    #     # Called when the user changes the selection in the dropbox.
    #     size_name = self.size_combobox.currentText()
    #     latex_command = self.latex_size_mapping.get(size_name, "\\normalsize")
    #     point_size = self.size_point_mapping.get(size_name, 12)
    #     cursor = self.TextEditor.textCursor()
    #     fmt = QTextCharFormat()
    #     fmt.setFontPointSize(point_size)
    #     # Store the LaTeX size command in the custom property.
    #     fmt.setProperty(LATEX_SIZE_PROPERTY, latex_command)
    #     cursor.mergeCharFormat(fmt)
    #     if not cursor.hasSelection():
    #         self.TextEditor.setCurrentCharFormat(fmt)

        

        
class itemRTF():
    
    def __init__(self):
        
        self.Type = "RTF"
        
        self.Text = ""
        
        self.RTF = QTextDocument()
        
        self.Alignment = "Left"
        
    
    def GetXMLContent(self):
        
        self.Text = self.RTF.toMarkdown()
        
        
        ContentXML = ET.Element('ItemWidget', ItemType='RTF')
        
        
        ContentXML.text = self.Text
        
        Alignment = ET.SubElement(ContentXML, "Alignment")
        Alignment.text = self.Alignment
        
        
        
        return ContentXML
        
        
        
    def ReadXMLContent(self, xblock):
        
        xmlblock = xmlutils(xblock)
        
        self.Text = xblock.text
        
        self.RTF.setMarkdown(self.Text)
        
        self.Alignment = xmlblock.GetField("Alignment", "Left")
        
        
    def CheckLaTeX(self, text):
        # Try to check if there is some basic latex command
        result = False
        
        options = ["\\begin", "\\["]
        
        for option in options:
            if option in text:
                return True
        
        return result
        
        
        
    def GenLatex(self):
        
        latexcontent = []
        
        outText = self.document_to_latex()
        
        
        
        # try:
        #     if not self.CheckLaTeX(outText):
        #         outText = self.Text.replace("\n", "\\"+"\\ \n")
        # except:
        #     None
            
        outText += "\\phantom{-}"
        # latexcontent.append(self.Text)
        
        print(outText)
        
        latexcontent.append(outText)
        
        return latexcontent
    
    
    def document_to_latex(self):
        """
        Traverse the QTextDocument and convert each block and its fragments to LaTeX,
        handling inline formatting (bold/italic) and list environments.
        """
        doc = self.RTF
        latex_lines = []
        previous_list = None
        block = doc.begin()
        
        openlist = ""
        
        while block.isValid():
            current_list = block.textList()
            # Start a new list environment if needed.
            if current_list is not None and (previous_list is None or previous_list != current_list):
                style = current_list.format().style()
                if style == QTextListFormat.Style.ListDisc:
                    if openlist != "":
                        latex_lines.append("\\end{"+openlist+"}")
                    openlist = "itemize"    
                    latex_lines.append("\\begin{itemize}")
                elif style == QTextListFormat.Style.ListDecimal:
                    if openlist != "":
                        latex_lines.append("\\end{"+openlist+"}")
                    openlist = "enumerate"    
                    latex_lines.append("\\begin{enumerate}")
            # End the list environment when the list ends.
            elif current_list is None and previous_list is not None:
                style = previous_list.format().style()
                if style == QTextListFormat.Style.ListDisc:
                    latex_lines.append("\\end{itemize}")
                    openlist = ""
                elif style == QTextListFormat.Style.ListDecimal:
                    latex_lines.append("\\end{enumerate}")
                    openlist = ""
                previous_list = None

            block_text = self.process_block_fragments(block)
            if current_list is not None:
                latex_lines.append("\\item " + block_text)
            else:
                latex_lines.append(block_text + "\n")
            previous_list = current_list
            block = block.next()

        # Close any unclosed list environments.
        if previous_list is not None:
            style = previous_list.format().style()
            if style == QTextListFormat.Style.ListDisc:
                latex_lines.append("\\end{itemize}")
            elif style == QTextListFormat.Style.ListDecimal:
                latex_lines.append("\\end{enumerate}")
        return "\n".join(latex_lines)
    
    def process_block_fragments(self, block):
        """
        Process each fragment in a block and convert inline formatting (including size)
        into corresponding LaTeX commands.
        """
        fragments = []
        it = block.begin()
        while not it.atEnd():
            fragment = it.fragment()
            if fragment.isValid():
                fragments.append(self.format_fragment(fragment.text(), fragment.charFormat()))
            it += 1
        return "".join(fragments)
    
    def format_fragment(self, text, char_format):
        """
        Convert a text fragment with its formatting to LaTeX. Inline commands for bold and italic
        are applied, and if a custom LaTeX size is set (and is not the default \normalsize),
        the text is wrapped in a group with that size command.
        """
        text = self.escape_latex(text)
        # First, wrap text for bold and italic.
        base = text
        bold = (char_format.fontWeight() == QFont.Weight.Bold)
        italic = char_format.fontItalic()
        if bold and italic:
            base = "\\textbf{\\textit{" + text + "}}"
        elif bold:
            base = "\\textbf{" + text + "}"
        elif italic:
            base = "\\textit{" + text + "}"
            
        return base
    
        # # Check for the custom LaTeX size property.
        # size_cmd = char_format.property(LATEX_SIZE_PROPERTY)
        # if size_cmd and size_cmd != "\\normalsize":
        #     return "{" + size_cmd + " " + base + "}"
        # else:
        #     return base
    
    def escape_latex(self, text):
        """
        Escape special characters for LaTeX.
        """
        return text
        replacements = {
            '\\': r'\textbackslash{}',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text    
        
        
    
        
        