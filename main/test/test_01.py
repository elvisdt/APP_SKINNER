# main_demo.py

import sys
from enum import Enum
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt6.QtCore import pyqtSignal, Qt

# Enum para las páginas
class PageEnum(Enum):
    HOME = 1
    SETTINGS = 2
    ABOUT = 3

# Menú lateral con señal
class SideMenu(QWidget):
    page_selected = pyqtSignal(PageEnum)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.setStyleSheet("background-color: #EB3A17;")

        # Botones
        self.home_btn = QPushButton("Home")
        self.settings_btn = QPushButton("Settings")
        self.about_btn = QPushButton("About")

        for btn in [self.home_btn, self.settings_btn, self.about_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: #34495e;
                    border: none;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #3b5998;
                }
            """)
            layout.addWidget(btn)

        self.setLayout(layout)

        # Conexiones
        self.home_btn.clicked.connect(lambda: self.page_selected.emit(PageEnum.HOME))
        self.settings_btn.clicked.connect(lambda: self.page_selected.emit(PageEnum.SETTINGS))
        self.about_btn.clicked.connect(lambda: self.page_selected.emit(PageEnum.ABOUT))

# Ventana principal
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo MainWindow + SideMenu")
        self.resize(800, 600)

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Side Menu
        self.side_menu = SideMenu()
        self.side_menu.page_selected.connect(self.load_page)
        layout.addWidget(self.side_menu)

        # Área principal
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_label = QLabel("Página inicial")
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_label.setStyleSheet("font-size: 24px; color: #333;")
        self.content_layout.addWidget(self.content_label)
        layout.addWidget(self.content)

        self.setCentralWidget(central)

    def load_page(self, page: PageEnum):
        print(f"Página seleccionada: {page.name}")
        self.content_label.setText(f"Página actual: {page.name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
