from PIL import Image
import numpy as np

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QFileDialog, QHBoxLayout, QSizePolicy

from modules.image_scaling import scale_pixmap_to_fit
from modules.image_selected import Image_Selected
from modules.selectable_imagebox import SelectableImageBox


class CategoryWidget(QWidget):
    add_image_to_array = pyqtSignal(str)
    deleted = pyqtSignal(object)

    def __init__(self, parent=None, category_name=None, second_col=None, image1=None, image2=None):
        super().__init__(parent)

        self.file_path = None
        self.preview_min_size = QSize(150, 110)

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

        self.Image_border = QFrame()
        self.Image_border.setStyleSheet("border: none;")

        self.Image_border_layout = QVBoxLayout(self.Image_border)
        self.Image_border_layout.setContentsMargins(0, 0, 0, 0)
        self.Image_border_layout.setSpacing(0)
        self.category_layout.addWidget(self.Image_border, alignment=Qt.AlignmentFlag.AlignCenter)

        self.Image_box = SelectableImageBox(
            self.Image_border,
            second_column=self.second_column,
            image1=image1,
            image2=image2,
            point_placer=self.point_overlay,
            duped_layer=self.duped_layer,
            grid_overlay=self.grid_overlay,
            grid_overlay2=self.grid_overlay2,
            index=self.index,
        )

        self.image_selection_handler = Image_Selected(self.Image_box, self.second_column)
        self.Image_box.selection_changed.connect(self.second_column.spectral_filterer.set_image)

        self.Image_box.setStyleSheet("border: none;")
        self.Image_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.Image_box.setMinimumSize(self.preview_min_size)
        self.Image_border_layout.addWidget(self.Image_box)

        self.bottom_container = QHBoxLayout()
        self.bottom_widget = QWidget()
        self.bottom_widget.setStyleSheet("border: none; background-color: transparent;")
        self.bottom_widget.setLayout(self.bottom_container)
        self.category_layout.addWidget(self.bottom_widget, alignment=Qt.AlignmentFlag.AlignBottom)

        self.add_image_btn = QPushButton("Додати зображення")
        self.add_image_btn.setMinimumHeight(32)
        self.add_image_btn.setStyleSheet("color: white; border: 1px solid #808080; padding: 6px 12px; border-radius: 8px; background-color: #3b3b3b;")
        self.add_image_btn.clicked.connect(self.add_image)
        self.bottom_container.addWidget(self.add_image_btn)

        self.switch_image_btn = QPushButton("Змінити зображення")
        self.switch_image_btn.setStyleSheet("color: white; border: 1px solid #808080; padding: 6px 12px; border-radius: 8px; background-color: #3b3b3b;")
        self.switch_image_btn.clicked.connect(self.switch_image)

        self.delete_category_button = QPushButton()
        self.delete_category_button.setStyleSheet("background-color: #3b3b3b; border-radius: 8px; border: 1px solid #808080;")
        self.bottom_container.addWidget(self.delete_category_button)
        self.delete_category_button.setIcon(QIcon("app/assets/delete_icon.png"))
        self.delete_category_button.setIconSize(QSize(24, 24))
        self.delete_category_button.setMinimumSize(32, 32)
        self.delete_category_button.setMaximumSize(38, 38)
        self.delete_category_button.clicked.connect(self.delete_category)

        self.Image_box.image_selected.connect(self.second_column.ai_module.select_image)
        manager = getattr(self.second_column.window, "settings_manager", None)
        language = manager.get_language() if manager else "uk"
        self.apply_language(language)

    def _refresh_preview(self):
        if not self.file_path:
            return

        pixmap = QPixmap(self.file_path)
        scaled = scale_pixmap_to_fit(pixmap, self.Image_box.size(), min_w=1, min_h=1)
        if scaled.isNull():
            return

        self.Image_box.setPixmap(scaled)
        self.Image_box.setScaledContents(False)

    def add_image(self):
        start_path = self.second_column.window.get_default_open_path()
        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.second_column.window.get_text("pick_image_title"),
            start_path,
            "Image Files (*.png *.jpg *.jpeg *.svg *.dng)",
        )
        if not self.file_path:
            return

        self._refresh_preview()
        self.add_image_btn.hide()
        self.bottom_container.insertWidget(0, self.switch_image_btn)

        self.Image_box.set_image_path(self.file_path)
        self.add_image_to_array.emit(self.file_path)

    def switch_image(self):
        old_path = self.file_path

        start_path = self.second_column.window.get_default_open_path()
        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.second_column.window.get_text("pick_image_title"),
            start_path,
            "Image Files (*.png *.jpg *.jpeg *.tiff *.svg)",
        )
        if not self.file_path:
            self.file_path = old_path
            return

        index = next((i for i, item in enumerate(self.image_array) if item["path"] == old_path), None)

        if index is not None:
            img = Image.open(self.file_path).convert("RGB")
            img_ar = np.array(img)
            self.image_array[index] = {"path": self.file_path, "np_array": img_ar}

        if SelectableImageBox.path[1] == old_path:
            SelectableImageBox.path[1] = self.file_path
        elif SelectableImageBox.path[2] == old_path:
            SelectableImageBox.path[2] = self.file_path

        self.Image_box.set_image_path(self.file_path)
        self._refresh_preview()
        self.second_column.refresh_selected_images()
        self.second_column.spectral_filterer.set_image()

    def delete_category(self):
        if SelectableImageBox.path[1] == self.Image_box.file_path:
            self.Image_box.image1.setPixmap(QPixmap())
            SelectableImageBox.path[1] = None
            SelectableImageBox.count[1] = None
            self.point_overlay.hide()
            self.grid_overlay.hide()

        elif SelectableImageBox.path[2] == self.Image_box.file_path:
            self.Image_box.image2.setPixmap(QPixmap())
            SelectableImageBox.path[2] = None
            SelectableImageBox.count[2] = None
            self.duped_layer.hide()
            self.grid_overlay2.hide()

        for image in self.image_array:
            if image["path"] == self.file_path:
                self.image_array.remove(image)
                break

        self.second_column.refresh_selected_images()
        self.second_column.spectral_filterer.set_image()

        self.deleted.emit(self)
        self.setParent(None)
        self.deleteLater()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_preview()

    def apply_language(self, language):
        self.add_image_btn.setText(self.second_column.window.get_text("add_image"))
        self.switch_image_btn.setText(self.second_column.window.get_text("switch_image"))
