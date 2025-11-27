from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel


class SelectableImageBox(QLabel):
    count = {1: None, 2: None}  # List for both images
    path = {1: None, 2: None}  # Dictionary to store paths for both images
    index = 0
     
    def __init__(self, parent=None, second_column=None, image1=None, image2=None, point_placer=None, duped_layer=None, grid_overlay=None, grid_overlay2=None, index=None):
        super().__init__(parent)
        self.selected = False
        self.setStyleSheet("border: none;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_path = None

        self.frame = parent
        self.image1 = image1  # Reference to the first image in the second column
        self.image2 = image2  # Reference to the second image in the second column
        self.index = index

        self.point_placer = point_placer
        self.duped_layer = duped_layer
        self.grid_overlay = grid_overlay
        self.grid_overlay2 = grid_overlay2

        self.image_layout = second_column # Layout for the second column where selected images will be displayed


    def set_image_path(self, file_path):
        self.file_path = file_path


    def mousePressEvent(self, event):
        self.selected = not self.selected
        
        index = SelectableImageBox.index

        if self.selected:
            self.frame.setStyleSheet("border: 2px solid #007acc;")


            if SelectableImageBox.count[1] is None:

                pixmap = QPixmap(self.file_path)

                ratio = pixmap.size().width() / pixmap.size().height()
                #print("Aspect Ratio of img1:", ratio)

                # Adjust scaling based on aspect ratio
                if pixmap.size().width() > pixmap.size().height():
                    pixmap = pixmap.scaled(320, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                elif pixmap.size().height() > pixmap.size().width():
                    pixmap = pixmap.scaled(180, 320, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                self.image1.setPixmap(pixmap)
                self.image1.setFixedSize(pixmap.size())

                self.point_placer.resize(self.image1.size())
                self.grid_overlay.resize(self.image1.size())

                self.image1.parent().update()

                if index == 0:
                    self.point_placer.show()
                if index == 1: 
                    self.grid_overlay.show()


                SelectableImageBox.path[1] = self.file_path 

                SelectableImageBox.count[1] = 1

            elif SelectableImageBox.count[2] is None:

                pixmap = QPixmap(self.file_path)

                ratio = pixmap.size().width() / pixmap.size().height()
                #print("Aspect Ratio of img2:", ratio)

                # Adjust scaling based on aspect ratio
                if pixmap.size().width() > pixmap.size().height():
                    pixmap = pixmap.scaled(320, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                elif pixmap.size().height() > pixmap.size().width():
                    pixmap = pixmap.scaled(180, 320, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                self.image2.setPixmap(pixmap)
                self.image2.setFixedSize(pixmap.size())

                self.duped_layer.resize(self.image2.size())
                self.grid_overlay2.resize(self.image2.size())

                self.image2.parent().update()

                if index == 0:
                    self.duped_layer.show()
                if index == 1: 
                    self.grid_overlay2.show()

                SelectableImageBox.path[2] = self.file_path

                SelectableImageBox.count[2] = 1

        else:
            self.frame.setStyleSheet("border: none;")
            
            if SelectableImageBox.count[2] is not None and SelectableImageBox.path[2] == self.file_path:
                self.image2.clear()

                self.duped_layer.hide()
                self.grid_overlay2.hide()

                SelectableImageBox.count[2] = None
                SelectableImageBox.path[2] = None
            else:
                self.image1.clear()

                self.point_placer.hide()
                self.grid_overlay.hide()

                SelectableImageBox.count[1] = None
                SelectableImageBox.path[1] = None


    @staticmethod
    def update_index(index):
        SelectableImageBox.index = index

