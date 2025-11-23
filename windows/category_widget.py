from windows.selectable_imagebox import SelectableImageBox
from windows.second_column import SecondColumn

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QFileDialog
from PIL import Image
import numpy as np



class CategoryWidget(QWidget):
    add_image_to_array = pyqtSignal(str)
    def __init__(self, parent=None, category_name=None, second_col=None, image1=None, image2=None):
        super().__init__(parent)
        
        self.image_layout = second_col.image_layout  
        self.image_array = second_col.image_array
        self.category_layout = QVBoxLayout(self)

        self.second_column = second_col
        self.point_overlay = second_col.point_overlay
        self.duped_layer = second_col.duped_layer
        self.grid_overlay = second_col.grid_overlay
        self.grid_overlay2 = second_col.grid_overlay2
        self.index = second_col.mode_selection.currentIndex()

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

        self.Image_box = SelectableImageBox(
            self.Image_border, 
            second_column = self.image_layout, 
            image1=image1, 
            image2=image2, 
            point_placer = self.point_overlay, 
            duped_layer = self.duped_layer, 
            grid_overlay = self.grid_overlay, 
            grid_overlay2 = self.grid_overlay2,
            index = self.index)
        

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
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Виберіть зображення", "/media/auxidtex/Local Disk/Project Data/ai_module/Frames/train", "Image Files (*.png *.jpg *.jpeg *.svg *.dng)")
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

        file_path, _ = QFileDialog.getOpenFileName(self, "Виберіть зображення", "/media/auxidtex/Local Disk/Project Data/ai_module/Frames/train", "Image Files (*.png *.jpg *.jpeg *.tiff *.svg)")
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