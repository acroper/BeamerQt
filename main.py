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



from PyQt6 import QtWidgets
from gui.mainwindow import *
import shutil
import multiprocessing
import platform
import sys


def main():
   
    # Launching GUI
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    
    
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
