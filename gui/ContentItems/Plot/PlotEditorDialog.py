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

from PyQt6 import uic, QtCore
from PyQt6.QtWidgets import (
    QDialog, QWidget, QHBoxLayout, QLabel, QToolButton, QListWidgetItem,
    QMessageBox, QButtonGroup, QApplication,
)
from PyQt6.QtCore import Qt

from . import csv_parser
from . import plot_compiler
from .CsvFormatDialog import CsvFormatDialog
from .SeriesEditDialog import SeriesEditDialog, DEFAULT_PALETTE

from gui.LatexPreviewWidget import LatexPreviewWidget

import tempfile
import shutil



LINE_STYLE_LATEX = {
    "Solid": "solid",
    "Dashed": "dashed",
    "Dotted": "dotted",
    "DashDot": "dashdotted",
}

SYMBOL_LATEX = {
    "None": "none",
    "Circle": "*",
    "Square": "square*",
    "Triangle": "triangle*",
    "Diamond": "diamond*",
    "Star": "star",
    "Plus": "+",
    "X": "x",
}

PLOT_TYPE_RADIO = {
    "LineScatter": "radioLineScatter",
    "Bar": "radioBar",
    "Area": "radioArea",
    "Histogram": "radioHistogram",
    "Pie": "radioPie",
}

# "Default" means no override (item field stored as ""); the rest are LaTeX
# size command names, used without their leading backslash in the combo.
FONT_SIZE_CHOICES = [
    "Default", "tiny", "scriptsize", "footnotesize", "small",
    "normalsize", "large", "Large", "LARGE",
]

# The CSV referenced by the generated LaTeX is always the normalized copy
# written by csv_parser.write_normalized_csv() (comma-delimited, period
# decimals) -- never the user's original file verbatim -- so the table
# column separator pgfplots is told to expect is always "comma".
TABLE_COL_SEP = "comma"


