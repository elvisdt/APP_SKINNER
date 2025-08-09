from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt
from main.styles.styles import AppStyles


class UartSection(QGroupBox):
    def __init__(self, ports: list[str] = None):
        super().__init__("Conexión UART: Desconectado")
        self.setStyleSheet(AppStyles.groupbox_style("#3498db"))
        self._init_ui()
        if ports:
            self.update_list_port(ports)
            self.port_input.setEnabled(True)
            self.connect_btn.setEnabled(True)
        else:
            self.port_input.setEnabled(False)
            self.connect_btn.setEnabled(False)
        
        
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Label
        port_label = QLabel("Puerto:")
        port_label.setStyleSheet(AppStyles.LABEL_STYLE)

        # ComboBox
        self.port_input = QComboBox()
        self.port_input.setStyleSheet(AppStyles.CMBOX_PLNC_STYLE)
        self.port_input.setMinimumWidth(120)
        self.port_input.setMaximumWidth(200)

        # Botón conectar
        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.setStyleSheet(AppStyles.BUTTON_START)
        self.connect_btn.setMinimumSize(150, 30)

        # Layouts
        port_layout = QHBoxLayout()
        port_layout.addStretch()
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        port_layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.connect_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addLayout(port_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def update_uart_status(self, connected: bool):
        estado = "Conectado" if connected else "Desconectado"
        if connected:
            self.port_input.setEnabled(False)
            self.port_input.setStyleSheet(AppStyles.CMBOX_STYLE_DISABLED)
            self.connect_btn.setText("Desconectar")
            self.connect_btn.setStyleSheet(AppStyles.BUTTON_STOP)
        else:
            self.port_input.setEnabled(True)
            self.port_input.setStyleSheet(AppStyles.CMBOX_PLNC_STYLE)
            self.connect_btn.setText("Conectar")
            self.connect_btn.setStyleSheet(AppStyles.BUTTON_START)
            
        self.setTitle(f"Conexión UART: {estado}")
        
        
    def update_list_port(self, ports: list[str]):
        self.port_input.clear()
        if ports:
            self.port_input.addItems(ports)
            self.port_input.setEnabled(True)
            self.connect_btn.setEnabled(True)
            
        else:
            self.port_input.setEnabled(False)
            self.connect_btn.setEnabled(False)
            



