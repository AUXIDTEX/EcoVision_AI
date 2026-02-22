from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy


class Image_Output(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #2b2b2b; border: 1px solid #808080; border-radius: 8px;")

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        self.current_color = 70, 130, 180  # Default color (steel blue)

        self.number_label = QLabel()
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        #self.number_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.number_label.setFixedWidth(35)
        self.number_label.setStyleSheet("color: white; border: none; font-size: 14px;")
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        self.layout.addWidget(self.number_label)
        
        self.color = QLabel()
        self.color.setStyleSheet("border: 1px solid black; border-radius: 2px;")
        self.color.setFixedSize(30, 30)
        self.layout.addWidget(self.color)
        self.color.show()

        self.color_value = QLabel()
        self.color_value.setStyleSheet("color: white; border: none; font-size: 14px;")
        self.layout.addWidget(self.color_value)

        #self.layout.addStretch()

    def set_number(self, number):
        self.number_label.setText(number)

    def set_color(self, color, number):
        r, g, b = color
        self.set_number(number)

        self.color_value.setText(', '.join(str(int(c)) for c in color))
        
        self.color.setStyleSheet(f"background-color: rgb({r},{g},{b}); border: 1px solid black; border-radius: 2px;")
