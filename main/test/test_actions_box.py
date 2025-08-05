import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtGui import QPalette, QColor

from main.views.sections.acctions_section import AcctionsSectionBox


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
    actions_box = AcctionsSectionBox()
    layout.addWidget(actions_box)

    window.setLayout(layout)
    window.resize(500, 400)
    window.show()

    actions_box.btn_export.setEnabled(False)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
