from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel
import os

from logic.average_color import Average_color
from modules.selectable_imagebox import SelectableImageBox


class PointPlacer(QLabel):
    point_added = pyqtSignal(int, int)
    right_clicked = pyqtSignal(int, int)
    send_color = pyqtSignal(tuple, int, int, str)  # Signal to send average color and coordinates

    def __init__(self, parent=None, slider = None, second_column=None, mode=None):
        super().__init__(parent)

        self.second_column = second_column
        self.mode = mode
        
        self.setStyleSheet("background-color: transparent;")
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        
        self.radius_slider = slider

        self.points = []
        self.radius = 10


    def add_point(self, x, y):
        circle_path = os.path.join(os.path.dirname(__file__), "..", "assets", "circle.png")

        self.radius = self.radius_slider.value()
        
        image1 = QLabel(self)
        image1.setFixedSize(self.radius * 2, self.radius * 2)
        pixmap = QPixmap(circle_path)
        pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image1.setPixmap(pixmap) 
        image1.setScaledContents(True)

        self.points.append({
            "number": len(self.points) + 1,
            "x": x,
            "y": y,
            "image": image1, 
            "radius": self.radius
            })

        image1.move(x - self.radius // 2, y - self.radius // 2)  # Center the image on the click position
        image1.show()



    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self.mode == 0:
            self.x, self.y = int(event.position().x()), int(event.position().y())
            self.point_added.emit(self.x, self.y)
            self.right_clicked.emit(self.x, self.y)

            for point in self.points:
                px, py = point["x"], point["y"]
                img = point["image"]
                radius = point["radius"]
                

                if (px - self.x)**2 + (py - self.y)**2 <= radius**2:
                    img.deleteLater()
                    if point.get("label_first"):
                        self.second_column.output_widgets.remove(point["label_first"])

                        point["label_first"].deleteLater()

                    if point.get("label_second"):
                        self.second_column.output_widgets.remove(point["label_second"])

                        point["label_second"].deleteLater()

                    self.points.remove(point)
                    self.second_column.renumber_point_outputs()
                    break

        else:
            super().mousePressEvent(event)


    def average_colors(self):

        avg_colors = []
        selected_paths = [SelectableImageBox.path[1], SelectableImageBox.path[2]]

        point = self.points[-1]  # Get the last added point's coordinates and radius
        x, y = point["x"], point["y"]
        rad = point["radius"]


        for img_arr in self.second_column.image_array:    
            if img_arr["path"] in selected_paths:
                
                calculator = Average_color(
                    img_arr["np_array"],
                    self.second_column.image1.width(),
                    self.second_column.image1.height()
                )

                avg_color = calculator.calculate(x, y, rad)

                which = "first" if img_arr["path"] == SelectableImageBox.path[1] else "second"

                avg_colors.append(avg_color)
                self.send_color.emit(avg_color, x, y, which)  # Emit the average color

        return avg_colors
