from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap


def clamp_size(size: QSize, min_w: int = 1, min_h: int = 1) -> QSize:
    return QSize(max(size.width(), min_w), max(size.height(), min_h))


def scale_pixmap_to_fit(
    pixmap: QPixmap,
    target_size: QSize,
    min_w: int = 1,
    min_h: int = 1,
) -> QPixmap:
    if pixmap.isNull():
        return QPixmap()

    safe_target = clamp_size(target_size, min_w=min_w, min_h=min_h)
    return pixmap.scaled(
        safe_target,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
