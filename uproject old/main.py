from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QLabel, QFileDialog, QFrame, QSlider, QSizePolicy, QMessageBox, QScrollArea, QComboBox
from PyQt6.QtGui import QIcon, QPainter, QPen, QColor, QPalette, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

# Pillow and numpy imports
from PIL import Image
import numpy as np
import math
from run_AI import run_yolo
import os





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Порівняння зображень")
        self.setGeometry(0, 0, 1400, 900) #x, y, width, height
        self.setWindowIcon(QIcon('radar.ico'))
        self.Main_Widget = QWidget() # Main Widget
        self.Main_layout = QHBoxLayout()
        self.Main_layout.setContentsMargins(10, 10, 10, 10)
        self.Main_layout.setSpacing(10)
        self.Main_Widget.setLayout(self.Main_layout)
        self.setCentralWidget(self.Main_Widget) # Setting the central widget

        self.main_col_widget = QWidget()
        self.main_col = QVBoxLayout()
        self.main_col_widget.setLayout(self.main_col)
        self.main_col_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.Main_layout.addWidget(self.main_col_widget, stretch=1)



        self.add_layout = QHBoxLayout()
        self.add_layout.setContentsMargins(0, 0, 0, 0)
        self.add_layout.setSpacing(5)
        self.add_widget = QWidget()
        self.add_widget.setLayout(self.add_layout)
        self.main_col.addWidget(self.add_widget, alignment=Qt.AlignmentFlag.AlignTop)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введіть назву")
        self.name_input.setStyleSheet("padding: 6px; border-radius: 8px; background-color: #3b3b3b; color: white; border: 1px solid #808080;")
        self.add_layout.addWidget(self.name_input)

        self.add_button = QPushButton("Додати")
        self.add_button.clicked.connect(self.add_category)
        self.add_button.setStyleSheet("background-color: transparent; color: #ffd500; padding: 8px 14px; border-radius: 8px; border: 1px solid #ffd500;")
        self.add_layout.addWidget(self.add_button)


        self.cats_frame = QFrame()
        self.cats_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #808080; border-radius: 8px; padding: 2px;")

        self.cats_layout = QHBoxLayout(self.cats_frame)
        self.cats_layout.setContentsMargins(5, 5, 5, 5)
        self.cats_layout.setSpacing(10)
        self.cats_layout.addStretch()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setMinimumHeight(300)
        self.scroll_area.setMaximumHeight(400)

        self.scroll_area.setWidget(self.cats_frame)
        self.main_col.addWidget(self.scroll_area, alignment=Qt.AlignmentFlag.AlignTop)


        self.settings_widget = QWidget()
        self.settings_layout = QHBoxLayout()
        self.main_col.addWidget(self.settings_widget)
        self.settings_widget.setLayout(self.settings_layout)
        self.settings_widget.setStyleSheet("background-color: #2b2b2b; border: 1px solid #808080; border-radius: 8px; padding: 5px;")

        self.second_col = SecondColumn(self, settings_layout = self.settings_layout)
        self.second_col.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.Main_layout.addWidget(self.second_col, stretch=1) 

        self.main_col.addStretch()
        

    def add_category(self):
        category_name = self.name_input.text().strip()
        if category_name:
            self.name_input.clear()

            category = CategoryWidget(self, category_name=category_name, second_col = self.second_col, image1=self.second_col.image1, image2=self.second_col.image2)

            category.setMaximumWidth(300)
            category.setMinimumWidth(200)

            category.add_image_to_array.connect(self.second_col.add_image_to_array) # Connect signal to second column method

            self.cats_layout.insertWidget(self.cats_layout.count() - 1, category)
              







