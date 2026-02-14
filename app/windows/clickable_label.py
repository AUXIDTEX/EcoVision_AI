from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel

class ClickableLabel(QLabel):
    clicked = pyqtSignal(int,int)
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.x = int(event.position().x())
            self.y = int(event.position().y())

            self.clicked.emit(self.x, self.y)  # Emit the signal with x and y coordinates