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
"""
This module was created with the assistance of Google Gemini chat
"""

import sys
from PyQt6.QtCore import Qt, QSize, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QFontMetrics, QPalette, QFont
from PyQt6.QtWidgets import *

class DualSlider(QWidget):
    
    ValueUpdated = pyqtSignal()
    Released = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.minimum = 0
        self.maximum = 100
        self.value1 = 25
        self.value2 = 50
        self.value3 = 75
        self.handleWidth = 20
        self.handleHeight = 10

        self.selected1 = False
        self.selected2 = False
        self.selected3 = False
        
        self.Minimum = 10
        self.Maximum = 90
        
        self.ActiveSliders = 3
        
        self.Updating = False
        
        self.showNumbers = True
        
        self.NextRounding = 5
        
        self.LabelPosition = "Down"
    
    
    def UpdateValues(self, values):
        self.Updating = True
        
        if len(values) > 0:
            self.value1 = values[0]
        if len(values) > 1:
            self.value2 = values[1]
        if len(values) > 2:
            self.value3 = values[2]
        
        self.update()
        
        self.Updating = False
    
    
    def setSliders(self, number):
        self.ActiveSliders = number
        self.update()
    
    def adjustValues(self, PosValues):
        	current = 0
        	for k in range(len(PosValues)):
        		if PosValues[k]-current < self.Minimum:
        			PosValues[k] = current + self.Minimum
        		current = PosValues[k]
        		
        	current = 100
        	for k in range(len(PosValues)):
        		if current-PosValues[-1-k] < self.Minimum:
        			PosValues[-1-k] = current - self.Minimum
        		current = PosValues[-1-k]
        	return PosValues
    
    def verifyValues(self):
        # Check range of the values
        if self.ActiveSliders ==3:
            PosValues = [self.value1, self.value2, self.value3]
        if self.ActiveSliders == 2:
            PosValues = [self.value1, self.value2]
        if self.ActiveSliders == 1:
            PosValues = [self.value1]
        if self.ActiveSliders ==0:
            return
        
        PosValues = self.adjustValues(PosValues)       	
        if PosValues[0] < self.Minimum:
       		PosValues[0] = self.Minimum
       	if PosValues[-1] > self.Maximum:
       		PosValues[-1] = self.Maximum
       
        if self.ActiveSliders > 0:
            self.value1 = int(PosValues[0])
    
        if self.ActiveSliders > 1:         
            self.value2 = int(PosValues[1])
        
        if self.ActiveSliders > 2:
            self.value3 = int(PosValues[2])
            
        if not self.Updating:
            self.ValueUpdated.emit()
        
    
    def extraRound(self):
        k = self.NextRounding
        self.value1 = k*round(self.value1/k)
        self.value2 = k*round(self.value2/k)
        self.value3 = k*round(self.value3/k)
        
        self.update()
        
        

    def paintEvent(self, event):
        self.verifyValues()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw the slider track
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.fillRect(rect, self.palette().brush(QPalette.ColorRole.Mid))

        # Draw the slider handles
        self.handle1Rect = QRect( int( self.mapFromValue(self.value1-0.9)) , int( self.rect().y() ), self.handleWidth, self.handleHeight)
        self.handle2Rect = QRect(int(self.mapFromValue(self.value2-0.9)), int(self.rect().y()), self.handleWidth, self.handleHeight)
        self.handle3Rect = QRect(int(self.mapFromValue(self.value3-0.9)), int(self.rect().y()), self.handleWidth, self.handleHeight)
        
        handle1Rect = QRect( int( self.mapFromValue(self.value1)) , int( self.rect().y() ), 2, self.handleHeight)
        handle2Rect = QRect(int(self.mapFromValue(self.value2)), int(self.rect().y()), 2, self.handleHeight)
        handle3Rect = QRect(int(self.mapFromValue(self.value3)), int(self.rect().y()), 2, self.handleHeight)
        
        lineRect = QRect(int(self.mapFromValue(0)), 0, int(self.mapFromValue(100)), 1)


        # Draw the slider labels (optional)
        labelFont = QFont("Arial", 5)
        labelMetrics = QFontMetrics(labelFont)
        painter.setFont(labelFont)

        value1Label = str(self.value1)
        value2Label = str(self.value2)
        value3Label = str(self.value3)
        
        painter.fillRect(lineRect, self.palette().brush(QPalette.ColorRole.Dark))
        
        adjustB = 0
        adjustS = 0
        
        if self.LabelPosition == "Right":
            adjustB = 9
            adjustS = -10
        
        
        if self.ActiveSliders > 0:
            painter.fillRect(handle1Rect, self.palette().brush(QPalette.ColorRole.Shadow))
            label1Rect = QRect(handle1Rect.left() - 5 + adjustB, handle1Rect.bottom() + adjustS , 10, 10)
            if self.showNumbers:
                painter.drawText(label1Rect, Qt.AlignmentFlag.AlignCenter , value1Label)
        
        if self.ActiveSliders > 1:
            painter.fillRect(handle2Rect, self.palette().brush(QPalette.ColorRole.Shadow))
            label2Rect = QRect(handle2Rect.left() - 5 + adjustB, handle2Rect.bottom()  + adjustS, 10, 10)
            if self.showNumbers:
                painter.drawText(label2Rect, Qt.AlignmentFlag.AlignCenter, value2Label)
        
        if self.ActiveSliders > 2:
            painter.fillRect(handle3Rect, self.palette().brush(QPalette.ColorRole.Shadow))        
            label3Rect = QRect(handle3Rect.left() - 5 + adjustB, handle3Rect.bottom()  + adjustS, 10, 10)
            if self.showNumbers:
                painter.drawText(label3Rect, Qt.AlignmentFlag.AlignCenter, value3Label)
        
        
        

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.handle1Rect.contains(event.pos()) and not (self.selected2 or self.selected3):
                self.selected1 = True
                self.value1 = round(self.valueFromPosition(event.pos()), 0)
                # self.value2 = round(self.valueFromPosition(event.pos()), 0)
                self.update()
                
            if self.handle2Rect.contains(event.pos()) and not (self.selected1 or self.selected3):
                self.selected2 = True
                self.value2 = round(self.valueFromPosition(event.pos()), 0)
                # self.value2 = round(self.valueFromPosition(event.pos()), 0)
                self.update()
                
            if self.handle3Rect.contains(event.pos()) and not (self.selected1 or self.selected2):
                self.selected3 = True
                self.value3 = round(self.valueFromPosition(event.pos()), 0)
                # self.value2 = round(self.valueFromPosition(event.pos()), 0)
                self.update()
            
            self.grabMouse()
                
            

    def mouseMoveEvent(self, event):
        
        if  self.selected1:
            self.value1 = round(self.valueFromPosition(event.pos()), 0)
            # self.value2 = round(self.valueFromPosition(event.pos()), 0)
            self.update()
            
        if  self.selected2:
            self.value2 = round(self.valueFromPosition(event.pos()), 0)
            # self.value2 = round(self.valueFromPosition(event.pos()), 0)
            self.update()  
            
        if  self.selected3:
            self.value3 = round(self.valueFromPosition(event.pos()), 0)
            # self.value2 = round(self.valueFromPosition(event.pos()), 0)
            self.update() 
                
    def mouseReleaseEvent(self, event):
        self.selected1 = False
        self.selected2 = False
        self.selected3 = False
        self.extraRound()
        self.Released.emit()
        self.releaseMouse()


    def sizeHint(self):
        return QSize(100, 30)

    def minimumSizeHint(self):
        return QSize(20, 20)

    def setMinimum(self, minimum):
        self.minimum = minimum
        self.update()

    def setMaximum(self, maximum):
        self.maximum = maximum
        self.update()

    def setValue1(self, value):
        self.value1 = value
        self.update()

    def setValue2(self, value):
        self.value2 = value
        self.update()

    def valueFromPosition(self, pos):
        return self.minimum + (pos.x() - self.rect().left()) * (self.maximum - self.minimum) / self.rect().width()


    def mapFromValue(self, value):
        return self.rect().left() + (value - self.minimum) * self.rect().width() / (self.maximum - self.minimum)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = QWidget()
#     layout = QVBoxLayout()
#     slider = DualSlider()
#     layout.addWidget(slider)
#     window.setLayout(layout)
#     window.show()
#     sys.exit(app.exec())