class SecondColumn(QWidget):
    def __init__(self, parent=None, settings_layout=None):
        super().__init__(parent)

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


        self.image_box = QLabel()
        self.image_box.hide()
        self.image_box.setFixedSize(300, 533)
        self.secon_layout.addWidget(self.image_box)
        
        self.secon_layout.addStretch()



    def add_image_to_array(self, file_path):
        self.file_path = file_path

        self.img = Image.open(self.file_path).convert("RGB")
        self.img_ar = np.array(self.img)
        self.image_array.append({
                                "path": self.file_path,
                                "np_array": self.img_ar}) 
        




    def add_color(self, color, x, y, which):
        self.output = Image_Output(self, second_col=self)
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
        if index == 0 and self.image_array:
            self.image_widget.show()
            self.color_title.show()
            self.color_widget.show()

            self.image_box.hide()

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

        elif index == 1 and len(self.image_array) > 0:
            self.image_widget.show()
            self.color_title.show()
            self.color_widget.show()

            self.image_box.hide()

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

        elif index == 2 and self.image_array:
            self.image_box.show()
            
            self.image_widget.hide()
            self.color_title.hide()
            self.color_widget.hide()

            output_path = run_yolo(SelectableImageBox.path[1])

            pixmap = QPixmap(output_path)
            pixmap = pixmap.scaled(1200, 1200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_box.setPixmap(pixmap)
            self.image_box.setScaledContents(True)

            current_width = window.width()
            window.resize(current_width, 900)



        else:
            QMessageBox.warning(self, "Попередження", "Будь ласка, додайте 2 зображення в категорію перед перемиканням режимів.")
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
        if self.mode_selection.currentIndex == 1:
            return

        if SelectableImageBox.path[1] is None or SelectableImageBox.path[2] is None:
            QMessageBox.warning(self, "Попередження", "Будь ласка, виберіть два зображення для порівняння.")
            return

        self.point_overlay.add_point(x, y)
        self.point_overlay.average_colors()
        self.duped_layer.add_point(x, y)





class Image_Output(QWidget):
    def __init__(self, parent=None, second_col=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)
        self.current_color = 70, 130, 180  # Default color (steel blue)
        
        self.color = QLabel()
        self.color.setStyleSheet("border: 1px solid black; border-radius: 2px;")
        self.color.setFixedSize(20, 20)
        self.layout.addWidget(self.color)
        self.color.show()

        self.color_value = QLabel()
        self.color_value.setStyleSheet("color: white; border: none;")
        self.layout.addWidget(self.color_value)

    def set_color(self, color):
        r, g, b = color
        self.color_value.setText(', '.join(str(int(c)) for c in color))
        
        self.color.setStyleSheet(f"background-color: rgb({r},{g},{b}); border: 1px solid black; border-radius: 2px;")



            

        
class ClickableLabel(QLabel):
    clicked = pyqtSignal(int,int)
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.x = int(event.position().x())
            self.y = int(event.position().y())

            self.clicked.emit(self.x, self.y)  # Emit the signal with x and y coordinates








class CategoryWidget(QWidget):
    add_image_to_array = pyqtSignal(str)
    def __init__(self, parent=None, category_name=None, second_col=None, image1=None, image2=None):
        super().__init__(parent)
        
        self.image_layout = second_col.image_layout  
        self.image_array = second_col.image_array
        self.category_layout = QVBoxLayout(self)

        self.category_name = QLabel()
        self.category_name.setStyleSheet("background-color: #3b3b3b; border-radius: 8px; padding: 0px 30px; color: white")
        self.category_name.setText(category_name)
        self.category_name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.category_layout.addWidget(self.category_name, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        #Picture
        self.Image_border = QFrame()
        self.Image_border.setStyleSheet("border: none;")

        self.Image_border_layout = QVBoxLayout(self.Image_border)
        self.Image_border_layout.setContentsMargins(0, 0, 0, 0)
        self.Image_border_layout.setSpacing(0)
        self.category_layout.addWidget(self.Image_border, alignment=Qt.AlignmentFlag.AlignCenter)

        self.Image_box = QLabel()
        self.Image_box = SelectableImageBox(self.Image_border, second_column=self.image_layout, image1=image1, image2=image2)
        self.Image_box.setStyleSheet("border: none;")
        self.Image_box.setMinimumHeight(100)
        self.Image_border_layout.addWidget(self.Image_box)

        self.add_image_btn = QPushButton("Додати зображення")
        self.add_image_btn.setStyleSheet("color: white")
        self.add_image_btn.clicked.connect(self.add_image)
        self.category_layout.addWidget(self.add_image_btn, alignment=Qt.AlignmentFlag.AlignBottom)

        self.switch_image_btn = QPushButton("Змінити зображення")
        self.switch_image_btn.setStyleSheet("color: white;")
        self.switch_image_btn.clicked.connect(self.switch_image)


    def add_image(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Виберіть зображення", "C:\\Users\\AUXIDTEX\\Documents\\Project Data\\Frames", "Image Files (*.png *.jpg *.jpeg *.svg *.dng)")
        if self.file_path:

            pixmap = QPixmap(self.file_path)
            pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation) #Quality 300 x 300
            self.Image_box.setPixmap(pixmap)
            self.Image_box.setFixedHeight(200)

            self.add_image_btn.hide() 
            self.category_layout.addWidget(self.switch_image_btn, alignment=Qt.AlignmentFlag.AlignBottom)

            self.Image_box.set_image_path(self.file_path)  # Set the file path for the image box
            
            self.add_image_to_array.emit(self.file_path)

    def switch_image(self):
        old_path = self.file_path

        file_path, _ = QFileDialog.getOpenFileName(self, "Виберіть зображення", "C:\\Users\\AUXIDTEX\\Pictures", "Image Files (*.png *.jpg *.jpeg *.tiff *.svg)")
        if file_path:

            index = next((i for i, item in enumerate(self.image_array) if item["path"] == old_path), None)


            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.Image_box.setPixmap(pixmap)
            self.Image_box.setFixedHeight(200)

            
            if index is not None:
                img = Image.open(file_path).convert("RGB")
                img_ar = np.array(img)

                self.image_array[index] = {
                                    "path": file_path,
                                    "np_array": img_ar}  # Update the image array if path exists

            
                print(len(self.image_array))
            

            if SelectableImageBox.path[1] == file_path:

                pixmap = QPixmap(file_path)
                pixmap = pixmap.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.Image_box.image1.setPixmap(pixmap)
                self.Image_box.image1.setScaledContents(True)

                SelectableImageBox.path[1] = file_path

            else:
                
                pixmap = QPixmap(file_path)
                pixmap = pixmap.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.Image_box.image2.setPixmap(pixmap)
                self.Image_box.image2.setScaledContents(True)

                SelectableImageBox.path[2] = file_path    


            self.Image_box.set_image_path(file_path)  # Update the file path for the image box









        





            
class SelectableImageBox(QLabel):
    count = {1: None, 2: None}  # List for both images
    path = {1: None, 2: None}  # Dictionary to store paths for both images
     
    def __init__(self, parent=None, second_column=None, image1=None, image2=None):
        super().__init__(parent)
        self.selected = False
        self.setStyleSheet("border: none;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_path = None

        self.frame = parent
        self.image1 = image1  # Reference to the first image in the second column
        self.image2 = image2  # Reference to the second image in the second column

        self.image_layout = second_column # Layout for the second column where selected images will be displayed


    def set_image_path(self, file_path):
        self.file_path = file_path


    def mousePressEvent(self, event):
        self.selected = not self.selected

        if self.selected:
            self.frame.setStyleSheet("border: 2px solid #007acc;")


            if SelectableImageBox.count[1] is None:

                pixmap = QPixmap(self.file_path)
                pixmap = pixmap.scaled(300, 225, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image1.setPixmap(pixmap)
                self.image1.setFixedSize(180,320)

                print(self.image1.size())

                SelectableImageBox.path[1] = self.file_path 

                SelectableImageBox.count[1] = 1

            elif SelectableImageBox.count[2] is None:

                pixmap = QPixmap(self.file_path)
                pixmap = pixmap.scaled(300, 225, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image2.setPixmap(pixmap)
                self.image2.setFixedSize(180, 320)


                SelectableImageBox.path[2] = self.file_path

                SelectableImageBox.count[2] = 1

        else:
            self.frame.setStyleSheet("border: none;")
            
            if SelectableImageBox.count[2] is not None and SelectableImageBox.path[2] == self.file_path:
                self.image2.clear()
                SelectableImageBox.count[2] = None
                SelectableImageBox.path[2] = None
            else:
                self.image1.clear()
                SelectableImageBox.count[1] = None
                SelectableImageBox.path[1] = None








        
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
        circle_path = os.path.join(os.path.dirname(__file__), "circle.png")

        self.radius = self.radius_slider.value()
        
        image1 = QLabel(self)
        image1.setFixedSize(self.radius * 2, self.radius * 2)
        pixmap = QPixmap(circle_path)
        pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image1.setPixmap(pixmap) 
        image1.setScaledContents(True)

        self.points.append({
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

        print(avg_color)
        return avg_colors


class Duped_layer(QLabel):
    def __init__(self, parent=None, slider = None, mode=None):
        super().__init__(parent)
        
        self.setStyleSheet("background-color: transparent;")
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())

        self.mode = mode
        self.points = []
        self.radius_slider = slider
        
    def add_point(self, x, y):
        circle_path = os.path.join(os.path.dirname(__file__), "circle.png")
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







class Average_color:
    def __init__(self, image_arr, label_width, label_height):
        self.img_arr = image_arr
        self.label_w = label_width
        self.label_h = label_height


    def calculate(self, x, y, rad):
        h, w, _ = self.img_arr.shape

        scale_x = w / self.label_w
        scale_y = h / self.label_h
            
        real_x = int(x * scale_x)
        real_y = int(y * scale_y)

        x_min = max(real_x - rad, 0)
        x_max = min(real_x + rad, w)
        y_min = max(real_y - rad, 0)
        y_max = min(real_y + rad, h)

        region = self.img_arr[y_min:y_max + 1, x_min:x_max + 1, :]
        avg_chanel = np.mean(region, axis=(0, 1))

        avg_color = tuple(avg_chanel.astype(int))
        return avg_color
    



    
class Grid_Analyzer(QLabel):
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

    def calculate_grid(self): 
        if self.img_arr is None:
            return 

        h, w, _ = self.img_arr.shape
        self.math_size = math.gcd(w, h)
        self.square_size = self.math_size // self.sizer_slider.value()

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

if __name__ == "__main__":
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(35,35,35))

    app = QApplication([])
    app.setPalette(palette)
    window = MainWindow()
    window.show()
    app.exec()