class SeriesRowWidget(QWidget):
    """A Plot Series list row: label + a small delete ('X') button."""

    clicked = QtCore.pyqtSignal()
    deleteRequested = QtCore.pyqtSignal()

    def __init__(self, text, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        self.label = QLabel(text)
        layout.addWidget(self.label, 1)
        self.deleteButton = QToolButton()
        self.deleteButton.setText("X")
        self.deleteButton.setToolTip("Delete series")
        layout.addWidget(self.deleteButton)
        self.deleteButton.clicked.connect(self.deleteRequested.emit)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class PlotEditorDialog(QDialog):
    """
    Editor dialog for a Plot content item. Operates on a private copy of the
    itemPlot passed in, so Cancel discards all edits; only Accept commits them
    back (retrieved via result_item()).
    """

    def __init__(self, item, parent=None):
        super().__init__(parent)
        uic.loadUi('gui/ContentItems/Plot/ItemPlot.ui', self)

        self.previewLabel.setVisible(False)  # superseded by latexPreview below

        self.latexPreview = LatexPreviewWidget(self)
        self.previewFrameLayout.addWidget(self.latexPreview)
        self.latexPreview.compileFinished.connect(self._onPreviewCompileFinished)

        self._previewDir = None  # see onPreview() below -- holds both the normalized CSV and preview.tex

        # Lets onAccept() skip re-running pdflatex if the box is unchanged
        # since the last successful Preview: _lastPreviewedLatex is the
        # resolved text that compile actually used; _previewPdfPath is
        # where that compile's PDF landed (inside _previewDir).
        self._pendingPreviewLatex = None
        self._lastPreviewedLatex = None
        self._previewPdfPath = None


        self.item = copy.deepcopy(item)

        self.csvHeaders = []
        self.csvColumns = {}

        # Text of the last auto-generated LaTeX, used to detect whether the user
        # has hand-edited the box (in which case settings changes must not
        # silently clobber it). None means "never auto-touch until asked".
        self.lastAutoLatex = ""

        # True while RefreshFromItem() is populating widgets one at a time.
        # Their change signals are already wired at that point, so without
        # this guard each intermediate setText()/setChecked() would trigger
        # onSettingsChanged() -> syncItemFromUI(), which reads *every* widget
        # -- including ones RefreshFromItem hasn't gotten to yet -- and bakes
        # their still-default values into self.item, permanently clobbering
        # fields that haven't been populated yet.
        self._populating = False

        self.typeGroup = QButtonGroup(self)
        for radio_name in PLOT_TYPE_RADIO.values():
            radio = getattr(self, radio_name)
            self.typeGroup.addButton(radio)
            radio.toggled.connect(self.onTypeChanged)

        for combo in (self.xTickFontCombo, self.yTickFontCombo, self.legendFontCombo):
            combo.addItems(FONT_SIZE_CHOICES)

        self.loadCsvButton.clicked.connect(self.onLoadCsv)
        self.newSeriesButton.clicked.connect(self.onNewSeries)
        self.regenerateLatexButton.clicked.connect(self.onRegenerateLatex)
        self.PreviewBtn.clicked.connect(self.onPreview)
        self.acceptBtn.clicked.connect(self.onAccept)
        self.cancelBtn.clicked.connect(self.reject)

        for widget in (self.titleEdit, self.xLabelEdit, self.yLabelEdit):
            widget.textChanged.connect(self.onSettingsChanged)
        for widget in (self.gridXCheck, self.gridYCheck, self.legendCheck):
            widget.stateChanged.connect(self.onSettingsChanged)
        self.binsSpin.valueChanged.connect(self.onSettingsChanged)
        self.xTickStepSpin.valueChanged.connect(self.onSettingsChanged)
        for combo in (self.xTickFontCombo, self.yTickFontCombo, self.legendFontCombo):
            combo.currentTextChanged.connect(self.onSettingsChanged)

        self.RefreshFromItem()

    # ---------- populate UI from self.item ----------

    def RefreshFromItem(self):
        self._populating = True
        try:
            radio_name = PLOT_TYPE_RADIO.get(self.item.PlotType, "radioLineScatter")
            getattr(self, radio_name).setChecked(True)

            self.csvPathEdit.setText(self.item.CsvPath)
            if self.item.CsvPath and os.path.exists(self.item.CsvPath):
                self.loadCsvColumns()

            self.titleEdit.setText(self.item.Title)
            self.xLabelEdit.setText(self.item.XLabel)
            self.yLabelEdit.setText(self.item.YLabel)
            self.gridXCheck.setChecked(self.item.GridX)
            self.gridYCheck.setChecked(self.item.GridY)
            self.legendCheck.setChecked(self.item.ShowLegend)
            self.binsSpin.setValue(self.item.Bins)
            self.xTickStepSpin.setValue(self.item.XTickStep)
            self.xTickFontCombo.setCurrentText(self.item.XTickFontSize or "Default")
            self.yTickFontCombo.setCurrentText(self.item.YTickFontSize or "Default")
            self.legendFontCombo.setCurrentText(self.item.LegendFontSize or "Default")

            self.refreshSeriesList()
            self.updateBinsVisibility()
            self.updateTickStepVisibility()
        finally:
            self._populating = False

        if self.item.LatexCode.strip():
            self.plainTextEdit.setPlainText(self.item.LatexCode)
            self.lastAutoLatex = None  # existing/custom code, don't auto-clobber
        else:
            self.regenerateLatexText()

    def loadCsvColumns(self):
        try:
            self.csvHeaders, self.csvColumns = csv_parser.read_csv(
                self.item.CsvPath,
                delimiter=self.item.CsvDelimiter,
                has_header=self.item.CsvHasHeader,
            )
        except OSError as exc:
            QMessageBox.warning(self, "CSV error", f"Could not read the CSV file.\n{exc}")
            self.csvHeaders, self.csvColumns = [], {}

    def currentPlotType(self):
        for plot_type, radio_name in PLOT_TYPE_RADIO.items():
            if getattr(self, radio_name).isChecked():
                return plot_type
        return "LineScatter"

    def updateBinsVisibility(self):
        is_hist = self.currentPlotType() == "Histogram"
        self.binsLabel.setVisible(is_hist)
        self.binsSpin.setVisible(is_hist)

    def updateTickStepVisibility(self):
        # Only meaningful for the axis types that can end up with a
        # categorical (symbolic) X column -- Pie/Histogram don't have one.
        applies = self.currentPlotType() in ("LineScatter", "Bar", "Area")
        self.xTickStepLabel.setVisible(applies)
        self.xTickStepSpin.setVisible(applies)

    # ---------- series list ----------

    def refreshSeriesList(self):
        self.seriesListWidget.clear()
        for idx, series in enumerate(self.item.Series):
            text = f"{series['Name']} ({series['X']} vs {series['Y']})"
            row = SeriesRowWidget(text)
            row.clicked.connect(lambda checked=False, i=idx: self.onEditSeries(i))
            row.deleteRequested.connect(lambda checked=False, i=idx: self.onDeleteSeries(i))
            list_item = QListWidgetItem(self.seriesListWidget)
            list_item.setSizeHint(row.sizeHint())
            self.seriesListWidget.addItem(list_item)
            self.seriesListWidget.setItemWidget(list_item, row)

    def maxSeriesAllowed(self):
        return 1 if self.currentPlotType() in ("Histogram", "Pie") else None

    def onNewSeries(self):
        if not self.csvHeaders:
            QMessageBox.information(self, "No CSV loaded", "Load a CSV file before adding a series.")
            return

        max_allowed = self.maxSeriesAllowed()
        if max_allowed is not None and len(self.item.Series) >= max_allowed:
            QMessageBox.information(
                self, "Series limit",
                "This plot type only supports a single series. Edit or delete the existing one first.",
            )
            return

        dlg = SeriesEditDialog(
            self.csvHeaders, plot_type=self.currentPlotType(),
            palette_index=len(self.item.Series), parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.item.Series.append(dlg.result_series())
            self.refreshSeriesList()
            self.onSettingsChanged()

    def onEditSeries(self, index):
        if index >= len(self.item.Series):
            return
        dlg = SeriesEditDialog(
            self.csvHeaders, series=self.item.Series[index],
            plot_type=self.currentPlotType(), palette_index=index, parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.item.Series[index] = dlg.result_series()
            self.refreshSeriesList()
            self.onSettingsChanged()

    def onDeleteSeries(self, index):
        if index >= len(self.item.Series):
            return
        del self.item.Series[index]
        self.refreshSeriesList()
        self.onSettingsChanged()

    # ---------- CSV loading ----------

    def onLoadCsv(self):
        dlg = CsvFormatDialog(
            self.item.CsvPath, plot_type=self.currentPlotType(),
            existing_series=self.item.Series, parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            path, delimiter, decimal, has_header, headers, columns = dlg.result_data()
            self.item.CsvPath = path
            self.item.CsvDelimiter = delimiter
            self.item.CsvDecimal = decimal
            self.item.CsvHasHeader = has_header
            self.csvHeaders = headers
            self.csvColumns = columns
            self.csvPathEdit.setText(path)

            # Auto-build series from the X/Y assignment grid, if the user
            # checked any Y column -- replaces the current list outright,
            # matching what's now checked. Leave existing series alone if
            # nothing was checked (e.g. just tweaking the CSV format).
            auto_series = dlg.result_series()
            if auto_series:
                max_allowed = self.maxSeriesAllowed()
                if max_allowed is not None:
                    auto_series = auto_series[:max_allowed]
                self.item.Series = auto_series

            self.refreshSeriesList()
            self.onSettingsChanged()

    # ---------- plot type ----------

    def onTypeChanged(self, checked):
        if not checked:
            return
        new_type = self.currentPlotType()
        self.item.PlotType = new_type
        if new_type in ("Histogram", "Pie") and len(self.item.Series) > 1:
            self.item.Series = self.item.Series[:1]
            self.refreshSeriesList()
        self.updateBinsVisibility()
        self.updateTickStepVisibility()
        self.onSettingsChanged()

    # ---------- LaTeX box ----------

    def onSettingsChanged(self, *args):
        # Ignore signals fired while RefreshFromItem() is still populating
        # widgets -- see the _populating comment in __init__.
        if self._populating:
            return
        # Only auto-refresh the LaTeX box if it still matches the last
        # auto-generated text (i.e. the user hasn't hand-edited it since).
        if self.lastAutoLatex is not None and self.plainTextEdit.toPlainText() == self.lastAutoLatex:
            self.regenerateLatexText()

    def onRegenerateLatex(self):
        current = self.plainTextEdit.toPlainText()
        if current.strip() == "" or (self.lastAutoLatex is not None and current == self.lastAutoLatex):
            self.regenerateLatexText()
            return
        reply = QMessageBox.question(
            self, "Regenerate LaTeX",
            "This will discard your manual edits to the LaTeX code and rebuild it "
            "from the current settings. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.regenerateLatexText()

    def regenerateLatexText(self):
        text = self.buildLatex()
        self.plainTextEdit.setPlainText(text)
        self.lastAutoLatex = text

    def syncItemFromUI(self):
        """Push the current widget state onto self.item. Called before both
        building the preview LaTeX and any actual compile (Preview/Accept),
        so those always see live settings even if the box itself hasn't been
        regenerated (e.g. the user hand-edited it)."""
        self.item.Title = self.titleEdit.text()
        self.item.XLabel = self.xLabelEdit.text()
        self.item.YLabel = self.yLabelEdit.text()
        self.item.GridX = self.gridXCheck.isChecked()
        self.item.GridY = self.gridYCheck.isChecked()
        self.item.ShowLegend = self.legendCheck.isChecked()
        self.item.Bins = self.binsSpin.value()
        self.item.XTickStep = self.xTickStepSpin.value()

        def _combo_font(combo):
            text = combo.currentText()
            return "" if text == "Default" else text

        self.item.XTickFontSize = _combo_font(self.xTickFontCombo)
        self.item.YTickFontSize = _combo_font(self.yTickFontCombo)
        self.item.LegendFontSize = _combo_font(self.legendFontCombo)

        self.item.PlotType = self.currentPlotType()

    def buildLatex(self):
        self.syncItemFromUI()

        if not self.item.Series:
            return ""

        plot_type = self.currentPlotType()

        if plot_type == "Pie":
            return self.buildPieLatex()

        if plot_type == "Histogram":
            return self.buildHistogramLatex()

        return self.buildAxisLatex(plot_type)

    @staticmethod
    def styleOption(key, parts):
        """Build a `<key>={part1, part2, ...}` axis option, or "" if parts
        (after dropping falsy entries) ends up empty."""
        parts = [p for p in parts if p]
        if not parts:
            return ""
        return key + "={" + ", ".join(parts) + "}"

    def axisOptions(self, plot_type):
        options = []
        if self.item.Title.strip():
            options.append("title={" + self.item.Title + "}")
        if self.item.XLabel.strip():
            options.append("xlabel={" + self.item.XLabel + "}")
        if self.item.YLabel.strip():
            options.append("ylabel={" + self.item.YLabel + "}")

        if self.item.GridX and self.item.GridY:
            options.append("grid=both")
        elif self.item.GridX:
            options.append("xmajorgrids")
        elif self.item.GridY:
            options.append("ymajorgrids")

        if self.item.ShowLegend:
            options.append("legend pos=north east")
            legend_style = self.styleOption(
                "legend style",
                [f"font=\\{self.item.LegendFontSize}"] if self.item.LegendFontSize else [],
            )
            if legend_style:
                options.append(legend_style)

        options.append("width=0.85\\linewidth")

        if plot_type == "Bar":
            options.append("ybar")
            options.append("bar width=12pt")

        # Any axis-based type plotting a categorical (non-numeric) X column
        # needs pgfplots told about it explicitly, or it will try to parse
        # labels like "Jan" as floating point numbers and fail to compile.
        # The actual unique-value list is only computed at compile time (see
        # csv_parser.resolve_tags) -- showing it literally here would just be
        # noise the user has no reason to hand-edit.
        is_categorical_x = False
        if plot_type in ("LineScatter", "Bar", "Area"):
            series = self.item.Series[0]
            is_categorical_x = not csv_parser.is_numeric_column(self.csvColumns, series["X"], self.item.CsvDecimal)
            if is_categorical_x:
                options.append(csv_parser.TAG_XCOORDS)

        # Rotate + shrink so categorical labels don't overlap; which ones
        # actually show is thinned separately at compile time (XTickStep).
        # Font size is user-controlled either way (XTickFontSize/YTickFontSize).
        x_style_parts = ["rotate=45", "anchor=east"] if is_categorical_x else []
        if self.item.XTickFontSize:
            x_style_parts.append(f"font=\\{self.item.XTickFontSize}")
        x_style = self.styleOption("xticklabel style", x_style_parts)
        if x_style:
            options.append(x_style)

        if self.item.YTickFontSize:
            options.append(self.styleOption("yticklabel style", [f"font=\\{self.item.YTickFontSize}"]))

        return options

    @staticmethod
    def defineColor(name, hex_color):
        """A \\definecolor line for a hex color -- tikz/xcolor's `color=`/`fill=`
        keys don't accept raw '#rrggbb' strings, so every color is predefined
        under a plain name and referenced by that name instead."""
        return f"\\definecolor{{{name}}}{{HTML}}{{{hex_color.lstrip('#').upper()}}}"

    def buildAxisLatex(self, plot_type):
        lines = ["\\begin{center}", "\\begin{tikzpicture}"]

        color_names = [f"plotSeriesColor{idx}" for idx in range(len(self.item.Series))]
        for idx, series in enumerate(self.item.Series):
            lines.append(self.defineColor(color_names[idx], series["Color"]))

        lines.append("\\begin{axis}[")
        lines.append("    " + ",\n    ".join(self.axisOptions(plot_type)))
        lines.append("]")

        csv_filename = self.item.CsvFilename()
        col_sep = TABLE_COL_SEP

        for idx, series in enumerate(self.item.Series):
            color_name = color_names[idx]

            style_parts = [f"color={color_name}"]
            symbol = SYMBOL_LATEX.get(series["Symbol"], "none")
            style_parts.append(f"mark={symbol}")

            if series["LineStyle"] == "None":
                style_parts.append("only marks")
            else:
                style_parts.append(LINE_STYLE_LATEX.get(series["LineStyle"], "solid"))

            style_parts.append(f"line width={series['Thickness']}pt")

            if plot_type == "Area":
                style_parts.append(f"fill={color_name}")
                style_parts.append("fill opacity=0.3")

            addplot_style = ", ".join(style_parts)
            table_opts = f"x={series['X']}, y={series['Y']}, col sep={col_sep}"
            line = f"\\addplot[{addplot_style}] table[{table_opts}] {{{csv_filename}}}"
            line += " \\closedcycle;" if plot_type == "Area" else ";"
            lines.append(line)

            if self.item.ShowLegend:
                lines.append("\\addlegendentry{" + series["Name"] + "}")

        lines.append("\\end{axis}")
        lines.append("\\end{tikzpicture}")
        lines.append("\\end{center}")
        return "\n".join(lines)

    def buildHistogramLatex(self):
        # Bin edges/counts are only computed at actual compile time (see
        # csv_parser.resolve_tags), not here: it's a derived aggregate (bin
        # counts), not a row-for-row passthrough of the CSV, so showing the
        # raw numbers in this box would just be noise the user has no reason
        # to hand-edit -- the tag stands in for them instead.
        series = self.item.Series[0]

        lines = ["\\begin{center}", "\\begin{tikzpicture}"]
        lines.append(self.defineColor("plotSeriesColor0", series["Color"]))
        lines.append("\\begin{axis}[")

        options = []
        if self.item.Title.strip():
            options.append("title={" + self.item.Title + "}")
        if self.item.XLabel.strip():
            options.append("xlabel={" + self.item.XLabel + "}")
        if self.item.YLabel.strip():
            options.append("ylabel={" + self.item.YLabel + "}")
        if self.item.GridX and self.item.GridY:
            options.append("grid=both")
        elif self.item.GridX:
            options.append("xmajorgrids")
        elif self.item.GridY:
            options.append("ymajorgrids")
        options.append("width=0.85\\linewidth")
        options.append("ybar interval")
        # ybar interval places a tick at every bin edge; with more than a
        # couple of bins the plain horizontal labels overlap, so always
        # rotate them (font size is still up to the user, via XTickFontSize).
        x_style_parts = ["rotate=45", "anchor=east"]
        if self.item.XTickFontSize:
            x_style_parts.append(f"font=\\{self.item.XTickFontSize}")
        options.append(self.styleOption("xticklabel style", x_style_parts))

        if self.item.YTickFontSize:
            options.append(self.styleOption("yticklabel style", [f"font=\\{self.item.YTickFontSize}"]))

        lines.append("    " + ",\n    ".join(options))
        lines.append("]")

        # The tag sits alone on its own line: if ever left unresolved, "%"
        # only comments out this one line, leaving an empty (not unterminated)
        # coordinates block rather than corrupting the rest of the picture.
        lines.append("\\addplot[fill=plotSeriesColor0] coordinates {")
        lines.append(csv_parser.TAG_HISTDATA)
        lines.append("};")

        lines.append("\\end{axis}")
        lines.append("\\end{tikzpicture}")
        lines.append("\\end{center}")
        return "\n".join(lines)

    def buildPieLatex(self):
        series = self.item.Series[0]
        labels_raw = self.csvColumns.get(series["X"], [])
        values_raw = csv_parser.get_numeric_column(self.csvColumns, series["Y"], self.item.CsvDecimal)

        totals = {}
        order = []
        for label, value in zip(labels_raw, values_raw):
            if value is None:
                continue
            if label not in totals:
                totals[label] = 0.0
                order.append(label)
            totals[label] += value

        total = sum(totals.values())
        if total <= 0 or not order:
            return ""

        lines = ["\\begin{center}", "\\begin{tikzpicture}"]
        for idx in range(len(order)):
            hex_color = DEFAULT_PALETTE[idx % len(DEFAULT_PALETTE)]
            lines.append(self.defineColor(f"pieSliceColor{idx}", hex_color))

        angle = 90.0
        radius = 2.0
        for idx, label in enumerate(order):
            fraction = totals[label] / total
            sweep = fraction * 360.0
            end_angle = angle - sweep
            color_name = f"pieSliceColor{idx}"
            lines.append(
                f"\\draw[fill={color_name}, draw=white] (0,0) -- ({angle:.3f}:{radius}) "
                f"arc ({angle:.3f}:{end_angle:.3f}:{radius}) -- cycle;"
            )
            mid_angle = (angle + end_angle) / 2.0
            label_radius = radius * 0.65
            percent = fraction * 100
            lines.append(
                f"\\node at ({mid_angle:.3f}:{label_radius:.3f}) "
                f"{{\\small {label} ({percent:.1f}\\%)}};"
            )
            angle = end_angle

        if self.item.Title.strip():
            lines.append(f"\\node at (0,{radius + 0.6}) {{\\large {self.item.Title}}};")

        lines.append("\\end{tikzpicture}")
        lines.append("\\end{center}")
        return "\n".join(lines)

    # ---------- preview compile ----------

    def onPreview(self):
        latex_body = self.plainTextEdit.toPlainText()
        if not latex_body.strip():
            QMessageBox.information(self, "Nothing to preview", "There is no LaTeX content to compile yet.")
            return

        self.syncItemFromUI()

        resolved = csv_parser.resolve_tags(
            latex_body, self.item.Series, self.item.CsvPath,
            self.item.CsvDelimiter, self.item.CsvDecimal, self.item.CsvHasHeader,
            self.item.Bins, xtick_step=self.item.XTickStep,
        )

        # CSV and preview.tex live side by side in the same folder, and
        # latexPreview compiles in place there (SetTexFile), so the CSV is
        # referenced by its normal relative filename -- same as everywhere
        # else in this file. Created once, reused across repeated Preview
        # clicks; this dialog owns and cleans up the folder (see done()).
        if self._previewDir is None:
            self._previewDir = tempfile.mkdtemp(prefix="beamerQT_plotpreview_")

        if self.item.CsvPath and os.path.exists(self.item.CsvPath):
            csv_parser.write_normalized_csv(
                self.item.CsvPath, os.path.join(self._previewDir, self.item.CsvFilename()),
                delimiter=self.item.CsvDelimiter, decimal=self.item.CsvDecimal,
                has_header=self.item.CsvHasHeader,
            )

        tex_path = os.path.join(self._previewDir, "preview.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write("\\documentclass{beamer}\n")
            with open("core/preamble.tex", "r", encoding="utf-8") as pf:
                f.write(pf.read())
            f.write("\n\\begin{document}\n\\begin{frame}\n")
            f.write(resolved)
            f.write("\n\\end{frame}\n\\end{document}\n")

        self._pendingPreviewLatex = resolved
        self.latexPreview.SetTexFile(tex_path)
        self.latexPreview.Compile()

    def _onPreviewCompileFinished(self, success):
        # Records what the Preview panel actually has on screen right now,
        # so onAccept() can tell whether it's still current and skip
        # recompiling. A failed compile can't be reused for anything.
        if success:
            self._lastPreviewedLatex = self._pendingPreviewLatex
            self._previewPdfPath = os.path.join(self._previewDir, "preview.pdf")
        else:
            self._lastPreviewedLatex = None
            self._previewPdfPath = None

    def done(self, result):
        self.latexPreview.Cleanup()
        if self._previewDir and os.path.isdir(self._previewDir):
            shutil.rmtree(self._previewDir, ignore_errors=True)
        super().done(result)

    # ---------- accept / cancel ----------

    def onAccept(self):
        self.syncItemFromUI()
        self.item.LatexCode = self.plainTextEdit.toPlainText()

        resolved = csv_parser.resolve_tags(
            self.item.LatexCode, self.item.Series, self.item.CsvPath,
            self.item.CsvDelimiter, self.item.CsvDecimal, self.item.CsvHasHeader,
            self.item.Bins, xtick_step=self.item.XTickStep,
        )

        # The inline widget's preview is only (re)compiled here, once, on
        # Accept -- compile_and_store_preview caches it on self.item.Pixmap
        # and saves it into the active document's persistent media folder,
        # so nothing needs to recompile (or even re-read from disk) on
        # every redisplay, this session or a later one.
        #
        # If the Preview panel already compiled this exact content, reuse
        # that PDF instead of running pdflatex a second time -- just
        # re-rasterize it at the (higher) resolution the stored preview
        # uses, which is cheap compared to the actual compile.
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            reused_pixmap = None
            if resolved == self._lastPreviewedLatex and self._previewPdfPath:
                reused_pixmap = plot_compiler.render_pdf_page(self._previewPdfPath, dpi=150)
            plot_compiler.compile_and_store_preview(self.item, pixmap=reused_pixmap)
        finally:
            QApplication.restoreOverrideCursor()

        self.accept()

    def result_item(self):
        return self.item
