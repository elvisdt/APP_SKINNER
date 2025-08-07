from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QFont

from fpdf import FPDF
from PyQt6.QtCore import QTimer, QTime, QDateTime
from reportlab.lib import colors  # Ya deberías tener este import

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



from reportlab.lib.units import inch, mm  # Añade esto con los otros imports
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from main.components.pdf_builder import PDFBuilder  # La clase que te proporcioné

#--------------------------------------------------------------##

##-------------------------------------------------------------##
class ReporteView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger(__name__)
        self.setup_connections()
        
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
    def setup_connections(self):
        self.log_box.btn_pdf.clicked.connect(self.generate_pdf_report)
        
    def generate_pdf_report(self):
        """Versión mejorada del generador de PDF"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte PDF", 
            "reporte_eventos.pdf", 
            "PDF Files (*.pdf)")
        
        if not filename:
            return
            
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        try:
            pdf = PDFBuilder(
                title="Reporte de Eventos",
                author="Sistema de Monitoreo",
                page_size=A4
            )
            


 
            curr_date = QDateTime.currentDateTime()

            # Formatear como "dd-MM-yyyy - HH:mm:ss"
            txt_date_time = curr_date.toString("dd/MM/yyyy - HH:mm:ss")


            pdf.set_header(text=txt_date_time)
            pdf.set_footer(text="Skinner V02")
            
            # Contenido del reporte
            pdf.add_title("Reporte de Eventos del Sistema")
            
            
            pdf.add_section("Detalles de Configuración")
            # pdf.add_text("Este reporte contiene los eventos registrados en el sistema.")
            # Campos del formulario
            pdf.add_form_field("Nombre Completo", "María García López")
            pdf.add_form_field("ID de Usuario", "123456")
            pdf.add_form_field("Àrea", "Psicología")
            pdf.add_form_field("Prueba Realizado Palanca 01", "CRC")
            pdf.add_form_field("Prueba Realizado Palanca 02", "CRC")
            pdf.add_form_field("Fecha de Inicio", txt_date_time)

            # Añadir gráfico (versión en memoria)
            pdf.add_section("Gráfico de Eventos")
            pdf.add_widget_as_image(
                self.plot_g01,
                width="16cm",  
                height="8cm",
                caption="Gráfico generado en tiempo real"
            )
            
            # Datos de ejemplo (lista de listas)
            # 1. Preparar los datos de la tabla
            indicadores = [
                ["Indicador", "Valor"],  # Encabezados
                ["ID de Sesión", "N/A"],
                ["Hora de Inicio", ""],
                ["Hora de Fin", ""],
                ["Duración", "00:00:00"],
                ["Latencia", "0 ms"],
                ["Tasa de Respuesta", "0%"],
                ["Palanca 01", "0"],
                ["Palanca 02", "0"],
                ["LED 01", "OFF"],
                ["LED 02", "OFF"],
                ["Recompensas", "0"],
                ["Intentos", "0"]
            ]

            # 2. Crear el PDF y añadir la tabla
            pdf.add_section("Indicadores del Sistema")

            # Añadir tabla con estilo personalizado
            pdf.add_table(
                data=indicadores,
                col_widths=["5cm", "3cm"],  # Anchos de columna
                style=[
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#005588')),  # Encabezado azul
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6)  # Espacio para el encabezado
                ]
            )

            
            pdf.add_section("Observaciones")
            pdf.add_text(self.log_box.logs_area.toPlainText())
            
            # Generar PDF
            pdf.build(filename)
            
            QMessageBox.information(
                self, "Éxito", 
                f"PDF generado correctamente:\n{filename}")
                
        except Exception as e:
            QMessageBox.critical(
                self, "Error", 
                f"Error al generar PDF:\n{str(e)}")
            self.logger.error(f"Error al generar PDF: {str(e)}")
           