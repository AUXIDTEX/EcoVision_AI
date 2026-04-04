from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QLineEdit, QPushButton, QScrollArea, QSplitter
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
import os

from modules.second_column import SecondColumn
from modules.category_widget import CategoryWidget
from modules.app_settings_manager import AppSettingsManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("РџРѕСЂС–РІРЅСЏРЅРЅСЏ Р·РѕР±СЂР°Р¶РµРЅСЊ")
        self.resize(1366, 768)
        self.setMinimumSize(1280, 720)
        self.setWindowIcon(QIcon('app/assets/radar.ico'))
        self.setStyleSheet("background-color: #1d1d1d; color: white;")
        self.setFont(QFont("Arial", 14))
        self.Main_Widget = QWidget() # Main Widget
        self.Main_layout = QHBoxLayout()
        self.Main_layout.setContentsMargins(10, 10, 10, 10)
        self.Main_layout.setSpacing(10)
        self.Main_Widget.setLayout(self.Main_layout)
        self.setCentralWidget(self.Main_Widget) # Setting the central widget

        self.main_col_widget = QWidget()
        self.main_col = QVBoxLayout()
        self.main_col_widget.setLayout(self.main_col)
        self.main_col_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.main_col_widget.setMinimumWidth(340)



        self.add_layout = QHBoxLayout()
        self.add_layout.setContentsMargins(0, 0, 0, 0)
        self.add_layout.setSpacing(5)
        self.add_widget = QWidget()
        self.add_widget.setLayout(self.add_layout)
        self.main_col.addWidget(self.add_widget, alignment=Qt.AlignmentFlag.AlignTop)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Р’РІРµРґС–С‚СЊ РЅР°Р·РІСѓ")
        self.name_input.setStyleSheet("padding: 6px; border-radius: 8px; background-color: #3b3b3b; color: white; border: 1px solid #808080;")
        self.add_layout.addWidget(self.name_input)

        self.add_button = QPushButton("Р”РѕРґР°С‚Рё")
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
        self.scroll_area.setMinimumHeight(220)

        self.scroll_area.setWidget(self.cats_frame)
        self.main_col.addWidget(self.scroll_area, stretch=1)


        self.settings_widget = QWidget()
        self.settings_layout = QHBoxLayout()
        self.main_col.addWidget(self.settings_widget)
        self.settings_widget.setLayout(self.settings_layout)
        self.settings_widget.setStyleSheet("background-color: #2b2b2b; border: 1px solid #808080; border-radius: 8px; padding: 5px;")

        self.second_col = SecondColumn(self, main_window=self, settings_layout=self.settings_layout, settings_widget=self.settings_widget)
        self.second_col.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.second_col.setMinimumWidth(520)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.addWidget(self.main_col_widget)
        self.main_splitter.addWidget(self.second_col)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 2)
        self.main_splitter.setSizes([460, 900])
        self.Main_layout.addWidget(self.main_splitter)

        self.main_col.addStretch()

        self.settings_manager = AppSettingsManager(self)
        self.settings_manager.apply_loaded_settings()
        

    def add_category(self):
        category_name = self.name_input.text().strip()
        if category_name:
            self.name_input.clear()

            category = CategoryWidget(self, category_name=category_name, second_col = self.second_col, image1=self.second_col.image1, image2=self.second_col.image2)

            category.setMaximumWidth(420)
            category.setMinimumWidth(220)

            category.add_image_to_array.connect(self.second_col.add_image_to_array) # Connect signal to second column method

            self.cats_layout.insertWidget(self.cats_layout.count() - 1, category)
            category.apply_language(self.settings_manager.get_language())

    def get_text(self, key):
        if hasattr(self, "settings_manager"):
            return self.settings_manager.get_text(key)
        return key

    def get_default_open_path(self):
        if hasattr(self, "settings_manager"):
            return self.settings_manager.get_default_open_path()
        return os.path.expanduser("~")

    def apply_language(self, language):
        self.setWindowTitle(self.get_text("window_title"))
        self.name_input.setPlaceholderText(self.get_text("name_placeholder"))
        self.add_button.setText(self.get_text("add_category"))

        if hasattr(self, "second_col"):
            self.second_col.apply_language(language)

        for i in range(self.cats_layout.count()):
            item = self.cats_layout.itemAt(i)
            widget = item.widget() if item else None
            if widget and hasattr(widget, "apply_language"):
                widget.apply_language(language)
