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

import sys
import os

import xml.etree.ElementTree as ET

import tempfile


class beamerDocument():
    
    def __init__(self, Path):
        
        # Define a path inside the given Path. It is expected to be
        # a temporary folder.
        
        self.DocLocation =  tempfile.mkdtemp(prefix= Path+"/" )
        
        # Store everything in DocLocation
        
        
        self.Slides = []
        
    
    def NewSlide(self, Location):
        None
        
    def RemoveSlide(self, Location):
        None
        
    def InsertSlide(self, Slide, Location):
        None
    
    def SaveXML (self):
        None
        
    def GenLaTeX(self):
        None
    
    def ExportPDF(self, filename):
        None
    
    
    def WriteFile(self, filename):
        None
    
    def ReadFile(self, filename):
        None
        
