import os
import sys
import time
import json
import tempfile
from PyQt6.QtCore import QProcess, QSize, Qt, QRect
from PyQt6.QtGui import QIcon, QIcon, QPixmap, QPdfWriter, QPainter, QFont, QPageSize, QFontMetrics
from PyQt6.QtWidgets import QFrame, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QProgressBar, QScrollArea, QButtonGroup, QFileDialog

from modules.selectable_imagebox import SelectableImageBox


class AI_Module:
    def __init__(self, second_column):
        self.second_column = second_column
        self.secon_layout = second_column.secon_layout



        self.ai_process = None
        self.ai_source_path = None
        self.ai_cancel_requested = False
        self.ai_selected_folder = None
        self.ai_folder_process = None
        self.ai_folder_paths = []
        self.ai_folder_total = 0
        self.ai_folder_processed = 0
        self.ai_folder_total_processed_time = 0.0
        self.ai_folder_item_started_at = 0.0
        self.ai_folder_cancel_requested = False

        self.previous_mode = None
        self.preview_state = True  # True = closed, False = open
        self.pixmap_arr = []
        self.current_image_path = None
        self.last_ai_report = None
        self.last_ai_folder_report = []
        


        self.vertical_ai_layout = QVBoxLayout()
        self.vertical_ai_widget = QWidget()
        self.vertical_ai_widget.hide()
        self.vertical_ai_widget.setStyleSheet("background-color: #2b2b2b; border: 1px solid #808080; border-radius: 10px;")
        #self.secon_layout.addWidget(self.vertical_ai_widget)
        self.vertical_ai_widget.setLayout(self.vertical_ai_layout)



        self.mode_switch = QHBoxLayout()
        self.mode_switch.setSpacing(0)
        self.mode_switch.setContentsMargins(0, 0, 0, 0)

        self.mode_widget = QWidget()
        self.mode_widget.setStyleSheet("background-color: transparent; border: none;")
        self.mode_widget.setLayout(self.mode_switch)
        self.vertical_ai_layout.addWidget(self.mode_widget, alignment=Qt.AlignmentFlag.AlignTop)

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


        self.file_mode_label.toggled.connect(self.update_styles)
        self.file_mode_label.toggled.connect(lambda: self.mode_switch_func("1"))
        self.folder_mode_label.toggled.connect(self.update_styles)
        self.folder_mode_label.toggled.connect(lambda: self.mode_switch_func("2"))



        self.ai_layout = QHBoxLayout()
        self.ai_widget = QWidget()
        self.ai_widget.setStyleSheet("background-color: transparent; border: none;")
        self.vertical_ai_layout.addWidget(self.ai_widget)

        self.ai_widget.setLayout(self.ai_layout)
        #self.secon_layout.addWidget(self.ai_widget)


        self.ai_image_box = QLabel()
        self.ai_image_box.setStyleSheet("border: none; background-color: transparent;")
        self.ai_image_box.setFixedSize(300, 533)
        self.ai_layout.addWidget(self.ai_image_box, alignment=Qt.AlignmentFlag.AlignLeft)

        self.ai_info_widget = QWidget()
        self.ai_info_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ai_info_widget.setStyleSheet("background-color: transparent; border: none;")
        self.ai_layout.addWidget(self.ai_info_widget, 1)
        self.ai_info_layout = QVBoxLayout()
        self.ai_info_widget.setLayout(self.ai_info_layout)

        self.info_title = QLabel("Звіт нейромережі")
        self.ai_info_layout.addWidget(self.info_title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.info_title.setStyleSheet("color: #ffd500; font-size: 15px; padding-bottom: 10px; border: none;")


        self.image_name = QLabel()
        self.info_class_name = QLabel()
        self.info_conf = QLabel()
        self.info_xyxy = QLabel()

        self.info_x1 = QLabel()
        self.info_y1 = QLabel()
        self.info_x2 = QLabel()
        self.info_y2 = QLabel()

        self.info_class_name.setWordWrap(True)
        self.info_conf.setWordWrap(True)
        self.info_x1.setWordWrap(True)
        self.info_class_name.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.info_conf.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.info_x1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.info_class_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.info_conf.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.info_x1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.ai_info_layout.addWidget(self.image_name, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_class_name, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_conf, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_xyxy, alignment=Qt.AlignmentFlag.AlignLeft)

        self.ai_info_layout.addWidget(self.info_x1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_y1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_x2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ai_info_layout.addWidget(self.info_y2, alignment=Qt.AlignmentFlag.AlignLeft)

        self.ai_progress_bar = QProgressBar()
        self.ai_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #808080;
                border-radius: 8px;
                text-align: center;
                background-color: #1d1d1d;
                color: white;
                max-height: 15px;
            }
            QProgressBar::chunk {
                background-color: #2e7d32;
                border-radius: 8px;
            }
        """)
        self.ai_progress_bar.setFormat("Обробка ШІ...")
        self.ai_progress_bar.hide()
        self.vertical_ai_layout.addWidget(self.ai_progress_bar)

        self.ai_folder_widget = QWidget()
        self.ai_folder_widget.setStyleSheet("background-color: transparent; border: none;")
        self.ai_folder_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ai_folder_widget.hide()
        self.vertical_ai_layout.addWidget(self.ai_folder_widget)
        self.ai_folder_layout = QVBoxLayout()
        self.ai_folder_widget.setLayout(self.ai_folder_layout)


        self.ai_folder_scroll_widget = QWidget()
        self.ai_folder_scroll_widget.setMinimumHeight(500)
        self.ai_folder_scroll = QScrollArea()

        self.ai_folder_scroll_layout = QVBoxLayout()
        self.ai_folder_scroll_layout.addWidget(self.ai_folder_scroll)
        self.ai_folder_scroll_widget.setLayout(self.ai_folder_scroll_layout)

        self.ai_folder_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ai_folder_scroll.setWidgetResizable(True)
        self.ai_folder_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ai_folder_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ai_folder_scroll.setStyleSheet("QScrollArea { border: 1px solid #808080; border-radius: 8px; background-color: #1d1d1d; }")
        self.ai_folder_layout.addWidget(self.ai_folder_scroll_widget, 1)



        self.ai_folder_select_btn = QPushButton("Вибрати папку")
        self.ai_folder_select_btn.setMinimumHeight(36)
        self.ai_folder_select_btn.setStyleSheet("background-color: #3b3b3b; border: 1px solid #808080; border-radius: 8px; color: white;")
        self.ai_folder_select_btn.clicked.connect(self.select_ai_folder)
        self.ai_folder_layout.addWidget(self.ai_folder_select_btn)


        self.ai_folder_find_btn = QPushButton("Виконати")
        self.ai_folder_find_btn.setMinimumHeight(36)
        self.ai_folder_find_btn.setStyleSheet("background-color: #ffd500; border: 1px solid #808080; border-radius: 8px; color: black; font-weight: 600;")
        self.ai_folder_find_btn.clicked.connect(self.start_ai_folder_processing)
        self.ai_folder_layout.addWidget(self.ai_folder_find_btn)



        self.ai_folder_content = QWidget()
        self.ai_folder_content_layout = QVBoxLayout()
        self.ai_folder_content_layout.setContentsMargins(8, 8, 8, 8)
        self.ai_folder_content_layout.setSpacing(8)
        self.ai_folder_content_layout.addStretch()
        self.ai_folder_content.setLayout(self.ai_folder_content_layout)
        self.ai_folder_scroll.setWidget(self.ai_folder_content)


        self.process_button = QPushButton("Виконати")
        self.process_button.setMinimumHeight(36)
        self.vertical_ai_layout.addWidget(self.process_button)
        self.process_button.setStyleSheet("background-color: #ffd500; border: 1px solid #808080; border-radius: 8px; color: black; font-weight: 600;")
        self.process_button.clicked.connect(lambda: self.start_ai_inference(self._get_selected_image_path()))


        self.info_label = QLabel("Натисніть 'Виконати' для обробки вибраних зображень")
        self.info_label.setStyleSheet("color: #d0d0d0; border: none; font-size: 14px;")
        self.ai_info_layout.addWidget(self.info_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.info_label.hide()



        self.preview_button = QPushButton("", self.ai_image_box)
        self.preview_button.clicked.connect(self.preview_func)
        self.preview_button.setIcon(QIcon("app/assets/eye_closed.png"))
        self.preview_button.setStyleSheet("Background-color: #2e7d32; border: none;")
        self.preview_button.setIconSize(QSize(24, 24))
        self.preview_button.setFixedSize(32, 32)
        self.sync_overlay()
        

        self.export_button = QPushButton("Експортувати звіт")
        self.export_button.setMinimumHeight(36)
        self.export_button.setStyleSheet("background-color: #3b3b3b; border: 1px solid #808080; border-radius: 8px; color: white;")
        self.export_button.clicked.connect(self.export_ai_report)
        self.vertical_ai_layout.addWidget(self.export_button)


        self.img_w = self.ai_image_box.width()
        self.img_h = self.ai_image_box.height()
        self.apply_language("uk")

    def get_text(self, key, fallback):
        if self.second_column and self.second_column.window and hasattr(self.second_column.window, "get_text"):
            return self.second_column.window.get_text(key)
        return fallback

    def apply_language(self, language):
        self.file_mode_label.setText(self.get_text("file_mode", "Файл"))
        self.folder_mode_label.setText(self.get_text("folder_mode", "Папка"))
        self.info_title.setText(self.get_text("ai_report_title", "Звіт нейромережі"))
        if self.ai_selected_folder:
            self.ai_folder_select_btn.setText(
                f"{self.get_text('selected_folder', 'Вибрана папка')}: {os.path.basename(self.ai_selected_folder)}"
            )
        else:
            self.ai_folder_select_btn.setText(self.get_text("pick_folder", "Вибрати папку"))
        self.ai_folder_find_btn.setText(self.get_text("run", "Виконати"))
        self.process_button.setText(self.get_text("run", "Виконати"))
        self.info_label.setText(self.get_text("ai_run_hint", "Натисніть 'Виконати' для обробки вибраних зображень"))
        self.export_button.setText(self.get_text("export_report", "Експортувати звіт"))



    def select_image(self, number, w=1200, h=675):
        image_path = SelectableImageBox.path.get(number)
        if not image_path:
            return

        # Switching to another image should reset analysis state for that image.
        if self.ai_process and self.ai_process.state() != QProcess.ProcessState.NotRunning:
            self.stop_ai_inference()
        self.ai_progress_bar.hide()
        self.image_name.setText("")
        self.info_class_name.setText("")
        self.info_conf.setText("")
        self.info_xyxy.setText("")
        self.info_x1.setText("")
        self.info_y1.setText("")
        self.info_x2.setText("")
        self.info_y2.setText("")





        pixmap = QPixmap(image_path)
        if pixmap.width() > pixmap.height():
            pixmap = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.ai_image_box.setFixedSize(self.img_h, self.img_w)

            self.sync_overlay()
        else:
            pixmap = pixmap.scaled(h, w, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.ai_image_box.setFixedSize(self.img_w, self.img_h)

            self.sync_overlay()

        self.ai_image_box.setPixmap(pixmap)
        self.ai_image_box.setScaledContents(True)
            

        


        self.current_image_path = image_path
        self.add_pixmap_to_array(image_path, pixmap, None)
        for item in self.pixmap_arr:
            if item["path"] == image_path:
                item["analyzed_pixmap"] = None
                break
        self.preview_state = True
        self.preview_button.setIcon(QIcon("app/assets/eye_closed.png"))




    def add_pixmap_to_array(self, path, pixmap, analysed_pixmap):
        entry = None
        for item in self.pixmap_arr:
            if item["path"] == path:
                entry = item
                break

        if entry is None:
            entry = {"path": path, "original_pixmap": None, "analyzed_pixmap": None}
            self.pixmap_arr.append(entry)

        if pixmap is not None:
            entry["original_pixmap"] = pixmap
        if analysed_pixmap is not None:
            entry["analyzed_pixmap"] = analysed_pixmap





    def sync_overlay(self):
        margin = 8
        x = max(self.ai_image_box.width() - self.preview_button.width() - margin, 0)
        y = margin
        self.preview_button.move(x, y)
        self.preview_button.raise_()



    
    def preview_func(self):
        if not self.current_image_path:
            return

        entry = None
        for item in self.pixmap_arr:
            if item["path"] == self.current_image_path:
                entry = item
                break
        if entry is None:
            return

        if self.preview_state:
            if entry["analyzed_pixmap"] is None:
                return
            self.preview_state = False
            self.preview_button.setIcon(QIcon("app/assets/eye_openned.png"))
            self.ai_image_box.setPixmap(entry["analyzed_pixmap"])
        else:
            if entry["original_pixmap"] is None:
                return
            self.preview_state = True
            self.preview_button.setIcon(QIcon("app/assets/eye_closed.png"))
            self.ai_image_box.setPixmap(entry["original_pixmap"])
                

        


    def mode_switch_func(self, mode):


        if mode == "1":

            
            self.stop_ai_folder_processing()
            self.ai_folder_widget.hide()
            self.ai_widget.show()
            self.process_button.show()


            self._on_mode_switched(self._get_selected_image_path())

            if self.previous_mode == 1:
                self.previous_mode = 2


            #if self.second_column.mode == 10:
            #    selected_path = SelectableImageBox.path[1] or SelectableImageBox.path[2]
            #    if selected_path:
            #        self.start_ai_inference(selected_path)
            #    else:
            #        self.clear_ai_file_report()

    
        elif mode == "2":
            self.previous_mode = 1
            
            self.stop_ai_inference()
            self.ai_progress_bar.hide()
            self.ai_widget.hide()
            self.ai_folder_widget.show()
            
            self.process_button.hide()

        


    def update_styles(self):
        if self.file_mode_label.isChecked():
            self.file_mode_label.setStyleSheet(
                "background-color: #505050; border-top-left-radius: 8px; border-bottom-left-radius: 8px; border-top-right-radius: 0px; border-bottom-right-radius: 0px; color: white; border: 1px solid #808080;"
            )
            self.folder_mode_label.setStyleSheet(
                "background-color: #3b3b3b; border-top-right-radius: 8px; border-bottom-right-radius: 8px; border-top-left-radius: 0px; border-bottom-left-radius: 0px; color: white; border: 1px solid #808080;"
            )
        else:
            self.file_mode_label.setStyleSheet(
                "background-color: #3b3b3b; border-top-left-radius: 8px; border-bottom-left-radius: 8px; border-top-right-radius: 0px; border-bottom-right-radius: 0px; color: white; border: 1px solid #808080;"
            )
            self.folder_mode_label.setStyleSheet(
                "background-color: #505050; border-top-right-radius: 8px; border-bottom-right-radius: 8px; border-top-left-radius: 0px; border-bottom-left-radius: 0px; color: white; border: 1px solid #808080;"
            )




    def _on_mode_switched(self, image_path):
        if not image_path:
            self.ai_image_box.clear()
            return
        
        if self.file_mode_label.isChecked():
            #self.start_ai_inference(image_path)

            w=1200
            h=675

            pixmap = QPixmap(image_path)

            if self.previous_mode == None or self.previous_mode == 1:


                if pixmap.width() > pixmap.height():
                    pixmap = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                else:
                    pixmap = pixmap.scaled(h, w, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                
                self.ai_image_box.setPixmap(pixmap)
                self.ai_image_box.setScaledContents(True)
                self.current_image_path = image_path
                self.preview_state = True
                self.preview_button.setIcon(QIcon("app/assets/eye_closed.png"))

                self.info_label.show()






    def _get_selected_image_path(self):
        return SelectableImageBox.path.get(1) or SelectableImageBox.path.get(2)



    def start_ai_inference(self, image_path):
        if not image_path:
            QMessageBox.warning(self.second_column, "Помилка", "Не вдалося отримати шлях до зображення")
            return



        #source_pixmap = QPixmap(image_path)
        #source_pixmap = source_pixmap.scaled(1200, 1200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        #self.ai_image_box.setPixmap(source_pixmap)
        #self.ai_image_box.setScaledContents(True)



        self.ai_cancel_requested = False
        if self.ai_process and self.ai_process.state() != QProcess.ProcessState.NotRunning:
            self.stop_ai_inference()

        self.info_label.hide()

        self.ai_source_path = image_path
        self.ai_progress_bar.setRange(0, 0)
        self.ai_progress_bar.setFormat("Обробка ШІ...")
        self.ai_progress_bar.show()
        self.image_name.setText(f"Name: {image_path.split('/')[-1]}")
        self.info_class_name.setText("Classes: обробка...")
        self.info_conf.setText("Confidence: обробка...")
        self.info_xyxy.setText("Bounding Box cords:")
        self.info_x1.setText("  обробка...")
        self.info_y1.setText("")
        self.info_x2.setText("")
        self.info_y2.setText("")

        self.ai_process = QProcess(self.second_column)
        self.ai_process.setProgram(sys.executable)
        self.ai_process.setArguments(["app/logic/run_yolo.py", image_path])
        self.ai_process.finished.connect(self.on_ai_inference_finished)
        self.ai_process.errorOccurred.connect(self.on_ai_inference_error)
        self.ai_process.start()





    def stop_ai_inference(self):
        self.ai_cancel_requested = True
        self.ai_progress_bar.hide()
        if self.ai_process and self.ai_process.state() != QProcess.ProcessState.NotRunning:
            self.ai_process.kill()
            self.ai_process.waitForFinished(2000)


        

    def select_ai_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self.second_column,
            self.second_column.window.get_text("pick_folder_images"),
            self.second_column.window.get_default_open_path(),
        )
        if not folder:
            return

        self.ai_selected_folder = folder
        self.last_ai_folder_report = []
        self.ai_folder_select_btn.setText(
            f"{self.get_text('selected_folder', 'Вибрана папка')}: {os.path.basename(folder)}"
        )
        self.clear_ai_folder_results()
        self.ai_folder_content_layout.insertWidget(
            len(self.ai_folder_content_layout) - 1,
            QLabel(self.get_text("ai_run_hint", "Натисніть 'Виконати' для обробки вибраних зображень")),
        )



    def start_next_ai_folder_item(self):
        if self.ai_folder_cancel_requested:
            self.ai_folder_cancel_requested = False
            self.ai_folder_process = None
            self.ai_progress_bar.hide()
            self.ai_folder_find_btn.setEnabled(True)
            self.ai_folder_select_btn.setEnabled(True)
            return

        if not self.ai_folder_paths:
            self.ai_folder_process = None
            self.ai_progress_bar.hide()
            self.ai_folder_find_btn.setEnabled(True)
            self.ai_folder_select_btn.setEnabled(True)
            return

        image_path = self.ai_folder_paths.pop(0)
        self.ai_folder_item_started_at = time.perf_counter()

        self.ai_folder_process = QProcess(self.second_column)
        self.ai_folder_process.setProgram(sys.executable)
        self.ai_folder_process.setArguments(["app/logic/run_yolo.py", image_path])
        self.ai_folder_process.finished.connect(
            lambda code, status, p=image_path: self.on_ai_folder_item_finished(code, status, p)
        )
        self.ai_folder_process.start()






    def _build_ai_folder_item_widget(self, image_path, detections=None, error_text=None, preview_path=None):
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: #2b2b2b; border: 1px solid #808080; border-radius: 8px; }")
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        frame.setLayout(layout)

        header = QHBoxLayout()

        thumb = QLabel()
        thumb.setFixedSize(400, 225)
        thumb.setStyleSheet("border: none; background-color: transparent;")
        thumb_source = preview_path if preview_path and os.path.exists(preview_path) else image_path
        pm = QPixmap(thumb_source)
        pm = pm.scaled(400, 225, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        thumb.setPixmap(pm)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(thumb)


        toggle_btn = QPushButton("▶")
        toggle_btn.setCheckable(True)
        toggle_btn.setFixedWidth(24)
        toggle_btn.setStyleSheet("QPushButton { border: none; color: #ffd500; font-weight: bold; }")
        header.addWidget(toggle_btn, alignment=Qt.AlignmentFlag.AlignTop)


        meta_col = QVBoxLayout()
        name_label = QLabel(os.path.basename(image_path))
        name_label.setStyleSheet("color: white; border: none; font-weight: 600;")
        meta_col.addWidget(name_label)

        if error_text:
            summary = QLabel(f"Помилка: {error_text}")
            details_text = f"Помилка обробки:\n{error_text}"
        else:
            class_text, conf_text, bbox_text, summary_text = self._build_detection_blocks(detections or [])
            details_text = f"{class_text}\n\n{conf_text}\n\n{bbox_text}"
            summary = QLabel(summary_text)
        summary.setWordWrap(True)
        summary.setStyleSheet("color: #d0d0d0; border: none;")
        meta_col.addWidget(summary)
        header.addLayout(meta_col, 1)
        layout.addLayout(header)

        details = QLabel(details_text)
        details.setWordWrap(True)
        details.setStyleSheet("color: #f0f0f0; border: none;")
        details.hide()
        layout.addWidget(details)

        def toggle_details(checked):
            toggle_btn.setText("▼" if checked else "▶")
            details.setVisible(checked)

        toggle_btn.toggled.connect(toggle_details)
        return frame
    




    def _build_detection_blocks(self, detections):
        class_stats = {}
        for det in detections:
            cls = str(det.get("class_name", "N/A"))
            conf = float(det.get("conf", 0.0))
            xyxy = det.get("xyxy", [0.0, 0.0, 0.0, 0.0])
            if len(xyxy) != 4:
                xyxy = [0.0, 0.0, 0.0, 0.0]
            if cls not in class_stats:
                class_stats[cls] = {"confs": [], "boxes": []}
            class_stats[cls]["confs"].append(conf)
            class_stats[cls]["boxes"].append(xyxy)

        if not class_stats:
            return (
                "Classes:\n  N/A (0)",
                "Confidence:\n  N/A (0%)",
                "Bounding Box cords:\n  Нічого не знайдено",
                "N/A (0)",
            )

        class_lines = ["Classes:"]
        conf_lines = ["Confidence:"]
        bbox_lines = ["Bounding Box cords:"]
        summary_parts = []

        for cls, stats in class_stats.items():
            class_lines.append(f"  {cls} ({len(stats['boxes'])})")
            summary_parts.append(f"{cls} ({len(stats['boxes'])})")
            conf_percent = ", ".join(f"{round(c * 100, 2)}%" for c in stats["confs"])
            conf_lines.append(f"  {cls} ({conf_percent})")
            bbox_lines.append(f"  {cls}:")
            for idx, box in enumerate(stats["boxes"], start=1):
                bbox_lines.append(
                    f"    #{idx}: x1={box[0]} px, y1={box[1]} px, x2={box[2]} px, y2={box[3]} px"
                )

        return (
            "\n".join(class_lines),
            "\n".join(conf_lines),
            "\n".join(bbox_lines),
            ", ".join(summary_parts),
        )






    def on_ai_folder_item_finished(self, exit_code, _exit_status, image_path):
        if self.ai_folder_cancel_requested:
            return

        elapsed = time.perf_counter() - self.ai_folder_item_started_at
        self.ai_folder_processed += 1
        self.ai_folder_total_processed_time += elapsed

        if not self.ai_folder_process:
            return

        stdout_text = bytes(self.ai_folder_process.readAllStandardOutput()).decode("utf-8", errors="ignore")
        stderr_text = bytes(self.ai_folder_process.readAllStandardError()).decode("utf-8", errors="ignore")

        parsed = None
        for line in reversed([ln.strip() for ln in stdout_text.splitlines() if ln.strip()]):
            try:
                candidate = json.loads(line)
                if isinstance(candidate, dict) and "ok" in candidate:
                    parsed = candidate
                    break
            except json.JSONDecodeError:
                continue

        if exit_code != 0 or not parsed or not parsed.get("ok"):
            err = stderr_text.strip()
            if not err and parsed:
                err = parsed.get("error", "Невідома помилка")
            item = self._build_ai_folder_item_widget(image_path, error_text=err or "Невідома помилка")
            self.last_ai_folder_report.append(
                {
                    "name": os.path.basename(image_path),
                    "path": image_path,
                    "ok": False,
                    "error": err or "Невідома помилка",
                    "report": {
                        "classes": "Classes:\n  N/A (0)",
                        "confidence": "Confidence:\n  N/A (0%)",
                        "bounding_box_title": "Bounding Box cords:",
                        "bounding_box_values": "  Нічого не знайдено",
                    },
                    "detections": [],
                }
            )
        else:
            folder_detections = parsed.get("detections", [])
            folder_class_text, folder_conf_text, folder_bbox_text, _summary = self._build_detection_blocks(folder_detections)
            item = self._build_ai_folder_item_widget(
                image_path,
                detections=folder_detections,
                preview_path=parsed.get("output_path"),
            )
            self.last_ai_folder_report.append(
                {
                    "name": os.path.basename(image_path),
                    "path": image_path,
                    "ok": True,
                    "error": "",
                    "output_path": parsed.get("output_path", ""),
                    "report": {
                        "classes": folder_class_text,
                        "confidence": folder_conf_text,
                        "bounding_box_title": "Bounding Box cords:",
                        "bounding_box_values": folder_bbox_text,
                    },
                    "detections": folder_detections,
                }
            )

        self.ai_folder_content_layout.insertWidget(self.ai_folder_content_layout.count() - 1, item)

        if self.ai_folder_processed == 1:
            self.ai_progress_bar.setRange(0, self.ai_folder_total)
        self.ai_progress_bar.setValue(self.ai_folder_processed)

        avg_time = self.ai_folder_total_processed_time / self.ai_folder_processed
        remaining = max(self.ai_folder_total - self.ai_folder_processed, 0)
        eta = avg_time * remaining
        self.ai_progress_bar.setFormat(
            f"Середній час: {avg_time:.2f} с/зображення | Залишилось: {eta:.1f} с ({self.ai_folder_processed}/{self.ai_folder_total})"
        )

        self.start_next_ai_folder_item()


    



    def start_ai_folder_processing(self):
        folder = self.ai_selected_folder
        if not folder:
            QMessageBox.warning(self.second_column, "Попередження", "Спочатку виберіть папку.")
            return

        image_ext = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp")
        paths = [
            os.path.join(folder, name)
            for name in sorted(os.listdir(folder))
            if name.lower().endswith(image_ext)
            
        ]

        self.clear_ai_folder_results()
        if not paths:
            self.ai_folder_content_layout.insertWidget(
                0, QLabel("У вибраній папці немає зображень.")
            )
            return

        self.stop_ai_folder_processing()
        self.last_ai_folder_report = []
        self.ai_folder_cancel_requested = False
        self.ai_folder_paths = paths
        self.ai_folder_total = len(paths)
        self.ai_folder_processed = 0
        self.ai_folder_total_processed_time = 0.0

        self.ai_folder_find_btn.setEnabled(False)
        self.ai_folder_select_btn.setEnabled(False)
        self.ai_progress_bar.setRange(0, 0)
        self.ai_progress_bar.setFormat("Processing...")
        self.vertical_ai_layout.removeWidget(self.ai_progress_bar)
        self.vertical_ai_layout.addWidget(self.ai_progress_bar)
        self.ai_progress_bar.show()
        self.start_next_ai_folder_item()






    def stop_ai_folder_processing(self):
        self.ai_folder_cancel_requested = True
        if self.ai_folder_process and self.ai_folder_process.state() != QProcess.ProcessState.NotRunning:
            self.ai_folder_process.kill()
            self.ai_folder_process.waitForFinished(2000)

        self.ai_folder_process = None
        self.ai_folder_paths = []
        self.ai_progress_bar.hide()
        self.ai_folder_find_btn.setEnabled(True)
        self.ai_folder_select_btn.setEnabled(True)






    def clear_ai_file_report(self):
        self.ai_image_box.clear()
        self.current_image_path = None
        self.last_ai_report = None
        self.preview_state = True
        self.preview_button.setIcon(QIcon("app/assets/eye_closed.png"))
        self.image_name.setText("")
        self.info_class_name.setText("")
        self.info_conf.setText("")
        self.info_xyxy.setText("")
        self.info_x1.setText("")
        self.info_y1.setText("")
        self.info_x2.setText("")
        self.info_y2.setText("")





    def clear_ai_folder_results(self):
        self.last_ai_folder_report = []
        while self.ai_folder_content_layout.count() > 1:
            item = self.ai_folder_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()





    def on_ai_inference_finished(self, exit_code, _exit_status):
        self.ai_progress_bar.hide()

        if not self.ai_process:
            return

        if self.ai_cancel_requested:
            self.ai_cancel_requested = False
            self.ai_process = None
            return

        stdout_text = bytes(self.ai_process.readAllStandardOutput()).decode("utf-8", errors="ignore")
        stderr_text = bytes(self.ai_process.readAllStandardError()).decode("utf-8", errors="ignore")

        parsed = None
        for line in reversed([ln.strip() for ln in stdout_text.splitlines() if ln.strip()]):
            try:
                candidate = json.loads(line)
                if isinstance(candidate, dict) and "ok" in candidate:
                    parsed = candidate
                    break
            except json.JSONDecodeError:
                continue

        if exit_code != 0 or not parsed or not parsed.get("ok"):
            message = "Не вдалося завершити обробку ШІ."
            error_text = stderr_text.strip()
            if not error_text and parsed:
                error_text = parsed.get("error", "")
            if error_text:
                message = f"{message}\n\n{error_text}"
            QMessageBox.critical(self.second_column, "Помилка ШІ", message)
            self.ai_process = None
            return

        output_path = parsed.get("output_path")
        detections = parsed.get("detections", [])

        pixmap = QPixmap(output_path)
        pixmap = pixmap.scaled(1200, 1200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.ai_image_box.setPixmap(pixmap)
        self.ai_image_box.setScaledContents(True)
        self.current_image_path = self.ai_source_path
        self.add_pixmap_to_array(self.ai_source_path, None, pixmap)
        self.preview_state = False
        self.preview_button.setIcon(QIcon("app/assets/eye_openned.png"))

        if self.ai_source_path:
            self.image_name.setText(f"Name: {self.ai_source_path.split('/')[-1]}")

        class_stats = {}
        for det in detections:
            cls = str(det.get("class_name", "N/A"))
            conf = float(det.get("conf", 0.0))
            xyxy = det.get("xyxy", [0.0, 0.0, 0.0, 0.0])
            if len(xyxy) != 4:
                xyxy = [0.0, 0.0, 0.0, 0.0]

            if cls not in class_stats:
                class_stats[cls] = {"confs": [], "boxes": []}

            class_stats[cls]["confs"].append(conf)
            class_stats[cls]["boxes"].append(xyxy)

        if not class_stats:
            self.info_class_name.setText("Classes:\n  N/A (0)")
            self.info_conf.setText("Confidence:\n  N/A (0%)")
            self.info_xyxy.setText("Bounding Box cords:")
            self.info_x1.setText("  Нічого не знайдено")
            self.info_y1.setText("")
            self.info_x2.setText("")
            self.info_y2.setText("")
            self.last_ai_report = {
                "name": os.path.basename(self.ai_source_path) if self.ai_source_path else "",
                "source_path": self.ai_source_path or "",
                "output_path": output_path or "",
                "classes_text": self.info_class_name.text(),
                "confidence_text": self.info_conf.text(),
                "bbox_title_text": self.info_xyxy.text(),
                "bbox_text": self.info_x1.text(),
                "detections": [],
            }
            return

        class_lines = ["Classes:"]
        conf_lines = ["Confidence:"]
        bbox_lines = []

        for cls, stats in class_stats.items():
            class_lines.append(f"  {cls} ({len(stats['boxes'])})")
            conf_percent = ", ".join(f"{round(c * 100, 2)}%" for c in stats["confs"])
            conf_lines.append(f"  {cls} ({conf_percent})")

            bbox_lines.append(f"  {cls}:")
            for idx, box in enumerate(stats["boxes"], start=1):
                bbox_lines.append(
                    f"    #{idx}: x1={box[0]} px, y1={box[1]} px, x2={box[2]} px, y2={box[3]} px"
                )

        self.info_class_name.setText("\n".join(class_lines))
        self.info_conf.setText("\n".join(conf_lines))
        self.info_xyxy.setText("Bounding Box cords:")
        self.info_x1.setText("\n".join(bbox_lines))
        self.info_y1.setText("")
        self.info_x2.setText("")
        self.info_y2.setText("")
        self.info_class_name.adjustSize()
        self.info_conf.adjustSize()
        self.info_x1.adjustSize()
        self.ai_info_layout.activate()
        self.last_ai_report = {
            "name": os.path.basename(self.ai_source_path) if self.ai_source_path else "",
            "source_path": self.ai_source_path or "",
            "output_path": output_path or "",
            "classes_text": self.info_class_name.text(),
            "confidence_text": self.info_conf.text(),
            "bbox_title_text": self.info_xyxy.text(),
            "bbox_text": self.info_x1.text(),
            "detections": detections,
        }
        self.ai_process = None




    def export_ai_report(self):
        export_format = self._ask_export_format()
        if not export_format:
            return

        if self.folder_mode_label.isChecked():
            if not self.last_ai_folder_report:
                QMessageBox.warning(self.second_column, "Попередження", "Немає даних для експорту папки. Спочатку виконайте аналіз.")
                return

            folder_name = os.path.basename(self.ai_selected_folder) if self.ai_selected_folder else "folder"
            payload = {
                "mode": "folder",
                "folder_path": self.ai_selected_folder or "",
                "total": len(self.last_ai_folder_report),
                "items": self.last_ai_folder_report,
            }

            if export_format == "json":
                save_path = self._ask_save_path("Зберегти звіт папки", f"ai_folder_report_{folder_name}", "json")
                if not save_path:
                    return
                self._export_json(payload, save_path)
            else:
                save_path = self._ask_save_path("Зберегти PDF звіт папки", f"ai_folder_report_{folder_name}", "pdf")
                if not save_path:
                    return
                self._export_folder_pdf(save_path)
            return

        if not self.last_ai_report:
            QMessageBox.warning(self.second_column, "Попередження", "Немає даних для експорту. Спочатку виконайте аналіз.")
            return

        default_name = self.last_ai_report.get("name") or "ai_report"
        payload = {
            "mode": "file",
            "name": self.last_ai_report.get("name", ""),
            "source_path": self.last_ai_report.get("source_path", ""),
            "output_path": self.last_ai_report.get("output_path", ""),
            "report": {
                "classes": self.last_ai_report.get("classes_text", ""),
                "confidence": self.last_ai_report.get("confidence_text", ""),
                "bounding_box_title": self.last_ai_report.get("bbox_title_text", ""),
                "bounding_box_values": self.last_ai_report.get("bbox_text", ""),
            },
            "detections": self.last_ai_report.get("detections", []),
        }

        if export_format == "json":
            save_path = self._ask_save_path("Зберегти звіт", default_name, "json")
            if not save_path:
                return
            self._export_json(payload, save_path)
        else:
            save_path = self._ask_save_path("Зберегти PDF звіт", default_name, "pdf")
            if not save_path:
                return
            self._export_single_pdf(save_path)





    def _ask_export_format(self):
        dialog = QMessageBox(self.second_column)
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setWindowTitle("Формат експорту")
        dialog.setText("Оберіть формат звіту:")

        json_btn = dialog.addButton("JSON", QMessageBox.ButtonRole.AcceptRole)
        pdf_btn = dialog.addButton("PDF", QMessageBox.ButtonRole.AcceptRole)
        dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.exec()

        clicked = dialog.clickedButton()
        if clicked == json_btn:
            return "json"
        if clicked == pdf_btn:
            return "pdf"
        return None


    def _ask_save_path(self, title, default_name, ext):
        filter_text = "JSON Files (*.json)" if ext == "json" else "PDF Files (*.pdf)"
        save_path, _ = QFileDialog.getSaveFileName(
            self.second_column,
            title,
            os.path.join(self.second_column.window.get_default_open_path(), f"{default_name}.{ext}"),
            filter_text,
        )
        if not save_path:
            return None
        if not save_path.lower().endswith(f".{ext}"):
            save_path += f".{ext}"
        return save_path





    def _export_json(self, payload, save_path):
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self.second_column, "Експорт", f"Звіт збережено:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self.second_column, "Помилка експорту", f"Не вдалося зберегти файл:\n{e}")





    def _draw_pixmap_in_rect(self, painter, pixmap, rect):
        if pixmap.isNull():
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Image is unavailable")
            return

        scaled = pixmap.scaled(
            rect.width(),
            rect.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = rect.x() + (rect.width() - scaled.width()) // 2
        y = rect.y() + (rect.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)


    def _wrap_text_lines(self, text, max_width, font):
        fm = QFontMetrics(font)
        lines = []

        for paragraph in text.splitlines():
            if paragraph == "":
                lines.append("")
                continue

            words = paragraph.split(" ")
            current = ""
            for word in words:
                candidate = word if not current else f"{current} {word}"
                if fm.horizontalAdvance(candidate) <= max_width:
                    current = candidate
                    continue

                if current:
                    lines.append(current)
                    current = word
                    continue

                # Very long token: split by characters.
                chunk = ""
                for ch in word:
                    char_candidate = f"{chunk}{ch}"
                    if fm.horizontalAdvance(char_candidate) <= max_width or not chunk:
                        chunk = char_candidate
                    else:
                        lines.append(chunk)
                        chunk = ch
                current = chunk

            lines.append(current)

        return lines





    def _draw_page_header(self, painter, content, title, subtitle, section_title):
        y = content.top()

        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(QRect(content.left(), y, content.width(), 28), Qt.AlignmentFlag.AlignLeft, title)
        y += 28

        painter.setFont(QFont("Arial", 10))
        painter.drawText(QRect(content.left(), y, content.width(), 22), Qt.AlignmentFlag.AlignLeft, subtitle)
        y += 24

        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(QRect(content.left(), y, content.width(), 18), Qt.AlignmentFlag.AlignLeft, section_title)
        y += 20
        return y





    def _draw_image_text_pages(self, writer, painter, page_rect, title, subtitle, section_title, image_path, report_text):
        margin = 40
        content = page_rect.adjusted(margin, margin, -margin, -margin)
        y = self._draw_page_header(painter, content, title, subtitle, section_title)

        image_h = 660
        image_rect = QRect(content.left(), y, content.width(), image_h)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawRect(image_rect)
        self._draw_pixmap_in_rect(
            painter,
            QPixmap(image_path) if image_path else QPixmap(),
            image_rect.adjusted(4, 4, -4, -4),
        )

        y = image_rect.bottom() + 24
        text_font = QFont("Arial", 9)
        painter.setFont(text_font)

        wrapped_lines = self._wrap_text_lines(report_text, content.width(), text_font)
        fm = QFontMetrics(text_font)
        line_h = max(fm.lineSpacing() + 2, 12)

        idx = 0
        while idx < len(wrapped_lines):
            available_h = content.bottom() - y + 1
            max_lines = max(1, available_h // line_h)
            chunk = wrapped_lines[idx: idx + max_lines]

            text_rect = QRect(content.left(), y, content.width(), available_h)
            painter.drawText(
                text_rect,
                int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop),
                "\n".join(chunk),
            )
            idx += len(chunk)

            if idx >= len(wrapped_lines):
                break

            writer.newPage()
            content = page_rect.adjusted(margin, margin, -margin, -margin)
            y = self._draw_page_header(
                painter,
                content,
                title,
                subtitle,
                f"{section_title} (text continued)",
            )
            painter.setFont(text_font)






    def _build_dashboard_image(self, report_title, item_name, detections, source_path, output_path):
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import numpy as np
        except Exception:
            return None

        detections = detections or []
        class_counts = {}
        class_confs = {}
        centers_x = []
        centers_y = []
        areas = []

        for det in detections:
            cls = str(det.get("class_name", "N/A"))
            conf = float(det.get("conf", 0.0))
            xyxy = det.get("xyxy", [0.0, 0.0, 0.0, 0.0])
            if len(xyxy) != 4:
                continue
            x1, y1, x2, y2 = [float(v) for v in xyxy]
            class_counts[cls] = class_counts.get(cls, 0) + 1
            class_confs.setdefault(cls, []).append(conf)
            centers_x.append((x1 + x2) / 2.0)
            centers_y.append((y1 + y2) / 2.0)
            areas.append(max((x2 - x1) * (y2 - y1), 1.0))

        total = len(detections)
        mean_conf = float(np.mean([c for vals in class_confs.values() for c in vals])) if total else 0.0
        med_conf = float(np.median([c for vals in class_confs.values() for c in vals])) if total else 0.0
        uniq_classes = len(class_counts)

        # Larger dashboard canvas for better readability in PDF.
        fig = plt.figure(figsize=(18, 11), dpi=220)
        gs = fig.add_gridspec(2, 3, height_ratios=[0.75, 2.8], width_ratios=[1.3, 1.3, 1.8])

        ax_kpi = fig.add_subplot(gs[0, :])
        ax_kpi.axis("off")
        kpi_text = (
            f"Detections: {total}    "
            f"Classes: {uniq_classes}    "
            f"Mean confidence: {mean_conf * 100:.1f}%    "
            f"Median confidence: {med_conf * 100:.1f}%"
        )
        ax_kpi.text(0.01, 0.80, report_title, fontsize=20, fontweight="bold")
        ax_kpi.text(0.01, 0.48, item_name, fontsize=15)
        ax_kpi.text(0.01, 0.10, kpi_text, fontsize=13)

        ax_classes = fig.add_subplot(gs[1, 0])
        if class_counts:
            labels = list(class_counts.keys())
            values = [class_counts[k] for k in labels]
            order = np.argsort(values)
            labels = [labels[i] for i in order]
            values = [values[i] for i in order]
            ax_classes.barh(labels, values, color="#f39c12")
            ax_classes.set_title("Objects per class", fontsize=14, fontweight="bold")
            ax_classes.set_xlabel("Count", fontsize=12)
            ax_classes.tick_params(axis="both", labelsize=11)
        else:
            ax_classes.text(0.5, 0.5, "No detections", ha="center", va="center")
            ax_classes.set_title("Objects per class", fontsize=14, fontweight="bold")
            ax_classes.set_xticks([])
            ax_classes.set_yticks([])

        ax_conf = fig.add_subplot(gs[1, 1])
        if class_confs:
            labels = list(class_confs.keys())
            data = [class_confs[k] for k in labels]
            ax_conf.boxplot(data, labels=labels, vert=True, patch_artist=True)
            ax_conf.set_ylim(0.0, 1.05)
            ax_conf.set_title("Confidence distribution", fontsize=14, fontweight="bold")
            ax_conf.tick_params(axis="x", rotation=25, labelsize=10)
            ax_conf.tick_params(axis="y", labelsize=11)
        else:
            ax_conf.text(0.5, 0.5, "No detections", ha="center", va="center")
            ax_conf.set_title("Confidence distribution", fontsize=14, fontweight="bold")
            ax_conf.set_xticks([])
            ax_conf.set_yticks([])

        ax_map = fig.add_subplot(gs[1, 2])
        if centers_x and centers_y:
            ax_map.scatter(centers_x, centers_y, s=np.clip(np.array(areas) / 120.0, 16, 260), alpha=0.58, c="#1f77b4")
            ax_map.invert_yaxis()
            ax_map.set_title("Spatial map of detections", fontsize=14, fontweight="bold")
            ax_map.set_xlabel("X center", fontsize=12)
            ax_map.set_ylabel("Y center", fontsize=12)
            ax_map.tick_params(axis="both", labelsize=11)
        else:
            ax_map.text(0.5, 0.5, "No detections", ha="center", va="center")
            ax_map.set_title("Spatial map of detections", fontsize=14, fontweight="bold")
            ax_map.set_xticks([])
            ax_map.set_yticks([])

        fig.tight_layout()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix="_ai_dashboard.png")
        tmp_path = tmp.name
        tmp.close()
        fig.savefig(tmp_path, bbox_inches="tight")
        plt.close(fig)
        return tmp_path





    def _draw_dashboard_page(self, painter, page_rect, title, subtitle, dashboard_path):
        margin = 22
        content = page_rect.adjusted(margin, margin, -margin, -margin)
        y = content.top()
        painter.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        painter.drawText(QRect(content.left(), y, content.width(), 24), Qt.AlignmentFlag.AlignLeft, title)
        y += 24
        painter.setFont(QFont("Arial", 10))
        painter.drawText(QRect(content.left(), y, content.width(), 20), Qt.AlignmentFlag.AlignLeft, subtitle)
        y += 22

        dash_rect = QRect(content.left(), y, content.width(), content.bottom() - y)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawRect(dash_rect)
        self._draw_pixmap_in_rect(
            painter,
            QPixmap(dashboard_path) if dashboard_path else QPixmap(),
            dash_rect.adjusted(4, 4, -4, -4),
        )





    def _export_single_pdf(self, save_path):
        report = self.last_ai_report or {}
        dashboard_path = None
        report_text = (
            f"Name: {report.get('name', '')}\n"
            f"Source path: {report.get('source_path', '')}\n"
            f"Output path: {report.get('output_path', '')}\n\n"
            f"{report.get('classes_text', '')}\n\n"
            f"{report.get('confidence_text', '')}\n\n"
            f"{report.get('bbox_title_text', '')}\n"
            f"{report.get('bbox_text', '')}"
        )

        try:
            writer = QPdfWriter(save_path)
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            writer.setResolution(150)
            painter = QPainter(writer)
            page_rect = writer.pageLayout().paintRectPixels(writer.resolution())

            self._draw_image_text_pages(
                writer,
                painter,
                page_rect,
                "AI Report (File Mode)",
                report.get("name", ""),
                "Before analysis",
                report.get("source_path", ""),
                report_text,
            )

            writer.newPage()
            self._draw_image_text_pages(
                writer,
                painter,
                page_rect,
                "AI Report (File Mode)",
                report.get("name", ""),
                "After analysis",
                report.get("output_path", ""),
                report_text,
            )

            dashboard_path = self._build_dashboard_image(
                "AI Report (File Mode)",
                report.get("name", ""),
                report.get("detections", []),
                report.get("source_path", ""),
                report.get("output_path", ""),
            )
            if dashboard_path:
                writer.newPage()
                self._draw_dashboard_page(
                    painter,
                    page_rect,
                    "AI Report (File Mode)",
                    report.get("name", ""),
                    dashboard_path,
                )

            painter.end()
            QMessageBox.information(self.second_column, "Експорт", f"PDF звіт збережено:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self.second_column, "Помилка експорту", f"Не вдалося зберегти PDF:\n{e}")
        finally:
            if dashboard_path and os.path.exists(dashboard_path):
                try:
                    os.remove(dashboard_path)
                except OSError:
                    pass





    def _export_folder_pdf(self, save_path):
        try:
            writer = QPdfWriter(save_path)
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            writer.setResolution(150)
            painter = QPainter(writer)
            page_rect = writer.pageLayout().paintRectPixels(writer.resolution())

            first_item = True
            for item in self.last_ai_folder_report:
                if not first_item:
                    writer.newPage()
                first_item = False

                report = item.get("report", {})
                item_report_text = (
                    f"Name: {item.get('name', '')}\n"
                    f"Source path: {item.get('path', '')}\n"
                    f"Output path: {item.get('output_path', '')}\n"
                    f"Status: {'OK' if item.get('ok') else 'Error'}\n"
                    f"Error: {item.get('error', '')}\n\n"
                    f"{report.get('classes', '')}\n\n"
                    f"{report.get('confidence', '')}\n\n"
                    f"{report.get('bounding_box_title', '')}\n"
                    f"{report.get('bounding_box_values', '')}"
                )

                self._draw_image_text_pages(
                    writer,
                    painter,
                    page_rect,
                    "AI Report (Folder Mode)",
                    item.get("name", ""),
                    "Before analysis",
                    item.get("path", ""),
                    item_report_text,
                )

                writer.newPage()
                self._draw_image_text_pages(
                    writer,
                    painter,
                    page_rect,
                    "AI Report (Folder Mode)",
                    item.get("name", ""),
                    "After analysis",
                    item.get("output_path", ""),
                    item_report_text,
                )

                dashboard_path = self._build_dashboard_image(
                    "AI Report (Folder Mode)",
                    item.get("name", ""),
                    item.get("detections", []),
                    item.get("path", ""),
                    item.get("output_path", ""),
                )
                if dashboard_path:
                    writer.newPage()
                    self._draw_dashboard_page(
                        painter,
                        page_rect,
                        "AI Report (Folder Mode)",
                        item.get("name", ""),
                        dashboard_path,
                    )
                    try:
                        os.remove(dashboard_path)
                    except OSError:
                        pass

            painter.end()
            QMessageBox.information(self.second_column, "Експорт", f"PDF звіт збережено:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self.second_column, "Помилка експорту", f"Не вдалося зберегти PDF:\n{e}")




    def on_ai_inference_error(self, process_error):
        if self.ai_cancel_requested:
            return
        self.ai_progress_bar.hide()
        QMessageBox.critical(
            self.second_column,
            "Помилка запуску ШІ",
            f"Не вдалося запустити процес обробки (код: {int(process_error)}).",
        )

