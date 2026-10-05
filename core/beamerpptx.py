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


import csv
import os

from pptx import Presentation
from pptx.util import Emu
from pptx.enum.shapes import PP_PLACEHOLDER, MSO_SHAPE_TYPE
from pptx.oxml.ns import qn

from PyQt6.QtCore import QByteArray
from PyQt6.QtGui import QTextCursor, QTextBlockFormat, QTextCharFormat, QTextListFormat, QFont, QImage

from core.beamerBlock import BeamerBlock
from core.equationpptx import omml_to_latex, M_NS
from gui.ContentItems.RTF.ContentItemRTF import ListStyleForLevel, MAX_LIST_LEVEL


TITLE_TYPES = (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE)

# Placeholders whose paragraphs are bulleted unless told otherwise
BULLETED_TYPES = (PP_PLACEHOLDER.BODY, PP_PLACEHOLDER.OBJECT)

# Longest first paragraph accepted as a block title
MAX_BLOCK_TITLE = 60

# Default import options
OPTIONS = {"TitlePage": True, "Images": True, "Equations": True,
           "Tables": True, "Charts": True, "Diagrams": False}

LATEX_SPECIAL = {"\\": "\\textbackslash{}", "&": "\\&", "%": "\\%", "$": "\\$", "#": "\\#",
                 "_": "\\_", "{": "\\{", "}": "\\}", "~": "\\textasciitilde{}",
                 "^": "\\textasciicircum{}"}

# Image formats LaTeX includes directly; others are converted to PNG with Qt
LATEX_IMAGES = ("png", "jpg", "jpeg")

MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def LatexEscape(text):
    return "".join(LATEX_SPECIAL.get(ch, ch) for ch in text)


class Content:
    # Something placed on a slide (text, picture, table, chart or diagram) and its box
    def __init__(self, kind, left, top, width, height, data):
        self.kind = kind
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.data = data


