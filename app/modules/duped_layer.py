from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel
import os


class Duped_layer(QLabel):
    def __init__(self, parent=None, slider=None, mode=None):
        super().__init__(parent)

        self.setStyleSheet("background-color: transparent;")
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())

        self.mode = mode
        self.points = []
        self.radius_slider = slider

    def _size_base(self):
        return max(min(self.width(), self.height()), 1)

    def _to_screen(self, point):
        x = int(point["x_ratio"] * self.width())
        y = int(point["y_ratio"] * self.height())
        radius = max(int(point["radius_ratio"] * self._size_base()), 2)
        return x, y, radius

    def _render_point(self, point):
        x, y, radius = self._to_screen(point)
        image = point["image"]
        image.setFixedSize(radius * 2, radius * 2)
        image.move(x - radius // 2, y - radius // 2)
        image.show()

    def add_point_by_ratio(self, x_ratio, y_ratio):
        circle_path = os.path.join(os.path.dirname(__file__), "..", "assets", "circle.png")
        radius = self.radius_slider.value()

        image = QLabel(self)
        pixmap = QPixmap(circle_path)
        pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image.setPixmap(pixmap)
        image.setScaledContents(True)

        point = {
            "x_ratio": x_ratio,
            "y_ratio": y_ratio,
            "radius_ratio": radius / self._size_base(),
            "image": image,
        }
        self.points.append(point)
        self._render_point(point)

    def add_point(self, x, y):
        x_ratio = x / max(self.width(), 1)
        y_ratio = y / max(self.height(), 1)
        self.add_point_by_ratio(x_ratio, y_ratio)

    def refresh_points_positions(self):
        for point in self.points:
            self._render_point(point)

    def delete_point(self, x_ratio, y_ratio):
        if self.mode != 0:
            return

        x = int(x_ratio * self.width())
        y = int(y_ratio * self.height())

        for point in list(self.points):
            px, py, radius = self._to_screen(point)
            if (px - x) ** 2 + (py - y) ** 2 <= radius ** 2:
                point["image"].deleteLater()
                self.points.remove(point)
                break
