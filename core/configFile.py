#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 12:58:24 2024

@author: acroper
"""

import os 

import platform

from pathlib import Path

import configparser


class Config:
    
    def __init__(self):
        
        self.ConfigFolder = ""
        
        self.DefineFolder()
        
        self.config = None
        
        self.StartConfig()

        
    def DefineFolder(self):
        
        LocalSystem = platform.system() 
        
        if LocalSystem == "Linux" or LocalSystem == "Darwin":
            self.ConfigFolder = os.path.join(os.path.expanduser("~"), ".config/BeamerQt")
            
        if LocalSystem == "Windows":
            self.ConfigFolder = os.path.join( os.environ.get("APPDATA"), "BeamerQt")
            
        
        if not os.path.exists(self.ConfigFolder):
            os.makedirs(self.ConfigFolder)

            
    def StartConfig(self):
        
        self.configFile = os.path.join ( self.ConfigFolder, "config.ini")
        
        self.config = configparser.ConfigParser()
        
        if not os.path.exists(self.configFile):
            self.DefaultSettings()
            self.SaveConfig()
        
        self.config.read ( self.configFile )
        
    
    def DefaultSettings(self):
        self.config.add_section("CustomThemes")
        self.config.add_section("Converters")
        
        self.config.add_section("SoftwarePath")
        
        self.config.set("Converters", "TEX-PDF", "pdflatex -interaction=nonstopmode $$i ")
        self.config.set("Converters", "SVG-PDF", "inkscape --file=$$i --export-area-drawing --without-gui --export-pdf=$$o ")
        
    
    def SaveConfig(self):
        with open(self.configFile,"w") as file_object:
            self.config.write(file_object)
        
        
        
        
    