class Paragraph:
    # A text paragraph as (kind, text, bold, italic) segments; kind is "text", "math" or "display"
    def __init__(self, level, env, segments, explicit_bullet=False):
        self.level = level
        self.env = env
        self.segments = segments
        self.explicit_bullet = explicit_bullet


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



    def Import(self, filename, Document, folder, options=None):
        """
        Fill Document with the slides of a PowerPoint file. Images, chart data and
        diagrams are written under folder. Returns a list of messages about
        content that was skipped or approximated.
        """
        self.Options = dict(OPTIONS, **(options or {}))
        self.Folder = folder
        self.Messages = []

        prs = Presentation(filename)
        self.SlideWidth = prs.slide_width

        # Plot previews are stored in the current document's media folder
        from core.beamerDocument import beamerDocument
        previous = getattr(beamerDocument, "Current", None)
        beamerDocument.Current = Document
        try:
            self.ImportSlides(prs, Document)
        finally:
            beamerDocument.Current = previous

        return self.Messages


    def ImportSlides(self, prs, Document):

        if prs.slide_width * 3 == prs.slide_height * 4:
            Document.FrontMatter.AspectRatio = "43"
        else:
            Document.FrontMatter.AspectRatio = "169"

        for k, pslide in enumerate(prs.slides):
            if k == 0 and self.Options["TitlePage"] and self.ImportTitlePage(pslide, Document):
                continue

            self.SlideNumber = k + 1
            self.Counter = {}

            slide = Document.NewSlide()

            if pslide.shapes.title is not None:
                slide.Title = LatexEscape(self.PlainText(pslide.shapes.title.text_frame))

            columns = self.SplitColumns(self.SlideContents(pslide))

            proportions = [100]
            if len(columns) > 1:
                slide.CurrentLayout = "layout_2cols"
                left = min(c.left for c in columns[0])
                split = max(c.left + c.width for c in columns[0])
                right = max(c.left + c.width for c in columns[1])
                proportion = 100 * (split - left) / (right - left)
                slide.LeftColumnProportion = int(min(75, max(25, 5 * round(proportion / 5))))
                proportions = [slide.LeftColumnProportion, 100 - slide.LeftColumnProportion]

            for col, column in enumerate(columns):
                for content in column:
                    slide.Columns[col].extend(self.ContentToBlocks(content, proportions[col]))


    def Message(self, text):
        self.Messages.append("Slide " + str(self.SlideNumber) + ": " + text)


    def NextName(self, kind):
        # slide4_image1, slide4_image2, ...
        self.Counter[kind] = self.Counter.get(kind, 0) + 1
        return "slide" + str(self.SlideNumber) + "_" + kind + str(self.Counter[kind])


    def Subfolder(self, name):
        path = os.path.join(self.Folder, name)
        os.makedirs(path, exist_ok=True)
        return path


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

        Document.FrontMatter.Title = LatexEscape(self.PlainText(title.text_frame))
        if subtitle is not None:
            Document.FrontMatter.Subtitle = LatexEscape(self.PlainText(subtitle.text_frame))
        return True


    # ---------- Slide contents ----------

    def SlideContents(self, pslide):
        contents = []
        diagram = []

        for shape in pslide.shapes:
            if self.IsPlaceholder(shape, TITLE_TYPES):
                continue

            box = (shape.left or 0, shape.top or 0, shape.width or 0, shape.height or 0)

            if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                if self.Options["Diagrams"]:
                    contents.append(Content("diagram", *box, self.Leaves(shape)))
                else:
                    self.Message("grouped shapes skipped")

            elif shape.shape_type == MSO_SHAPE_TYPE.LINE:
                if self.Options["Diagrams"]:
                    diagram.append((shape, None))

            elif getattr(shape, "has_chart", False) and shape.has_chart:
                if self.Options["Charts"]:
                    contents.append(Content("chart", *box, shape))

            elif getattr(shape, "has_table", False) and shape.has_table:
                if self.Options["Tables"]:
                    contents.append(Content("table", *box, shape))

            elif self.IsPicture(shape):
                if self.Options["Images"]:
                    contents.append(Content("image", *box, shape))

            elif (self.Options["Diagrams"] and shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE
                  and not shape.is_placeholder):
                diagram.append((shape, None))

            elif getattr(shape, "has_text_frame", False):
                if self.HasText(shape):
                    contents.append(Content("text", *box, shape))

            elif shape.shape_type == MSO_SHAPE_TYPE.EMBEDDED_OLE_OBJECT:
                self.Message("embedded object skipped")

        # Loose boxes and connectors: one diagram if there are connectors or several boxes
        connectors = [s for s, t in diagram if s.shape_type == MSO_SHAPE_TYPE.LINE]
        if connectors or len(diagram) > 1:
            left = min(s.left for s, t in diagram)
            top = min(s.top for s, t in diagram)
            right = max(s.left + s.width for s, t in diagram)
            bottom = max(s.top + s.height for s, t in diagram)
            contents.append(Content("diagram", left, top, right - left, bottom - top, diagram))
        elif diagram and self.HasText(diagram[0][0]):
            shape = diagram[0][0]
            contents.append(Content("text", shape.left, shape.top, shape.width, shape.height, shape))

        return contents


    def SplitColumns(self, contents):
        # Contents that do not overlap horizontally go to different columns.
        # BeamerQt has two columns, so any extra column joins the right one.
        columns = []
        right_edge = None
        for content in sorted(contents, key=lambda c: c.left):
            if right_edge is None or content.left >= right_edge:
                columns.append([])
                right_edge = content.left + content.width
            else:
                right_edge = max(right_edge, content.left + content.width)
            columns[-1].append(content)

        if len(columns) > 2:
            columns = [columns[0], [c for column in columns[1:] for c in column]]

        return [sorted(column, key=lambda c: c.top) for column in columns]


    def ContentToBlocks(self, content, column_proportion):
        block = BeamerBlock()

        if content.kind == "text":
            return self.TextBlocks(content.data)

        elif content.kind == "image":
            width = 100 * content.width * 100 / (self.SlideWidth * column_proportion)
            block.SubBlocks.append(self.MakeImage(block, content.data, int(min(100, max(10, round(width))))))

        elif content.kind == "table":
            block.SubBlocks.append(self.MakeTable(block, content.data.table))

        elif content.kind == "chart":
            item = self.MakeChart(block, content.data.chart)
            if item is None:
                return []
            block.SubBlocks.append(item)

        elif content.kind == "diagram":
            block.SubBlocks.append(self.MakeDiagram(block, content.data))

        return [block]


    # ---------- Text ----------

    def TextBlocks(self, shape):
        # Equations on their own line become Equation items, splitting the text around them.
        # Each piece gets its own block, since a block lays several items out in a row.
        block = BeamerBlock()
        blocks = [block]
        default_list = "itemize" if self.IsPlaceholder(shape, BULLETED_TYPES) else None
        paragraphs = [p for p in (self.ReadParagraph(p, default_list) for p in shape.text_frame.paragraphs)
                      if p.segments]

        if self.IsBlockTitle(paragraphs):
            block.Title = LatexEscape("".join(s[1] for s in paragraphs[0].segments).strip())
            paragraphs = paragraphs[1:]

        pending = []
        for paragraph in paragraphs:
            display = [s for s in paragraph.segments if s[0] == "display"]
            if not display:
                pending.append(paragraph)
                continue

            text = [s for s in paragraph.segments if s[0] != "display" and s[1].strip()]
            if text:
                pending.append(Paragraph(paragraph.level, paragraph.env, text))
            self.FlushText(blocks, pending)
            pending = []

            equation = blocks[-1].GetItemType("EquationQT")
            equation.Latex = " \\\\ ".join(s[1] for s in display)
            self.AddItem(blocks, equation)

        self.FlushText(blocks, pending)
        return blocks


    def AddItem(self, blocks, item):
        # The first item goes in the first block (which may have the title), others in new blocks
        if blocks[-1].SubBlocks:
            blocks.append(BeamerBlock())
        blocks[-1].SubBlocks.append(item)


    def FlushText(self, blocks, paragraphs):
        if not paragraphs:
            return
        item = blocks[-1].GetItemType("RTF")
        self.FillDocument(item.RTF, paragraphs)
        self.AddItem(blocks, item)


    def ReadParagraph(self, paragraph, default_list):
        # Text runs, fields, line breaks and equations, in document order
        p = paragraph._p
        segments = []
        for child in p:
            tag = child.tag
            if tag in (qn("a:r"), qn("a:fld")):
                t = child.find(qn("a:t"))
                if t is not None and t.text:
                    rPr = child.find(qn("a:rPr"))
                    bold = rPr is not None and rPr.get("b") in ("1", "true")
                    italic = rPr is not None and rPr.get("i") in ("1", "true")
                    segments.append(("text", t.text, bold, italic))
            elif tag == qn("a:br"):
                segments.append(("text", " ", False, False))
            elif tag in (qn("a:pPr"), qn("a:endParaRPr")):
                continue
            else:
                segments.extend(self.ReadEquations(child))

        if not any(s[1].strip() for s in segments):
            segments = []

        level = int(p.pPr.get("lvl", "0")) if p.pPr is not None else 0
        return Paragraph(level, self.ParagraphList(p, default_list), segments,
                         self.ParagraphList(p, None) is not None)


    def ReadEquations(self, element):
        # Equations sit in mc:AlternateContent, next to a fallback picture
        if not self.Options["Equations"]:
            return []

        choice = element.find("{" + MC_NS + "}Choice")
        search = choice if choice is not None else element

        segments = []
        for node in search.iter("{" + M_NS + "}oMathPara", "{" + M_NS + "}oMath"):
            if node.tag.endswith("oMath") and node.getparent().tag.endswith("oMathPara"):
                continue
            kind = "display" if node.tag.endswith("oMathPara") else "math"
            latex = omml_to_latex(node)
            if latex:
                segments.append((kind, latex, False, False))
        return segments


    def IsBlockTitle(self, paragraphs):
        # A short, fully bold first paragraph followed by more text. Content placeholders
        # bullet every paragraph by default, so only an explicit bullet rules it out.
        if len(paragraphs) < 2:
            return False

        paragraph = paragraphs[0]
        segments = [s for s in paragraph.segments if s[1].strip()]
        text = "".join(s[1] for s in paragraph.segments).strip()

        return (not paragraph.explicit_bullet and paragraph.level == 0 and len(segments) > 0
                and all(s[0] == "text" and s[2] for s in segments)
                and len(text) <= MAX_BLOCK_TITLE and not text.endswith("."))


    def ParagraphList(self, p, default):
        # "itemize", "enumerate" or None, from the paragraph bullet settings
        pPr = p.pPr
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

        for k, paragraph in enumerate(paragraphs):
            if k > 0:
                cursor.insertBlock(QTextBlockFormat())

            env = paragraph.env
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

            for kind, text, bold, italic in paragraph.segments:
                fmt = QTextCharFormat()
                fmt.setFontWeight(QFont.Weight.Bold if bold else QFont.Weight.Normal)
                fmt.setFontItalic(italic)
                if kind == "text":
                    cursor.insertText(LatexEscape(text), fmt)
                else:
                    cursor.insertText("$" + text + "$", fmt)


    def HasText(self, shape):
        if not getattr(shape, "has_text_frame", False) or not shape.has_text_frame:
            return False
        if shape.text_frame.text.strip() != "":
            return True
        return self.Options["Equations"] and \
            next(shape._element.iter("{" + M_NS + "}oMath"), None) is not None


    def IsPlaceholder(self, shape, types):
        return shape.is_placeholder and shape.placeholder_format.type in types


    def PlainText(self, text_frame):
        # Line breaks and paragraphs joined in a single line
        return " ".join(text_frame.text.replace("\v", "\n").split())


    # ---------- Images ----------

    def IsPicture(self, shape):
        try:
            return shape.image is not None
        except (AttributeError, ValueError):
            return False


    def MakeImage(self, block, shape, width):
        image = shape.image
        try:
            ext = image.ext.lower()
        except Exception:
            # python-pptx reads the format with Pillow, which rejects some files;
            # use the extension of the image inside the .pptx instead
            rId = shape._element.xpath(".//a:blip/@r:embed")
            ext = shape.part.related_part(rId[0]).partname.ext.lower() if rId else "unknown"
        name = self.NextName("image")

        if ext in LATEX_IMAGES:
            path = os.path.join(self.Subfolder("images"), name + "." + ext)
            with open(path, "wb") as f:
                f.write(image.blob)
        else:
            qimage = QImage.fromData(QByteArray(image.blob))
            if qimage.isNull():
                # Keep a visible note where the image was
                self.Message("image not supported (" + ext.upper() + " format)")
                item = block.GetItemType("Text")
                item.Text = "[Image not supported]"
                item.Alignment = "Center"
                return item
            path = os.path.join(self.Subfolder("images"), name + ".png")
            qimage.save(path, "PNG")

        item = block.GetItemType("Image")
        item.image_path = path
        item.Width = width
        return item


    # ---------- Tables ----------

    def MakeTable(self, block, table):
        item = block.GetItemType("Table")
        item.rows = len(table.rows)
        item.cols = len(table.columns)
        item.table = [["" for _ in range(item.cols)] for _ in range(item.rows)]

        merged = False
        for r, row in enumerate(table.rows):
            for c, cell in enumerate(row.cells):
                if cell.is_spanned:
                    merged = True
                    continue
                item.table[r][c] = LatexEscape(self.PlainText(cell.text_frame))

        if merged:
            self.Message("merged table cells were split")
        return item


    # ---------- Charts ----------

    def MakeChart(self, block, chart):
        from gui.ContentItems.Plot.SeriesEditDialog import DEFAULT_PALETTE
        from gui.ContentItems.Plot import csv_parser, plot_compiler

        name = chart.chart_type.name
        markers_only = name == "XY_SCATTER"
        if "PIE" in name or "DOUGHNUT" in name:
            plot_type = "Pie"
        elif any(k in name for k in ("BAR", "COLUMN", "CYLINDER", "CONE", "PYRAMID")):
            plot_type = "Bar"
        elif "XY_SCATTER" in name or "LINE" in name:
            plot_type = "LineScatter"
        elif "AREA" in name:
            plot_type = "Area"
        else:
            self.Message("chart skipped (" + name.lower().replace("_", " ") + ")")
            return None

        # One shared x column for category charts; scatter series each have their own
        headers = []
        columns = []
        series_list = []
        scatter = "XY_SCATTER" in name
        for plot in chart.plots:
            categories = [] if scatter else [str(c) for c in plot.categories]
            for s in plot.series:
                idx = len(series_list) + 1
                if scatter:
                    x_header = "x" + str(idx)
                    headers.append(x_header)
                    columns.append(self.ScatterX(s))
                else:
                    x_header = "x"
                    if "x" not in headers:
                        headers.insert(0, "x")
                        columns.insert(0, categories)
                headers.append("y" + str(idx))
                columns.append(["" if v is None else v for v in s.values])
                series_list.append({
                    "Name": LatexEscape(s.name or "Series " + str(idx)),
                    "X": x_header, "Y": "y" + str(idx),
                    "LineStyle": "None" if markers_only else "Solid", "Thickness": 1.0,
                    "Symbol": "Circle" if markers_only else "None",
                    "Color": DEFAULT_PALETTE[(idx - 1) % len(DEFAULT_PALETTE)],
                })

        if not series_list:
            self.Message("empty chart skipped")
            return None

        if plot_type == "Pie":
            series_list = series_list[:1]

        path = os.path.join(self.Subfolder("data"), self.NextName("chart") + ".csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for r in range(max(len(c) for c in columns)):
                writer.writerow([c[r] if r < len(c) else "" for c in columns])

        item = block.GetItemType("Plot")
        item.PlotType = plot_type
        item.CsvPath = path
        item.Series = series_list
        item.ShowLegend = chart.has_legend
        item.Title = LatexEscape(self.ChartText(lambda: chart.chart_title))
        item.XLabel = LatexEscape(self.ChartText(lambda: chart.category_axis.axis_title))
        item.YLabel = LatexEscape(self.ChartText(lambda: chart.value_axis.axis_title))

        builder = PlotLatex(item, csv_parser.read_csv(path)[1])
        item.LatexCode = builder.buildPieLatex() if plot_type == "Pie" else builder.buildAxisLatex(plot_type)

        if item.LatexCode:
            plot_compiler.compile_and_store_preview(item)
        else:
            self.Message("chart has no data to plot")
        return item


    def ScatterX(self, series):
        points = series._element.xpath("./c:xVal//c:pt")
        values = {}
        for pt in points:
            v = pt.find(qn("c:v"))
            values[int(pt.get("idx"))] = v.text if v is not None else ""
        return [values.get(i, "") for i in range(max(values) + 1)] if values else []


    def ChartText(self, getter):
        # Title text, or "" when the chart or axis has none (pie charts have no axes)
        try:
            title = getter()
            if title.has_text_frame:
                return self.PlainText(title.text_frame)
        except (ValueError, AttributeError, KeyError):
            pass
        return ""


    # ---------- Diagrams ----------

    def Leaves(self, group, transform=None):
        # Shapes inside a group, with the transform from group to slide coordinates
        transform = transform or (lambda x, y: (x, y))
        xfrm = group._element.grpSpPr.find(qn("a:xfrm"))
        off, ext = xfrm.find(qn("a:off")), xfrm.find(qn("a:ext"))
        choff, chext = xfrm.find(qn("a:chOff")), xfrm.find(qn("a:chExt"))
        sx = int(ext.get("cx")) / max(1, int(chext.get("cx")))
        sy = int(ext.get("cy")) / max(1, int(chext.get("cy")))

        def local(x, y, ox=int(off.get("x")), oy=int(off.get("y")),
                  cx=int(choff.get("x")), cy=int(choff.get("y"))):
            return transform(ox + (x - cx) * sx, oy + (y - cy) * sy)

        leaves = []
        for shape in group.shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                leaves.extend(self.Leaves(shape, local))
            else:
                leaves.append((shape, local))
        return leaves


    def MakeDiagram(self, block, shapes):
        name = self.NextName("diagram")
        path = os.path.join(self.Subfolder("diagrams"), name + ".tex")

        tikz, skipped = DiagramToTikz(shapes)
        with open(path, "w", encoding="utf-8") as f:
            f.write("% Imported diagram, slide " + str(self.SlideNumber) + "\n")
            f.write(tikz)

        if skipped:
            self.Message(str(skipped) + " diagram element(s) skipped")

        item = block.GetItemType("Text")
        item.Text = "\\input{" + path.replace("\\", "/") + "}"
        item.Alignment = "Center"
        return item



class PlotLatex:
    # Reuses the plot editor's LaTeX builders without opening the dialog
    def __init__(self, item, columns):
        from gui.ContentItems.Plot.PlotEditorDialog import PlotEditorDialog
        self.item = item
        self.csvColumns = columns
        self.editor = PlotEditorDialog

    def axisOptions(self, plot_type):
        return self.editor.axisOptions(self, plot_type)

    def styleOption(self, key, parts):
        return self.editor.styleOption(key, parts)

    def defineColor(self, name, hex_color):
        return self.editor.defineColor(name, hex_color)

    def buildAxisLatex(self, plot_type):
        return self.editor.buildAxisLatex(self, plot_type)

    def buildPieLatex(self):
        return self.editor.buildPieLatex(self)



# ---------- Diagram to TikZ ----------

ROUNDED = ("ROUNDED_RECTANGLE", "FLOWCHART_ALTERNATE_PROCESS")
TERMINATOR = ("FLOWCHART_TERMINATOR",)
ELLIPSES = ("OVAL", "FLOWCHART_CONNECTOR")
DIAMONDS = ("DIAMOND", "FLOWCHART_DECISION")
PARALLELOGRAMS = ("PARALLELOGRAM", "FLOWCHART_DATA")


def DiagramToTikz(shapes):
    """
    TikZ picture for a list of (shape, transform) pairs, where transform maps
    the shape coordinates to slide coordinates (None for shapes on the slide).
    Returns (code, number of shapes that could not be drawn).
    """
    identity = lambda x, y: (x, y)
    boxes = []
    lines = []
    skipped = 0

    for shape, transform in shapes:
        transform = transform or identity
        if shape.shape_type == MSO_SHAPE_TYPE.LINE:
            a = transform(shape.begin_x, shape.begin_y)
            b = transform(shape.end_x, shape.end_y)
            lines.append((shape, a, b))
        elif shape.shape_type in (MSO_SHAPE_TYPE.AUTO_SHAPE, MSO_SHAPE_TYPE.TEXT_BOX) or \
                getattr(shape, "has_text_frame", False):
            x1, y1 = transform(shape.left, shape.top)
            x2, y2 = transform(shape.left + shape.width, shape.top + shape.height)
            boxes.append((shape, x1, y1, x2, y2))
        else:
            skipped += 1

    points = [(b[1], b[2]) for b in boxes] + [(b[3], b[4]) for b in boxes] + \
        [l[1] for l in lines] + [l[2] for l in lines]
    if not points:
        return "", skipped

    minx = min(p[0] for p in points)
    miny = min(p[1] for p in points)
    width = max(1, max(p[0] for p in points) - minx)
    height = max(1, max(p[1] for p in points) - miny)

    # Coordinates as fractions of the diagram width; fit the width and keep the height reasonable
    unit = round(min(0.95, 0.55 * width / height), 3)

    def P(x, y):
        return "(" + str(round((x - minx) / width, 3)) + "," + str(round((y - miny) / width, 3)) + ")"

    def S(length):
        return str(round(length / width, 3))

    out = ["\\begin{tikzpicture}[x=" + str(unit) + "\\linewidth, y=-" + str(unit)
           + "\\linewidth, >=stealth, font=\\footnotesize]"]

    for shape, x1, y1, x2, y2 in boxes:
        out.extend(BoxTikz(shape, x1, y1, x2, y2, P, S))

    for shape, a, b in lines:
        out.append(LineTikz(shape, a, b, P))

    out.append("\\end{tikzpicture}")
    return "\n".join(out) + "\n", skipped


def BoxTikz(shape, x1, y1, x2, y2, P, S):
    out = []
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

    kind = ""
    if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
        try:
            kind = shape.auto_shape_type.name
        except (ValueError, AttributeError):
            kind = "RECTANGLE"

    if kind in ELLIPSES:
        out.append("\\draw " + P(cx, cy) + " ellipse [x radius=" + S((x2 - x1) / 2)
                   + ", y radius=" + S((y2 - y1) / 2) + "];")
    elif kind in DIAMONDS:
        out.append("\\draw " + P(cx, y1) + " -- " + P(x2, cy) + " -- " + P(cx, y2) + " -- "
                   + P(x1, cy) + " -- cycle;")
    elif kind in PARALLELOGRAMS:
        o = (x2 - x1) * 0.2
        out.append("\\draw " + P(x1 + o, y1) + " -- " + P(x2, y1) + " -- " + P(x2 - o, y2) + " -- "
                   + P(x1, y2) + " -- cycle;")
    elif kind in TERMINATOR:
        out.append("\\draw[rounded corners=6pt] " + P(x1, y1) + " rectangle " + P(x2, y2) + ";")
    elif kind in ROUNDED:
        out.append("\\draw[rounded corners=3pt] " + P(x1, y1) + " rectangle " + P(x2, y2) + ";")
    elif kind:
        out.append("\\draw " + P(x1, y1) + " rectangle " + P(x2, y2) + ";")

    if getattr(shape, "has_text_frame", False) and shape.has_text_frame:
        lines = [LatexEscape(" ".join(p.text.replace("\v", " ").split()))
                 for p in shape.text_frame.paragraphs if p.text.strip()]
        if lines:
            out.append("\\node[align=center] at " + P(cx, cy) + " {" + " \\\\ ".join(lines) + "};")

    return out


def LineTikz(shape, a, b, P):
    ln = shape._element.find(".//" + qn("a:ln"))
    head = tail = False
    if ln is not None:
        head_end, tail_end = ln.find(qn("a:headEnd")), ln.find(qn("a:tailEnd"))
        head = head_end is not None and head_end.get("type", "none") != "none"
        tail = tail_end is not None and tail_end.get("type", "none") != "none"
    arrow = {(False, False): "-", (False, True): "->", (True, False): "<-", (True, True): "<->"}[(head, tail)]

    geometry = shape._element.xpath(".//a:prstGeom/@prst")
    geometry = geometry[0] if geometry else "line"

    horizontal = abs(b[0] - a[0]) >= abs(b[1] - a[1])
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2

    if geometry.startswith("bentConnector"):
        if horizontal:
            path = P(*a) + " -- " + P(mx, a[1]) + " -- " + P(mx, b[1]) + " -- " + P(*b)
        else:
            path = P(*a) + " -- " + P(a[0], my) + " -- " + P(b[0], my) + " -- " + P(*b)
    elif geometry.startswith("curvedConnector"):
        if horizontal:
            path = P(*a) + " .. controls " + P(mx, a[1]) + " and " + P(mx, b[1]) + " .. " + P(*b)
        else:
            path = P(*a) + " .. controls " + P(a[0], my) + " and " + P(b[0], my) + " .. " + P(*b)
    else:
        path = P(*a) + " -- " + P(*b)

    return "\\draw[" + arrow + "] " + path + ";"
