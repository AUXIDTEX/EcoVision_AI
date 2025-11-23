from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel


class Image_Output(QWidget):
    def __init__(self, parent=None, second_col=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)
        self.current_color = 70, 130, 180  # Default color (steel blue)
        
        self.color = QLabel()
        self.color.setStyleSheet("border: 1px solid black; border-radius: 2px;")
        self.color.setFixedSize(20, 20)
        self.layout.addWidget(self.color)
        self.color.show()

        self.color_value = QLabel()
        self.color_value.setStyleSheet("color: white; border: none;")
        self.layout.addWidget(self.color_value)

    def set_color(self, color):
        r, g, b = color
        self.color_value.setText(', '.join(str(int(c)) for c in color))
        
        self.color.setStyleSheet(f"background-color: rgb({r},{g},{b}); border: 1px solid black; border-radius: 2px;")