from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit,
    QSizePolicy
)
from PyQt6.QtCore import Qt
from main.styles.styles import AppStyles
from main.components.plot_data import PulseGraph


class LogsSection(QGroupBox):
    def __init__(self):
        super().__init__("Logs de la Aplicación")
        self.setStyleSheet(AppStyles.groupbox_style("#e67e22"))

        layout = QVBoxLayout()

        self.logs_area = QTextEdit()
        self.logs_area.setReadOnly(True)
        self.logs_area.setPlaceholderText("Aquí aparecerán los mensajes...")
        self.logs_area.setStyleSheet(AppStyles.LOG_AREA_STYLE)
        self.logs_area.setMinimumHeight(200)
        self.logs_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        command_row = QHBoxLayout()
        command_label = QLabel("Enviar comando:")
        command_label.setStyleSheet(AppStyles.LABEL_STYLE)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Escribe un comando...")
        self.command_input.setStyleSheet(AppStyles.INPUT_FIELD_STYLE)

        self.send_btn = QPushButton("Enviar")
        self.send_btn.setStyleSheet(AppStyles.ACTION_BUTTON)
        self.clear_btn = QPushButton("Limpiar Logs")
        self.clear_btn.setStyleSheet(AppStyles.ACTION_BUTTON)

        command_row.addWidget(command_label)
        command_row.addWidget(self.command_input)
        command_row.addWidget(self.send_btn)
        command_row.addWidget(self.clear_btn)

        layout.addWidget(self.logs_area)
        layout.addLayout(command_row)
        self.setLayout(layout)
