from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QFont

from fpdf import FPDF
from PyQt6.QtCore import QTimer, QTime, QDateTime


import csv

from main.views.base_view import BaseView
from main.styles.styles import AppStyles

from PyQt6.QtSerialPort import QSerialPort

from main.enums.indicators_enum import IndicatorKey
from main.core.serial_port_model import SerialPortModel

from main.views.sections.acctions_section import AcctionsSectionBox
from main.views.sections.indicators_section import IndicatorsSectionBox
from main.views.sections.plot_section import PlotGroupBox
from main.views.sections.logs_section import LogsSection
from main.views.sections.uart_section import UartSection

from main.components.header_view import HeaderWidget
from main.utils.resource_path import get_resource_path
from main.utils.logger import Logger


#--------------------------------------------------------------##

##-------------------------------------------------------------##
class ReporteView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger(__name__)
        

    def setup_ui(self):
        """Configura la interfaz de usuario de la vista de inicio"""
        try:
            # ───── CONFIGURACIÓN INICIAL ─────
            self.layout.setContentsMargins(5, 5, 5, 5)
            self.layout.setSpacing(10)
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
                    title="REPORTE - SKINNER",
                    logo_path=logo_path,
                    logo_url="https://presitec.pe/index.php/nosotros/",
                    title_font_size=20,
                    parent=self
                )
            else:
                self.header = HeaderWidget(
                    title="REPORTE - SKINNER",
                    title_font_size=20,
                    parent=self
                )
                self.logger.warning("No se encontro el archivo de logo")
            
            self.layout.addWidget(self.header)
        except Exception as e:
            self.logger.error(f"Error al configurar header: {str(e)}")
            raise
        
    def setup_content(self):
        """Configura el contenido principal"""
        try:
        
            # ───── TOP LAYOUT ─────
            top_layout = QHBoxLayout()
            top_layout.setContentsMargins(0, 0, 0, 0)
            top_layout.setSpacing(5)
            
            
            # p_layout = QVBoxLayout()
            # p_layout.setContentsMargins(0, 0, 0, 0)
            # p_layout.setSpacing(5)
            
            self.plot_g01 = PlotGroupBox()
            # self.plot_g02 = PlotGroupBox()
            self.info_group = IndicatorsSectionBox()
            self.log_box = LogsSection()
            
            # p_layout.addWidget(self.plot_g01)
            # p_layout.addWidget(self.plot_g02)
            
            top_layout.addWidget(self.plot_g01)
            top_layout.addWidget(self.info_group)


            # ───── BUTTON LAYOUT ─────
            bot_layout = QHBoxLayout()
            bot_layout.setContentsMargins(0, 0, 0, 0)
            bot_layout.setSpacing(5)

            bot_layout.addWidget(self.log_box)

            # Asignar proporciones 2:3:1
            # bot_layout.setStretch(0, 1)  # INFO
            # bot_layout.setStretch(1, 3)  # PLOT

            top_container = QWidget()
            top_container.setLayout(top_layout)
            
            bot_container = QWidget()
            bot_container.setLayout(bot_layout)
            
            self.layout.addWidget(top_container)
            self.layout.addWidget(bot_container)
            
            # Asignar proporciones 1:3
            self.layout.setStretch(0, 5)  # top_container
            self.layout.setStretch(1, 1)  # bot_container

        except Exception as e:
                self.logger.error(f"Error al configurar contenido: {str(e)}")
                raise
    
         

    
