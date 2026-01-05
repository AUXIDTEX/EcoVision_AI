from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QButtonGroup, QScrollArea, QColorDialog
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon

from windows.selectable_imagebox import SelectableImageBox


class SpectralFilterer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.count = 0 #Starting filter count

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)

        self.mode_switch = QHBoxLayout()
        self.mode_switch.setSpacing(0)
        self.mode_switch.setContentsMargins(0, 0, 0, 0)

        self.mode_widget = QWidget()
        self.mode_widget.setLayout(self.mode_switch)
        self.main_layout.addWidget(self.mode_widget, alignment=Qt.AlignmentFlag.AlignTop)

        self.file_mode_label = QPushButton("Файл")
        self.file_mode_label.setCheckable(True)
        self.file_mode_label.setMinimumSize(80, 30)

        self.folder_mode_label = QPushButton("Папка")
        self.folder_mode_label.setCheckable(True)
        self.folder_mode_label.setMinimumSize(80, 30)

        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.file_mode_label)
        self.button_group.addButton(self.folder_mode_label)

        self.file_mode_label.setChecked(True)

        self.mode_switch.addStretch()
        self.mode_switch.addWidget(self.file_mode_label)
        self.mode_switch.addWidget(self.folder_mode_label)
        self.mode_switch.addStretch()

        self.file_mode_label.toggled.connect(self.update_styles)
        self.folder_mode_label.toggled.connect(self.update_styles)
        
        self.update_styles()

        self.horizontal_layout = QHBoxLayout()
        self.main_layout.addLayout(self.horizontal_layout)

        self.image_layout = QHBoxLayout()
        self.image_widget = QWidget()
        self.image_widget.setMinimumSize(220, 220)
        self.image_widget.setStyleSheet("border: 2px solid #808080; border-radius: 8px; background-color: #2b2b2b;")
        self.image_widget.setLayout(self.image_layout)

        self.image_box = QLabel()
        self.image_box.setStyleSheet("border: none; background-color: transparent;")
        self.image_box.setMinimumSize(220, 220)
        self.image_layout.addWidget(self.image_box)

        self.horizontal_layout.addWidget(self.image_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        #self.horizontal_layout.addStretch()

        pixmap = QPixmap("app/assets/select_image3.png")
        pixmap = pixmap.scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_box.setPixmap(pixmap)
        self.image_box.setScaledContents(True)



        self.filter_layout = QVBoxLayout()
        self.horizontal_layout.addLayout(self.filter_layout)


        self.add_filter_btn = QPushButton()
        self.filter_layout.addWidget(self.add_filter_btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.add_filter_btn.setIcon(QIcon("app/assets/plus_icon.png"))
        self.add_filter_btn.setIconSize(QSize(24,24))
        self.add_filter_btn.setFixedSize(32,32)
        self.add_filter_btn.setStyleSheet("background-color: #3b3b3b; border: 1px solid #808080; border-radius: 8px;")
        self.add_filter_btn.clicked.connect(lambda: self.create_filter("#ffffff"))


        self.filter_scroll = QScrollArea()
        self.filter_layout.addWidget(self.filter_scroll)
        self.filter_scroll.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()

        self.scroll_layout.addStretch()

        self.scroll_widget.setLayout(self.scroll_layout)
        self.filter_scroll.setWidget(self.scroll_widget)

        self.filter1_color = "#ebe534"
        self.create_filter(self.filter1_color)
        self.filter2_color = "#820c0c"
        self.create_filter(self.filter2_color)
        self.filter3_color = "#ba4c49"
        self.create_filter(self.filter3_color)
        self.filter4_color = "#436fcc"
        self.create_filter(self.filter4_color)
        self.filter5_color = "#157510"
        self.create_filter(self.filter5_color)


    




    def update_styles(self):
        if self.file_mode_label.isChecked():
            self.file_mode_label.setStyleSheet(
                "background-color: #505050; border-top-left-radius: 8px; border-bottom-left-radius: 8px; color: white; border: 1px solid #808080;"
            )
            self.folder_mode_label.setStyleSheet(
                "background-color: #3b3b3b; border-top-right-radius: 8px; border-bottom-right-radius: 8px; color: white; border: 1px solid #808080;"
            )
        else:
            self.file_mode_label.setStyleSheet(
                "background-color: #3b3b3b; border-top-left-radius: 8px; border-bottom-left-radius: 8px; color: white; border: 1px solid #808080;"
            )
            self.folder_mode_label.setStyleSheet(
                "background-color: #505050; border-top-right-radius: 8px; border-bottom-right-radius: 8px; color: white; border: 1px solid #808080;"
            )




    def set_image(self):
        w, h = 320, 180

        if SelectableImageBox.path[1] is not None:

            pixmap = QPixmap(SelectableImageBox.path[1])

            if pixmap.width() > pixmap.height():
                pixmap = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            else:
                pixmap = pixmap.scaled(h, w, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            self.image_box.setPixmap(pixmap)
            self.image_box.setFixedSize(pixmap.size())

        else:
            pixmap = QPixmap("app/assets/select_image3.png")
            pixmap = pixmap.scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_box.setPixmap(pixmap)
            self.image_box.setScaledContents(True)
            self.image_box.setFixedSize(pixmap.size())



    
    def create_filter(self, color):
        self.count += 1
        starter_color = color

        filter_widget = QWidget()
        filter_widget.setFixedHeight(50)
        filter_widget.setStyleSheet("background-color: #3b3b3b; border-radius: 8px; padding: 5px;")
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, filter_widget)

        filter_layout = QHBoxLayout()
        filter_widget.setLayout(filter_layout)

        filter_label = QLabel("Фільтр " + str(self.count))
        filter_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        filter_layout.addWidget(filter_label)

        color_label = QPushButton()
        color_label.setMinimumSize(20, 20)
        color_label.setStyleSheet(f"background-color: {color}; border-radius: 4px; width: 20px; height: 20px; border: 1px solid #050505;")
        filter_layout.addWidget(color_label)

        color_code_label = QLabel(color)
        color_code_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        filter_layout.addWidget(color_code_label)

        color_label.clicked.connect(lambda _, label = color_label, code = color_code_label: self.select_color(label, code))

        reset_btn = QPushButton("Скинути")
        reset_btn.setStyleSheet("background-color: #3b3b3b; color: white; padding: 4px 10px; border-radius: 8px; border: 1px solid black;")
        reset_btn.clicked.connect(lambda _, color = starter_color, color_widget = color_label, name_widget = color_code_label: self.reset_filter(color, color_widget, name_widget))
        filter_layout.addWidget(reset_btn)


        delete_btn = QPushButton()
        delete_btn.setStyleSheet("background-color: transparent; border: none;")
        delete_btn.setIcon(QIcon('app/assets/delete_icon.png'))
        delete_btn.setIconSize(QSize(24,24))
        delete_btn.setMinimumSize(32,32)
        delete_btn.clicked.connect(lambda: filter_widget.deleteLater())
        filter_layout.addWidget(delete_btn)




    def select_color(self, label, code):
        color = QColorDialog.getColor()

        if color.isValid():
            label.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px; width: 20px; height: 20px; border: 1px solid #050505;")
            code.setText(color.name())

    def reset_filter(self, color, color_widget, name_widget):
        
        color_widget.setStyleSheet(f"background-color: {color}; border-radius: 4px; width: 20px; height: 20px; border: 1px solid #050505;")
        name_widget.setText(color)