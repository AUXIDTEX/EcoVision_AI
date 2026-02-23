import os
import tempfile

from PIL import Image, ImageDraw
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QFont, QPainter, QPageSize, QPdfWriter, QPixmap
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from modules.json_mode_exporter import build_mode_payload


def export_mode_pdf(second_column, mode):
    payload = build_mode_payload(second_column, mode)
    if payload is None:
        return

    default_name = "points_export.pdf" if mode == 0 else "grid_export.pdf"
    title = second_column.get_text("save_pdf_points") if mode == 0 else second_column.get_text("save_pdf_grid")
    save_path = ask_pdf_export_path(second_column, title, default_name)
    if not save_path:
        return

    render_pdf_report(second_column, payload, save_path)


def ask_pdf_export_path(parent, title, default_name):
    save_path, _ = QFileDialog.getSaveFileName(
        parent,
        title,
        os.path.join(parent.window.get_default_open_path(), default_name),
        "PDF Files (*.pdf)",
    )
    if not save_path:
        return None
    if not save_path.lower().endswith(".pdf"):
        save_path += ".pdf"
    return save_path


def render_pdf_report(parent, payload, save_path):
    temp_paths = []
    try:
        writer = QPdfWriter(save_path)
        writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        writer.setResolution(150)
        painter = QPainter(writer)
        page_rect = writer.pageLayout().paintRectPixels(writer.resolution())

        mode_name = payload.get("mode", "")
        images = payload.get("images", [])
        first_page = True

        for image_data in images:
            before_path = image_data.get("image_path", "")
            if not before_path:
                continue

            if mode_name == "points":
                after_path = create_points_after_image(before_path, image_data)
                chart_path = create_points_chart_image(image_data)
            else:
                after_path = create_grid_after_image(before_path, image_data)
                chart_path = create_grid_chart_image(image_data)

            if after_path:
                temp_paths.append(after_path)
            if chart_path:
                temp_paths.append(chart_path)

            if not first_page:
                writer.newPage()
            first_page = False

            draw_before_after_page(painter, page_rect, mode_name, image_data, before_path, after_path)

            writer.newPage()
            draw_chart_page(painter, page_rect, mode_name, image_data, chart_path)

        painter.end()
        QMessageBox.information(parent, parent.get_text("export"), f"{parent.get_text('pdf_saved')}:\n{save_path}")
    except Exception as error:
        QMessageBox.critical(parent, parent.get_text("export_error"), f"{parent.get_text('cannot_build_pdf')}:\n{error}")
    finally:
        for path in temp_paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass


def draw_before_after_page(painter, page_rect, mode_name, image_data, before_path, after_path):
    margin = 40
    content = page_rect.adjusted(margin, margin, -margin, -margin)

    draw_header(painter, content, mode_name, image_data.get("image_name", ""))

    top_y = content.top() + 70
    block_height = (content.height() - 220) // 2
    first_rect = QRect(content.left(), top_y, content.width(), block_height)
    second_rect = QRect(content.left(), top_y + block_height + 30, content.width(), block_height)

    draw_image_block(painter, "Before", before_path, first_rect)
    draw_image_block(painter, "After", after_path if after_path else before_path, second_rect)
    draw_summary_block(painter, mode_name, image_data, QRect(content.left(), second_rect.bottom() + 20, content.width(), 120))


def draw_chart_page(painter, page_rect, mode_name, image_data, chart_path):
    margin = 40
    content = page_rect.adjusted(margin, margin, -margin, -margin)

    painter.setPen(Qt.GlobalColor.black)
    painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
    painter.drawText(QRect(content.left(), content.top(), content.width(), 30), Qt.AlignmentFlag.AlignLeft, "Data Visualization")

    subtitle = f"{image_data.get('image_name', '')} | Режим: {'Точки' if mode_name == 'points' else 'Сітка'}"
    painter.setFont(QFont("Arial", 10))
    painter.drawText(QRect(content.left(), content.top() + 32, content.width(), 22), Qt.AlignmentFlag.AlignLeft, subtitle)

    chart_rect = QRect(content.left(), content.top() + 62, content.width(), content.height() - 62)
    painter.drawRect(chart_rect)

    if chart_path and os.path.exists(chart_path):
        draw_pixmap_in_rect(painter, QPixmap(chart_path), chart_rect.adjusted(6, 6, -6, -6))
    else:
        painter.setFont(QFont("Arial", 11))
        painter.drawText(chart_rect, Qt.AlignmentFlag.AlignCenter, "Графік недоступний (matplotlib не встановлено).")


def draw_header(painter, content_rect, mode_name, image_name):
    painter.setPen(Qt.GlobalColor.black)
    painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
    title = f"Звіт експорту ({'Point mode' if mode_name == 'points' else 'Grid mode'})"
    painter.drawText(QRect(content_rect.left(), content_rect.top(), content_rect.width(), 28), Qt.AlignmentFlag.AlignLeft, title)

    painter.setFont(QFont("Arial", 10))
    painter.drawText(
        QRect(content_rect.left(), content_rect.top() + 32, content_rect.width(), 22),
        Qt.AlignmentFlag.AlignLeft,
        f"Image: {image_name}",
    )


