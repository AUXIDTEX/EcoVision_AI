from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy


class Image_Output(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        self.current_color = 70, 130, 180  # Default color (steel blue)

        self.number_label = QLabel()
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        #self.number_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.number_label.setFixedWidth(28)
        self.number_label.setStyleSheet("color: white; border: none;")
        self.layout.addWidget(self.number_label)
        
        self.color = QLabel()
        self.color.setStyleSheet("border: 1px solid black; border-radius: 2px;")
        self.color.setFixedSize(20, 20)
        self.layout.addWidget(self.color)
        self.color.show()

        self.color_value = QLabel()
        self.color_value.setStyleSheet("color: white; border: none;")
        self.layout.addWidget(self.color_value)

        #self.layout.addStretch()

    def set_number(self, number):
        self.number_label.setText(number)

    def set_color(self, color, number):
        r, g, b = color
        self.set_number(number)

        self.color_value.setText(', '.join(str(int(c)) for c in color))
        
        self.color.setStyleSheet(f"background-color: rgb({r},{g},{b}); border: 1px solid black; border-radius: 2px;")
