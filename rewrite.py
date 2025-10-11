
# PyQt6 imports
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QLabel, QFileDialog, QFrame, QSlider
from PyQt6.QtGui import QPixmap
from PyQt6.QtGui import QIcon, QPainter, QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QPoint, pyqtSignal

# Pillow and numpy imports
from PIL import Image
from PIL.ImageQt import ImageQt
import numpy as np





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Просте вікно")
        self.setGeometry(300, 100, 1200, 900) #x, y, width, height
        self.setWindowIcon(QIcon('radar.ico'))
        self.Main_Widget = QWidget() # Main Widget
        self.Main_layout = QHBoxLayout()
        self.Main_layout.setContentsMargins(10, 10, 10, 10)
        self.Main_layout.setSpacing(10)
        self.Main_Widget.setLayout(self.Main_layout)
        self.setCentralWidget(self.Main_Widget) # Setting the central widget

        self.main_col = QVBoxLayout()
        self.Main_layout.addLayout(self.main_col)


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

        self.cats_layout = QHBoxLayout()
        self.cats_widget = QWidget()
        self.cats_widget.setMinimumHeight(300)
        self.cats_widget.setMaximumHeight(400)
        self.cats_widget.setStyleSheet("background-color: #2b2b2b; border-radius: 8px; padding: 2px; border: 1px solid #808080;")
        self.cats_widget.setLayout(self.cats_layout)

        self.main_col.addWidget(self.cats_widget, alignment=Qt.AlignmentFlag.AlignTop)

        self.main_col.addStretch()


        self.add_second_col = SecondColumn()
        self.Main_layout.addWidget(self.add_second_col)

    def add_category(self):
        category_name = self.name_input.text().strip()
        if category_name:
            self.name_input.clear()

            category = CategoryWidget(self, category_name=category_name, second_col = self.add_second_col, image1=self.add_second_col.image1, image2=self.add_second_col.image2)

            category.setMaximumWidth(300)
            category.setMinimumWidth(200)

            category.add_image_to_array.connect(self.add_second_col.add_image_to_array) # Connect signal to second column method

            self.cats_layout.addWidget(category, alignment=Qt.AlignmentFlag.AlignLeft)
              







