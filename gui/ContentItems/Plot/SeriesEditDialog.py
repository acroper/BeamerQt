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

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QLineEdit,
    QDoubleSpinBox, QPushButton, QDialogButtonBox, QColorDialog,
)
from PyQt6.QtGui import QColor


LINE_STYLES = ["Solid", "Dashed", "Dotted", "DashDot", "None"]
SYMBOLS = ["None", "Circle", "Square", "Triangle", "Diamond", "Star", "Plus", "X"]

# A small, distinct qualitative palette used both as the default series color
# suggestion and for auto-assigned Pie slice colors.
DEFAULT_PALETTE = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2",
    "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD",
]


class SeriesEditDialog(QDialog):
    """Add/edit a single Plot series: X/Y columns plus line/symbol/color styling."""

    def __init__(self, headers, series=None, plot_type="LineScatter", palette_index=0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BeamerQT - Series Editor")
        self.plot_type = plot_type
        self.is_style_hidden = plot_type in ("Pie", "Histogram")

        self.color = (series or {}).get("Color", DEFAULT_PALETTE[palette_index % len(DEFAULT_PALETTE)])

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.xCombo = QComboBox()
        self.xCombo.addItems(headers)
        x_label = "Label Column" if plot_type == "Pie" else "X Series"
        if plot_type == "Histogram":
            x_label = "X Series (unused)"
        form.addRow(x_label, self.xCombo)

        self.yCombo = QComboBox()
        self.yCombo.addItems(headers)
        y_label = "Value Column" if plot_type == "Pie" else "Y Series"
        form.addRow(y_label, self.yCombo)

        self.nameEdit = QLineEdit()
        form.addRow("Series Name", self.nameEdit)

        self.lineStyleCombo = QComboBox()
        self.lineStyleCombo.addItems(LINE_STYLES)
        form.addRow("Line Type", self.lineStyleCombo)

        self.thicknessSpin = QDoubleSpinBox()
        self.thicknessSpin.setRange(0.1, 10.0)
        self.thicknessSpin.setSingleStep(0.1)
        self.thicknessSpin.setValue(1.0)
        form.addRow("Thickness (pt)", self.thicknessSpin)

        self.symbolCombo = QComboBox()
        self.symbolCombo.addItems(SYMBOLS)
        form.addRow("Symbol", self.symbolCombo)

        self.colorButton = QPushButton()
        self.colorButton.clicked.connect(self.pickColor)
        form.addRow("Color", self.colorButton)

        layout.addLayout(form)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        if self.is_style_hidden:
            self.lineStyleCombo.setEnabled(False)
            self.thicknessSpin.setEnabled(False)
            self.symbolCombo.setEnabled(False)
            self.colorButton.setEnabled(False)
        if plot_type == "Histogram":
            self.xCombo.setEnabled(False)

        self.updateColorSwatch()

        if series:
            self.loadSeries(series)
        else:
            if headers:
                self.nameEdit.setText(self.yCombo.currentText())
            self.yCombo.currentTextChanged.connect(self.autofillName)

    def autofillName(self, text):
        if not self.nameEdit.isModified():
            self.nameEdit.setText(text)

    def updateColorSwatch(self):
        self.colorButton.setStyleSheet(f"background-color: {self.color};")
        self.colorButton.setText(self.color)

    def pickColor(self):
        color = QColorDialog.getColor(QColor(self.color), self, "Select series color")
        if color.isValid():
            self.color = color.name()
            self.updateColorSwatch()

    def loadSeries(self, series):
        self.xCombo.setCurrentText(series.get("X", ""))
        self.yCombo.setCurrentText(series.get("Y", ""))
        self.nameEdit.setText(series.get("Name", ""))
        self.lineStyleCombo.setCurrentText(series.get("LineStyle", "Solid"))
        self.thicknessSpin.setValue(float(series.get("Thickness", 1.0)))
        self.symbolCombo.setCurrentText(series.get("Symbol", "None"))
        self.color = series.get("Color", self.color)
        self.updateColorSwatch()

    def result_series(self):
        return {
            "Name": self.nameEdit.text().strip() or self.yCombo.currentText(),
            "X": self.xCombo.currentText(),
            "Y": self.yCombo.currentText(),
            "LineStyle": self.lineStyleCombo.currentText(),
            "Thickness": self.thicknessSpin.value(),
            "Symbol": self.symbolCombo.currentText(),
            "Color": self.color,
        }
