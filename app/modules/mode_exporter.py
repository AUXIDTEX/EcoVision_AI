from PyQt6.QtWidgets import QMessageBox

from modules.json_mode_exporter import export_mode_json
from modules.pdf_mode_exporter import export_mode_pdf


def export_by_mode(second_column):
    mode = second_column.mode

    if mode not in (0, 1):
        QMessageBox.warning(
            second_column,
            second_column.get_text("export"),
            second_column.get_text("export_points_grid_only"),
        )
        return

    export_format = ask_export_format(second_column)
    if not export_format:
        return

    if export_format == "json":
        export_mode_json(second_column, mode)
    elif export_format == "pdf":
        export_mode_pdf(second_column, mode)


def ask_export_format(parent):
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Question)
    dialog.setWindowTitle(parent.get_text("export_format_title"))
    dialog.setText(parent.get_text("export_format_prompt"))

    json_button = dialog.addButton("JSON", QMessageBox.ButtonRole.AcceptRole)
    pdf_button = dialog.addButton("PDF", QMessageBox.ButtonRole.AcceptRole)
    dialog.addButton(QMessageBox.StandardButton.Cancel)
    dialog.exec()

    clicked = dialog.clickedButton()
    if clicked == json_button:
        return "json"
    if clicked == pdf_button:
        return "pdf"
    return None
