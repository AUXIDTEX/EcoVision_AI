from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QMessageBox


class SelectableImageBox(QLabel):
    count = {1: None, 2: None}
    path = {1: None, 2: None}
    index = 0
    instances = []

    image_selected = pyqtSignal(int)
    selection_changed = pyqtSignal()

    def __init__(
        self,
        parent=None,
        second_column=None,
        image1=None,
        image2=None,
        point_placer=None,
        duped_layer=None,
        grid_overlay=None,
        grid_overlay2=None,
        index=None,
    ):
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
        self.second_column = second_column

        SelectableImageBox.instances.append(self)

    def set_image_path(self, file_path):
        self.file_path = file_path

    def mousePressEvent(self, event):
        self.selected = not self.selected

        if self.selected:
            if SelectableImageBox.count[1] is None:
                self._set_image(1)
                self.image_selected.emit(1)
            elif SelectableImageBox.count[2] is None:
                self._set_image(2)
                self.image_selected.emit(2)
            else:
                QMessageBox.warning(
                    self,
                    "Вже вибрано 2 зображення",
                    "Можна вибрати лише два зображення одночасно.",
                )
                return
        else:
            if SelectableImageBox.path[2] == self.file_path:
                self._clear_image(2)
            elif SelectableImageBox.path[1] == self.file_path:
                self._clear_image(1)

        if SelectableImageBox.count[1] is None and SelectableImageBox.count[2] is None:
            SelectableImageBox.path[1] = None
            SelectableImageBox.path[2] = None

    def _set_image(self, slot):
        SelectableImageBox.path[slot] = self.file_path
        SelectableImageBox.count[slot] = 1

        if self.frame is not None:
            self.frame.setStyleSheet("border: 2px solid #007acc;")

        if self.second_column is not None:
            self.second_column.refresh_selected_images()

        self.selection_changed.emit()

    def _clear_image(self, slot):
        SelectableImageBox.count[slot] = None
        SelectableImageBox.path[slot] = None

        if self.frame is not None:
            self.frame.setStyleSheet("border: none;")

        if self.second_column is not None:
            self.second_column.refresh_selected_images()

        self.selection_changed.emit()

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
