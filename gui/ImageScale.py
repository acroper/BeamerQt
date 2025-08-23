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
"""
This module was created with the assistance of Google Gemini chat
"""


import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen
from PyQt6.QtCore import Qt, pyqtSignal

class ImageScale(QLabel):
    """
    A custom QLabel that displays a QPixmap, automatically scaling it to fit the
    widget's size while maintaining the original aspect ratio. It also emits
    a 'clicked' signal on a left mouse press.
    """
    # Define a custom signal that will be emitted when the label is clicked.
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap()
        self.setMinimumSize(1, 1)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setPixmap(self, pixmap):
        """
        Sets the pixmap for the label. The initial scaling is also performed.
        Args:
            pixmap (QPixmap): The pixmap to display.
        """
        self._pixmap = pixmap
        self.update_scaled_pixmap()

    def resizeEvent(self, event):
        """
        Handles the resize event of the widget. This is where the scaling
        logic is triggered.
        """
        self.update_scaled_pixmap()
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        """
        Handles the mouse press event. If the left button is pressed, the
        'clicked' signal is emitted.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        # Call the base class implementation to ensure proper event handling
        super().mousePressEvent(event)

    def update_scaled_pixmap(self):
        """
        Scales the original pixmap to fit the current size of the label while
        preserving the aspect ratio. The Qt.KeepAspectRatio mode ensures the
        image is never distorted.
        """
        if self._pixmap.isNull():
            return

        # Scale the original pixmap to the label's size
        scaled_pixmap = self._pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        # The parent class setPixmap is called to avoid recursion
        super().setPixmap(scaled_pixmap)


# class MainWindow(QMainWindow):
#     """
#     The main window of the application.
#     """
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("PyQt6 Scalable Image Widget")
#         self.setGeometry(100, 100, 800, 600)  # x, y, width, height

#         # --- Main Layout and Central Widget ---
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         layout = QVBoxLayout(central_widget)

#         # --- Create the custom image label ---
#         self.image_label = ScalableImageLabel()
        
#         # --- Connect the clicked signal to a handler method ---
#         self.image_label.clicked.connect(self.image_was_clicked)

#         # --- Load Image ---
#         # Option 1: Generate a sample pixmap (no external file needed)
#         sample_pixmap = self.create_sample_pixmap()
#         self.image_label.setPixmap(sample_pixmap)

#         # Add the image label to the layout
#         layout.addWidget(self.image_label)

#     def image_was_clicked(self):
#         """This method is the slot that handles the 'clicked' signal from the image label."""
#         print("Image was clicked!")

#     def create_sample_pixmap(self):
#         """
#         Creates a sample 800x600 QPixmap with some drawings for demonstration.
#         """
#         pixmap = QPixmap(800, 600)
#         pixmap.fill(QColor("darkslategray"))

#         # Use QPainter to draw on the pixmap
#         painter = QPainter(pixmap)
        
#         # Draw a red rectangle
#         pen = QPen(QColor("firebrick"), 15)
#         painter.setPen(pen)
#         painter.drawRect(50, 50, 700, 500)

#         # Draw a blue ellipse
#         pen.setColor(QColor("steelblue"))
#         pen.setWidth(10)
#         painter.setPen(pen)
#         painter.drawEllipse(150, 150, 500, 300)
        
#         # Draw some text
#         pen.setColor(QColor("lightgray"))
#         painter.setPen(pen)
#         font = painter.font()
#         font.setPointSize(36)
#         font.setBold(True)
#         painter.setFont(font)
#         painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Resizable Image")

#         painter.end()
#         return pixmap


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     main_window = MainWindow()
#     main_window.show()
#     sys.exit(app.exec())
