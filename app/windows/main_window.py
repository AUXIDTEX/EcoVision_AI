from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QLineEdit, QPushButton, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from windows.second_column import SecondColumn
from windows.category_widget import CategoryWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Порівняння зображень")
        self.setGeometry(0, 0, 1400, 900) #x, y, width, height
        self.setWindowIcon(QIcon('radar.ico'))
        self.Main_Widget = QWidget() # Main Widget
        self.Main_layout = QHBoxLayout()
        self.Main_layout.setContentsMargins(10, 10, 10, 10)
        self.Main_layout.setSpacing(10)
        self.Main_Widget.setLayout(self.Main_layout)
        self.setCentralWidget(self.Main_Widget) # Setting the central widget

        self.main_col_widget = QWidget()
        self.main_col = QVBoxLayout()
        self.main_col_widget.setLayout(self.main_col)
        self.main_col_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.Main_layout.addWidget(self.main_col_widget, stretch=1)



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
        self.scroll_area.setMinimumHeight(300)
        self.scroll_area.setMaximumHeight(400)

        self.scroll_area.setWidget(self.cats_frame)
        self.main_col.addWidget(self.scroll_area, alignment=Qt.AlignmentFlag.AlignTop)


        self.settings_widget = QWidget()
        self.settings_layout = QHBoxLayout()
        self.main_col.addWidget(self.settings_widget)
        self.settings_widget.setLayout(self.settings_layout)
        self.settings_widget.setStyleSheet("background-color: #2b2b2b; border: 1px solid #808080; border-radius: 8px; padding: 5px;")

        self.second_col = SecondColumn(self, main_window=self, settings_layout=self.settings_layout)
        self.second_col.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.Main_layout.addWidget(self.second_col, stretch=1) 

        self.main_col.addStretch()
        

    def add_category(self):
        category_name = self.name_input.text().strip()
        if category_name:
            self.name_input.clear()

            category = CategoryWidget(self, category_name=category_name, second_col = self.second_col, image1=self.second_col.image1, image2=self.second_col.image2)

            category.setMaximumWidth(300)
            category.setMinimumWidth(200)

            category.add_image_to_array.connect(self.second_col.add_image_to_array) # Connect signal to second column method

            self.cats_layout.insertWidget(self.cats_layout.count() - 1, category)