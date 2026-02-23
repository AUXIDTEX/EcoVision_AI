import json
import os

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


SETTINGS_FILE_PATH = os.path.join("app", "user_settings.json")

DEFAULT_SETTINGS = {
    "language": "uk",
    "default_open_path": os.path.expanduser("~"),
}


UI_TEXTS = {
    "uk": {
        "window_title": "Порівняння зображень",
        "name_placeholder": "Введіть назву",
        "add_category": "Додати",
        "mode_points": "Точки",
        "mode_grid": "Сітка",
        "mode_ai": "Нейромережа",
        "mode_spectral": "Фільтрування зображень",
        "compare_points": "Режим точок",
        "compare_grid": "Режим сітки",
        "compare_ai": "Режим нейромережі",
        "compare_spectral": "Режим фільтрування зображень",
        "radius": "Радіус",
        "points_coordinates": "Координати точок",
        "difference_percent": "Відмінність (%)",
        "grid_multiplier": "Кратність сітки",
        "export": "Експортувати",
        "add_image": "Додати зображення",
        "switch_image": "Змінити зображення",
        "pick_image_title": "Виберіть зображення",
        "pick_folder_images": "Виберіть папку з зображеннями",
        "pick_folder_save": "Виберіть папку для збереження",
        "settings_title": "Налаштування",
        "language": "Мова",
        "language_uk": "Українська",
        "language_en": "Англійська",
        "default_path": "Стандартний шлях",
        "browse": "Огляд...",
        "save": "Зберегти",
        "cancel": "Скасувати",
        "choose_default_path": "Виберіть стандартну папку",
        "settings_saved": "Налаштування збережено",
        "settings_save_error": "Не вдалося зберегти налаштування",
        "warning": "Попередження",
        "select_two_images": "Будь ласка, виберіть два зображення для порівняння.",
        "export_format_title": "Формат експорту",
        "export_format_prompt": "Оберіть формат експорту:",
        "export_points_grid_only": "Експорт доступний лише в режимах точок та сітки.",
        "save_json_points": "Зберегти JSON (режим точок)",
        "save_json_grid": "Зберегти JSON (режим сітки)",
        "save_pdf_points": "Зберегти PDF (режим точок)",
        "save_pdf_grid": "Зберегти PDF (режим сітки)",
        "select_image_for_export": "Оберіть зображення для експорту.",
        "no_points_for_export": "Немає точок для експорту.",
        "cannot_build_export_data": "Не вдалося отримати дані вибраних зображень.",
        "cannot_build_grid_export_data": "Не вдалося отримати дані сітки для експорту.",
        "file_saved": "Файл збережено",
        "export_error": "Помилка експорту",
        "cannot_save_file": "Не вдалося зберегти файл",
        "pdf_saved": "PDF звіт збережено",
        "cannot_build_pdf": "Не вдалося сформувати PDF",
        "file_mode": "Файл",
        "folder_mode": "Папка",
        "pick_folder": "Вибрати папку",
        "run": "Виконати",
        "export_report": "Експортувати звіт",
        "ai_report_title": "Звіт нейромережі",
        "ai_run_hint": "Натисніть 'Виконати' для обробки вибраних зображень",
        "save_all_variants": "Зберегти усі варіанти",
        "selected_folder": "Вибрана папка",
        "filter": "Фільтр",
        "reset": "Скинути",
    },
    "en": {
        "window_title": "Image Comparison",
        "name_placeholder": "Enter name",
        "add_category": "Add",
        "mode_points": "Points",
        "mode_grid": "Grid",
        "mode_ai": "Neural Network",
        "mode_spectral": "Image Filtering",
        "compare_points": "Points Mode",
        "compare_grid": "Grid Mode",
        "compare_ai": "Neural Network Mode",
        "compare_spectral": "Image Filtering Mode",
        "radius": "Radius",
        "points_coordinates": "Point Coordinates",
        "difference_percent": "Difference (%)",
        "grid_multiplier": "Grid Multiplier",
        "export": "Export",
        "add_image": "Add image",
        "switch_image": "Change image",
        "pick_image_title": "Choose image",
        "pick_folder_images": "Choose images folder",
        "pick_folder_save": "Choose save folder",
        "settings_title": "Settings",
        "language": "Language",
        "language_uk": "Ukrainian",
        "language_en": "English",
        "default_path": "Default path",
        "browse": "Browse...",
        "save": "Save",
        "cancel": "Cancel",
        "choose_default_path": "Choose default folder",
        "settings_saved": "Settings saved",
        "settings_save_error": "Failed to save settings",
        "warning": "Warning",
        "select_two_images": "Please select two images to compare.",
        "export_format_title": "Export Format",
        "export_format_prompt": "Choose export format:",
        "export_points_grid_only": "Export is available only in points and grid modes.",
        "save_json_points": "Save JSON (points mode)",
        "save_json_grid": "Save JSON (grid mode)",
        "save_pdf_points": "Save PDF (points mode)",
        "save_pdf_grid": "Save PDF (grid mode)",
        "select_image_for_export": "Select images for export.",
        "no_points_for_export": "No points to export.",
        "cannot_build_export_data": "Failed to collect selected images data.",
        "cannot_build_grid_export_data": "Failed to collect grid data for export.",
        "file_saved": "File saved",
        "export_error": "Export Error",
        "cannot_save_file": "Failed to save file",
        "pdf_saved": "PDF report saved",
        "cannot_build_pdf": "Failed to build PDF",
        "file_mode": "File",
        "folder_mode": "Folder",
        "pick_folder": "Choose folder",
        "run": "Run",
        "export_report": "Export report",
        "ai_report_title": "Neural Network Report",
        "ai_run_hint": "Press 'Run' to process selected images",
        "save_all_variants": "Save all variants",
        "selected_folder": "Selected folder",
        "filter": "Filter",
        "reset": "Reset",
    },
}


