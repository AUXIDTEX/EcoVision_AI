from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel
import os



class Duped_layer(QLabel):
    def __init__(self, parent=None, slider = None, mode=None):
        super().__init__(parent)
        
        self.setStyleSheet("background-color: transparent;")
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())

        self.mode = mode
        self.points = []
        self.radius_slider = slider
        
    def add_point(self, x, y):
        circle_path = os.path.join(os.path.dirname(__file__), "..", "assets", "circle.png")
        self.radius = self.radius_slider.value()

        image1 = QLabel(self)
        image1.setFixedSize(self.radius * 2, self.radius * 2)
        pixmap = QPixmap(circle_path)
        pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image1.setPixmap(pixmap) 
        image1.setScaledContents(True)
        self.points.append((x, y, image1, self.radius))

        image1.move(x - self.radius // 2, y - self.radius // 2)  # Center the image on the click position
        image1.show()

    def delete_point(self, xp, yp):
        if self.mode == 0:
            x, y = int(xp), int(yp)
            for px, py, img, radius in self.points:
                if (px - x)**2 + (py - y)**2 <= radius**2:
                    img.deleteLater() 
                    self.points.remove((px, py, img, radius))
                    break      
