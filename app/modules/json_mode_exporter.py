import json
import os

import numpy as np
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from logic.average_color import Average_color
from modules.selectable_imagebox import SelectableImageBox


def export_mode_json(second_column, mode):
    payload = build_mode_payload(second_column, mode)
    if payload is None:
        return

    default_name = "points_export.json" if mode == 0 else "grid_export.json"
    title = second_column.get_text("save_json_points") if mode == 0 else second_column.get_text("save_json_grid")
    save_path = ask_json_export_path(second_column, title, default_name)
    if not save_path:
        return

    write_json_payload(second_column, payload, save_path)


def build_mode_payload(second_column, mode):
    if mode == 0:
        return build_points_export(second_column)
    if mode == 1:
        return build_grid_export(second_column)

    QMessageBox.warning(second_column, second_column.get_text("export"), second_column.get_text("export_points_grid_only"))
    return None


def build_points_export(second_column):
    image_paths = get_selected_image_paths()
    if not image_paths:
        QMessageBox.warning(second_column, second_column.get_text("export"), second_column.get_text("select_image_for_export"))
        return None

    if not second_column.point_overlay.points:
        QMessageBox.warning(second_column, second_column.get_text("export"), second_column.get_text("no_points_for_export"))
        return None

    images = []
    for path in image_paths:
        image_entry = get_image_entry_by_path(second_column.image_array, path)
        if image_entry is None:
            continue

        points, label_width, label_height = collect_points_for_image(second_column, image_entry["np_array"], path)
        images.append(
            {
                "image_name": get_image_name(path),
                "image_path": path,
                "label_size": {"width": label_width, "height": label_height},
                "points": points,
            }
        )

    if not images:
        QMessageBox.warning(second_column, second_column.get_text("export"), second_column.get_text("cannot_build_export_data"))
        return None

    return {
        "mode": "points",
        "images": images,
    }


def build_grid_export(second_column):
    image_paths = get_selected_image_paths()
    if not image_paths:
        QMessageBox.warning(second_column, second_column.get_text("export"), second_column.get_text("select_image_for_export"))
        return None

    overlays = {
        SelectableImageBox.path.get(1): second_column.grid_overlay,
        SelectableImageBox.path.get(2): second_column.grid_overlay2,
    }

    images = []
    for path in image_paths:
        image_entry = get_image_entry_by_path(second_column.image_array, path)
        overlay = overlays.get(path)
        if image_entry is None or overlay is None:
            continue

        overlay.img_arr = image_entry["np_array"]
        overlay.calculate_grid()
        fragments = collect_grid_fragments(image_entry["np_array"], overlay.grid_diffs)

        images.append(
            {
                "image_name": get_image_name(path),
                "image_path": path,
                "grid_multiplier": int(second_column.sizer_slider.value()),
                "difference_percent": int(second_column.diff_slider.value()),
                "average_image_color": calculate_average_color(image_entry["np_array"]),
                "fragments": fragments,
            }
        )

    if not images:
        QMessageBox.warning(second_column, second_column.get_text("export"), second_column.get_text("cannot_build_grid_export_data"))
        return None

    return {
        "mode": "grid",
        "images": images,
    }


def collect_points_for_image(second_column, image_array, image_path):
    target_label = second_column.image1 if image_path == SelectableImageBox.path.get(1) else second_column.image2
    label_width = max(target_label.width(), 1)
    label_height = max(target_label.height(), 1)
    calculator = Average_color(image_array, label_width, label_height)

    height, width = image_array.shape[:2]
    scale_x = width / label_width
    scale_y = height / label_height

    points = []
    for point in second_column.point_overlay.points:
        x = int(point["x"])
        y = int(point["y"])
        radius = int(point["radius"])

        real_x = int(x * scale_x)
        real_y = int(y * scale_y)
        avg_color = tuple(int(c) for c in calculator.calculate(x, y, radius))

        points.append(
            {
                "index": int(point.get("number", len(points) + 1)),
                "coordinates": {"x": x, "y": y},
                "real_coordinates": {"x": real_x, "y": real_y},
                "radius": radius,
                "average_color": list(avg_color),
            }
        )

    return points, label_width, label_height


def collect_grid_fragments(image_array, grid_diffs):
    fragments = []
    for index, cell in enumerate(grid_diffs, start=1):
        x = int(cell["x"])
        y = int(cell["y"])
        x_max = int(cell["x_max"])
        y_max = int(cell["y_max"])

        region = image_array[y:y_max, x:x_max]
        average_color = calculate_average_color(region)

        fragments.append(
            {
                "index": index,
                "corner_points": {
                    "top_left": {"x": x, "y": y},
                    "top_right": {"x": x_max, "y": y},
                    "bottom_left": {"x": x, "y": y_max},
                    "bottom_right": {"x": x_max, "y": y_max},
                },
                "average_color": average_color,
                "difference_percent": int(cell.get("diff", 0)),
            }
        )

    return fragments


def calculate_average_color(image_array):
    if image_array is None or image_array.size == 0:
        return [0, 0, 0]
    return [int(c) for c in np.mean(image_array, axis=(0, 1))]


def get_image_entry_by_path(image_array, path):
    return next((item for item in image_array if item.get("path") == path), None)


def get_selected_image_paths():
    selected = [SelectableImageBox.path.get(1), SelectableImageBox.path.get(2)]
    return [path for path in selected if path]


def get_image_name(path):
    return os.path.basename(path) if path else ""


def ask_json_export_path(parent, title, default_name):
    save_path, _ = QFileDialog.getSaveFileName(
        parent,
        title,
        os.path.join(parent.window.get_default_open_path(), default_name),
        "JSON Files (*.json)",
    )
    if not save_path:
        return None
    if not save_path.lower().endswith(".json"):
        save_path += ".json"
    return save_path


def write_json_payload(parent, payload, save_path):
    try:
        with open(save_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        QMessageBox.information(parent, parent.get_text("export"), f"{parent.get_text('file_saved')}:\n{save_path}")
    except Exception as error:
        QMessageBox.critical(parent, parent.get_text("export_error"), f"{parent.get_text('cannot_save_file')}:\n{error}")
