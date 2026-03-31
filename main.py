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


from PyQt6 import QtWidgets, QtGui
from gui.mainwindow import *
from core.template import sync_templates_to_user_dir
import shutil
import multiprocessing
import platform
import sys
import os
import argparse
from PyQt6 import QtCore


def _set_runtime_workdir() -> None:
    if getattr(sys, "frozen", False):
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    else:
        base_dir = os.path.abspath(os.path.dirname(__file__))

    os.chdir(base_dir)


def _build_accessible_qss(app: QtWidgets.QApplication) -> str:
    palette = app.palette()
    window_color = palette.color(QtGui.QPalette.ColorRole.Window)
    text_color = palette.color(QtGui.QPalette.ColorRole.Text)
    window_text = palette.color(QtGui.QPalette.ColorRole.WindowText)
    base_color = palette.color(QtGui.QPalette.ColorRole.Base)
    button_color = palette.color(QtGui.QPalette.ColorRole.Button)
    button_text = palette.color(QtGui.QPalette.ColorRole.ButtonText)
    highlight_color = palette.color(QtGui.QPalette.ColorRole.Highlight)
    highlighted_text = palette.color(QtGui.QPalette.ColorRole.HighlightedText)
    border_color = palette.color(QtGui.QPalette.ColorRole.Mid)

    dark_theme = window_color.lightness() < 128
    if dark_theme:
        base_color = QtGui.QColor("#ffffff")
        text_color = QtGui.QColor("#111111")
        window_text = QtGui.QColor("#f2f2f2")
        button_color = QtGui.QColor("#f4f4f4")
        button_text = QtGui.QColor("#111111")
        border_color = QtGui.QColor("#8a8a8a")

    return f"""
    QLabel {{
        color: {window_text.name()};
    }}
    QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox, QComboBox,
    QDateEdit, QTimeEdit, QDateTimeEdit, QListWidget, QTreeWidget, QTableWidget {{
        background-color: {base_color.name()};
        color: {text_color.name()};
        selection-background-color: {highlight_color.name()};
        selection-color: {highlighted_text.name()};
        border: 1px solid {border_color.name()};
    }}
    QComboBox QAbstractItemView {{
        background-color: {base_color.name()};
        color: {text_color.name()};
        selection-background-color: {highlight_color.name()};
        selection-color: {highlighted_text.name()};
    }}
    QHeaderView::section {{
        background-color: {button_color.name()};
        color: {button_text.name()};
        border: 1px solid {border_color.name()};
        padding: 4px;
    }}
    QPushButton, QToolButton {{
        background-color: {button_color.name()};
        color: {button_text.name()};
        border: 1px solid {border_color.name()};
        border-radius: 4px;
        padding: 2px 6px;
    }}
    QPushButton:hover, QToolButton:hover {{
        border: 1px solid {highlight_color.name()};
    }}
    QPushButton:pressed, QToolButton:pressed {{
        background-color: {highlight_color.name()};
        color: {highlighted_text.name()};
    }}
    """


def main():
    _set_runtime_workdir()
    sync_templates_to_user_dir()
   
    parser = argparse.ArgumentParser(add_help=True, description="BeamerQt")
    parser.add_argument("file", nargs="?", help="Optional .bqt file to open")
    parser.add_argument("-o", "--open", dest="open_file", help="Open a .bqt file")
    args, _unknown = parser.parse_known_args()

    file_to_open = args.open_file or args.file
    if file_to_open:
        file_to_open = os.path.abspath(os.path.expanduser(file_to_open))

    # Launching GUI
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet((app.styleSheet() or "") + "\n" + _build_accessible_qss(app))

    window = MainWindow()

    if file_to_open and os.path.exists(file_to_open):
        QtCore.QTimer.singleShot(0, lambda p=file_to_open: window.Open(p))
    
    
    app.aboutToQuit.connect(app.deleteLater)
    app.exec()
    
    # Closing and deleting temporal folder
    try:
        shutil.rmtree(window.WorkDirectory)
    except: 
        pass
    
    
if __name__ == "__main__":
    # macOS multiprocessing compatibility fix
    if platform.system() == "Darwin":
        try:
            multiprocessing.set_start_method("fork")
        except RuntimeError:
            pass
        
    if platform.system() == "Windows":
        # Windows issue required to create the executable with pyinstall
        multiprocessing.freeze_support()

    main()
