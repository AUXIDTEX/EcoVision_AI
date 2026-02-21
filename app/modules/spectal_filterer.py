from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QButtonGroup, QScrollArea, QColorDialog, QStyleOption, QStyle, QFileDialog, QProgressBar, QApplication
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor
import os

from modules.selectable_imagebox import SelectableImageBox


class SpectralFilterer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.count = 0 #Starting filter count
        self.filters_array = [] #Array to hold filters
        self.active_images = [] #List to track active images
        self.selected_image_path = None
        self.active_filter = None
        self.selected_folder = None

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

        

        self.update_styles()

        self.horizontal_layout = QHBoxLayout()
        self.main_layout.addLayout(self.horizontal_layout)

        self.image_widget = QWidget()
        self.image_layout = QHBoxLayout()
        self.image_widget.setMinimumSize(220, 220)
        self.image_widget.setStyleSheet("border: 2px solid #808080; border-radius: 8px; background-color: #2b2b2b;")
        self.image_widget.setLayout(self.image_layout)

        self.image_box = QLabel()
        self.image_box.setStyleSheet("border: none; background-color: transparent;")
        self.image_box.setMinimumSize(220, 220)
        self.image_layout.addWidget(self.image_box)

        self.horizontal_layout.addWidget(self.image_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        #self.horizontal_layout.addStretch()

        pixmap = QPixmap("app/assets/select_image.png")
        pixmap = pixmap.scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_box.setPixmap(pixmap)
        self.image_box.setScaledContents(True)



        self.filter_layout = QVBoxLayout()
        self.horizontal_layout.addLayout(self.filter_layout)




        self.filter_scroll = QScrollArea()
        self.filter_layout.addWidget(self.filter_scroll)
        self.filter_scroll.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()

        self.add_filter_btn = QPushButton()
        self.scroll_layout.addWidget(self.add_filter_btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.add_filter_btn.setIcon(QIcon("app/assets/plus_icon.png"))
        self.add_filter_btn.setIconSize(QSize(24,24))
        self.add_filter_btn.setFixedSize(32,32)
        self.add_filter_btn.setStyleSheet("background-color: #3b3b3b; border: 1px solid #808080; border-radius: 8px;")
        self.add_filter_btn.clicked.connect(lambda: self.create_filter("#ffffff", None))


        self.scroll_layout.addStretch()

        self.scroll_widget.setLayout(self.scroll_layout)
        self.filter_scroll.setWidget(self.scroll_widget)

        self.filter1_color = "#ebe534"
        self.create_filter(self.filter1_color, 1)
        self.filter2_color = "#820c0c"
        self.create_filter(self.filter2_color, 2)
        self.filter3_color = "#ff8383"
        self.create_filter(self.filter3_color, 3)
        self.filter4_color = "#436fcc"
        self.create_filter(self.filter4_color, 4)
        self.filter5_color = "#157510"
        self.create_filter(self.filter5_color, 5)



        self.save_button = QPushButton("Зберегти усі варіанти")
        self.save_button.setFixedHeight(40)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32; 
                color: white; 
                border-radius: 8px; 
                font-weight: bold;
            }
            QPushButton:hover { background-color: #388e3c; }
        """)
        self.save_button.clicked.connect(self.save_filtered_images)
        self.main_layout.addWidget(self.save_button)


        self.folder_select_btn = QPushButton("Вибрати папку")
        self.folder_select_btn.setFixedHeight(40)
        self.main_layout.addWidget(self.folder_select_btn)
        self.folder_select_btn.setStyleSheet("""
                                             QPushButton {
                                                 background-color: #1976d2;
                                                 color: white;
                                                 border-radius: 8px;
                                                 font-weight: bold;}
                                            QPushButton:hover { background-color: #2196f3; }
                                            """)
        
        self.folder_select_btn.clicked.connect(self.select_folder)
        self.folder_select_btn.hide()




        self.file_mode_label.toggled.connect(self.update_styles)
        self.file_mode_label.toggled.connect(lambda: self.mode_switch_func("1"))
        self.folder_mode_label.toggled.connect(self.update_styles)
        self.folder_mode_label.toggled.connect(lambda: self.mode_switch_func("2"))


        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #808080;
                border-radius: 5px;
                text-align: center;
                background-color: #2b2b2b;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #2e7d32;
                width: 10px;
            }
        """)
        self.progress_bar.hide() # Ховаємо за замовчуванням
        self.main_layout.addWidget(self.progress_bar)




    def mode_switch_func(self, mode):
        if mode == "1":
            

            self.image_widget.show()
            self.folder_select_btn.hide()

        elif mode == "2":
            

            self.image_widget.hide()
            self.folder_select_btn.show()



    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Виберіть папку з зображеннями")

        if folder:
            self.selected_folder = folder
            self.folder_select_btn.setText(f"Вибрана папка: {os.path.basename(folder)}")

            self.active_images = []

            valid_extensions = (".png", ".jpg", ".jpeg", ".bmp", "webp")

            for file in os.listdir(folder):
                if file.lower().endswith(valid_extensions):
                    full_path = os.path.join(folder, file)
                    self.active_images.append(full_path)

            if self.active_images:
                self.selected_image_path = self.active_images[0]
                
                pixmap = QPixmap(self.active_images[0])
                self.image_box.setPixmap(pixmap)
        

    

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

            self.active_images.append(SelectableImageBox.path[1])
            self.selected_image_path = SelectableImageBox.path[1]

            self.apply_filter(self.active_filter)

        else:
            pixmap = QPixmap("app/assets/select_image.png")
            pixmap = pixmap.scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_box.setPixmap(pixmap)
            self.image_box.setScaledContents(True)
            self.image_box.setFixedSize(pixmap.size())

            for i in self.active_images:
                if i == SelectableImageBox.path[1]:
                    self.active_images.remove(i)

            self.selected_image_path = None


    
    def create_filter(self, color, standart_filter):

        self.count += 1
        starter_color = color


    
        filter_widget = Filter_visuals(self)
        filter_widget.setObjectName("FilterCard")
        filter_widget.setFixedHeight(50)
        filter_widget.update_appearance()
        
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, filter_widget)

        filter_layout = QHBoxLayout()
        filter_widget.setLayout(filter_layout)

        filter_label = QLabel("Фільтр " + str(self.count))
        filter_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        filter_layout.addWidget(filter_label)

        color_label = QPushButton()
        color_label.setMinimumSize(20, 20)
        color_label.setFixedWidth(75)
        color_label.setStyleSheet(f"background-color: {color}; border-radius: 4px; width: 20px; height: 20px; border: 1px solid #050505;")
        filter_layout.addWidget(color_label)

        color_code_label = QLabel(color)
        color_code_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        filter_layout.addWidget(color_code_label)

        color_label.clicked.connect(lambda _, label = color_label, code = color_code_label, filter_widget = filter_widget: self.select_color(label, code, filter_widget))

        reset_btn = QPushButton("Скинути")
        reset_btn.setStyleSheet("background-color: #3b3b3b; color: white; padding: 4px 10px; border-radius: 8px; border: 1px solid black;")
        reset_btn.clicked.connect(lambda _, color = starter_color, color_widget = color_label, name_widget = color_code_label, filter_widget = filter_widget: self.reset_filter(color, color_widget, name_widget, filter_widget))
        filter_layout.addWidget(reset_btn)


        delete_btn = QPushButton()
        delete_btn.setStyleSheet("background-color: transparent; border: none;")
        delete_btn.setIcon(QIcon('app/assets/delete_icon.png'))
        delete_btn.setIconSize(QSize(24,24))
        delete_btn.setMinimumSize(32,32)
        delete_btn.clicked.connect(lambda _, widget=filter_widget: self.remove_filter(widget))
        filter_layout.addWidget(delete_btn)


        array_data = {"widget": filter_widget, "label_widget": filter_label, "color": color}
        self.filters_array.append(array_data)




    def select_color(self, label, code, filter_widget):
        color = QColorDialog.getColor()

        if color.isValid():
            label.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px; width: 20px; height: 20px; border: 1px solid #050505;")
            code.setText(color.name())

            for item in self.filters_array:
                if item["widget"] == filter_widget:
                    item["color"] = color.name()
                    break
            
            if filter_widget == self.active_filter:
                self.apply_filter(self.active_filter)




    def reset_filter(self, color, color_widget, name_widget, filter_widget):
        
        color_widget.setStyleSheet(f"background-color: {color}; border-radius: 4px; width: 20px; height: 20px; border: 1px solid #050505;")
        name_widget.setText(color)

        for item in self.filters_array:
            if item["widget"] == filter_widget:
                item["color"] = color
                break   
        
        if self.active_filter == filter_widget:
            self.apply_filter(self.active_filter)




    def deactivate_all_filters(self):
        for item in self.filters_array:
            widget = item["widget"]
            if widget.active:
                widget.active = False
                widget.update_appearance() 



    def remove_filter(self, widget):
        for i, item in enumerate(self.filters_array):
            if item["widget"] == widget:
                self.filters_array.pop(i)
                break
     
        widget.deleteLater()

        for i, item in enumerate(self.filters_array):
            item["label_widget"].setText("Фільтр " + str(i + 1))
        self.count = len(self.filters_array)

        if self.active_filter == widget:
            self.active_filter = None
            self.set_image()



    def apply_filter(self, filter_widget):
        if filter_widget is None:
            return

        color = None
        for i in self.filters_array:
            if i["widget"] == filter_widget:
                color = i["color"]
                break

        if self.selected_image_path is None:
            return
        
        pixmap = QPixmap(self.selected_image_path)

        painter = QPainter(pixmap)

        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)

        painter.fillRect(pixmap.rect(), QColor(color))

        painter.end()

        self.image_box.setPixmap(pixmap)





    def save_filtered_images(self):
        if not self.active_images or not self.filters_array:
            return

        folder = QFileDialog.getExistingDirectory(self, "Виберіть папку для збереження")
        if not folder:
            return

        total_tasks = len(self.active_images) * len(self.filters_array)
        current_task = 0

        self.progress_bar.setMaximum(total_tasks)
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        for image_path in self.active_images:
            original_name = os.path.splitext(os.path.basename(image_path))[0]
            
            for i, item in enumerate(self.filters_array):
                filter_color = item["color"]
                
                saved_pixmap = QPixmap(image_path)
                painter = QPainter(saved_pixmap)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
                painter.fillRect(saved_pixmap.rect(), QColor(filter_color))
                painter.end()

                save_name = f"{original_name}_Filter_{i+1}.png"
                save_path = os.path.join(folder, save_name)
                saved_pixmap.save(save_path, "PNG")

                current_task += 1
                self.progress_bar.setValue(current_task)
                

                QApplication.processEvents()

        # Завершення
        print(f"Збережено {current_task} зображень.")
        self.progress_bar.hide()

    


class Filter_visuals(QWidget):
    def __init__(self, parent_app, parent=None):
        super().__init__(parent)
        self.active = False 
        self.app = parent_app
       
        self.setObjectName("FilterCard")



    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)




    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            
            if not self.active:
               
                self.app.deactivate_all_filters()
                self.active = True

                self.app.active_filter = self
                self.app.apply_filter(self)
            else:
                
                if self.app.active_filter == self:
                    self.app.active_filter = None
                    self.app.set_image()

                self.active = False


            
            self.update_appearance()




    def update_appearance(self):
        bg_color = "#4a4a4a" if self.active else "#3b3b3b"
        hover_color = "#555555" if self.active else "#454545"
        border = "1px solid #808080" if self.active else "none"
        
        
        self.setStyleSheet(f"""
            #FilterCard {{
                background-color: {bg_color}; 
                border-radius: 8px; 
                padding: 5px;
                border: {border};
            }} 
            #FilterCard:hover {{
                background-color: {hover_color};
            }}
        """)