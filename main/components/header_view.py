from PyQt6.QtWidgets import (
    QLabel, QWidget, QHBoxLayout, 
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QDesktopServices, QCursor, QFont

class ClickableLabel(QLabel):
    """QLabel personalizado que funciona como botón"""
    def __init__(self, url="", parent=None):
        super().__init__(parent)
        self.url = url
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Eliminamos la transición CSS no soportada
        self.setStyleSheet("""
            ClickableLabel:hover {
                opacity: 0.8;
            }
        """)

    def mousePressEvent(self, event):
        if self.url and event.button() == Qt.MouseButton.LeftButton:
            QDesktopServices.openUrl(QUrl(self.url))

class HeaderWidget(QWidget):
    """Widget de cabecera reutilizable con título y logo"""
    def __init__(self, 
                 title: str = "", 
                 logo_path: str = None, 
                 logo_url: str = None,
                 title_font_size: int = 20,
                 parent=None):
        super().__init__(parent)
        self.setup_ui(title, logo_path, logo_url, title_font_size)
        
    def setup_ui(self, title, logo_path, logo_url, title_font_size):
        # Layout principal
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 0)
        self.layout.setSpacing(0)

        # ---------- Logo a la derecha ----------
        self.logo_label = None
        if logo_path:
            self.logo_label = ClickableLabel(logo_url, self)
            logo_pixmap = QPixmap(logo_path).scaled(180, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(logo_pixmap)
            self.logo_label.setFixedSize(180, 40)
        else:
            self.logo_label = QWidget()  # placeholder invisible
            self.logo_label.setFixedWidth(180)

        # ---------- Título centrado ----------
        self.title_label = QLabel(title)
        self.title_label.setObjectName("HeaderTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", title_font_size, QFont.Weight.Bold)
        title_font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 105)
        self.title_label.setFont(title_font)

        # ---------- Espaciadores y orden ----------
        self.layout.addStretch(2)                       # Izquierdo
        self.layout.addWidget(self.title_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.layout.addStretch(1)                       # Derecho
        self.layout.addWidget(self.logo_label, 0, Qt.AlignmentFlag.AlignRight)

        # ---------- Estilos ----------
        self.setStyleSheet("""
            #HeaderTitle {
                color: #2c3e50;
                padding: 5px 10px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
            QWidget {
                background-color: transparent;
            }
        """)


    def set_logo(self, path: str, url: str = None, width: int = 180, height: int = 40):
        """Configura o actualiza el logo con tamaño personalizable"""
        if not hasattr(self, 'logo_label'):
            self.logo_label = ClickableLabel(url, self)
            self.layout.addWidget(self.logo_label)
            self.layout.addStretch(1)  # Añade stretch después del logo
        
        logo_pixmap = QPixmap(path)
        self.logo_label.setPixmap(logo_pixmap.scaled(
            width, height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self.logo_label.url = url  # Actualiza URL si se proporciona