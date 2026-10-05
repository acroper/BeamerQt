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



from PyQt6 import QtGui, QtWidgets
from gui.mainwindow import *
import shutil
import multiprocessing
import platform
import sys
import os
import argparse
from PyQt6 import QtCore


def apply_light_theme(app):
    app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(240, 240, 240))
    palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(245, 245, 245))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(255, 255, 220))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(240, 240, 240))
    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(0, 120, 215))
    palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.ColorRole.PlaceholderText, QtGui.QColor(96, 96, 96))

    palette.setColor(
        QtGui.QPalette.ColorGroup.Disabled,
        QtGui.QPalette.ColorRole.WindowText,
        QtGui.QColor(120, 120, 120),
    )
    palette.setColor(
        QtGui.QPalette.ColorGroup.Disabled,
        QtGui.QPalette.ColorRole.Text,
        QtGui.QColor(120, 120, 120),
    )
    palette.setColor(
        QtGui.QPalette.ColorGroup.Disabled,
        QtGui.QPalette.ColorRole.ButtonText,
        QtGui.QColor(120, 120, 120),
    )

    app.setPalette(palette)


def main():
   
    parser = argparse.ArgumentParser(add_help=True, description="BeamerQt")
    parser.add_argument("file", nargs="?", help="Optional .bqt file to open")
    parser.add_argument("-o", "--open", dest="open_file", help="Open a .bqt file")
    args, _unknown = parser.parse_known_args()

    file_to_open = args.open_file or args.file
    if file_to_open:
        file_to_open = os.path.abspath(os.path.expanduser(file_to_open))

    # Launching GUI
    app = QtWidgets.QApplication(sys.argv)
    apply_light_theme(app)

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
