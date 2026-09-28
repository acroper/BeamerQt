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


# Beamer only defines templates for three levels of itemize/enumerate
MAX_LIST_LEVEL = 3

BULLET_STYLES = (QTextListFormat.Style.ListDisc,
                 QTextListFormat.Style.ListCircle,
                 QTextListFormat.Style.ListSquare)

NUMBERED_STYLES = (QTextListFormat.Style.ListDecimal,
                   QTextListFormat.Style.ListLowerAlpha,
                   QTextListFormat.Style.ListUpperAlpha,
                   QTextListFormat.Style.ListLowerRoman,
                   QTextListFormat.Style.ListUpperRoman)


def ListEnvironment(style):
    # LaTeX environment for a QTextList style
    if style in BULLET_STYLES:
        return "itemize"
    if style in NUMBERED_STYLES:
        return "enumerate"
    return None


def ListStyleForLevel(env, level):
    # Same defaults Qt uses when reading markdown, so styles survive the round trip
    if env == "itemize":
        return BULLET_STYLES[(level - 1) % len(BULLET_STYLES)]
    return QTextListFormat.Style.ListDecimal


class itemWidgetRTF(QtWidgets.QWidget):
    
    def __init__(self):
        
        super(itemWidgetRTF, self).__init__()
        
        uic.loadUi('gui/ContentItems/RTF/ItemRTF.ui', self)
        
        self.InnerObject = itemRTF()
        
        self.AssignActions()
        
        self.TextEditor.installEventFilter(self)

    
    def eventFilter(self, obj, event):
        if obj == self.TextEditor and event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key.Key_Tab and not (event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier):
                if self.change_list_level(1):
                    return True
            elif event.key() == QtCore.Qt.Key.Key_Backtab:
                if self.change_list_level(-1):
                    return True
        
        return super().eventFilter(obj, event)
    
    def AssignActions(self):
        self.bold_action.clicked.connect(self.toggle_bold)
        self.italic_action.clicked.connect(self.toggle_italic)
        self.bullet_list_action.clicked.connect(self.toggle_bullet_list)
        self.numbered_list_action.clicked.connect(self.toggle_numbered_list)
        
    
        
    def GetInnerObject(self):
        # self.InnerObject.Text = self.TextEditor.toPlainText()
        # self.InnerObject.RTF = self.TextEditor.document()
        # Copy the document directly: a markdown round trip loses bullet lists nested in numbered lists
        self.InnerObject.RTF = self.TextEditor.document().clone()
        
        return self.InnerObject
    
    def SetInnerObject(self, inner):
        self.InnerObject = inner
        self.Refresh()
        
    def Refresh(self):
        # self.TextEditor.setText(self.InnerObject.Text)
        # self.TextEditor.setDocument(self.InnerObject.RTF)
        
        font = self.TextEditor.font()
        # The editor is the parent, so it owns (and later deletes) the copy
        doc = self.InnerObject.RTF.clone(self.TextEditor)
        doc.setDefaultFont(font)
        self.TextEditor.setDocument(doc)

        
        
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
        if current_list and current_list.format().style() in BULLET_STYLES:
            # Remove list formatting.
            block_format = cursor.blockFormat()
            block_format.setObjectIndex(-1)
            cursor.setBlockFormat(block_format)
        else:
            # Apply bullet list formatting, keeping the current level.
            level = current_list.format().indent() if current_list else 1
            list_format = QTextListFormat()
            list_format.setStyle(ListStyleForLevel("itemize", level))
            list_format.setIndent(level)
            cursor.createList(list_format)
        cursor.endEditBlock()
        
        self.TextEditor.setFocus()

    def toggle_numbered_list(self):
        cursor = self.TextEditor.textCursor()
        block = cursor.block()
        current_list = block.textList()
        cursor.beginEditBlock()
        if current_list and current_list.format().style() in NUMBERED_STYLES:
            block_format = cursor.blockFormat()
            block_format.setObjectIndex(-1)
            cursor.setBlockFormat(block_format)
        else:
            level = current_list.format().indent() if current_list else 1
            list_format = QTextListFormat()
            list_format.setStyle(ListStyleForLevel("enumerate", level))
            list_format.setIndent(level)
            cursor.createList(list_format)
        cursor.endEditBlock()
        
        self.TextEditor.setFocus()

    def change_list_level(self, delta):
        """
        Move the list items under the cursor (or selection) one level deeper
        (delta = 1) or shallower (delta = -1). Returns False when the cursor
        is not in a list, so the key keeps its default behavior.
        """
        cursor = self.TextEditor.textCursor()
        doc = self.TextEditor.document()
        
        first = doc.findBlock(cursor.selectionStart())
        last = doc.findBlock(cursor.selectionEnd())
        
        if first.textList() is None:
            return False
        
        blocks = []
        block = first
        while block.isValid():
            if block.textList() is not None:
                blocks.append(block)
            if block == last:
                break
            block = block.next()
        
        cursor.beginEditBlock()
        for block in blocks:
            self.move_block_to_level(block, block.textList().format().indent() + delta)
        cursor.endEditBlock()
        
        self.TextEditor.setFocus()
        return True

    def move_block_to_level(self, block, level):
        if level < 1 or level > MAX_LIST_LEVEL:
            return
        
        env = ListEnvironment(block.textList().format().style())
        
        # Join a preceding list at the target level so numbering continues
        target = None
        prev = block.previous()
        while prev.isValid() and prev.textList() is not None:
            prev_list = prev.textList()
            prev_level = prev_list.format().indent()
            if prev_level < level:
                break
            if prev_level == level:
                if ListEnvironment(prev_list.format().style()) == env:
                    target = prev_list
                break
            prev = prev.previous()
        
        if target is not None:
            target.add(block)
        else:
            list_format = QTextListFormat()
            list_format.setStyle(ListStyleForLevel(env, level))
            list_format.setIndent(level)
            QTextCursor(block).createList(list_format)

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
        handling inline formatting (bold/italic) and nested list environments.
        """
        doc = self.RTF
        latex_lines = []
        # Open environments as (level, environment), innermost last
        open_lists = []
        block = doc.begin()
        
        while block.isValid():
            current_list = block.textList()
            env = ListEnvironment(current_list.format().style()) if current_list is not None else None
            
            if env is not None:
                level = current_list.format().indent()
                # Close deeper levels, and the same level if the list type changed
                while open_lists and (open_lists[-1][0] > level or
                                      (open_lists[-1][0] == level and open_lists[-1][1] != env)):
                    latex_lines.append("\\end{" + open_lists.pop()[1] + "}")
                if not open_lists or open_lists[-1][0] < level:
                    latex_lines.append("\\begin{" + env + "}")
                    open_lists.append((level, env))
                latex_lines.append("\\item " + self.process_block_fragments(block))
            else:
                while open_lists:
                    latex_lines.append("\\end{" + open_lists.pop()[1] + "}")
                latex_lines.append(self.process_block_fragments(block) + "\n")
            
            block = block.next()

        # Close any unclosed list environments.
        while open_lists:
            latex_lines.append("\\end{" + open_lists.pop()[1] + "}")
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
        
        
    
        
        