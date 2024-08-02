#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 12:58:24 2024

@author: acroper
"""

import os 

import platform

from pathlib import Path


class Config:
    
    def __init__(self):
        
        self.ConfigFolder = ""
        
        self.DefineFolder()

        
    def DefineFolder(self):
        
        LocalSystem = platform.system() 
        
        if LocalSystem == "Linux" or LocalSystem == "Darwin":
            self.ConfigFolder = os.path.join(os.path.expanduser("~"), ".config/BeamerQt")
            
        if LocalSystem == "Windows":
            self.ConfigFolder = os.path.join( os.environ.get("APPDATA"), "BeamerQt")
            
        
        if not os.path.exists(self.ConfigFolder):
            os.makedirs(self.ConfigFolder)
        
        
    