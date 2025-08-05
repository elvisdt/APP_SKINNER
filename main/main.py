"""
Punto de entrada principal de la aplicación
"""
import sys
from PyQt6.QtGui import QPalette, QColor

from PyQt6.QtWidgets import QApplication
from main.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f8f9fa"))  # gris muy claro
    app.setPalette(palette)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
    
