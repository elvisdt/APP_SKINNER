# test_uart_section.py
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from main.styles.styles import AppStyles  # Asegúrate de que esta ruta sea correcta
from main.views.sections.uart_section import UartSection  # Asegúrate que el archivo se llame así

from main.core.serial_model import SerialPortModel


import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout


import sys
if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Test UART Section")
    window.setStyleSheet("background-color: #f0f0f0;")  # Fondo claro

    layout = QVBoxLayout()
    serial_model = SerialPortModel()
    uart_section = UartSection()

    # Agregar puertos ficticios al combobox
    # uart_section.port_input.addItems(["COM1", "COM2", "COM3"])

    layout.addWidget(uart_section)
    window.setLayout(layout)
    window.show()

    sys.exit(app.exec())
