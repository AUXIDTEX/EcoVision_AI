from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QLabel, QMessageBox
import numpy as np
import math


class Grid_Analyzer(QLabel):
    block_size = 0
    warning_shown = False

    def __init__(self, parent=None, target_label=None, img_arr=None, mesh_arr=None, sizer_slider=None):
        super().__init__(parent)
        self.img_arr = img_arr
        self.mesh_arr = mesh_arr
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet("background-color: transparent;")
        self.treshold = 35
        self.target_label = target_label

        self.grid_diffs = []
        self.sizer_slider = sizer_slider

        self.secon_col = parent

    def calculate_grid(self): 
        if self.img_arr is None:
            return 

        h, w, _ = self.img_arr.shape
        self.math_size = math.gcd(w, h)


        self.square_size = self.math_size // self.sizer_slider.value()
        Grid_Analyzer.block_size = self.square_size

        avg_img_color = tuple(np.mean(self.img_arr, axis=(0, 1)).astype(int))

        self.grid_diffs.clear()

        for y in range(0, h, self.square_size):
            for x in range(0, w, self.square_size):
                y_max = min(y + self.square_size, h)
                x_max = min(x + self.square_size, w)
                region = self.img_arr[y:y_max, x:x_max]

                avg_square = tuple(np.mean(region, axis=(0, 1)).astype(int))
                pol_dist = np.linalg.norm(np.array(avg_square) - np.array(avg_img_color))
                diff = int((pol_dist / 441.67) * 100)

                self.grid_diffs.append({
                    "x": x, "y": y, "x_max": x_max, "y_max": y_max, "diff": diff
                })



    def draw_grid(self, treshold):
        self.treshold = treshold

        if not self.grid_diffs:
            self.calculate_grid()

        #if Grid_Analyzer.block_size < 20:
        #    if not Grid_Analyzer.warning_shown:
                #Grid_Analyzer.warning_shown = True
                #self.secon_col.mode_selection.setCurrentIndex(0)
                #self.grid_diffs.clear()

                #QMessageBox.warning(self, "Попередження", "Розмір блоку занадто малий для аналізу сітки.")

                #return

        self.update()


        
    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.grid_diffs:
            return

        h, w, _ = self.img_arr.shape
        scale_x = self.width() / w
        scale_y = self.height() / h

        painter = QPainter(self)
        pen = QPen(QColor(0, 0, 0, 100))
        pen.setWidth(1)
        painter.setPen(pen)

        for square in self.grid_diffs:
            x, y = square["x"], square["y"]
            x_max, y_max = square["x_max"], square["y_max"]
            diff = square["diff"]

            if diff < self.treshold:
                brush = QColor(255, 0, 0, 100)
                painter.fillRect(
                    int(x * scale_x),
                    int(y * scale_y),
                    int((x_max - x) * scale_x),
                    int((y_max - y) * scale_y),
                    brush
                )

            painter.drawRect(
                int(x * scale_x),
                int(y * scale_y),
                int((x_max - x) * scale_x),
                int((y_max - y) * scale_y)
            )
        painter.end()