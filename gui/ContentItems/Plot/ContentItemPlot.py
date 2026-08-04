"""
Beamer QT
Copyright (C) 2024-2026  Jorge Guerrero - acroper@gmail.com

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

import os
import copy
import pathlib
import uuid as uuidlib

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui import QPixmap

import xml.etree.ElementTree as ET

from core.xmlutils import *

from gui.ImageScale import ImageScale

from gui.ContentItems.Plot.PlotEditorDialog import PlotEditorDialog
from gui.ContentItems.Plot import csv_parser


class itemWidgetPlot(QtWidgets.QWidget):

    def __init__(self):
        super(itemWidgetPlot, self).__init__()

        uic.loadUi('gui/ContentItems/Plot/ItemPlotWidget.ui', self)

        self.InnerObject = itemPlot()

        # Placeholder shown until a plot has actually been generated, same
        # idea as itemImage's add-image.png fallback.
        self.initialImage = os.path.join(pathlib.Path(__file__).parent.resolve(), 'add-plot.png')

        # ImageScale (already used by itemWidgetImage) keeps its pixmap scaled
        # to whatever size the container ends up being and re-scales on every
        # resize, so the preview always fills the block/column it's given
        # instead of being stuck at a fixed size.
        self.Image = ImageScale(self)
        self.previewLayout.addWidget(self.Image)
        self.Image.clicked.connect(self.showPlotDialog)

        self.Refresh()

    def showPlotDialog(self, event=None):
        # No parent on purpose: the editor should be an independent top-level
        # window, not tied to the small inline widget's stacking/lifetime
        # (matches EquationEditorDialog / ImageBrowse elsewhere in this app).
        dialog = PlotEditorDialog(self.InnerObject)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.InnerObject = dialog.result_item()
            self.Refresh()

    def GetInnerObject(self):
        return self.InnerObject

    def SetInnerObject(self, inner):
        self.InnerObject = inner
        self.Refresh()

    def Refresh(self):
        # The preview is only ever (re)compiled by PlotEditorDialog on Accept
        # (see plot_compiler.compile_and_store_preview); here we just show
        # whatever's cached -- no recompiling on every redisplay. Mirrors
        # itemWidgetImage.Refresh(): use the in-memory Pixmap if we already
        # have it, else try loading the on-disk preview once (itemPlot's own
        # ReadXMLContent already does this after loading a saved document;
        # this covers the case where SetInnerObject() hands us a fresh item
        # that hasn't gone through that yet).
        if self.InnerObject.Pixmap is None:
            self.InnerObject.LoadPixmap()

        pixmap = self.InnerObject.Pixmap
        if pixmap is None or pixmap.isNull():
            pixmap = QPixmap(self.initialImage)

        self.Image.setPixmap(pixmap)


class itemPlot():

    def __init__(self):
        self.Type = "Plot"
        self.Alignment = "Center"

        self.PlotType = "LineScatter"

        self.CsvPath = ""
        self.CsvDelimiter = ","
        self.CsvDecimal = "."
        self.CsvHasHeader = True

        self.Series = []

        self.Title = ""
        self.XLabel = ""
        self.YLabel = ""
        self.GridX = False
        self.GridY = False
        self.ShowLegend = True
        self.Bins = 10

        # 0 = auto-thin categorical X tick labels to ~10 visible; >0 forces
        # "show every Nth label" (see csv_parser.symbolic_x_coords_fragment).
        self.XTickStep = 0

        # "" means no override (pgfplots/beamer default size) for each; else
        # a LaTeX size command name without the backslash, e.g. "footnotesize".
        self.XTickFontSize = ""
        self.YTickFontSize = ""
        self.LegendFontSize = ""

        self.LatexCode = ""

        self.uuid = str(uuidlib.uuid4())

        self.Pixmap = None # Used to store the image, and not load it everytime

    def __deepcopy__(self, memo):
        # QPixmap is a Qt/C++ object and isn't deep-copyable (copy.deepcopy
        # raises TypeError: cannot pickle 'QPixmap' object) -- PlotEditorDialog
        # deep-copies the item it's handed to make an isolated working copy,
        # so every other field gets copied normally, but Pixmap is shared by
        # reference instead. That's safe: it's a derived cache (recomputed by
        # plot_compiler.compile_and_store_preview), never mutated in place.
        cls = self.__class__
        new_obj = cls.__new__(cls)
        memo[id(self)] = new_obj
        for key, value in self.__dict__.items():
            if key == "Pixmap":
                setattr(new_obj, key, value)
            else:
                setattr(new_obj, key, copy.deepcopy(value, memo))
        return new_obj

    def CsvFilename(self):
        """Stable, per-item relative filename the generated LaTeX refers to."""
        return "plot_data_" + self.uuid + ".csv"

    def GetPreviewPath(self):
        """
        Where this item's compiled preview PNG lives, derived from the
        current document's persistent media folder plus this item's own
        uuid -- same idea as BeamerSlide.getSlideName(), recomputed on
        demand rather than stored, so it's never stale across sessions.
        Living inside Document.mediafolder means it's packaged into the
        .bqt file by WriteFile()/ReadFile() like slide previews are.
        Returns "" if no document is currently active.
        """
        from core.beamerDocument import beamerDocument
        doc = beamerDocument.Current
        if doc is None:
            return ""
        return os.path.join(doc.plotpreviews, "Plot_" + self.uuid + ".png")

    def LoadPixmap(self):
        """Load the cached preview PNG (if any) into self.Pixmap, so
        itemWidgetPlot.Refresh() can show it without recompiling."""
        path = self.GetPreviewPath()
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.Pixmap = pixmap

    def GetXMLContent(self):
        ContentXML = ET.Element('ItemWidget', ItemType='Plot')
        ContentXML.set('PlotType', self.PlotType)
        ContentXML.set('uuid', self.uuid)

        Csv = ET.SubElement(ContentXML, "Csv")
        Csv.set("path", self.CsvPath)
        Csv.set("delimiter", self.CsvDelimiter)
        Csv.set("decimal", self.CsvDecimal)
        Csv.set("hasHeader", "1" if self.CsvHasHeader else "0")

        Options = ET.SubElement(ContentXML, "Options")
        Options.set("title", self.Title)
        Options.set("xlabel", self.XLabel)
        Options.set("ylabel", self.YLabel)
        Options.set("gridX", "1" if self.GridX else "0")
        Options.set("gridY", "1" if self.GridY else "0")
        Options.set("legend", "1" if self.ShowLegend else "0")
        Options.set("bins", str(self.Bins))
        Options.set("xtickstep", str(self.XTickStep))
        Options.set("xtickfont", self.XTickFontSize)
        Options.set("ytickfont", self.YTickFontSize)
        Options.set("legendfont", self.LegendFontSize)

        for series in self.Series:
            SeriesXML = ET.SubElement(ContentXML, "Series")
            for key in ("Name", "X", "Y", "LineStyle", "Symbol", "Color"):
                SeriesXML.set(key, str(series.get(key, "")))
            SeriesXML.set("Thickness", str(series.get("Thickness", 1.0)))

        LatexCode = ET.SubElement(ContentXML, "LatexCode")
        LatexCode.text = self.LatexCode

        Alignment = ET.SubElement(ContentXML, "Alignment")
        Alignment.text = self.Alignment

        return ContentXML

    def ReadXMLContent(self, xblock):
        xmlblock = xmlutils(xblock)

        self.PlotType = xblock.get('PlotType', 'LineScatter')
        self.uuid = xblock.get('uuid', str(uuidlib.uuid4()))

        csv_elem = xblock.find("Csv")
        if csv_elem is not None:
            self.CsvPath = csv_elem.get("path", "")
            self.CsvDelimiter = csv_elem.get("delimiter", ",")
            self.CsvDecimal = csv_elem.get("decimal", ".")
            self.CsvHasHeader = csv_elem.get("hasHeader", "1") == "1"

        options_elem = xblock.find("Options")
        if options_elem is not None:
            self.Title = options_elem.get("title", "")
            self.XLabel = options_elem.get("xlabel", "")
            self.YLabel = options_elem.get("ylabel", "")
            self.GridX = options_elem.get("gridX", "0") == "1"
            self.GridY = options_elem.get("gridY", "0") == "1"
            self.ShowLegend = options_elem.get("legend", "1") == "1"
            try:
                self.Bins = int(options_elem.get("bins", "10"))
            except ValueError:
                self.Bins = 10
            try:
                self.XTickStep = int(options_elem.get("xtickstep", "0"))
            except ValueError:
                self.XTickStep = 0
            self.XTickFontSize = options_elem.get("xtickfont", "")
            self.YTickFontSize = options_elem.get("ytickfont", "")
            self.LegendFontSize = options_elem.get("legendfont", "")

        self.Series = []
        for series_elem in xblock.findall("Series"):
            self.Series.append({
                "Name": series_elem.get("Name", ""),
                "X": series_elem.get("X", ""),
                "Y": series_elem.get("Y", ""),
                "LineStyle": series_elem.get("LineStyle", "Solid"),
                "Thickness": float(series_elem.get("Thickness", "1.0")),
                "Symbol": series_elem.get("Symbol", "None"),
                "Color": series_elem.get("Color", "#4C72B0"),
            })

        latex_elem = xblock.find("LatexCode")
        self.LatexCode = latex_elem.text if latex_elem is not None and latex_elem.text else ""

        self.Alignment = xmlblock.GetField("Alignment", "Center")

        self.LoadPixmap()

    def GenLatex(self):
        latexcontent = []

        if not self.LatexCode.strip():
            return latexcontent

        outdir = getattr(self, "OutputDirectory", None)
        if outdir and self.CsvPath and os.path.exists(self.CsvPath):
            try:
                csv_parser.write_normalized_csv(
                    self.CsvPath, os.path.join(outdir, self.CsvFilename()),
                    delimiter=self.CsvDelimiter, decimal=self.CsvDecimal,
                    has_header=self.CsvHasHeader,
                )
            except OSError:
                pass

        # Resolve any %[BQT_...] placeholders (see csv_parser.resolve_tags)
        # against the CSV's current contents, fresh at every real compile.
        resolved = csv_parser.resolve_tags(
            self.LatexCode, self.Series, self.CsvPath,
            self.CsvDelimiter, self.CsvDecimal, self.CsvHasHeader, self.Bins,
            xtick_step=self.XTickStep,
        )
        latexcontent.append(resolved)
        return latexcontent
