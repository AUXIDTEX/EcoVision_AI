import os
import sys
import time
import json
from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QPixmap
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




    def mode_switch_func(self, mode):
        if mode == "1":
            self.stop_ai_folder_processing()
            self.ai_folder_widget.hide()
            self.ai_widget.show()


            if self.second_column.mode == 2:
                selected_path = SelectableImageBox.path[1] or SelectableImageBox.path[2]
                if selected_path:
                    self.start_ai_inference(selected_path)
                else:
                    self.clear_ai_file_report()

    
        elif mode == "2":
            self.stop_ai_inference()
            self.ai_progress_bar.hide()
            self.ai_widget.hide()
            self.ai_folder_widget.show()
            self.clear_ai_file_report()



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


    def start_ai_inference(self, image_path):
        if not image_path:
            QMessageBox.warning(self.second_column, "Помилка", "Не вдалося отримати шлях до зображення.")
            return



        source_pixmap = QPixmap(image_path)
        source_pixmap = source_pixmap.scaled(1200, 1200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.ai_image_box.setPixmap(source_pixmap)
        self.ai_image_box.setScaledContents(True)



        self.ai_cancel_requested = False
        if self.ai_process and self.ai_process.state() != QProcess.ProcessState.NotRunning:
            self.stop_ai_inference()

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
        folder = QFileDialog.getExistingDirectory(self.second_column, "Виберіть папку з зображеннями")
        if not folder:
            return

        self.ai_selected_folder = folder
        self.ai_folder_select_btn.setText(f"Вибрана папка: {os.path.basename(folder)}")
        self.clear_ai_folder_results()
        self.ai_folder_content_layout.insertWidget(len(self.ai_folder_content_layout) - 1, QLabel("Папка обрана. Натисніть 'Виконати' для обробки."))




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
        else:
            item = self._build_ai_folder_item_widget(
                image_path,
                detections=parsed.get("detections", []),
                preview_path=parsed.get("output_path"),
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
        self.image_name.setText("")
        self.info_class_name.setText("")
        self.info_conf.setText("")
        self.info_xyxy.setText("")
        self.info_x1.setText("")
        self.info_y1.setText("")
        self.info_x2.setText("")
        self.info_y2.setText("")


    def clear_ai_folder_results(self):
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
        self.ai_process = None




    def on_ai_inference_error(self, process_error):
        if self.ai_cancel_requested:
            return
        self.ai_progress_bar.hide()
        QMessageBox.critical(
            self.second_column,
            "Помилка запуску ШІ",
            f"Не вдалося запустити процес обробки (код: {int(process_error)}).",
        )