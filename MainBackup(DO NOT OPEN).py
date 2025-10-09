import sys
import numpy as np
from PIL import Image, ImageQt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QFileDialog, QVBoxLayout, QHBoxLayout, QRadioButton,
    QScrollArea, QGroupBox, QButtonGroup, QMessageBox, QLineEdit,
    QDialog, QComboBox,  QToolButton
)
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QSize

class ImageBox(QLabel):
    def __init__(self, np_array, display_name):
        super().__init__()
        self.np_array = np_array
        self.display_name = display_name
        self.setFixedSize(150, 150)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            border: 1px solid #808080;
            border-radius: 12px;
            background-color: #4d4d4d;
        """)
        self.selected = False

        # Перетворення NumPy → QImage → QPixmap
        image = Image.fromarray(np.clip(np_array, 0, 255).astype(np.uint8))
        qt_image = ImageQt.ImageQt(image)
        pixmap = QPixmap.fromImage(qt_image)

        # Масштабування до високоякісного прев'ю
        preview = pixmap.scaled(
            190, 190,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(preview)

    def mousePressEvent(self, event):
        self.selected = not self.selected
        if self.selected:
            self.setStyleSheet("border: 3px solid #007acc; border-radius: 12px; background-color: #4d4d4d;")
        else:
            self.setStyleSheet("border: 1px solid #808080; border-radius: 12px; background-color: #4d4d4d;")

class Category(QWidget):  # Вигляд категорії
    def __init__(self, name, main_window):
        super().__init__()
        self.main_window = main_window
        self.name = name
        self.images = []
        self.selected_images = []
        self.box = None  # локальний box

        self.setFixedWidth(250)
        self.setStyleSheet("border-radius: 16px;")

        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = QLabel(f"<b>{name}</b>")
        self.title.setFont(QFont("Arial", 10))
        self.title.setStyleSheet("color: white; border-radius: 10px; padding: 5px")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFixedWidth(210)
        self.layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        self.image_layout = QHBoxLayout()
        self.image_layout.setSpacing(5)
        self.image_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.image_layout)

        self.add_button = QPushButton("Додати зображення")
        self.add_button.setStyleSheet("background-color: transparent; color: #ffd500; padding: 5px 12px; border-radius: 10px; border: 1px solid #ffd500; font-size: 12px;")
        self.add_button.clicked.connect(self.add_image)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)
        self.setWindowIcon(QIcon('radar.ico'))

        self.additional_widget = QWidget()
        self.additional_widget.setStyleSheet("border: none")
        self.additional = QHBoxLayout()
        self.additional_widget.setLayout(self.additional)

        self.switch = QPushButton("Змінити зображення")
        self.switch.setStyleSheet("background-color: transparent; color: #ffd500; padding: 5px 12px; border-radius: 10px; border: 1px solid #ffd500; font-size: 12px;")
        self.switch.clicked.connect(self.switch_image)

        self.delete = QToolButton()
        self.delete.setIcon(QIcon("close.png"))
        self.delete.setIconSize(QSize(25,25))
        self.delete.setStyleSheet("border-radius: 10px; background-color: #3b3b3b; border: 1px solid #808080;")

        self.delete.clicked.connect(self.delete_category)

        self.additional.addWidget(self.switch)
        self.additional.addWidget(self.delete)

    def add_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Виберіть зображення", "C:/Users/Public/Pictures", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            pil = Image.open(file_path).convert("RGB")
            thumb = pil.copy()
            thumb.thumbnail((100, 100), Image.LANCZOS)
            arr = np.array(pil, dtype=np.int16)
            name = file_path.split("/")[-1]

            self.box = ImageBox(arr, name)
            self.box.mousePressEvent = lambda event, box=self.box: self.toggle_selection(box)

            self.images.append(self.box)
            self.box.setFixedSize(210, 210)
            self.image_layout.addWidget(self.box)

            self.add_button.hide()
            self.layout.addWidget(self.additional_widget)

    def switch_image(self):
        if self.box:
            if self.box in self.selected_images:
                self.selected_images.remove(self.box)
            if self.box in self.images:
                self.images.remove(self.box)

            self.image_layout.removeWidget(self.box)
            self.box.setParent(None)
            self.box.deleteLater()
            self.box = None

        file_path, _ = QFileDialog.getOpenFileName(self, "Виберіть зображення", "C:/Users/Public/Pictures", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            pil = Image.open(file_path).convert("RGB")
            arr = np.array(pil, dtype=np.int16)
            name = file_path.split("/")[-1]

            self.box = ImageBox(arr, name)
            self.box.mousePressEvent = lambda event, box=self.box: self.toggle_selection(box)

            self.images.append(self.box)
            self.box.setFixedSize(210, 210)
            self.image_layout.addWidget(self.box)

            self.add_button.hide()
            self.layout.addWidget(self.additional_widget)


    def delete_category(self):
        self.main_window.delete_category(self)
    
    def toggle_selection(self, box):
        if not box.selected and len(self.selected_images) >= 2:
            QMessageBox.warning(self, "Помилка", "Можна вибрати лише 2 зображення.")
            return

        box.selected = not box.selected
        if box.selected:
            self.selected_images.append(box)
        else:
            if box in self.selected_images:
                self.selected_images.remove(box)

        if box.selected:
            box.setStyleSheet("border: 2px solid #007acc; border-radius: 12px; background-color: #4d4d4d;")
        else:
            box.setStyleSheet("border: 2px solid #808080; border-radius: 12px; background-color: #4d4d4d;")

    def get_selected_images(self):
        return self.selected_images


class SettingsDialog(QDialog):
    def __init__(self, parent, names):
        super().__init__(parent)
        self.setWindowTitle("Налаштування дій")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()
        self.combo1 = QComboBox()
        self.combo2 = QComboBox()
        self.combo1.addItems(names)
        self.combo2.addItems(names)

        layout.addWidget(QLabel("Від якого зображення віднімати:"))
        layout.addWidget(self.combo1)
        layout.addWidget(QLabel("Що віднімати:"))
        layout.addWidget(self.combo2)

        apply_btn = QPushButton("Застосувати")
        apply_btn.setStyleSheet("padding: 6px; background-color: #28a745; color: white; border-radius: 8px;")
        apply_btn.clicked.connect(self.accept)
        layout.addWidget(apply_btn)

        self.setLayout(layout)

    def get_order(self):
        return self.combo1.currentIndex(), self.combo2.currentIndex()

class MainWindow(QMainWindow):   #головний блок
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Обробка зображень (NumPy + PyQt6)")
        self.setWindowIcon(QIcon("radar.ico"))
        self.setGeometry(100, 100, 1000, 700)

        self.categories = []
        self.subtract_order = (0, 1)

        scroll = QScrollArea()
        self.setCentralWidget(scroll)

        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("background-color: #262626;")
       
        self.main_area = QHBoxLayout()
        self.main_widget.setLayout(self.main_area)

        self.main_col = QVBoxLayout()
        self.main_col.setSpacing(20)
        self.secon_col = QVBoxLayout()

        self.main1_widget = QWidget()
        

        self.secon_widget = QWidget()
        self.secon_widget.setMinimumWidth(350)
        self.main1_widget.setMinimumWidth(500)

        self.main1_widget.setLayout(self.main_col)
        self.secon_widget.setLayout(self.secon_col)

        self.main_area.addWidget(self.main1_widget)
        self.main_area.addWidget(self.secon_widget)

        scroll.setWidgetResizable(True)
        scroll.setWidget(self.main_widget)


        self.cat_name_input = QLineEdit()
        self.cat_name_input.setPlaceholderText("Введіть Назву")
        self.cat_name_input.setStyleSheet("padding: 6px; border-radius: 8px; background-color: #3b3b3b; color: white; border: 1px solid #808080;")
        self.add_cat_btn = QPushButton("Додати")
        self.add_cat_btn.setMinimumWidth(100)
        self.add_cat_btn.setStyleSheet("background-color: transparent; color: #ffd500; padding: 8px 14px; border-radius: 8px; border: 1px solid #ffd500;")
        self.add_cat_btn.clicked.connect(self.add_category)

        cat_top_layout = QHBoxLayout()
        cat_top_layout.addWidget(self.cat_name_input)
        cat_top_layout.addWidget(self.add_cat_btn)
        self.main_col.addLayout(cat_top_layout)

        self.cat_scroll = QScrollArea()
        self.cat_scroll.setWidgetResizable(True)
        self.cat_scroll.setFixedHeight(320)
        self.cat_scroll.setStyleSheet("border: 1px solid #808080; background: #3b3b3b; border-radius: 10px;")

        self.cat_scroll_content = QWidget()
        self.cat_layout = QHBoxLayout()
        self.cat_layout.setContentsMargins(10, 10, 10, 10)
        self.cat_layout.setSpacing(15)
        self.cat_scroll_content.setLayout(self.cat_layout)

        self.cat_scroll.setWidget(self.cat_scroll_content)
        self.main_col.addWidget(self.cat_scroll)

        self.ops_box = QGroupBox()
        self.ops_box.setStyleSheet("QGroupBox {background-color: #3b3b3b; border: 1px solid #808080; border-radius: 10px; font-size: 16px;}")
        
        self.ops_layout = QHBoxLayout()
        self.ops_group = QButtonGroup()

        self.sub_radio = QRadioButton("Віднімання")
        self.sub_radio.setStyleSheet("QRadioButton{ color: white; background-color: transparent}")
        self.sub_radio.setChecked(False)
        self.ratio_radio = QRadioButton("Пропорція")
        self.ratio_radio.setStyleSheet("QRadioButton{ color: white; background-color: transparent}")
        self.avg_radio = QRadioButton("Середній колір")
        self.avg_radio.setStyleSheet("QRadioButton{ color: white; background-color: transparent}")

        self.ops_group.addButton(self.sub_radio)
        self.ops_group.addButton(self.ratio_radio)
        self.ops_group.addButton(self.avg_radio)

        self.ops_layout.addWidget(self.sub_radio)
        self.ops_layout.addWidget(self.ratio_radio)
        self.ops_layout.addWidget(self.avg_radio)


        self.ops_box.setLayout(self.ops_layout)
        self.main_col.addWidget(self.ops_box)


        self.run_layout = QHBoxLayout()
        self.run_layout.setSpacing(10)
        self.run_layout.setContentsMargins(0,5,0,5)
        self.run_widget = QWidget()

        self.settings_btn = QToolButton()
        self.settings_btn.setIcon(QIcon("settings.png"))
        self.settings_btn.setIconSize(QSize(30,30))
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setStyleSheet("background-color: #3b3b3b; color: white; border-radius:10px; border: 1px solid #808080;")
        
        self.run_btn = QPushButton("Виконати")
        self.run_btn.setStyleSheet("background-color: transparent; color: #ffd500; border-radius: 10px; border: 1px solid #ffd500;")
        self.run_btn.clicked.connect(self.run_operation)
        self.run_btn.setFixedHeight(40)
        
        self.run_layout.addWidget(self.run_btn)
        self.run_layout.addWidget(self.settings_btn)

        self.run_widget.setLayout(self.run_layout)
        self.main_col.addWidget(self.run_widget)


        self.image_label = QLabel("Перегляд Результату")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("color: white; background-color: #3b3b3b; border-radius: 10px; border: 1px solid #808080;")
        self.image_label.setMaximumHeight(40)
        self.image_label.setMinimumHeight(30)
        
        self.result_label = QLabel()

        self.secon_col.addWidget(self.image_label)
        self.secon_col.addWidget(self.result_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def add_category(self):
        name = self.cat_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Помилка", "Введіть назву Фото")
            return

        category = Category(name, self)
        self.categories.append(category)
        self.cat_layout.addWidget(category, alignment=Qt.AlignmentFlag.AlignLeft)
        self.cat_name_input.clear()

    def delete_category(self, category):
        if category in self.categories:
            self.categories.remove(category)
            self.cat_layout.removeWidget(category)
            category.setParent(None)  # від'єднуємо від layout і видаляємо з UI
            category.deleteLater()
    
    def open_settings(self):
        selected = []
        names = []
        for cat in self.categories:
            selected += cat.get_selected_images()
            names += [img.display_name for img in cat.get_selected_images()]

        if len(selected) != 2:
            QMessageBox.warning(self, "Увага", "Спочатку виберіть 2 зображення.")
            return

        dialog = SettingsDialog(self, names)
        if dialog.exec():
            self.subtract_order = dialog.get_order()

    def run_operation(self):
        selected = []
        for cat in self.categories:
            selected += cat.get_selected_images()

        if len(selected) != 2:
            QMessageBox.critical(self, "Помилка", "Потрібно вибрати 2 зображення.")
            return

        img1 = selected[self.subtract_order[0]].np_array
        img2 = selected[self.subtract_order[1]].np_array

        if img1.shape != img2.shape:
            QMessageBox.critical(self, "Помилка", "Зображення мають бути однакового розміру.")
            return

        if self.sub_radio.isChecked():
            result = np.clip(img1 - img2, 0, 255).astype(np.uint8)
        elif self.ratio_radio.isChecked():
            img2_safe = np.where(img2 == 0, 1, img2)
            result = np.clip((img1 / img2_safe) * 128, 0, 255).astype(np.uint8)
        elif self.avg_radio.isChecked():
            result = np.clip((img1 + img2) / 2, 0, 255).astype(np.uint8)
        else:
            QMessageBox.warning(self, "Помилка", "Операція не вибрана.")
            return

        image = Image.fromarray(result)
        qt_image = ImageQt.ImageQt(image)
        pixmap = QPixmap.fromImage(qt_image).scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
        self.result_label.setPixmap(pixmap)

        save_path, _ = QFileDialog.getSaveFileName(self, "Зберегти результат", "", "PNG Files (*.png)")
        if save_path:
            image.save(save_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())