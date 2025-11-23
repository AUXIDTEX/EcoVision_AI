from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel


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