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
        super().__init__("Observacion")
        self.setStyleSheet(AppStyles.groupbox_style("#e67e22"))

        layout = QHBoxLayout()

        self.logs_area = QTextEdit()
        #self.logs_area.setReadOnly(True)
        self.logs_area.setPlaceholderText("Escribir aquì su observaciòn o comentario...")
        self.logs_area.setStyleSheet(AppStyles.LOG_AREA_STYLE)
        self.logs_area.setMinimumHeight(100)
        self.logs_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        command_row = QVBoxLayout()
        self.btn_pdf = QPushButton("Exportar PDF")
        self.btn_pdf.setStyleSheet(AppStyles.ACTION_BUTTON)
        self.btn_clear = QPushButton("Limpiar Logs")
        self.btn_clear.setStyleSheet(AppStyles.ACTION_BUTTON)

        command_row.addWidget(self.btn_pdf)
        command_row.addWidget(self.btn_clear)

        layout.addWidget(self.logs_area)
        layout.addLayout(command_row)
        
        layout.setStretch(0, 4)  # top_container
        layout.setStretch(1, 1)  # bot_container
        
        self.setLayout(layout)
