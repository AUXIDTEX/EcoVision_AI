import json
import os
import sys
import time

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QComboBox, QSizePolicy, QLineEdit, QSlider, QScrollArea, QMessageBox, QProgressBar, QPushButton, QButtonGroup, QFileDialog, QFrame
from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtGui import QPixmap

from PIL import Image
import numpy as np

from modules.clickable_label import ClickableLabel
from modules.point_placer import PointPlacer
from modules.duped_layer import Duped_layer
from modules.grid_analyzer import Grid_Analyzer
from modules.selectable_imagebox import SelectableImageBox
from modules.image_output import Image_Output
from modules.spectal_filterer import SpectralFilterer
from modules.change_modes import switch_modes
from modules.ai_module import AI_Module

class SecondColumn(QWidget):
    index = 0
    def __init__(self, parent=None, main_window = None, settings_layout = None, settings_widget = None):
        super().__init__(parent)

        self.mode = 0
        self.window = main_window

        self.image_array = []   # List to store image pixel data
        self.output_widgets = []  # List to store output widgets 
        self.mesh_arr = []   

        self.settings_layout = settings_layout
        self.settings_widget = settings_widget 

        self.secon_layout = QVBoxLayout(self)
        
        self.compare_widget = QWidget()
        self.compare_widget.setFixedHeight(50)
        self.compare_widget.setStyleSheet("background-color: #2b2b2b; border-radius: 10px; border: 1px solid #808080;")
        self.compare_layout = QHBoxLayout()
        self.compare_widget.setLayout(self.compare_layout)
        self.secon_layout.addWidget(self.compare_widget)

        self.compare_title = QLabel("Режим точок")
        self.compare_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.compare_title.setStyleSheet("font-size: 16px; color: #ffd500; border: none;")
        self.compare_layout.addWidget(self.compare_title, alignment=Qt.AlignmentFlag.AlignRight)


        self.mode_selection = QComboBox()
        self.mode_selection.addItem("Точки")
        self.mode_selection.addItem("Сітка")
        self.mode_selection.addItem("Нейромережа")
        self.mode_selection.addItem("Фільтрування зображень")
        self.mode_selection.setCurrentIndex(0)
        
        self.mode_selection.currentIndexChanged.connect(self.switch_mode_func)
        self.mode_selection.currentIndexChanged.connect(SelectableImageBox.update_index)

        self.switch_layout = QHBoxLayout()
        self.switch_widget = QWidget()
        self.switch_widget.setStyleSheet("border: none; background-color: transparent;")
        self.switch_widget.setLayout(self.switch_layout)

        self.switch_layout.addWidget(self.mode_selection)

        self.compare_layout.addWidget(self.switch_widget, alignment=Qt.AlignmentFlag.AlignRight)

        

        self.image_widget = QWidget()
        self.image_widget.setStyleSheet("border: 1px solid #808080; border-radius: 10px; background-color: #2b2b2b;")
        self.image_layout = QHBoxLayout()
        self.image_widget.setLayout(self.image_layout)
        self.secon_layout.addWidget(self.image_widget)

        self.image1 = ClickableLabel(self)
        self.image1.setStyleSheet("border: none; background: transparent")
        self.image1.setMinimumHeight(180)
        self.image1.setMinimumWidth(320)

        self.image2 = QLabel()
        self.image2.setMinimumWidth(320)
        self.image2.setStyleSheet("border: none; background: transparent")
        self.image_layout.addWidget(self.image1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.image_layout.addWidget(self.image2, alignment=Qt.AlignmentFlag.AlignCenter)

        self.help_overlay = QHBoxLayout()
        self.help_overlay.setContentsMargins(0, 0, 0, 0)
        self.help_overlay.setSpacing(0)
        self.image1.setLayout(self.help_overlay)

        self.help_overlay2 = QHBoxLayout()
        self.help_overlay2.setContentsMargins(0,0,0,0)
        self.help_overlay2.setSpacing(0)
        self.image2.setLayout(self.help_overlay2)
        
        self.sliders_widget = QWidget()
        self.sliders_widget.setStyleSheet("background-color: #2b2b2b; border: 1px solid #808080; border-radius: 10px; padding: 5px;")
        self.sliders_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.sliders_layout = QHBoxLayout()
        self.sliders_layout.addStretch()
        self.sliders_widget.setLayout(self.sliders_layout)


        self.slider_widget = QWidget()
        self.settings_layout.addWidget(self.slider_widget, alignment=Qt.AlignmentFlag.AlignRight)

        self.slider_widget.setStyleSheet("background-color: transparent; border: none;")
        self.slider_layout = QVBoxLayout()
        self.slider_widget.setLayout(self.slider_layout)

        self.title_value_layout = QHBoxLayout()
        self.slider_layout.addLayout(self.title_value_layout)

        self.radius_title = QLabel("Радіус")
        self.title_value_layout.addWidget(self.radius_title)
        self.radius_title.setStyleSheet("color: #ffd500; border: none; font-size: 13px;")

        self.radius_input = QLineEdit()
        self.radius_input.setStyleSheet("border: 1px solid #808080; border-radius: 10px; color: white;")
        self.radius_input.setMinimumHeight(25)
        self.radius_input.setFixedWidth(50)
        self.radius_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.radius_input.setText(str(10))
        self.title_value_layout.addWidget(self.radius_input)

        self.radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.radius_slider.setStyleSheet("border:none;")
        self.radius_slider.setFixedWidth(200)
        self.slider_layout.addWidget(self.radius_slider)
        self.radius_slider.setMinimum(3)
        self.radius_slider.setMaximum(50)
        self.radius_slider.setValue(10)
        self.radius_slider.setTickPosition(QSlider.TickPosition.NoTicks)

        self.radius_slider.valueChanged.connect(lambda value: self.radius_input.setText(str(value)))
        self.radius_input.textChanged.connect(lambda text: self.radius_slider.setValue(int(text)) if text.isdigit() and 3 <= int(text) <= 50 else None)
        self.radius_input.returnPressed.connect(lambda: self.radius_input.clearFocus())

        
        self.point_overlay = PointPlacer(self, slider = self.radius_slider, second_column=self, mode = self.mode_selection.currentIndex())
        self.point_overlay.resize(self.image1.size())
        self.point_overlay.show()


        self.duped_layer = Duped_layer(self, slider = self.radius_slider, mode = self.mode_selection.currentIndex())
        self.duped_layer.resize(self.image2.size())
        self.duped_layer.show()


        self.point_overlay.right_clicked.connect(self.duped_layer.delete_point)

        self.image1.clicked.connect(self.check_images)

        self.help_overlay.addWidget(self.point_overlay)
        self.help_overlay2.addWidget(self.duped_layer)

        self.point_overlay.send_color.connect(self.add_color)


        self.color_title = QLabel("Координати точок")
        self.color_title.setStyleSheet("color: #ffd500; border: none; font-size: 16px; padding: 5px 10px")
        self.secon_layout.addWidget(self.color_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.color_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)


        self.color_layout = QHBoxLayout()
        self.color_widget = QWidget()
        self.color_widget.setFixedHeight(500)
        self.color_widget.setLayout(self.color_layout)
        self.secon_layout.addWidget(self.color_widget)


        self.first_color_widget = QWidget()
        self.first_color_widget.setStyleSheet("background-color: #2b2b2b; border: 1px solid #808080; border-radius: 8px;")
        self.first_color_col = QVBoxLayout(self.first_color_widget)
        self.first_color_col.addStretch()

        self.second_color_widget = QWidget()
        self.second_color_widget.setStyleSheet("background-color: #2b2b2b; border: 1px solid #808080; border-radius: 8px;")
        self.second_color_col = QVBoxLayout(self.second_color_widget)
        self.second_color_col.addStretch()

        self.first_scroll = QScrollArea()
        self.first_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.first_scroll.setWidget(self.first_color_widget)
        self.first_scroll.setWidgetResizable(True)
        self.first_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.first_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        

        self.second_scroll = QScrollArea()
        self.second_scroll.setWidget(self.second_color_widget)
        self.second_scroll.setWidgetResizable(True)
        self.second_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.second_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.color_layout.addWidget(self.first_scroll)
        self.color_layout.addWidget(self.second_scroll)
        self._syncing_color_scroll = False
        self.first_scroll.verticalScrollBar().valueChanged.connect(self.sync_color_scroll_from_first)
        self.second_scroll.verticalScrollBar().valueChanged.connect(self.sync_color_scroll_from_second)



        self.diff_widget = QWidget()
        self.settings_layout.addWidget(self.diff_widget, alignment=Qt.AlignmentFlag.AlignRight)

        self.diff_widget.setStyleSheet("background-color: transparent; border: none;")
        self.diff_widget.hide()
        self.diff_layout = QVBoxLayout()
        self.diff_widget.setLayout(self.diff_layout)

        self.diff_title_layout = QHBoxLayout()
        self.diff_layout.addLayout(self.diff_title_layout)

        self.diff_title = QLabel("Відмінність (%)")
        self.diff_title.setStyleSheet("color: #ffd500; font-size: 13px;")
        self.diff_title_layout.addWidget(self.diff_title)

        self.diff_input = QLineEdit()
        self.diff_input.setStyleSheet("border: 1px solid #808080; border-radius: 10px; font-size: 13px; color: white;")
        self.diff_input.setMinimumHeight(25)
        self.diff_input.setFixedWidth(50)
        self.diff_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.diff_input.setText(str(35))
        self.diff_title_layout.addWidget(self.diff_input)

        self.diff_slider = QSlider(Qt.Orientation.Horizontal)
        self.diff_layout.addWidget(self.diff_slider)
        self.diff_slider.setMinimumWidth(200)
        self.diff_slider.setMinimum(0)
        self.diff_slider.setMaximum(100)
        self.diff_slider.setValue(35)

        self.diff_slider.valueChanged.connect(lambda value: self.diff_input.setText(str(value)))
        self.diff_input.textChanged.connect(lambda text: self.diff_slider.setValue(int(text)) if text.isdigit() and 0 <= int(text) <= 100 else None)
        self.diff_input.returnPressed.connect(lambda: self.diff_input.clearFocus())
        self.diff_slider.valueChanged.connect(self.rewrite_grid)


        self.sizer_widget = QWidget()
        self.settings_layout.addWidget(self.sizer_widget, alignment=Qt.AlignmentFlag.AlignRight)

        self.sizer_widget.setStyleSheet("background-color: transparent; border: none;")
        self.sizer_widget.hide()
        self.sizer_layout = QVBoxLayout()
        self.sizer_widget.setLayout(self.sizer_layout)

        self.sizer_title_layout = QHBoxLayout()
        self.sizer_layout.addLayout(self.sizer_title_layout)

        self.sizer_title = QLabel("Кратність сітки")
        self.sizer_title.setStyleSheet("color: #ffd500; font-size: 13px;")
        self.sizer_title_layout.addWidget(self.sizer_title)

        self.sizer_input = QLineEdit()
        self.sizer_input.setStyleSheet("border: 1px solid #808080; border-radius: 10px; font-size: 13px; color: white;")
        self.sizer_input.setMinimumHeight(25)
        self.sizer_input.setFixedWidth(50)
        self.sizer_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sizer_input.setText(str(1))
        self.sizer_title_layout.addWidget(self.sizer_input)

        self.sizer_slider = QSlider(Qt.Orientation.Horizontal)
        self.sizer_layout.addWidget(self.sizer_slider)
        self.sizer_slider.setMinimumWidth(200)
        self.sizer_slider.setMinimum(1)
        self.sizer_slider.setMaximum(10)
        self.sizer_slider.setValue(1)

        self.sizer_slider.valueChanged.connect(lambda value: self.sizer_input.setText(str(value)))
        self.sizer_input.textChanged.connect(lambda text: self.sizer_slider.setValue(int(text)) if text.isdigit() and 1 <= int(text) <= 10 else None)
        self.sizer_input.returnPressed.connect(lambda: self.sizer_input.clearFocus())
        self.sizer_slider.valueChanged.connect(self.resize_grid)


        self.grid_overlay = Grid_Analyzer(self, self.image1, mesh_arr = self.mesh_arr, sizer_slider = self.sizer_slider)
        self.grid_overlay.resize(self.image1.size())
        self.help_overlay.addWidget(self.grid_overlay)
        self.grid_overlay.hide()


        self.grid_overlay2 = Grid_Analyzer(self, self.image2, mesh_arr = self.mesh_arr, sizer_slider = self.sizer_slider)
        self.grid_overlay2.resize(self.image2.size())
        self.help_overlay2.addWidget(self.grid_overlay2)
        self.grid_overlay2.hide()

        self.spectral_filterer = SpectralFilterer()
        self.secon_layout.addWidget(self.spectral_filterer)
        self.spectral_filterer.hide()


        self.ai_module = AI_Module( self)
        self.secon_layout.addWidget(self.ai_module.vertical_ai_widget)


        
        self.secon_layout.addStretch()



    def add_image_to_array(self, file_path):
        self.file_path = file_path

        self.img = Image.open(self.file_path).convert("RGB")
        self.img_ar = np.array(self.img)
        self.image_array.append({
                                "path": self.file_path,
                                "np_array": self.img_ar}) 



    def sync_color_scroll_from_first(self, value):
        if self._syncing_color_scroll:
            return
        self._syncing_color_scroll = True
        self.second_scroll.verticalScrollBar().setValue(value)
        self._syncing_color_scroll = False

    def sync_color_scroll_from_second(self, value):
        if self._syncing_color_scroll:
            return
        self._syncing_color_scroll = True
        self.first_scroll.verticalScrollBar().setValue(value)
        self._syncing_color_scroll = False


    

    def add_color(self, color, x, y, which):
        # average_colors() always emits color for the last added point
        current_point = self.point_overlay.points[-1] if self.point_overlay.points else None
        number = current_point.get("number", 1) if current_point else 1

        self.output = Image_Output(self)
        self.output.set_color(color, str(number))

        self.output_widgets.append(self.output)

        if which == "first":
            self.first_color_col.insertWidget(self.first_color_col.count() - 1, self.output)
            
        else:
            self.second_color_col.insertWidget(self.second_color_col.count() - 1, self.output)
            
        if current_point:
            if which == "first":
                current_point["label_first"] = self.output
            else:
                current_point["label_second"] = self.output




    def renumber_point_outputs(self):
        for idx, point in enumerate(self.point_overlay.points, start=1):
            point["number"] = idx

            if point.get("label_first"):
                point["label_first"].set_number(str(idx))

            if point.get("label_second"):
                point["label_second"].set_number(str(idx))



    def switch_mode_func(self, index):
        switch_modes(self, index)


    def clear_selected_images(self):
        SelectableImageBox.reset_selection_state()
        self.image1.clear()
        self.image2.clear()

        for point in self.point_overlay.points:
            point["image"].deleteLater()
            if point.get("label_first"):
                point["label_first"].deleteLater()
            if point.get("label_second"):
                point["label_second"].deleteLater()

        for _x, _y, image, _radius in self.duped_layer.points:
            image.deleteLater()

        self.point_overlay.points.clear()
        self.duped_layer.points.clear()
        self.output_widgets.clear()

        self.grid_overlay.grid_diffs.clear()
        self.grid_overlay2.grid_diffs.clear()
        self.grid_overlay.img_arr = None
        self.grid_overlay2.img_arr = None
        self.grid_overlay.update()
        self.grid_overlay2.update()




    def rewrite_grid(self):
        if not self.image_array:
            return
        
        self.update_grid_paths()

        self.grid_overlay.draw_grid(self.diff_slider.value())
        self.grid_overlay2.draw_grid(self.diff_slider.value())





    def resize_grid(self):
        if not self.image_array:
            return
    
        self.update_grid_paths()

        self.grid_overlay.grid_diffs.clear()
        self.grid_overlay2.grid_diffs.clear()

        self.grid_overlay.draw_grid(self.diff_slider.value())
        self.grid_overlay2.draw_grid(self.diff_slider.value())


    def update_grid_paths(self):
        for image in self.image_array:
            if image["path"] == SelectableImageBox.path[1]:
                self.grid_overlay.img_arr = image["np_array"]
            elif image["path"] == SelectableImageBox.path[2]:
                self.grid_overlay2.img_arr = image["np_array"]




    def check_images(self, x, y):
        if self.mode_selection.currentIndex() == 1:
            return

        if SelectableImageBox.path[1] is None or SelectableImageBox.path[2] is None:
            QMessageBox.warning(self, "Попередження", "Будь ласка, виберіть два зображення для порівняння.")
            return

        self.point_overlay.add_point(x, y)
        self.point_overlay.average_colors()
        self.duped_layer.add_point(x, y)
