from PyQt6.QtWidgets import (
    QLabel, QWidget, QVBoxLayout, 
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QFont

from main.styles.styles import AppStyles
from main.views.base_view import BaseView
from main.components.header_view import HeaderWidget
from main.utils.resource_path import get_resource_path
from main.utils.logger import Logger

class InicioView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger(__name__)
        

    def setup_ui(self):
        """Configura la interfaz de usuario de la vista de inicio"""
        try:
            # ───── CONFIGURACIÓN INICIAL ─────
            self.layout.setContentsMargins(20, 10, 20, 20)
            self.layout.setSpacing(15)
            self.setup_header()
            self.setup_content()
            # self.setup_footer()
            
            self.logger.info("Vista de inicio configurada correctamente")
        except Exception as e:
            self.logger.error(f"Error al configurar vista de inicio: {str(e)}")
            raise

    def setup_header(self):
        """Configura la sección del encabezado"""
        try:
            logo_path = get_resource_path("presitec-logo_01.png")
            if not QPixmap(logo_path).isNull():
                self.header = HeaderWidget(
                    title="SKINNER SOFTWARE",
                    logo_path=logo_path,
                    logo_url="https://presitec.pe/index.php/nosotros/",
                    title_font_size=22,
                    parent=self
                )
            else:
                self.header = HeaderWidget(
                    title="SKINNER SOFTWARE",
                    title_font_size=22,
                    parent=self
                )
                self.logger.warning("No se encontró el archivo de logo")
            
            self.layout.addWidget(self.header)
        except Exception as e:
            self.logger.error(f"Error al configurar header: {str(e)}")
            raise

    def setup_content(self):
        """Configura el contenido principal"""
        try:
            # ───── DESCRIPCIÓN PRINCIPAL ─────
            short_desc = QLabel(
                "Dispositivo experimental utilizado para el estudio del comportamiento "
                "operante bajo condiciones controladas."
            )
            short_desc.setObjectName("ShortDescription")
            short_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            short_desc.setWordWrap(True)
            short_desc.setStyleSheet(AppStyles.SHORT_DESCRIPTION)
            self.layout.addWidget(short_desc)

            # ───── IMAGEN CENTRAL ─────
            image_path = get_resource_path("maquina.jpg")
            if QPixmap(image_path).isNull():
                self.logger.warning("No se encontró la imagen principal")
                image_path = get_resource_path("default-image.png")
            
            image_label = QLabel()
            image_label.setObjectName("MainImage")
            original_pixmap = QPixmap(image_path)
            scaled_pixmap = original_pixmap.scaled(
                400, 300, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            image_label.setPixmap(self.rounded_pixmap(scaled_pixmap, 20))
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

            # ───── DESCRIPCIÓN SECUNDARIA ─────
            subtitle = QLabel(
                "La caja de Skinner permite implementar protocolos de reforzamiento "
                "y registrar datos conductuales de forma precisa y automatizada."
            )
            subtitle.setObjectName("Subtitle")
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle.setWordWrap(True)
            subtitle.setStyleSheet(AppStyles.LABEL_STYLE)
            self.layout.addWidget(subtitle)
        except Exception as e:
            self.logger.error(f"Error al configurar contenido: {str(e)}")
            raise

    def setup_footer(self):
        """Configura el pie de página"""
        try:
            # ───── ESPACIADOR FINAL ─────
            self.layout.addSpacerItem(
                QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            )
        except Exception as e:
            self.logger.error(f"Error al configurar footer: {str(e)}")
            raise

    def rounded_pixmap(self, pixmap: QPixmap, radius: int) -> QPixmap:
        """Crea una imagen con bordes redondeados"""
        try:
            rounded = QPixmap(pixmap.size())
            rounded.fill(Qt.GlobalColor.transparent)

            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            path = QPainterPath()
            path.addRoundedRect(QRectF(0, 0, pixmap.width(), pixmap.height()), radius, radius)

            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            return rounded
        except Exception as e:
            self.logger.error(f"Error al crear imagen redondeada: {str(e)}")
            return pixmap  # Retorna la imagen original si hay error

    def refresh_data(self):
        """Actualiza los datos de la vista"""
        pass
    
    def clear_view(self):
        """Limpia la vista"""
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()