from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QComboBox, QSizePolicy, QLineEdit, QSlider, QScrollArea, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from PIL import Image
import numpy as np

from windows.clickable_label import ClickableLabel
from windows.point_placer import PointPlacer
from windows.duped_layer import Duped_layer
from windows.grid_analyzer import Grid_Analyzer
from windows.selectable_imagebox import SelectableImageBox
from windows.image_output import Image_Output
from logic.run_yolo import run_yolo



class SecondColumn(QWidget):
    def __init__(self, parent=None, main_window = None, settings_layout = None):
        super().__init__(parent)

        self.window = main_window

        self.image_array = []   # List to store image pixel data
        self.output_widgets = []  # List to store output widgets 
        self.mesh_arr = []   

        self.settings_layout = settings_layout

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

        
        self.point_overlay = PointPlacer(self, slider = self.radius_slider, second_column=self, mode = self.mode_selection.currentIndex)
        self.point_overlay.resize(self.image1.size())
        self.point_overlay.show()


        self.duped_layer = Duped_layer(self, slider = self.radius_slider, mode = self.mode_selection.currentIndex)
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


        self.ai_layout = QHBoxLayout()
        self.ai_widget = QWidget()
        self.ai_widget.setStyleSheet("background-color: #2b2b2b; border: 1px solid #808080; border-radius: 10px;")
        self.ai_widget.hide()
        self.ai_widget.setLayout(self.ai_layout)
        self.secon_layout.addWidget(self.ai_widget)

        self.ai_image_box = QLabel()
        self.ai_image_box.setStyleSheet("border: none; background-color: transparent;")
        self.ai_image_box.setFixedSize(300, 533)
        self.ai_layout.addWidget(self.ai_image_box, alignment=Qt.AlignmentFlag.AlignLeft)

        self.ai_info_widget = QWidget()
        self.ai_info_widget.setStyleSheet("background-color: transparent; border: none;")
        self.ai_layout.addWidget(self.ai_info_widget)
        self.ai_info_layout = QVBoxLayout()
        self.ai_info_widget.setLayout(self.ai_info_layout)

        self.info_title = QLabel("Звіт нейромережі")
        self.ai_info_layout.addWidget(self.info_title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.info_title.setStyleSheet("color: #ffd500; font-size: 15px;")

        self.info_class_name = QLabel()
        self.info_conf = QLabel()
        self.info_xyxy = QLabel()

        self.info_x1 = QLabel()
        self.info_y1 = QLabel()
        self.info_x2 = QLabel()
        self.info_y2 = QLabel()

        self.ai_info_layout.addWidget(self.info_class_name, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_conf, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_xyxy, alignment=Qt.AlignmentFlag.AlignLeft)

        self.ai_info_layout.addWidget(self.info_x1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_y1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_x2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_y2, alignment=Qt.AlignmentFlag.AlignLeft)

        self.ai_info_layout.addStretch()

        
        self.secon_layout.addStretch()



    def add_image_to_array(self, file_path):
        self.file_path = file_path

        self.img = Image.open(self.file_path).convert("RGB")
        self.img_ar = np.array(self.img)
        self.image_array.append({
                                "path": self.file_path,
                                "np_array": self.img_ar}) 
        




    def add_color(self, color, x, y, which):
        self.output = Image_Output(self)
        self.output.set_color(color)

        self.output_widgets.append(self.output)

        if which == "first":
            self.first_color_col.insertWidget(self.first_color_col.count() - 1, self.output)
            
        else:
            self.second_color_col.insertWidget(self.second_color_col.count() - 1, self.output)
            
        for p in self.point_overlay.points:
            if p["x"] == x and p["y"] == y:
                if which == "first":
                    p["label_first"] = self.output
                else:
                    p["label_second"] = self.output
                break



    def switch_mode_func(self, index):
        #print("img1 size:", self.image1.size(), "img2 size:", self.image2.size())
        #print("point overlay size:", self.point_overlay.size(), "duped layer size:", self.duped_layer.size())
        #print("grid overlay size:", self.grid_overlay.size(), "grid overlay2 size:", self.grid_overlay2.size())

        if index == 0 and self.image_array:
            #POINT MODE

            self.ai_widget.hide()

            self.image_widget.show()
            self.color_title.show()
            self.color_widget.show()

            self.ai_image_box.hide()

            self.point_overlay.show()
            self.duped_layer.show()

            self.grid_overlay.hide()
            self.grid_overlay2.hide()

            self.compare_title.setText("Режим точок")

            for widget in self.output_widgets:
                widget.show()
            
            for frame in self.mesh_arr:
                frame.deleteLater()
            self.mesh_arr.clear()

            self.slider_widget.show()
            self.diff_widget.hide()
            self.sizer_widget.hide()

            self.window.update()

        elif index == 1 and SelectableImageBox.path[1] is not None and SelectableImageBox.path[2] is not None:
            #GRID MODE 

            self.ai_widget.hide()

            self.image_widget.show()
            self.color_title.show()
            self.color_widget.show()

            self.ai_image_box.hide()

            self.compare_title.setText("Режим сітки")

            self.point_overlay.hide()
            self.duped_layer.hide()

            self.grid_overlay.show()
            self.grid_overlay2.show()

            self.grid_overlay.img_arr = self.image_array[0]["np_array"]
            self.grid_overlay2.img_arr = self.image_array[1]["np_array"]

            self.grid_overlay.draw_grid(self.diff_slider.value())
            self.grid_overlay2.draw_grid(self.diff_slider.value())
                

            self.slider_widget.hide()
            self.diff_widget.show()
            self.sizer_widget.show()

            for widget in self.output_widgets:
                widget.hide()

            self.window.update()

        elif index == 2 and self.image_array:
            #NEURAL NETWORK MODE

            self.image_widget.hide()
            self.color_title.hide()
            self.color_widget.hide()

            self.compare_title.setText("Режим нейромережі")

            output_path, self.class_name, self.conf, self.xyxy = run_yolo(SelectableImageBox.path[1])

            pixmap = QPixmap(output_path)
            pixmap = pixmap.scaled(1200, 1200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.ai_image_box.setPixmap(pixmap)
            self.ai_image_box.setScaledContents(True)


            self.info_class_name.setText(f"Classes: {self.class_name}")
            self.info_conf.setText(f"Confidence: {self.conf * 100} %")
            self.info_xyxy.setText(f"Bounding Box cords:")

            self.info_x1.setText(f"  x1: {self.xyxy[0]} px")
            self.info_y1.setText(f"  y1: {self.xyxy[1]} px")
            self.info_x2.setText(f"  x2: {self.xyxy[2]} px")
            self.info_y2.setText(f"  y2: {self.xyxy[3]} px")

            self.ai_widget.show()
            self.ai_image_box.show()

            self.window.update()

        else:
            QMessageBox.warning(self, "Попередження", "Будь ласка, виберіть два зображення для порівняння.")
            self.mode_selection.blockSignals(True)
            self.mode_selection.setCurrentIndex(0)
            self.mode_selection.blockSignals(False)





    def rewrite_grid(self):
        if not self.image_array:
            return
        

        self.grid_overlay.img_arr = self.image_array[0]["np_array"]
        self.grid_overlay.draw_grid(self.diff_slider.value())

        self.grid_overlay2.img_arr = self.image_array[1]["np_array"]
        self.grid_overlay2.draw_grid(self.diff_slider.value())





    def resize_grid(self):
        if not self.image_array:
            return

        self.grid_overlay.img_arr = self.image_array[0]["np_array"]
        self.grid_overlay2.img_arr = self.image_array[1]["np_array"]

        self.grid_overlay.calculate_grid()
        self.grid_overlay2.calculate_grid()

        self.grid_overlay.draw_grid(self.diff_slider.value())
        self.grid_overlay2.draw_grid(self.diff_slider.value())




    def check_images(self, x, y):
        if self.mode_selection.currentIndex() == 1:
            return

        if SelectableImageBox.path[1] is None or SelectableImageBox.path[2] is None:
            QMessageBox.warning(self, "Попередження", "Будь ласка, виберіть два зображення для порівняння.")
            return

        self.point_overlay.add_point(x, y)
        self.point_overlay.average_colors()
        self.duped_layer.add_point(x, y)