import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtGui import QPalette, QColor

from main.views.sections.program_section import ProgramControlBox


def main():
    app = QApplication(sys.argv)

    # Establecer fondo claro para toda la app
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f8f9fa"))  # gris muy claro
    app.setPalette(palette)

    # Crear ventana principal
    window = QWidget()
    window.setWindowTitle("Test Program Control Box")

    layout = QVBoxLayout()
    program_box = ProgramControlBox()
    layout.addWidget(program_box)

    program_box.btn_start.setEnabled(False)
    window.setLayout(layout)
    window.resize(500, 150)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