class SecondColumn(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.image_array = []   # List to store image pixel data
        self.output_widgets = []  # List to store output widgets    

        self.secon_layout = QVBoxLayout(self)
        
        self.compare_layout = QHBoxLayout()
        self.secon_layout.addLayout(self.compare_layout)

        self.compare_title = QLabel("Порівняння категорій")
        self.compare_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.compare_title.setStyleSheet("font-size: 14px; color: #ffd500; padding: 10px;")
        self.compare_layout.addWidget(self.compare_title, alignment=Qt.AlignmentFlag.AlignHCenter)

        

        self.mode_1 = QLabel("Точки")
        self.mode_1.setStyleSheet("color: #ffd500;")

        self.mode_2 = QLabel("Сітка")
        self.mode_2.setStyleSheet("color: #ffd500;")

        self.switch_mode = QSlider()
        self.switch_mode.setFixedSize(60, 30)
        self.switch_mode.setOrientation(Qt.Orientation.Horizontal)
        self.switch_mode.setMinimum(1)
        self.switch_mode.setMaximum(2)
        self.switch_mode.setValue(1)
        self.switch_mode.setTickInterval(1)
        self.switch_mode.setTickPosition(QSlider.TickPosition.NoTicks)
        self.switch_mode.valueChanged.connect(self.switch_mode_func)

        self.switch_layout = QHBoxLayout()
        self.switch_widget = QWidget()
        self.switch_widget.setLayout(self.switch_layout)

        self.switch_layout.addWidget(self.mode_2)
        self.switch_layout.addWidget(self.switch_mode)
        self.switch_layout.addWidget(self.mode_1)

        self.compare_layout.addWidget(self.switch_widget, alignment=Qt.AlignmentFlag.AlignRight)



        

        self.image_widget = QWidget()
        self.image_widget.setStyleSheet("border: 1px solid #808080; border-radius: 10px; background-color: #2b2b2b;")
        self.image_layout = QHBoxLayout()
        self.image_widget.setLayout(self.image_layout)
        self.secon_layout.addWidget(self.image_widget)

        self.image1 = ClickableLabel(self)
        self.image1.setStyleSheet("border: none; background: transparent")
        self.image1.setMinimumHeight(135)
        self.image1.setMinimumWidth(240)
        self.image2 = QLabel()
        self.image2.setMinimumWidth(240)
        self.image2.setStyleSheet("border: none; background: transparent")
        self.image_layout.addWidget(self.image1)
        self.image_layout.addWidget(self.image2)

        self.help_overlay = QHBoxLayout()
        self.help_overlay.setContentsMargins(0, 0, 0, 0)
        self.help_overlay.setSpacing(0)
        self.image1.setLayout(self.help_overlay)

        self.help_overlay2 = QHBoxLayout()
        self.help_overlay2.setContentsMargins(0,0,0,0)
        self.help_overlay2.setSpacing(0)
        self.image2.setLayout(self.help_overlay2)

        self.slider_widget = QWidget()
        self.slider_layout = QVBoxLayout()
        self.slider_widget.setLayout(self.slider_layout)
        self.secon_layout.addWidget(self.slider_widget, alignment=Qt.AlignmentFlag.AlignRight)

        self.title_value_layout = QHBoxLayout()
        self.slider_layout.addLayout(self.title_value_layout)

        self.radius_title = QLabel("Радіус")
        self.title_value_layout.addWidget(self.radius_title)
        self.radius_title.setStyleSheet("color: #ffd500;")

        self.slider_value = QLabel()
        self.slider_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_value_layout.addWidget(self.slider_value)
        self.slider_value.setMinimumHeight(25)
        self.slider_value.setStyleSheet("border: 1px solid #808080; border-radius: 10px")

        self.radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.radius_slider.setFixedWidth(200)
        self.slider_layout.addWidget(self.radius_slider)
        self.radius_slider.setMinimum(3)
        self.radius_slider.setMaximum(50)
        self.radius_slider.setValue(10)
        self.radius_slider.setTickInterval(1)
        self.radius_slider.setTickPosition(QSlider.TickPosition.NoTicks)

        self.slider_value.setText(str(self.radius_slider.value()))
        self.radius_slider.valueChanged.connect(lambda value: self.slider_value.setText(str(value)))
        
        self.point_overlay = PointPlacer(self, image1=self.image1, slider = self.radius_slider, second_column=self, mode = self.switch_mode.value())
        self.point_overlay.resize(self.image1.size())
        self.point_overlay.show()


        self.duped_layer = Duped_layer(self, image2 = self.image2, slider = self.radius_slider, mode = self.switch_mode.value())
        self.duped_layer.resize(self.image2.size())
        self.duped_layer.show()


        self.point_overlay.right_clicked.connect(self.duped_layer.delete_point)

        self.image1.clicked.connect(self.point_overlay.add_point)
        self.image1.clicked.connect(self.point_overlay.average_colors)
        self.image1.clicked.connect(self.duped_layer.add_point)

        self.help_overlay.addWidget(self.point_overlay)
        self.help_overlay2.addWidget(self.duped_layer)

        self.point_overlay.send_color.connect(self.add_color)

        self.color_layout = QHBoxLayout()
        self.secon_layout.addLayout(self.color_layout)
        self.first_color_col = QVBoxLayout()
        self.color_layout.addLayout(self.first_color_col)
        self.second_color_col = QVBoxLayout()
        self.color_layout.addLayout(self.second_color_col)

        self.secon_layout.addStretch()


    def add_image_to_array(self, file_path):
        self.file_path = file_path

        self.img = Image.open(self.file_path).convert("RGB")
        self.img_ar = np.array(self.img)
        self.image_array.append({
                                "path": self.file_path,
                                "np_array": self.img_ar})  # Store the image array

    def add_color(self, color, x, y, which):
        self.output = Image_Output(self, second_col=self)
        self.output.set_color(color)
        self.first_color_col.addWidget(self.output)

        self.output_widgets.append(self.output)  # Store the output widget

        if which == "first":
            self.first_color_col.addWidget(self.output)
        else:
            self.second_color_col.addWidget(self.output)

        for p in self.point_overlay.points:
            if p["x"] == x and p["y"] == y:
                if which == "first":
                    p["label_first"] = self.output
                else:
                    p["label_second"] = self.output
                break


    def switch_mode_func(self):
        if self.switch_mode.value() == 1:
            self.point_overlay.show()
            self.duped_layer.show()

            for widget in self.output_widgets:
                widget.show()
        else:
            self.point_overlay.hide()
            self.duped_layer.hide()

            for widget in self.output_widgets:
                widget.hide()







class Image_Output(QWidget):
    def __init__(self, parent=None, second_col=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)
        self.current_color = 70, 130, 180  # Default color (steel blue)
        
        self.color = QLabel()
        self.color.setFixedSize(20, 20)
        self.layout.addWidget(self.color)
        self.color.show()

        self.color_value = QLabel()
        self.layout.addWidget(self.color_value)
        self.color.setStyleSheet("border: 1px solid black; border-radius: 2px;")

    def set_color(self, color):
        r, g, b = color
        self.color_value.setText(str(color))
        
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
        self.category_name.setStyleSheet("background-color: #3b3b3b; border-radius: 8px; padding: 0px 30px;")
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
        self.add_image_btn.clicked.connect(self.add_image)
        self.category_layout.addWidget(self.add_image_btn, alignment=Qt.AlignmentFlag.AlignBottom)

        self.switch_image_btn = QPushButton("Змінити зображення")
        self.switch_image_btn.clicked.connect(self.switch_image)


    def add_image(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Виберіть зображення", "C:\\Users\\AUXIDTEX\\Pictures", "Image Files (*.png *.jpg *.jpeg *.svg *.dng)")
        if self.file_path:

            pixmap = QPixmap(self.file_path)
            pixmap = pixmap.scaled(150, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation) #Quality 300 x 300
            self.Image_box.setPixmap(pixmap)
            self.Image_box.setScaledContents(True)

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
            pixmap = pixmap.scaled(150, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.Image_box.setPixmap(pixmap)
            self.Image_box.setScaledContents(True)

            
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
                pixmap = pixmap.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image1.setPixmap(pixmap)
                self.image1.setScaledContents(True)

                SelectableImageBox.path[1] = self.file_path 

                SelectableImageBox.count[1] = 1

            elif SelectableImageBox.count[2] is None:

                pixmap = QPixmap(self.file_path)
                pixmap = pixmap.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image2.setPixmap(pixmap)
                self.image2.setScaledContents(True)

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

    def __init__(self, parent=None, image1=None, slider = None, second_column=None, mode=None):
        super().__init__(parent)

        self.second_column = second_column
        self.mode = mode
        
        self.setStyleSheet("background-color: transparent;")
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        
        self.radius_slider = slider

        self.points = []
        self.radius = 10

    def add_point(self, x, y):

        self.radius = self.radius_slider.value()
        
        image1 = QLabel(self)
        image1.setFixedSize(self.radius * 2, self.radius * 2)
        pixmap = QPixmap('holo.png')
        pixmap = pixmap.scaled(1000, 1000, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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
        if event.button() == Qt.MouseButton.RightButton and self.mode == 1:
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
    def __init__(self, parent=None, image2=None, slider = None, mode=None):
        super().__init__(parent)
        
        self.setStyleSheet("background-color: transparent;")
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())

        self.mode = mode
        self.points = []
        self.radius_slider = slider
        
    def add_point(self, x, y):
        self.radius = self.radius_slider.value()

        image1 = QLabel(self)
        image1.setFixedSize(self.radius * 2, self.radius * 2)
        pixmap = QPixmap('holo.png')
        pixmap = pixmap.scaled(1000, 1000, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image1.setPixmap(pixmap) 
        image1.setScaledContents(True)
        self.points.append((x, y, image1, self.radius))

        image1.move(x - self.radius // 2, y - self.radius // 2)  # Center the image on the click position
        image1.show()

    def delete_point(self, xp, yp):
        if self.mode == 1:
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

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
