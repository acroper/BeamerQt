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
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
    QCheckBox, QRadioButton, QButtonGroup, QPushButton, QTableWidget,
    QTableWidgetItem, QDialogButtonBox, QLabel, QFileDialog, QWidget,
)
from PyQt6.QtCore import Qt

from . import csv_parser
from .SeriesEditDialog import DEFAULT_PALETTE

# Two pinned rows sit at the top of the preview table, right under the real
# column headers, holding the per-column X/Y picker widgets; actual data
# preview rows start below them.
X_ROW = 0
Y_ROW = 1
PINNED_ROWS = 2


class CsvFormatDialog(QDialog):
    """
    Lets the user pick a CSV file, confirm the delimiter / decimal separator /
    header row, and quickly assign which column is X and which columns are Y
    -- one X radio button plus a Y checkbox (or radio, for single-series plot
    types) per detected column, pinned into the top two rows of the preview
    table itself (directly under each column's header) so a whole set of
    series can be created in one step instead of going through "New Series"
    one at a time.
    """

    def __init__(self, initial_path="", plot_type="LineScatter", existing_series=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BeamerQT - Load CSV")
        self.resize(650, 480)

        self.plot_type = plot_type
        self.path = initial_path
        self.headers = []
        self.columns = {}

        self.xButtons = {}
        self.yButtons = {}
        self.xGroup = None
        self.yGroup = None

        existing_series = existing_series or []
        self._initial_x = existing_series[0].get("X") if existing_series and plot_type != "Histogram" else None
        self._initial_y = {s.get("Y") for s in existing_series if s.get("Y")}

        layout = QVBoxLayout(self)

        pathRow = QHBoxLayout()
        self.pathLabel = QLabel(self.path or "No file selected")
        self.browseButton = QPushButton("Browse...")
        pathRow.addWidget(self.pathLabel, 1)
        pathRow.addWidget(self.browseButton)
        layout.addLayout(pathRow)

        form = QFormLayout()

        self.delimiterCombo = QComboBox()
        self.delimiterCombo.addItems(list(csv_parser.DELIMITERS.keys()))
        form.addRow("Delimiter", self.delimiterCombo)

        self.decimalCombo = QComboBox()
        self.decimalCombo.addItems(["Period (.)", "Comma (,)"])
        form.addRow("Decimal separator", self.decimalCombo)

        self.headerCheck = QCheckBox("First row contains column names")
        self.headerCheck.setChecked(True)
        form.addRow("", self.headerCheck)

        layout.addLayout(form)

        self.previewTable = QTableWidget()
        self.previewTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.previewTable, 1)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(self.buttonBox)

        self.browseButton.clicked.connect(self.browseFile)
        self.delimiterCombo.currentTextChanged.connect(self.refreshPreview)
        self.decimalCombo.currentTextChanged.connect(self.refreshPreview)
        self.headerCheck.stateChanged.connect(self.refreshPreview)
        self.buttonBox.accepted.connect(self.tryAccept)
        self.buttonBox.rejected.connect(self.reject)

        if self.path:
            self.loadFile(self.path)

    def browseFile(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV file", "", "CSV files (*.csv);;All files (*)"
        )
        if path:
            self.loadFile(path)

    def loadFile(self, path):
        self.path = path
        self.pathLabel.setText(path)
        delimiter = csv_parser.sniff_delimiter(path)
        for name, char in csv_parser.DELIMITERS.items():
            if char == delimiter:
                self.delimiterCombo.setCurrentText(name)
                break
        self.refreshPreview()

    def currentDelimiter(self):
        return csv_parser.DELIMITERS.get(self.delimiterCombo.currentText(), ",")

    def currentDecimal(self):
        return "," if self.decimalCombo.currentText().startswith("Comma") else "."

    @staticmethod
    def _centered(widget):
        """Wrap a checkbox/radio so it's centered within its table cell."""
        container = QWidget()
        hbox = QHBoxLayout(container)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(widget, alignment=Qt.AlignmentFlag.AlignCenter)
        return container

    def refreshPreview(self, *args):
        if not self.path:
            return
        try:
            headers, columns = csv_parser.read_csv(
                self.path,
                delimiter=self.currentDelimiter(),
                has_header=self.headerCheck.isChecked(),
            )
        except OSError:
            return

        self.headers = headers
        self.columns = columns

        # Preserve whatever the user already picked in this dialog session;
        # only fall back to the item's pre-existing series the very first
        # time the table is built (so reopening "Load CSV" on an already
        # configured plot shows its current X/Y assignment).
        is_first_build = not self.xButtons and not self.yButtons
        if is_first_build:
            old_x = self._initial_x
            old_y = set(self._initial_y)
        else:
            old_x = next((h for h, b in self.xButtons.items() if b.isChecked()), None)
            old_y = {h for h, b in self.yButtons.items() if b.isChecked()}

        # Histogram only has a single value column (X is unused); Pie has
        # exactly one series too, so Y (its value column) is single-select
        # like X instead of a multi-check list.
        show_x_row = self.plot_type != "Histogram"
        x_label = "Label" if self.plot_type == "Pie" else "X"
        y_label = "Value" if self.plot_type == "Pie" else "Y"

        self.xButtons = {}
        self.yButtons = {}
        self.xGroup = QButtonGroup(self)
        self.xGroup.setExclusive(True)
        if self.plot_type in ("Pie", "Histogram"):
            self.yGroup = QButtonGroup(self)
            self.yGroup.setExclusive(True)
        else:
            self.yGroup = None

        row_count = min(8, max((len(v) for v in columns.values()), default=0))

        self.previewTable.clear()
        self.previewTable.setColumnCount(len(headers))
        self.previewTable.setHorizontalHeaderLabels(headers)
        self.previewTable.setRowCount(PINNED_ROWS + row_count)
        self.previewTable.setVerticalHeaderLabels(
            [x_label, y_label] + [str(i + 1) for i in range(row_count)]
        )
        self.previewTable.setRowHeight(X_ROW, 28)
        self.previewTable.setRowHeight(Y_ROW, 28)

        for col_idx, header in enumerate(headers):
            if show_x_row:
                xbtn = QRadioButton()
                self.xGroup.addButton(xbtn)
                self.previewTable.setCellWidget(X_ROW, col_idx, self._centered(xbtn))
                self.xButtons[header] = xbtn
                if header == old_x:
                    xbtn.setChecked(True)
            else:
                self.previewTable.setItem(X_ROW, col_idx, QTableWidgetItem(""))

            ybtn = QRadioButton() if self.yGroup is not None else QCheckBox()
            if self.yGroup is not None:
                self.yGroup.addButton(ybtn)
            self.previewTable.setCellWidget(Y_ROW, col_idx, self._centered(ybtn))
            self.yButtons[header] = ybtn
            if header in old_y:
                ybtn.setChecked(True)

            values = columns.get(header, [])
            for row_idx in range(row_count):
                value = values[row_idx] if row_idx < len(values) else ""
                self.previewTable.setItem(PINNED_ROWS + row_idx, col_idx, QTableWidgetItem(value))

        if show_x_row and old_x is None and headers:
            self.xButtons[headers[0]].setChecked(True)

    def tryAccept(self):
        if not self.path or not self.headers:
            return
        self.accept()

    def result_data(self):
        """Return (path, delimiter, decimal, has_header, headers, columns)."""
        return (
            self.path,
            self.currentDelimiter(),
            self.currentDecimal(),
            self.headerCheck.isChecked(),
            self.headers,
            self.columns,
        )

    def result_series(self):
        """
        Build one series dict per checked Y column, all sharing the single
        checked X column (empty for Histogram, which doesn't use X). Returns
        [] if no Y column has been checked yet.
        """
        x_header = None
        if self.xButtons:
            x_header = next((h for h, b in self.xButtons.items() if b.isChecked()), None)

        if self.plot_type != "Histogram" and x_header is None:
            return []

        series = []
        idx = 0
        for header, btn in self.yButtons.items():
            if not btn.isChecked():
                continue
            series.append({
                "Name": header,
                "X": x_header or "",
                "Y": header,
                "LineStyle": "Solid",
                "Thickness": 1.0,
                "Symbol": "None",
                "Color": DEFAULT_PALETTE[idx % len(DEFAULT_PALETTE)],
            })
            idx += 1
        return series
