

from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt
from main.styles.styles import AppStyles

class AcctionsSectionBox(QGroupBox):
    def __init__(self):
        super().__init__("Acciones")
        self.setStyleSheet(AppStyles.groupbox_style("#3498db"))
        self._init_ui()
    
    def _init_ui(self): 
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(15)
        
        # Botón principal con estilo moderno
        self.btn_report = QPushButton("Generar Reporte")
        self.btn_report.setStyleSheet(AppStyles.BUTTON_STYLE_MODERN)
        self.btn_report.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Botón secundario con estilo alternativo
        self.btn_export = QPushButton("Exportar CSV")
        self.btn_export.setStyleSheet(AppStyles.BUTTON_STYLE_ALT)
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Añadir íconos (opcional)
        from PyQt6.QtGui import QIcon
        try:
            self.btn_report.setIcon(QIcon(":/icons/report.png"))
            self.btn_export.setIcon(QIcon(":/icons/export.png"))
        except:
            pass  # Si no hay íconos, continuar sin ellos
        
        # Configurar tamaño mínimo
        self.btn_report.setMinimumWidth(140)
        self.btn_export.setMinimumWidth(140)
        
        # Layout con alineación centrada
        layout.addStretch()
        layout.addWidget(self.btn_report, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.btn_export, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
        
        self.setLayout(layout)