from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QPen, QColor
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        pixmap = self.pixmap()
        if pixmap is not None and not pixmap.isNull():
            scaled = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            target = QRect(x, y, scaled.width(), scaled.height())
            painter.drawPixmap(target, scaled)

            if self.selected:
                border_rect = target.adjusted(1, 1, -1, -1)
                pen = QPen(QColor("#007acc"))
                pen.setWidth(2)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(border_rect, 6, 6)
        else:
            if self.selected:
                pen = QPen(QColor("#007acc"))
                pen.setWidth(2)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)

    def set_image_path(self, file_path):
        self.file_path = file_path

    @staticmethod
    def unregister_instance(instance):
        if instance in SelectableImageBox.instances:
            SelectableImageBox.instances.remove(instance)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        if self.selected:
            self.selected = False
            if SelectableImageBox.path[2] == self.file_path:
                self._clear_image(2)
            elif SelectableImageBox.path[1] == self.file_path:
                self._clear_image(1)
        else:
            if SelectableImageBox.count[1] is None:
                self.selected = True
                self._set_image(1)
                self.image_selected.emit(1)
            elif SelectableImageBox.count[2] is None:
                self.selected = True
                self._set_image(2)
                self.image_selected.emit(2)
            else:
                QMessageBox.warning(
                    self,
                    "Вже вибрано 2 зображення",
                    "Можна вибрати лише два зображення одночасно.",
                )
                self.selected = False
                return

        if SelectableImageBox.count[1] is None and SelectableImageBox.count[2] is None:
            SelectableImageBox.path[1] = None
            SelectableImageBox.path[2] = None

    def _set_image(self, slot):
        SelectableImageBox.path[slot] = self.file_path
        SelectableImageBox.count[slot] = 1

        if self.second_column is not None:
            self.second_column.refresh_selected_images()

        self.update()
        self.selection_changed.emit()

    def _clear_image(self, slot):
        SelectableImageBox.count[slot] = None
        SelectableImageBox.path[slot] = None

        if self.second_column is not None:
            self.second_column.refresh_selected_images()

        self.update()
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
            instance.update()
            instance.selection_changed.emit()
