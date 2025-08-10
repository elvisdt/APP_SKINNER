import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtGui import QPalette, QColor

from main.views.sections.plot_section import PlotGroupBox



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
    program_box = PlotGroupBox()
    layout.addWidget(program_box)

    window.setLayout(layout)
    window.resize(600, 400)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