def get_text_by_language(language, key):
    lang_map = UI_TEXTS.get(language, UI_TEXTS["uk"])
    if key in lang_map:
        return lang_map[key]
    return UI_TEXTS["uk"].get(key, key)


def read_settings_file():
    if not os.path.exists(SETTINGS_FILE_PATH):
        return dict(DEFAULT_SETTINGS)

    try:
        with open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as file:
            loaded = json.load(file)
            result = dict(DEFAULT_SETTINGS)
            if isinstance(loaded, dict):
                result.update(loaded)
            return result
    except Exception:
        return dict(DEFAULT_SETTINGS)


def write_settings_file(settings):
    folder = os.path.dirname(SETTINGS_FILE_PATH)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=2)


class SettingsDialog(QDialog):
    def __init__(self, parent=None, language="uk", default_open_path=""):
        super().__init__(parent)
        self.current_language = language
        self.default_open_path = default_open_path or os.path.expanduser("~")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(get_text_by_language(self.current_language, "settings_title"))
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        self.language_combo = QComboBox()
        self.language_combo.addItem(get_text_by_language(self.current_language, "language_uk"), "uk")
        self.language_combo.addItem(get_text_by_language(self.current_language, "language_en"), "en")
        idx = 0 if self.current_language == "uk" else 1
        self.language_combo.setCurrentIndex(idx)
        form.addRow(QLabel(get_text_by_language(self.current_language, "language")), self.language_combo)

        path_row = QHBoxLayout()
        self.path_input = QLineEdit(self.default_open_path)
        self.path_button = QPushButton(get_text_by_language(self.current_language, "browse"))
        self.path_button.clicked.connect(self.pick_default_path)
        path_row.addWidget(self.path_input)
        path_row.addWidget(self.path_button)
        form.addRow(QLabel(get_text_by_language(self.current_language, "default_path")), path_row)

        buttons = QHBoxLayout()
        buttons.addStretch()

        self.save_button = QPushButton(get_text_by_language(self.current_language, "save"))
        self.cancel_button = QPushButton(get_text_by_language(self.current_language, "cancel"))
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)
        layout.addLayout(buttons)

    def pick_default_path(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            get_text_by_language(self.current_language, "choose_default_path"),
            self.path_input.text().strip() or os.path.expanduser("~"),
        )
        if folder:
            self.path_input.setText(folder)

    def get_values(self):
        language = self.language_combo.currentData()
        folder = self.path_input.text().strip() or os.path.expanduser("~")
        return {
            "language": language,
            "default_open_path": folder,
        }


class AppSettingsManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.settings = read_settings_file()

    def get_language(self):
        return self.settings.get("language", DEFAULT_SETTINGS["language"])

    def get_default_open_path(self):
        value = self.settings.get("default_open_path", DEFAULT_SETTINGS["default_open_path"])
        if value and os.path.isdir(value):
            return value
        return DEFAULT_SETTINGS["default_open_path"]

    def get_text(self, key):
        return get_text_by_language(self.get_language(), key)

    def apply_loaded_settings(self):
        self.main_window.apply_language(self.get_language())

    def open_settings_dialog(self, parent_widget=None):
        dialog = SettingsDialog(
            parent=parent_widget or self.main_window,
            language=self.get_language(),
            default_open_path=self.get_default_open_path(),
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        values = dialog.get_values()
        self.settings["language"] = values["language"]
        self.settings["default_open_path"] = values["default_open_path"]

        try:
            write_settings_file(self.settings)
        except Exception as error:
            QMessageBox.critical(
                self.main_window,
                self.get_text("settings_title"),
                f"{self.get_text('settings_save_error')}:\n{error}",
            )
            return

        self.apply_loaded_settings()
        QMessageBox.information(
            self.main_window,
            self.get_text("settings_title"),
            self.get_text("settings_saved"),
        )
