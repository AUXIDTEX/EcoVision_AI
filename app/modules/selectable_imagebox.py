from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QMessageBox

class SelectableImageBox(QLabel):
    count = {1: None, 2: None}  # Вибрані зображення
    path = {1: None, 2: None}   # Шляхи до зображень
    index = 0
    instances = []

    image_selected = pyqtSignal(int)
    selection_changed = pyqtSignal()  

    def __init__(self, parent=None, second_column=None, image1=None, image2=None, point_placer=None, duped_layer=None, grid_overlay=None, grid_overlay2=None, index=None):
        super().__init__(parent)
        self.selected = False
        self.setStyleSheet("border: none;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_path = None

        self.frame = parent
        self.image1 = image1
        self.image2 = image2
        self.index = index

        self.point_placer = point_placer
        self.duped_layer = duped_layer
        self.grid_overlay = grid_overlay
        self.grid_overlay2 = grid_overlay2

        self.image_layout = second_column
        SelectableImageBox.instances.append(self)

        

    def set_image_path(self, file_path):
        self.file_path = file_path




    def mousePressEvent(self, event):
        self.selected = not self.selected
        index = SelectableImageBox.index


        if self.selected:
            # Якщо можна вибрати нове зображення
            if SelectableImageBox.count[1] is None:
                self._set_image(1, self.image1, self.point_placer, self.grid_overlay, 320, 180)

                self.image_selected.emit(1)

            elif SelectableImageBox.count[2] is None:
                self._set_image(2, self.image2, self.duped_layer, self.grid_overlay2, 320, 180)

                self.image_selected.emit(2)

            else:
                QMessageBox.warning(self, "Вже вибрано 2 зображення",
                                    "Можна вибрати лише два зображення одночасно.")
                return
        else:
            # Зняття вибору
            if SelectableImageBox.path[2] == self.file_path:
                self._clear_image(2, self.image2, self.duped_layer, self.grid_overlay2)
            elif SelectableImageBox.path[1] == self.file_path:
                self._clear_image(1, self.image1, self.point_placer, self.grid_overlay)




        # Якщо обидва зображення знято, скидаємо шляхи
        if SelectableImageBox.count[1] is None and SelectableImageBox.count[2] is None:
            SelectableImageBox.path[1] = None
            SelectableImageBox.path[2] = None



    def _set_image(self, slot, widget, overlay1=None, overlay2=None, w=320, h=180):
        pixmap = QPixmap(self.file_path)
        # Зберігаємо пропорції
        if pixmap.width() > pixmap.height():
            pixmap = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        else:
            pixmap = pixmap.scaled(h, w, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)


        widget.setPixmap(pixmap)
        widget.setFixedSize(pixmap.size())

        if overlay1:
            overlay1.resize(widget.size())
            
        if overlay2:
            overlay2.resize(widget.size())
            

        SelectableImageBox.path[slot] = self.file_path
        SelectableImageBox.count[slot] = 1
        self.frame.setStyleSheet("border: 2px solid #007acc;")

        self.selection_changed.emit()  # Випустити сигнал

    def _clear_image(self, slot, widget, overlay1=None, overlay2=None):
        widget.clear()
        if overlay1:
            overlay1.hide()
        if overlay2:
            overlay2.hide()

        SelectableImageBox.count[slot] = None
        SelectableImageBox.path[slot] = None
        self.frame.setStyleSheet("border: none;")

        self.selection_changed.emit()  # Випустити сигнал


    @staticmethod
    def update_index(index):
        SelectableImageBox.index = index

    @staticmethod
    def reset_selection_state():
        SelectableImageBox.count[1] = None
        SelectableImageBox.count[2] = None
        SelectableImageBox.path[1] = None
        SelectableImageBox.path[2] = None

        for instance in SelectableImageBox.instances:
            instance.selected = False
            if instance.frame is not None:
                instance.frame.setStyleSheet("border: none;")
            instance.selection_changed.emit()
