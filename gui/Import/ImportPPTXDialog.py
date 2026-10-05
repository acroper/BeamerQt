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


import os

from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtWidgets import QDialogButtonBox, QFileDialog, QMessageBox, QApplication

from core.beamerDocument import beamerDocument
from core.template import BeamerTemplate
from gui.guidialogs import openFileNameDialog


class ImportPPTXDialog(QtWidgets.QDialog):
    """
    Imports a PowerPoint file into an import folder holding the new .bqt file
    and its images, chart data and diagrams. After exec(), FileName is the
    saved .bqt file.
    """

    def __init__(self, WorkDirectory, Config, parent=None):

        super(ImportPPTXDialog, self).__init__(parent)

        uic.loadUi('gui/Import/ImportPPTX.ui', self)

        self.WorkDirectory = WorkDirectory
        self.Config = Config
        self.FileName = ""

        self.ImportButton = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        self.ImportButton.setText("Import")

        self.LoadThemes()

        self.pptxBrowse.clicked.connect(self.BrowsePPTX)
        self.folderBrowse.clicked.connect(self.BrowseFolder)
        self.pptxEdit.textChanged.connect(self.PPTXChanged)
        self.folderEdit.textChanged.connect(self.UpdatePreview)
        for check in (self.imagesCheck, self.chartsCheck, self.diagramsCheck):
            check.toggled.connect(self.UpdatePreview)

        self.buttonBox.accepted.connect(self.Import)
        self.buttonBox.rejected.connect(self.reject)

        self.UpdatePreview()


    def LoadThemes(self):
        # Same list as the configurator
        self.ThemeList = []
        default = BeamerTemplate().Name
        for file in sorted(os.listdir("templates")):
            if file.endswith("xml"):
                templ = BeamerTemplate()
                templ.ReadXMLFile(os.path.join("templates", file))
                self.ThemeList.append(templ)
                self.themeBox.addItem(templ.Name)

        index = self.themeBox.findText(default)
        if index >= 0:
            self.themeBox.setCurrentIndex(index)


    def BrowsePPTX(self):
        filename = openFileNameDialog(self, "", "PowerPoint files (*.pptx)")
        if filename != "":
            self.pptxEdit.setText(filename)


    def BrowseFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select the import folder", self.folderEdit.text())
        if folder != "":
            self.folderEdit.setText(folder)


    def PPTXChanged(self, filename):
        # Default import folder: next to the PowerPoint file, named after it
        if filename.lower().endswith(".pptx"):
            self.folderEdit.setText(os.path.splitext(filename)[0])
        self.UpdatePreview()


    def BqtPath(self):
        name = os.path.splitext(os.path.basename(self.pptxEdit.text()))[0]
        return os.path.join(self.folderEdit.text(), name + ".bqt")


    def UpdatePreview(self):
        ready = self.pptxEdit.text().strip() != "" and self.folderEdit.text().strip() != ""
        self.ImportButton.setEnabled(ready)

        if not ready:
            self.previewLabel.setText("")
            return

        lines = [self.folderEdit.text().rstrip("/\\") + os.sep, "    " + os.path.basename(self.BqtPath())]
        if self.imagesCheck.isChecked():
            lines.append("    images" + os.sep)
        if self.chartsCheck.isChecked():
            lines.append("    data" + os.sep)
        if self.diagramsCheck.isChecked():
            lines.append("    diagrams" + os.sep)
        self.previewLabel.setText("\n".join(lines))


    def Import(self):
        pptx = self.pptxEdit.text().strip()
        folder = self.folderEdit.text().strip()

        if not os.path.isfile(pptx):
            QMessageBox.warning(self, self.windowTitle(), "The PowerPoint file does not exist.")
            return

        if os.path.isdir(folder) and os.listdir(folder):
            button = QMessageBox.question(self, self.windowTitle(),
                                          "The import folder is not empty. Existing files may be replaced.\n\nContinue?")
            if button != QMessageBox.StandardButton.Yes:
                return

        try:
            from core.beamerpptx import BeamerPPT
        except ImportError as e:
            QMessageBox.warning(self, self.windowTitle(),
                                "python-pptx is required to import PowerPoint files.\n\n" + str(e))
            return

        options = {"TitlePage": self.titlePageCheck.isChecked(),
                   "Images": self.imagesCheck.isChecked(),
                   "Equations": self.equationsCheck.isChecked(),
                   "Tables": self.tablesCheck.isChecked(),
                   "Charts": self.chartsCheck.isChecked(),
                   "Diagrams": self.diagramsCheck.isChecked()}

        QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            os.makedirs(folder, exist_ok=True)

            Document = beamerDocument(self.WorkDirectory)
            Document.Config = self.Config
            if self.ThemeList:
                Document.Template = self.ThemeList[self.themeBox.currentIndex()]

            messages = BeamerPPT().Import(pptx, Document, folder, options)

            if len(Document.Slides) == 0:
                Document.NewSlide()

            Document.WriteFile(self.BqtPath())
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, self.windowTitle(),
                                "Could not import " + os.path.basename(pptx) + "\n\n" + str(e))
            return
        QApplication.restoreOverrideCursor()

        if messages:
            QMessageBox.information(self, self.windowTitle(),
                                    "Imported with some content skipped or approximated:\n\n"
                                    + "\n".join(self.Summary(messages)))

        self.FileName = self.BqtPath()
        self.accept()


    def Summary(self, messages):
        # Repeated messages once, with a count
        counts = {}
        for message in messages:
            counts[message] = counts.get(message, 0) + 1
        return [m if n == 1 else m + " (x" + str(n) + ")" for m, n in counts.items()]
