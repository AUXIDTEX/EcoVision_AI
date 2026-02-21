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

        self.vertical_ai_layout = QVBoxLayout()
        self.vertical_ai_widget = QWidget()
        self.vertical_ai_widget.hide()
        self.vertical_ai_widget.setStyleSheet("background-color: #2b2b2b; border: 1px solid #808080; border-radius: 10px;")
        self.secon_layout.addWidget(self.vertical_ai_widget)
        self.vertical_ai_widget.setLayout(self.vertical_ai_layout)




        self.mode_switch = QHBoxLayout()
        self.mode_switch.setSpacing(0)
        self.mode_switch.setContentsMargins(0, 0, 0, 0)

        self.mode_widget = QWidget()
        self.mode_widget.setStyleSheet("background-color: transparent; border: none;")
        self.mode_widget.setLayout(self.mode_switch)
        self.vertical_ai_layout.addWidget(self.mode_widget, alignment=Qt.AlignmentFlag.AlignTop)

        self.file_mode_label = QPushButton("Файл")
        self.file_mode_label.setCheckable(True)
        self.file_mode_label.setMinimumSize(80, 30)

        self.folder_mode_label = QPushButton("Папка")
        self.folder_mode_label.setCheckable(True)
        self.folder_mode_label.setMinimumSize(80, 30)

        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.file_mode_label)
        self.button_group.addButton(self.folder_mode_label)

        self.file_mode_label.setChecked(True)

        self.mode_switch.addStretch()
        self.mode_switch.addWidget(self.file_mode_label)
        self.mode_switch.addWidget(self.folder_mode_label)
        self.mode_switch.addStretch()

        self.update_styles()


        self.file_mode_label.toggled.connect(self.update_styles)
        self.file_mode_label.toggled.connect(lambda: self.mode_switch_func("1"))
        self.folder_mode_label.toggled.connect(self.update_styles)
        self.folder_mode_label.toggled.connect(lambda: self.mode_switch_func("2"))



        self.ai_layout = QHBoxLayout()
        self.ai_widget = QWidget()
        self.ai_widget.setStyleSheet("background-color: transparent; border: none;")
        self.vertical_ai_layout.addWidget(self.ai_widget)

        self.ai_widget.setLayout(self.ai_layout)
        #self.secon_layout.addWidget(self.ai_widget)


        self.ai_image_box = QLabel()
        self.ai_image_box.setStyleSheet("border: none; background-color: transparent;")
        self.ai_image_box.setFixedSize(300, 533)
        self.ai_layout.addWidget(self.ai_image_box, alignment=Qt.AlignmentFlag.AlignLeft)

        self.ai_info_widget = QWidget()
        self.ai_info_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ai_info_widget.setStyleSheet("background-color: transparent; border: none;")
        self.ai_layout.addWidget(self.ai_info_widget, 1)
        self.ai_info_layout = QVBoxLayout()
        self.ai_info_widget.setLayout(self.ai_info_layout)

        self.info_title = QLabel("Звіт нейромережі")
        self.ai_info_layout.addWidget(self.info_title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.info_title.setStyleSheet("color: #ffd500; font-size: 15px; padding-bottom: 10px; border: none;")


        self.image_name = QLabel()
        self.info_class_name = QLabel()
        self.info_conf = QLabel()
        self.info_xyxy = QLabel()

        self.info_x1 = QLabel()
        self.info_y1 = QLabel()
        self.info_x2 = QLabel()
        self.info_y2 = QLabel()

        self.info_class_name.setWordWrap(True)
        self.info_conf.setWordWrap(True)
        self.info_x1.setWordWrap(True)
        self.info_class_name.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.info_conf.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.info_x1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.info_class_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.info_conf.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.info_x1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.ai_info_layout.addWidget(self.image_name, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_class_name, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_conf, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_xyxy, alignment=Qt.AlignmentFlag.AlignLeft)

        self.ai_info_layout.addWidget(self.info_x1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_y1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_x2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_y2, alignment=Qt.AlignmentFlag.AlignLeft)

        self.ai_progress_bar = QProgressBar()
        self.ai_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #808080;
                border-radius: 8px;
                text-align: center;
                background-color: #1d1d1d;
                color: white;
                max-height: 15px;
            }
            QProgressBar::chunk {
                background-color: #2e7d32;
                border-radius: 8px;
            }
        """)
        self.ai_progress_bar.setFormat("Обробка ШІ...")
        self.ai_progress_bar.hide()
        self.vertical_ai_layout.addWidget(self.ai_progress_bar)

        self.ai_folder_widget = QWidget()
        self.ai_folder_widget.setStyleSheet("background-color: transparent; border: none;")
        self.ai_folder_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ai_folder_widget.hide()
        self.vertical_ai_layout.addWidget(self.ai_folder_widget)
        self.ai_folder_layout = QVBoxLayout()
        self.ai_folder_widget.setLayout(self.ai_folder_layout)


        self.ai_folder_scroll_widget = QWidget()
        self.ai_folder_scroll_widget.setMinimumHeight(500)
        self.ai_folder_scroll = QScrollArea()

        self.ai_folder_scroll_layout = QVBoxLayout()
        self.ai_folder_scroll_layout.addWidget(self.ai_folder_scroll)
        self.ai_folder_scroll_widget.setLayout(self.ai_folder_scroll_layout)

        self.ai_folder_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ai_folder_scroll.setWidgetResizable(True)
        self.ai_folder_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ai_folder_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ai_folder_scroll.setStyleSheet("QScrollArea { border: 1px solid #808080; border-radius: 8px; background-color: #1d1d1d; }")
        self.ai_folder_layout.addWidget(self.ai_folder_scroll_widget, 1)



        self.ai_folder_select_btn = QPushButton("Вибрати папку")
        self.ai_folder_select_btn.setMinimumHeight(36)
        self.ai_folder_select_btn.setStyleSheet("background-color: #3b3b3b; border: 1px solid #808080; border-radius: 8px; color: white;")
        self.ai_folder_select_btn.clicked.connect(self.select_ai_folder)
        self.ai_folder_layout.addWidget(self.ai_folder_select_btn)


        self.ai_folder_find_btn = QPushButton("Виконати")
        self.ai_folder_find_btn.setMinimumHeight(36)
        self.ai_folder_find_btn.setStyleSheet("background-color: #ffd500; border: 1px solid #808080; border-radius: 8px; color: black; font-weight: 600;")
        self.ai_folder_find_btn.clicked.connect(self.start_ai_folder_processing)
        self.ai_folder_layout.addWidget(self.ai_folder_find_btn)



        self.ai_folder_content = QWidget()
        self.ai_folder_content_layout = QVBoxLayout()
        self.ai_folder_content_layout.setContentsMargins(8, 8, 8, 8)
        self.ai_folder_content_layout.setSpacing(8)
        self.ai_folder_content_layout.addStretch()
        self.ai_folder_content.setLayout(self.ai_folder_content_layout)
        self.ai_folder_scroll.setWidget(self.ai_folder_content)


        #self.ai_info_layout.addStretch()

        self.spectral_filterer = SpectralFilterer()
        self.secon_layout.addWidget(self.spectral_filterer)
        self.spectral_filterer.hide()

        
        self.secon_layout.addStretch()

        self.ai_process = None
        self.ai_source_path = None
        self.ai_cancel_requested = False
        self.ai_selected_folder = None
        self.ai_folder_process = None
        self.ai_folder_paths = []
        self.ai_folder_total = 0
        self.ai_folder_processed = 0
        self.ai_folder_total_processed_time = 0.0
        self.ai_folder_item_started_at = 0.0
        self.ai_folder_cancel_requested = False


    def add_image_to_array(self, file_path):
        self.file_path = file_path

        self.img = Image.open(self.file_path).convert("RGB")
        self.img_ar = np.array(self.img)
        self.image_array.append({
                                "path": self.file_path,
                                "np_array": self.img_ar}) 
        


    def mode_switch_func(self, mode):
        if mode == "1":
            self.stop_ai_folder_processing()
            self.ai_folder_widget.hide()
            self.ai_widget.show()
            if self.mode == 2:
                selected_path = SelectableImageBox.path[1] or SelectableImageBox.path[2]
                if selected_path:
                    self.start_ai_inference(selected_path)
                else:
                    self.clear_ai_file_report()
    
        elif mode == "2":
            self.stop_ai_inference()
            self.ai_progress_bar.hide()
            self.ai_widget.hide()
            self.ai_folder_widget.show()
            self.clear_ai_file_report()



    def update_styles(self):
        if self.file_mode_label.isChecked():
            self.file_mode_label.setStyleSheet(
                "background-color: #505050; border-top-left-radius: 8px; border-bottom-left-radius: 8px; border-top-right-radius: 0px; border-bottom-right-radius: 0px; color: white; border: 1px solid #808080;"
            )
            self.folder_mode_label.setStyleSheet(
                "background-color: #3b3b3b; border-top-right-radius: 8px; border-bottom-right-radius: 8px; border-top-left-radius: 0px; border-bottom-left-radius: 0px; color: white; border: 1px solid #808080;"
            )
        else:
            self.file_mode_label.setStyleSheet(
                "background-color: #3b3b3b; border-top-left-radius: 8px; border-bottom-left-radius: 8px; border-top-right-radius: 0px; border-bottom-right-radius: 0px; color: white; border: 1px solid #808080;"
            )
            self.folder_mode_label.setStyleSheet(
                "background-color: #505050; border-top-right-radius: 8px; border-bottom-right-radius: 8px; border-top-left-radius: 0px; border-bottom-left-radius: 0px; color: white; border: 1px solid #808080;"
            )

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

    def clear_ai_file_report(self):
        self.ai_image_box.clear()
        self.image_name.setText("")
        self.info_class_name.setText("")
        self.info_conf.setText("")
        self.info_xyxy.setText("")
        self.info_x1.setText("")
        self.info_y1.setText("")
        self.info_x2.setText("")
        self.info_y2.setText("")

    def clear_ai_folder_results(self):
        while self.ai_folder_content_layout.count() > 1:
            item = self.ai_folder_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def select_ai_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Виберіть папку з зображеннями")
        if not folder:
            return

        self.ai_selected_folder = folder
        self.ai_folder_select_btn.setText(f"Вибрана папка: {os.path.basename(folder)}")
        self.clear_ai_folder_results()
        self.ai_folder_content_layout.insertWidget(len(self.ai_folder_content_layout) - 1, QLabel("Папка обрана. Натисніть 'Виконати' для обробки."))

    def _build_detection_blocks(self, detections):
        class_stats = {}
        for det in detections:
            cls = str(det.get("class_name", "N/A"))
            conf = float(det.get("conf", 0.0))
            xyxy = det.get("xyxy", [0.0, 0.0, 0.0, 0.0])
            if len(xyxy) != 4:
                xyxy = [0.0, 0.0, 0.0, 0.0]
            if cls not in class_stats:
                class_stats[cls] = {"confs": [], "boxes": []}
            class_stats[cls]["confs"].append(conf)
            class_stats[cls]["boxes"].append(xyxy)

        if not class_stats:
            return (
                "Classes:\n  N/A (0)",
                "Confidence:\n  N/A (0%)",
                "Bounding Box cords:\n  Нічого не знайдено",
                "N/A (0)",
            )

        class_lines = ["Classes:"]
        conf_lines = ["Confidence:"]
        bbox_lines = ["Bounding Box cords:"]
        summary_parts = []

        for cls, stats in class_stats.items():
            class_lines.append(f"  {cls} ({len(stats['boxes'])})")
            summary_parts.append(f"{cls} ({len(stats['boxes'])})")
            conf_percent = ", ".join(f"{round(c * 100, 2)}%" for c in stats["confs"])
            conf_lines.append(f"  {cls} ({conf_percent})")
            bbox_lines.append(f"  {cls}:")
            for idx, box in enumerate(stats["boxes"], start=1):
                bbox_lines.append(
                    f"    #{idx}: x1={box[0]} px, y1={box[1]} px, x2={box[2]} px, y2={box[3]} px"
                )

        return (
            "\n".join(class_lines),
            "\n".join(conf_lines),
            "\n".join(bbox_lines),
            ", ".join(summary_parts),
        )

    def _build_ai_folder_item_widget(self, image_path, detections=None, error_text=None, preview_path=None):
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: #2b2b2b; border: 1px solid #808080; border-radius: 8px; }")
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        frame.setLayout(layout)

        header = QHBoxLayout()

        thumb = QLabel()
        thumb.setFixedSize(400, 225)
        thumb.setStyleSheet("border: none; background-color: transparent;")
        thumb_source = preview_path if preview_path and os.path.exists(preview_path) else image_path
        pm = QPixmap(thumb_source)
        pm = pm.scaled(400, 225, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        thumb.setPixmap(pm)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(thumb)


        toggle_btn = QPushButton("▶")
        toggle_btn.setCheckable(True)
        toggle_btn.setFixedWidth(24)
        toggle_btn.setStyleSheet("QPushButton { border: none; color: #ffd500; font-weight: bold; }")
        header.addWidget(toggle_btn, alignment=Qt.AlignmentFlag.AlignTop)


        meta_col = QVBoxLayout()
        name_label = QLabel(os.path.basename(image_path))
        name_label.setStyleSheet("color: white; border: none; font-weight: 600;")
        meta_col.addWidget(name_label)

        if error_text:
            summary = QLabel(f"Помилка: {error_text}")
            details_text = f"Помилка обробки:\n{error_text}"
        else:
            class_text, conf_text, bbox_text, summary_text = self._build_detection_blocks(detections or [])
            details_text = f"{class_text}\n\n{conf_text}\n\n{bbox_text}"
            summary = QLabel(summary_text)
        summary.setWordWrap(True)
        summary.setStyleSheet("color: #d0d0d0; border: none;")
        meta_col.addWidget(summary)
        header.addLayout(meta_col, 1)
        layout.addLayout(header)

        details = QLabel(details_text)
        details.setWordWrap(True)
        details.setStyleSheet("color: #f0f0f0; border: none;")
        details.hide()
        layout.addWidget(details)

        def toggle_details(checked):
            toggle_btn.setText("▼" if checked else "▶")
            details.setVisible(checked)

        toggle_btn.toggled.connect(toggle_details)
        return frame
    



    def start_ai_folder_processing(self):
        folder = self.ai_selected_folder
        if not folder:
            QMessageBox.warning(self, "Попередження", "Спочатку виберіть папку.")
            return

        image_ext = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp")
        paths = [
            os.path.join(folder, name)
            for name in sorted(os.listdir(folder))
            if name.lower().endswith(image_ext)
        ]

        self.clear_ai_folder_results()
        if not paths:
            self.ai_folder_content_layout.insertWidget(
                0, QLabel("У вибраній папці немає зображень.")
            )
            return

        self.stop_ai_folder_processing()
        self.ai_folder_cancel_requested = False
        self.ai_folder_paths = paths
        self.ai_folder_total = len(paths)
        self.ai_folder_processed = 0
        self.ai_folder_total_processed_time = 0.0

        self.ai_folder_find_btn.setEnabled(False)
        self.ai_folder_select_btn.setEnabled(False)
        self.ai_progress_bar.setRange(0, 0)
        self.ai_progress_bar.setFormat("Processing...")
        self.vertical_ai_layout.removeWidget(self.ai_progress_bar)
        self.vertical_ai_layout.addWidget(self.ai_progress_bar)
        self.ai_progress_bar.show()
        self.start_next_ai_folder_item()

    def stop_ai_folder_processing(self):
        self.ai_folder_cancel_requested = True
        if self.ai_folder_process and self.ai_folder_process.state() != QProcess.ProcessState.NotRunning:
            self.ai_folder_process.kill()
            self.ai_folder_process.waitForFinished(2000)

        self.ai_folder_process = None
        self.ai_folder_paths = []
        self.ai_progress_bar.hide()
        self.ai_folder_find_btn.setEnabled(True)
        self.ai_folder_select_btn.setEnabled(True)

    def start_next_ai_folder_item(self):
        if self.ai_folder_cancel_requested:
            self.ai_folder_cancel_requested = False
            self.ai_folder_process = None
            self.ai_progress_bar.hide()
            self.ai_folder_find_btn.setEnabled(True)
            self.ai_folder_select_btn.setEnabled(True)
            return

        if not self.ai_folder_paths:
            self.ai_folder_process = None
            self.ai_progress_bar.hide()
            self.ai_folder_find_btn.setEnabled(True)
            self.ai_folder_select_btn.setEnabled(True)
            return

        image_path = self.ai_folder_paths.pop(0)
        self.ai_folder_item_started_at = time.perf_counter()

        self.ai_folder_process = QProcess(self)
        self.ai_folder_process.setProgram(sys.executable)
        self.ai_folder_process.setArguments(["app/logic/run_yolo.py", image_path])
        self.ai_folder_process.finished.connect(
            lambda code, status, p=image_path: self.on_ai_folder_item_finished(code, status, p)
        )
        self.ai_folder_process.start()

    def on_ai_folder_item_finished(self, exit_code, _exit_status, image_path):
        if self.ai_folder_cancel_requested:
            return

        elapsed = time.perf_counter() - self.ai_folder_item_started_at
        self.ai_folder_processed += 1
        self.ai_folder_total_processed_time += elapsed

        if not self.ai_folder_process:
            return

        stdout_text = bytes(self.ai_folder_process.readAllStandardOutput()).decode("utf-8", errors="ignore")
        stderr_text = bytes(self.ai_folder_process.readAllStandardError()).decode("utf-8", errors="ignore")

        parsed = None
        for line in reversed([ln.strip() for ln in stdout_text.splitlines() if ln.strip()]):
            try:
                candidate = json.loads(line)
                if isinstance(candidate, dict) and "ok" in candidate:
                    parsed = candidate
                    break
            except json.JSONDecodeError:
                continue

        if exit_code != 0 or not parsed or not parsed.get("ok"):
            err = stderr_text.strip()
            if not err and parsed:
                err = parsed.get("error", "Невідома помилка")
            item = self._build_ai_folder_item_widget(image_path, error_text=err or "Невідома помилка")
        else:
            item = self._build_ai_folder_item_widget(
                image_path,
                detections=parsed.get("detections", []),
                preview_path=parsed.get("output_path"),
            )

        self.ai_folder_content_layout.insertWidget(self.ai_folder_content_layout.count() - 1, item)

        if self.ai_folder_processed == 1:
            self.ai_progress_bar.setRange(0, self.ai_folder_total)
        self.ai_progress_bar.setValue(self.ai_folder_processed)

        avg_time = self.ai_folder_total_processed_time / self.ai_folder_processed
        remaining = max(self.ai_folder_total - self.ai_folder_processed, 0)
        eta = avg_time * remaining
        self.ai_progress_bar.setFormat(
            f"Середній час: {avg_time:.2f} с/зображення | Залишилось: {eta:.1f} с ({self.ai_folder_processed}/{self.ai_folder_total})"
        )

        self.start_next_ai_folder_item()

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


    def start_ai_inference(self, image_path):
        if not image_path:
            QMessageBox.warning(self, "Помилка", "Не вдалося отримати шлях до зображення.")
            return



        source_pixmap = QPixmap(image_path)
        source_pixmap = source_pixmap.scaled(1200, 1200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.ai_image_box.setPixmap(source_pixmap)
        self.ai_image_box.setScaledContents(True)



        self.ai_cancel_requested = False
        if self.ai_process and self.ai_process.state() != QProcess.ProcessState.NotRunning:
            self.stop_ai_inference()

        self.ai_source_path = image_path
        self.ai_progress_bar.setRange(0, 0)
        self.ai_progress_bar.setFormat("Обробка ШІ...")
        self.ai_progress_bar.show()
        self.image_name.setText(f"Name: {image_path.split('/')[-1]}")
        self.info_class_name.setText("Classes: обробка...")
        self.info_conf.setText("Confidence: обробка...")
        self.info_xyxy.setText("Bounding Box cords:")
        self.info_x1.setText("  обробка...")
        self.info_y1.setText("")
        self.info_x2.setText("")
        self.info_y2.setText("")

        self.ai_process = QProcess(self)
        self.ai_process.setProgram(sys.executable)
        self.ai_process.setArguments(["app/logic/run_yolo.py", image_path])
        self.ai_process.finished.connect(self.on_ai_inference_finished)
        self.ai_process.errorOccurred.connect(self.on_ai_inference_error)
        self.ai_process.start()

    def stop_ai_inference(self):
        self.ai_cancel_requested = True
        self.ai_progress_bar.hide()
        if self.ai_process and self.ai_process.state() != QProcess.ProcessState.NotRunning:
            self.ai_process.kill()
            self.ai_process.waitForFinished(2000)

    def on_ai_inference_finished(self, exit_code, _exit_status):
        self.ai_progress_bar.hide()

        if not self.ai_process:
            return

        if self.ai_cancel_requested:
            self.ai_cancel_requested = False
            self.ai_process = None
            return

        stdout_text = bytes(self.ai_process.readAllStandardOutput()).decode("utf-8", errors="ignore")
        stderr_text = bytes(self.ai_process.readAllStandardError()).decode("utf-8", errors="ignore")

        parsed = None
        for line in reversed([ln.strip() for ln in stdout_text.splitlines() if ln.strip()]):
            try:
                candidate = json.loads(line)
                if isinstance(candidate, dict) and "ok" in candidate:
                    parsed = candidate
                    break
            except json.JSONDecodeError:
                continue

        if exit_code != 0 or not parsed or not parsed.get("ok"):
            message = "Не вдалося завершити обробку ШІ."
            error_text = stderr_text.strip()
            if not error_text and parsed:
                error_text = parsed.get("error", "")
            if error_text:
                message = f"{message}\n\n{error_text}"
            QMessageBox.critical(self, "Помилка ШІ", message)
            self.ai_process = None
            return

        output_path = parsed.get("output_path")
        detections = parsed.get("detections", [])

        pixmap = QPixmap(output_path)
        pixmap = pixmap.scaled(1200, 1200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.ai_image_box.setPixmap(pixmap)
        self.ai_image_box.setScaledContents(True)

        if self.ai_source_path:
            self.image_name.setText(f"Name: {self.ai_source_path.split('/')[-1]}")

        class_stats = {}
        for det in detections:
            cls = str(det.get("class_name", "N/A"))
            conf = float(det.get("conf", 0.0))
            xyxy = det.get("xyxy", [0.0, 0.0, 0.0, 0.0])
            if len(xyxy) != 4:
                xyxy = [0.0, 0.0, 0.0, 0.0]

            if cls not in class_stats:
                class_stats[cls] = {"confs": [], "boxes": []}

            class_stats[cls]["confs"].append(conf)
            class_stats[cls]["boxes"].append(xyxy)

        if not class_stats:
            self.info_class_name.setText("Classes:\n  N/A (0)")
            self.info_conf.setText("Confidence:\n  N/A (0%)")
            self.info_xyxy.setText("Bounding Box cords:")
            self.info_x1.setText("  Нічого не знайдено")
            self.info_y1.setText("")
            self.info_x2.setText("")
            self.info_y2.setText("")
            return

        class_lines = ["Classes:"]
        conf_lines = ["Confidence:"]
        bbox_lines = []

        for cls, stats in class_stats.items():
            class_lines.append(f"  {cls} ({len(stats['boxes'])})")
            conf_percent = ", ".join(f"{round(c * 100, 2)}%" for c in stats["confs"])
            conf_lines.append(f"  {cls} ({conf_percent})")

            bbox_lines.append(f"  {cls}:")
            for idx, box in enumerate(stats["boxes"], start=1):
                bbox_lines.append(
                    f"    #{idx}: x1={box[0]} px, y1={box[1]} px, x2={box[2]} px, y2={box[3]} px"
                )

        self.info_class_name.setText("\n".join(class_lines))
        self.info_conf.setText("\n".join(conf_lines))
        self.info_xyxy.setText("Bounding Box cords:")
        self.info_x1.setText("\n".join(bbox_lines))
        self.info_y1.setText("")
        self.info_x2.setText("")
        self.info_y2.setText("")
        self.info_class_name.adjustSize()
        self.info_conf.adjustSize()
        self.info_x1.adjustSize()
        self.ai_info_layout.activate()
        self.ai_process = None

    def on_ai_inference_error(self, process_error):
        if self.ai_cancel_requested:
            return
        self.ai_progress_bar.hide()
        QMessageBox.critical(
            self,
            "Помилка запуску ШІ",
            f"Не вдалося запустити процес обробки (код: {int(process_error)}).",
        )





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
