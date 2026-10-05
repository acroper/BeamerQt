"""
Beamer QT
Copyright (C) 2025  Jorge Guerrero - acroper@gmail.com

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



from pptx import Presentation
from pptx.util import Emu
from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.oxml.ns import qn

from PyQt6.QtGui import QTextCursor, QTextBlockFormat, QTextCharFormat, QTextListFormat, QFont

from core.beamerBlock import BeamerBlock
from gui.ContentItems.RTF.ContentItemRTF import ListStyleForLevel, MAX_LIST_LEVEL


TITLE_TYPES = (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE)

# Placeholders whose paragraphs are bulleted unless told otherwise
BULLETED_TYPES = (PP_PLACEHOLDER.BODY, PP_PLACEHOLDER.OBJECT)

# Longest first paragraph accepted as a block title
MAX_BLOCK_TITLE = 60


class BeamerPPT:
    
    def __init__(self):
        None
    
    
    def Export(self, Document):
        
        # Has to go through the document components
        
        self.prs = Presentation()
        
        aspect_ratio = Document.FrontMatter.AspectRatio
        if aspect_ratio == '43':
            self.prs.slide_width = Emu(9144000)
            self.prs.slide_height = Emu(6858000)
        else:
            self.prs.slide_width = Emu(12192000)
            self.prs.slide_height = Emu(6858000)
            
        
        # Create Title Page
        """Creates the title slide (this remains the same)."""
        slide_layout = self.prs.slide_layouts[0] # Title Slide
        slide = self.prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        title.text = Document.FrontMatter.Title
        st_text = Document.FrontMatter.Subtitle
        author_text = Document.FrontMatter.Author.replace(r'\and', ', ')
        subtitle.text = f"{st_text}\n{author_text}".strip()



    def Import(self, filename, Document):
        """
        Fill Document with the slides of a PowerPoint file. Each text shape
        becomes a block with a rich text item; shapes side by side are split
        in two columns.
        """
        prs = Presentation(filename)
        
        if prs.slide_width * 3 == prs.slide_height * 4:
            Document.FrontMatter.AspectRatio = "43"
        else:
            Document.FrontMatter.AspectRatio = "169"
        
        for k, pslide in enumerate(prs.slides):
            if k == 0 and self.ImportTitlePage(pslide, Document):
                continue
            
            slide = Document.NewSlide()
            
            if pslide.shapes.title is not None:
                slide.Title = self.PlainText(pslide.shapes.title.text_frame)
            
            shapes = [shape for shape in pslide.shapes
                      if shape.has_text_frame and shape.text_frame.text.strip() != ""
                      and not self.IsPlaceholder(shape, TITLE_TYPES)]
            
            columns = self.SplitColumns(shapes)
            
            for col, column in enumerate(columns):
                for shape in column:
                    slide.Columns[col].append(self.ShapeToBlock(shape))
            
            if len(columns) > 1:
                slide.CurrentLayout = "layout_2cols"
                left = min(shape.left for shape in columns[0])
                split = max(shape.left + shape.width for shape in columns[0])
                right = max(shape.left + shape.width for shape in columns[1])
                proportion = 100 * (split - left) / (right - left)
                slide.LeftColumnProportion = int(min(75, max(25, 5 * round(proportion / 5))))
    
    
    def ImportTitlePage(self, pslide, Document):
        # A first slide with a centered title fills the front matter instead of a slide
        title = None
        subtitle = None
        for shape in pslide.placeholders:
            if shape.placeholder_format.type == PP_PLACEHOLDER.CENTER_TITLE:
                title = shape
            elif shape.placeholder_format.type == PP_PLACEHOLDER.SUBTITLE:
                subtitle = shape
        
        if title is None:
            return False
        
        Document.FrontMatter.Title = self.PlainText(title.text_frame)
        if subtitle is not None:
            Document.FrontMatter.Subtitle = self.PlainText(subtitle.text_frame)
        return True
    
    
    def SplitColumns(self, shapes):
        # Shapes that do not overlap horizontally go to different columns.
        # BeamerQt has two columns, so any extra column joins the right one.
        columns = []
        right_edge = None
        for shape in sorted(shapes, key=lambda s: s.left):
            if right_edge is None or shape.left >= right_edge:
                columns.append([])
                right_edge = shape.left + shape.width
            else:
                right_edge = max(right_edge, shape.left + shape.width)
            columns[-1].append(shape)
        
        if len(columns) > 2:
            columns = [columns[0], [shape for column in columns[1:] for shape in column]]
        
        return [sorted(column, key=lambda s: s.top) for column in columns]
    
    
    def ShapeToBlock(self, shape):
        block = BeamerBlock()
        
        default_list = "itemize" if self.IsPlaceholder(shape, BULLETED_TYPES) else None
        paragraphs = [(p, self.ParagraphList(p, default_list)) for p in shape.text_frame.paragraphs
                      if p.text.strip() != ""]
        
        if self.IsBlockTitle(paragraphs):
            block.Title = paragraphs[0][0].text.strip()
            paragraphs = paragraphs[1:]
        
        item = block.GetItemType("RTF")
        self.FillDocument(item.RTF, paragraphs)
        block.SubBlocks.append(item)
        
        return block
    
    
    def IsBlockTitle(self, paragraphs):
        # A short, fully bold first paragraph followed by more text. Content placeholders
        # bullet every paragraph by default, so only an explicit bullet rules it out.
        if len(paragraphs) < 2:
            return False
        
        paragraph = paragraphs[0][0]
        text = paragraph.text.strip()
        runs = [run for run in paragraph.runs if run.text.strip() != ""]
        
        return (self.ParagraphList(paragraph, None) is None and paragraph.level == 0 and len(runs) > 0
                and all(run.font.bold is True for run in runs)
                and len(text) <= MAX_BLOCK_TITLE and "\v" not in text and not text.endswith("."))
    
    
    def ParagraphList(self, paragraph, default):
        # "itemize", "enumerate" or None, from the paragraph bullet settings
        pPr = paragraph._p.pPr
        if pPr is not None:
            if pPr.find(qn("a:buNone")) is not None:
                return None
            if pPr.find(qn("a:buAutoNum")) is not None:
                return "enumerate"
            if pPr.find(qn("a:buChar")) is not None:
                return "itemize"
        return default
    
    
    def FillDocument(self, doc, paragraphs):
        # Open lists by level, so consecutive items keep their list and numbering
        lists = {}
        cursor = QTextCursor(doc)
        
        for k, (paragraph, env) in enumerate(paragraphs):
            if k > 0:
                cursor.insertBlock(QTextBlockFormat())
            
            if env is None:
                lists.clear()
            else:
                level = min(paragraph.level + 1, MAX_LIST_LEVEL)
                for deeper in [l for l in lists if l > level]:
                    del lists[deeper]
                
                current = lists.get(level)
                if current is not None and current[0] == env:
                    current[1].add(cursor.block())
                else:
                    list_format = QTextListFormat()
                    list_format.setStyle(ListStyleForLevel(env, level))
                    list_format.setIndent(level)
                    lists[level] = (env, cursor.createList(list_format))
            
            for run in paragraph.runs:
                fmt = QTextCharFormat()
                fmt.setFontWeight(QFont.Weight.Bold if run.font.bold else QFont.Weight.Normal)
                fmt.setFontItalic(run.font.italic is True)
                cursor.insertText(run.text, fmt)
    
    
    def IsPlaceholder(self, shape, types):
        return shape.is_placeholder and shape.placeholder_format.type in types
    
    
    def PlainText(self, text_frame):
        # Line breaks and paragraphs joined in a single line
        return " ".join(text_frame.text.replace("\v", "\n").split())