def draw_image_block(painter, caption, image_path, rect):
    painter.setPen(Qt.GlobalColor.black)
    painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
    painter.drawText(QRect(rect.left(), rect.top() - 22, rect.width(), 20), Qt.AlignmentFlag.AlignLeft, caption)
    painter.drawRect(rect)

    pixmap = QPixmap(image_path) if image_path and os.path.exists(image_path) else QPixmap()
    draw_pixmap_in_rect(painter, pixmap, rect.adjusted(6, 6, -6, -6))


def draw_pixmap_in_rect(painter, pixmap, rect):
    if pixmap.isNull():
        painter.setFont(QFont("Arial", 10))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Зображення недоступне")
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


def draw_summary_block(painter, mode_name, image_data, rect):
    painter.setFont(QFont("Arial", 10))
    if mode_name == "points":
        points_count = len(image_data.get("points", []))
        summary = f"Кількість точок: {points_count}"
    else:
        fragments = image_data.get("fragments", [])
        summary = (
            f"Кратність сітки: {image_data.get('grid_multiplier', 0)} | "
            f"Поріг відмінності: {image_data.get('difference_percent', 0)}% | "
            f"Фрагментів: {len(fragments)}"
        )
    painter.drawText(rect, int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop), summary)


def create_points_after_image(image_path, image_data):
    if not os.path.exists(image_path):
        return None

    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    for point in image_data.get("points", []):
        real = point.get("real_coordinates", {})
        x = int(real.get("x", 0))
        y = int(real.get("y", 0))
        radius = int(point.get("radius", 0))
        idx = point.get("index", "")

        draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=(255, 0, 0), width=3)
        draw.text((x + radius + 2, y - radius), str(idx), fill=(255, 255, 0))

    return save_temp_image(image, "_points_after.png")


def create_grid_after_image(image_path, image_data):
    if not os.path.exists(image_path):
        return None

    threshold = int(image_data.get("difference_percent", 0))
    image = Image.open(image_path).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for fragment in image_data.get("fragments", []):
        corners = fragment.get("corner_points", {})
        top_left = corners.get("top_left", {})
        bottom_right = corners.get("bottom_right", {})

        x1 = int(top_left.get("x", 0))
        y1 = int(top_left.get("y", 0))
        x2 = int(bottom_right.get("x", 0))
        y2 = int(bottom_right.get("y", 0))
        diff = int(fragment.get("difference_percent", 0))

        if diff < threshold:
            draw.rectangle((x1, y1, x2, y2), fill=(255, 0, 0, 80), outline=(0, 0, 0, 120), width=1)
        else:
            draw.rectangle((x1, y1, x2, y2), outline=(0, 0, 0, 120), width=1)

    result = Image.alpha_composite(image, overlay).convert("RGB")
    return save_temp_image(result, "_grid_after.png")


def create_points_chart_image(image_data):
    points = image_data.get("points", [])
    if not points:
        return None

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except Exception:
        return None

    indices = [int(p.get("index", i + 1)) for i, p in enumerate(points)]
    colors = [p.get("average_color", [0, 0, 0]) for p in points]
    reds = [int(c[0]) for c in colors]
    greens = [int(c[1]) for c in colors]
    blues = [int(c[2]) for c in colors]

    x = np.arange(len(indices))
    width = 0.25

    fig, ax = plt.subplots(figsize=(11, 6), dpi=180)
    ax.bar(x - width, reds, width, label="R", color="#d32f2f")
    ax.bar(x, greens, width, label="G", color="#2e7d32")
    ax.bar(x + width, blues, width, label="B", color="#1565c0")
    ax.set_xticks(x)
    ax.set_xticklabels([str(i) for i in indices])
    ax.set_xlabel("Індекс точки")
    ax.set_ylabel("Середній колір")
    ax.set_title("Середні RGB значення по точках")
    ax.set_ylim(0, 255)
    ax.legend()
    fig.tight_layout()

    path = create_temp_file_path("_points_chart.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def create_grid_chart_image(image_data):
    fragments = image_data.get("fragments", [])
    if not fragments:
        return None

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    threshold = int(image_data.get("difference_percent", 0))
    diffs = [int(fragment.get("difference_percent", 0)) for fragment in fragments]
    below = sum(1 for value in diffs if value < threshold)
    above = len(diffs) - below

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=180)

    axes[0].hist(diffs, bins=12, color="#1976d2", edgecolor="white")
    axes[0].axvline(threshold, color="#d32f2f", linestyle="--", linewidth=2, label=f"Поріг: {threshold}%")
    axes[0].set_title("Розподіл відмінностей")
    axes[0].set_xlabel("Difference %")
    axes[0].set_ylabel("Кількість фрагментів")
    axes[0].legend()

    axes[1].pie([below, above], labels=["< Поріг", ">= Поріг"], autopct="%1.1f%%", colors=["#ef5350", "#66bb6a"])
    axes[1].set_title("Співвідношення фрагментів")

    fig.tight_layout()
    path = create_temp_file_path("_grid_chart.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def create_temp_file_path(suffix):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    path = temp_file.name
    temp_file.close()
    return path


def save_temp_image(image, suffix):
    path = create_temp_file_path(suffix)
    image.save(path)
    return path
