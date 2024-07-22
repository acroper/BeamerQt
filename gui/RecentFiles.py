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



class RecentFiles:
    
    def __init__(self):
        # Load recent files from disk
        self.RecentList = []
        
        self.RecentNames = []
        
        self.HistoryFile = "history.txt"
        
        self.LoadList()
        
    
    def LoadList(self):
        
        if os.path.exists(self.HistoryFile):
            hfile = open(self.HistoryFile, "r")
            self.RecentList = hfile.readlines()
        else:
            hfile = open(self.HistoryFile, "w")
        
        hfile.close()
        
        self.CheckList()
    
    def CheckList(self):
        tmplist = self.RecentList.copy()
        
        tmplist.reverse()
        self.RecentList.clear()
        
        for elemn in tmplist:
            
            if elemn not in ["", "\n"]:
                if elemn not in self.RecentList:
                    elemn = elemn.replace("\n","")
                    self.RecentList.append(elemn)
        
        self.RecentList.reverse()
        # reduce the list
        if len(self.RecentList) > 10:
            for k in range( len(self.RecentList) - 10 ) :
                self.RecentList.pop(0)
                
                
                
    def SaveRecent(self):
        hfile = open(self.HistoryFile, "w")
        
        for elemn in self.RecentList:
            hfile.write(elemn + "\n")
        
        hfile.close()
    
    def AppendFile(self, filename):
        
        self.RecentList.append(filename)
        self.CheckList()
        self.SaveRecent()
        
            
            
            
            

        
            

