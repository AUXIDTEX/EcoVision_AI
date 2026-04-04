from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel
import os

from logic.average_color import Average_color
from modules.selectable_imagebox import SelectableImageBox


class PointPlacer(QLabel):
    point_added = pyqtSignal(int, int)
    right_clicked = pyqtSignal(float, float)
    send_color = pyqtSignal(tuple, int, int, str)

    def __init__(self, parent=None, slider=None, second_column=None, mode=None):
        super().__init__(parent)

        self.second_column = second_column
        self.mode = mode

        self.setStyleSheet("background-color: transparent;")
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())

        self.radius_slider = slider
        self.points = []
        self.radius = 10

    def _point_size_base(self):
        return max(min(self.width(), self.height()), 1)

    def _to_ratio(self, x, y):
        return x / max(self.width(), 1), y / max(self.height(), 1)

    def _to_screen(self, point):
        x = int(point["x_ratio"] * self.width())
        y = int(point["y_ratio"] * self.height())
        radius = max(int(point["radius_ratio"] * self._point_size_base()), 2)
        return x, y, radius

    def _render_point(self, point):
        x, y, radius = self._to_screen(point)
        image = point["image"]
        image.setFixedSize(radius * 2, radius * 2)
        image.move(x - radius // 2, y - radius // 2)
        image.show()

    def add_point(self, x, y):
        circle_path = os.path.join(os.path.dirname(__file__), "..", "assets", "circle.png")
        self.radius = self.radius_slider.value()

        x_ratio, y_ratio = self._to_ratio(x, y)
        radius_ratio = self.radius / self._point_size_base()

        image = QLabel(self)
        pixmap = QPixmap(circle_path)
        pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image.setPixmap(pixmap)
        image.setScaledContents(True)

        point = {
            "number": len(self.points) + 1,
            "x_ratio": x_ratio,
            "y_ratio": y_ratio,
            "radius_ratio": radius_ratio,
            "image": image,
        }
        self.points.append(point)
        self._render_point(point)
        return x_ratio, y_ratio

    def refresh_points_positions(self):
        for point in self.points:
            self._render_point(point)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self.mode == 0:
            x = int(event.position().x())
            y = int(event.position().y())
            self.point_added.emit(x, y)
            x_ratio, y_ratio = self._to_ratio(x, y)
            self.right_clicked.emit(x_ratio, y_ratio)

            for point in list(self.points):
                px, py, radius = self._to_screen(point)
                if (px - x) ** 2 + (py - y) ** 2 <= radius ** 2:
                    point["image"].deleteLater()

                    if point.get("label_first"):
                        if point["label_first"] in self.second_column.output_widgets:
                            self.second_column.output_widgets.remove(point["label_first"])
                        point["label_first"].deleteLater()

                    if point.get("label_second"):
                        if point["label_second"] in self.second_column.output_widgets:
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

        if not self.points:
            return avg_colors

        point = self.points[-1]
        x, y, rad = self._to_screen(point)

        for img_arr in self.second_column.image_array:
            if img_arr["path"] in selected_paths:
                calculator = Average_color(
                    img_arr["np_array"],
                    self.second_column.image1.width(),
                    self.second_column.image1.height(),
                )
                avg_color = calculator.calculate(x, y, rad)
                which = "first" if img_arr["path"] == SelectableImageBox.path[1] else "second"

                avg_colors.append(avg_color)
                self.send_color.emit(avg_color, x, y, which)

        return avg_colors
