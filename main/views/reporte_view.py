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


from main.views.sections.resumen_section import ResumenSectionBox
from main.views.sections.plot_dinamic import DynamicPlotGroupBox
from main.views.sections.logs_section import LogsSection
from main.views.sections.sesion_select import SessionSelectorBox

from main.components.header_view import HeaderWidget
from main.utils.resource_path import get_resource_path
from main.utils.logger import Logger



from reportlab.lib.units import inch, mm  # Añade esto con los otros imports
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from main.components.pdf_builder import PDFBuilder  # La clase que te proporcioné





from PyQt6.QtCore import QTimer
import pandas as pd
from typing import List, Dict, Optional
import numpy as np

from main.views.sections.plot_dinamic import DynamicMultiPlot
from main.core.event_logger import EventType, EventLogger, DeviceID




# from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget)
# from PyQt6.QtCore import pyqtSignal
# from main.views.base_view import BaseView
# from main.components.header_view import HeaderWidget
# from main.utils.resource_path import get_resource_path
# from main.utils.logger import Logger
# from main.enums import DeviceID, EventType

class ReporteView(BaseView):
    def __init__(self, event_logger=None, parent=None):
        super().__init__(event_logger=event_logger, parent=parent)
        self.logger = Logger("ReporteView")
        self.plotter = None
        self.setup_connections()

    def setup_ui(self):
        """Configuración completa de la interfaz de usuario"""
        try:
            self.layout.setContentsMargins(5, 5, 5, 5)
            self.layout.setSpacing(10)
            
            # Configurar header
            self.setup_header()
            
            # Configurar contenido principal
            self.setup_content()
            
            self.logger.info("Vista de reportes configurada correctamente")
        except Exception as e:
            self.logger.error(f"Error configurando UI: {str(e)}")
            raise

    def setup_header(self):
        """Configura el encabezado con logo y título"""
        try:
            logo_path = get_resource_path("presitec-logo_01.png")
            self.header = HeaderWidget(
                title="REPORTE - SKINNER",
                logo_path=logo_path if QPixmap(logo_path).isNull() else None,
                logo_url="https://presitec.pe",
                title_font_size=20,
                parent=self
            )
            self.layout.addWidget(self.header)
        except Exception as e:
            self.logger.error(f"Error configurando header: {str(e)}")

    def setup_content(self):
        """Configura el área de contenido principal"""
        try:
            # Layout principal
            content_layout = QVBoxLayout()
            
            # Sección superior (selector, gráfico, resumen)
            top_section = self.create_top_section()
            
            # Sección inferior (logs)
            bottom_section = self.create_bottom_section()
            
            content_layout.addLayout(top_section)
            content_layout.addLayout(bottom_section)
            
            # Widget contenedor
            content_widget = QWidget()
            content_widget.setLayout(content_layout)
            self.layout.addWidget(content_widget)
            
        except Exception as e:
            self.logger.error(f"Error configurando contenido: {str(e)}")

    def create_top_section(self):
        """Crea la sección superior con gráfico y controles"""
        top_layout = QHBoxLayout()
        
        # Selector de sesión (20% ancho)
        self.session_selector = SessionSelectorBox()
        
        # Gráfico dinámico (60% ancho)
        self.plot_group = DynamicPlotGroupBox("Comportamiento en Sesión")
        
        # Resumen estadístico (20% ancho)
        self.summary_box = ResumenSectionBox()
        
        top_layout.addWidget(self.session_selector, 2)
        top_layout.addWidget(self.plot_group, 6)
        top_layout.addWidget(self.summary_box, 2)
        
        return top_layout

    def create_bottom_section(self):
        """Crea la sección inferior con logs y controles"""
        bottom_layout = QHBoxLayout()
        self.log_section = LogsSection()
        bottom_layout.addWidget(self.log_section)
        return bottom_layout

    def setup_connections(self):
        """Configura todas las conexiones de señales"""
        try:
            # Botón de generación de PDF
            self.log_section.btn_pdf.clicked.connect(self.generate_pdf_report)
            
            # Selección de sesión histórica
            if hasattr(self.session_selector, 'session_selected'):
                self.session_selector.session_selected.connect(self.load_historical_session)
                
        except Exception as e:
            self.logger.error(f"Error configurando conexiones: {str(e)}")

    def refresh_data(self, session_data=None):
        """
        Actualiza la vista con datos de sesión.
        Si no se proporcionan datos, usa los últimos disponibles.
        """
        if session_data is not None:
            self.current_session_data = session_data
            
        if self.current_session_data:
            try:
                self._update_plots(self.current_session_data)
                self._update_summary(self.current_session_data)
                self._update_logs(self.current_session_data)
            except Exception as e:
                self.logger.error(f"Error actualizando reporte: {str(e)}")
        else:
            self.logger.warning("No hay datos de sesión para mostrar")
            # Opcional: Mostrar mensaje al usuario o vista vacía

    def _update_plots(self, session_data: dict):
        """Actualiza los gráficos con datos de la sesión"""
        if not hasattr(self.plot_group, 'plot_widget'):
            return
            
        plot = self.plot_group.plot_widget
        plot.reset_plot()
        
        # Configurar series básicas
        plot.add_series("Palanca 01", color="#e74c3c")
        plot.add_series("Palanca 02", color="#3498db")
        plot.add_series("Recompensas", color="#2ecc71", line_style="dashed", symbol="d")
        
        # Añadir datos
        plot.add_data("Palanca 01", 
                    session_data.get("lever1_times", []),
                    session_data.get("lever1_presses", []))
        
        plot.add_data("Palanca 02",
                    session_data.get("lever2_times", []),
                    session_data.get("lever2_presses", []))
        
        reward_times = session_data.get("reward_times", [])
        if reward_times:
            plot.add_data("Recompensas", reward_times, [1]*len(reward_times))
        
        # Ajustar ejes
        max_time = session_data.get("duration", 10)
        plot.set_ranges(x_range=(0, max_time + 5), y_range=(-0.5, 1.5))

    def _update_summary(self, session_data: dict):
        """Actualiza el resumen estadístico"""
        if not hasattr(self.summary_box, 'update_data'):
            return
            
        self.summary_box.update_data({
            "session_id": session_data.get("session_id", 0),
            "duration": session_data.get("duration", 0),
            "lever1_presses": len(session_data.get("lever1_presses", [])),
            "lever2_presses": len(session_data.get("lever2_presses", [])),
            "rewards": len(session_data.get("reward_times", [])),
            "start_time": session_data.get("metadata", {}).get("start_time", "N/A")
        })

    def _update_logs(self, session_data: dict):
        """Actualiza la sección de logs"""
        if not hasattr(self.log_section, 'update_logs'):
            return
            
        log_lines = [
            f"Sesión {session_data.get('session_id', 'N/A')}",
            f"Duración: {session_data.get('duration', 0):.2f} segundos",
            "--- Eventos ---",
            f"Palanca 01: {len(session_data.get('lever1_presses', []))} activaciones",
            f"Palanca 02: {len(session_data.get('lever2_presses', []))} activaciones",
            f"Recompensas: {len(session_data.get('reward_times', []))} entregas"
        ]
        
        self.log_section.update_logs("\n".join(log_lines))

    def load_historical_session(self, session_id: int):
        """Carga datos de una sesión histórica"""
        if not self.event_logger:
            return
            
        try:
            events = self.event_logger.get_events(sessions=[session_id])
            metadata = self.event_logger.get_session_metadata(session_id)
            
            session_data = {
                "session_id": session_id,
                "duration": events["elapsed_sec"].max() if not events.empty else 0,
                "metadata": metadata,
                "lever1_presses": self._extract_events(events, DeviceID.LEVER_01),
                "lever2_presses": self._extract_events(events, DeviceID.LEVER_02),
                "reward_times": self._extract_rewards(events)
            }
            
            self.refresh_data(session_data)
        except Exception as e:
            self.logger.error(f"Error cargando sesión histórica: {str(e)}")

    def _extract_events(self, events_df, device_id):
        """Extrae tiempos y valores de eventos de palanca"""
        lever_events = events_df[
            (events_df["device_id"] == device_id.name) & 
            (events_df["event_type"] == EventType.LEVER_PRESS.name)
        ]
        return {
            "times": lever_events["elapsed_sec"].astype(float).tolist(),
            "values": lever_events["new_value"].tolist()
        }

    def _extract_rewards(self, events_df):
        """Extrae tiempos de recompensas"""
        reward_events = events_df[
            events_df["event_type"].isin([
                EventType.FOOD_DISPENSE.name, 
                EventType.FOOD_RECOMPENSE.name
            ])
        ]
        return reward_events["elapsed_sec"].astype(float).tolist()

    def generate_pdf_report(self):
        """Genera un reporte PDF de la sesión actual"""
        try:
            # Implementación de generación de PDF aquí
            pass
        except Exception as e:
            self.logger.error(f"Error generando PDF: {str(e)}")
            
           
# from PyQt6.QtWidgets import (QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, 
#                             QMessageBox, QTableWidget, QTableWidgetItem)
# from PyQt6.QtCore import QDateTime
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors


# class ReporteView(BaseView):
#     def __init__(self, event_logger: EventLogger = None, parent=None):
#         super().__init__(event_logger=event_logger, parent=parent)
#         self.setup_ui()
#         self.setup_connections()
        
        
#     def setup_ui(self):
#         """Configura la interfaz de usuario"""
#         try:
#             self.layout.setContentsMargins(5, 5, 5, 5)
#             self.layout.setSpacing(10)
#             self.setup_header()
#             self.setup_content()
            
#             self.logger.info("Vista de reportes configurada correctamente")
#         except Exception as e:
#             self.logger.error(f"Error al configurar vista de reportes: {str(e)}")
#             raise

#     def setup_header(self):
#         """Configura la sección del encabezado"""
#         try:
#             logo_path = get_resource_path("presitec-logo_01.png")
#             self.header = HeaderWidget(
#                 title="REPORTE - SKINNER",
#                 logo_path=logo_path if QPixmap(logo_path).isNull() else None,
#                 logo_url="https://presitec.pe/index.php/nosotros/",
#                 title_font_size=20,
#                 parent=self
#             )
#             self.layout.addWidget(self.header)
#         except Exception as e:
#             self.logger.error(f"Error al configurar header: {str(e)}")
#             raise
        
#     def setup_content(self):
#         """Configura el contenido principal con gráficos y selectores"""
#         try:
#             # Layout principal
#             main_layout = QVBoxLayout()
            
#             # Sección superior: Selector + Gráfico + Indicadores
#             top_layout = QHBoxLayout()
#             top_layout.setContentsMargins(0, 0, 0, 0)
#             top_layout.setSpacing(10)
            
#             # Componentes principales
#             self.session_selector = SessionSelectorBox()
#             self.plot_group = DynamicPlotGroupBox("Comportamiento en Sesión")
#             self.info_table = self._create_info_table()
            
#             top_layout.addWidget(self.session_selector, stretch=1)
#             top_layout.addWidget(self.plot_group, stretch=4)
#             top_layout.addWidget(self.info_table, stretch=1)
            
#             # Sección inferior: Logs y controles
#             bot_layout = QHBoxLayout()
#             self.log_box = LogsSection()
#             bot_layout.addWidget(self.log_box)
            
#             # Contenedores
#             top_container = QWidget()
#             top_container.setLayout(top_layout)
            
#             bot_container = QWidget()
#             bot_container.setLayout(bot_layout)
            
#             main_layout.addWidget(top_container, stretch=4)
#             main_layout.addWidget(bot_container, stretch=1)
            
#             self.layout.addLayout(main_layout)
            
#         except Exception as e:
#             self.logger.error(f"Error al configurar contenido: {str(e)}")
#             raise

#     def _create_info_table(self):
#         """Crea la tabla de información de sesión"""
#         table = QTableWidget()
#         table.setColumnCount(2)
#         table.setRowCount(8)
#         table.setHorizontalHeaderLabels(["Indicador", "Valor"])
#         table.verticalHeader().setVisible(False)
#         table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
#         # Configurar items de la tabla
#         indicators = [
#             ("ID Sesión", "N/A"),
#             ("Inicio", "--:--:--"),
#             ("Fin", "--:--:--"),
#             ("Duración", "00:00:00"),
#             ("Palanca 01", "0"),
#             ("Palanca 02", "0"),
#             ("Recompensas", "0"),
#             ("Estado", "Inactivo")
#         ]
        
#         for row, (label, value) in enumerate(indicators):
#             table.setItem(row, 0, QTableWidgetItem(label))
#             table.setItem(row, 1, QTableWidgetItem(value))
        
#         table.resizeColumnsToContents()
#         return table

#     def setup_connections(self):
#         """Configura las conexiones de señales"""
#         self.session_selector.session_selected.connect(self.load_session_data)
#         self.log_box.btn_pdf.clicked.connect(self.generate_pdf_report)
#         self.log_box.btn_csv.clicked.connect(self.export_to_csv)
        
#     def load_session_data(self, session_id: int):
#         """Carga los datos de una sesión específica"""
#         if not session_id:
#             return
            
#         # Obtener eventos de la sesión
#         events = self.event_logger.get_events(sessions=[session_id])
#         metadata = self.event_logger.get_session_metadata(session_id)
        
#         # Actualizar gráfico
#         self.plot_group.plot_session_data(session_id)
        
#         # Actualizar tabla de información
#         self._update_info_table(session_id, events, metadata)
        
#         # Actualizar logs
#         self.log_box.logs_area.append(f"Cargada sesión {session_id}")

#     def _update_info_table(self, session_id: int, events: pd.DataFrame, metadata: dict):
#         """Actualiza la tabla con información de la sesión"""
#         # Calcular estadísticas
#         lever_01 = len(events[events['device_id']] == DeviceID.LEVER_01.name)
#         lever_02 = len(events[events['device_id']] == DeviceID.LEVER_02.name)
#         rewards = len(events[events['device_id']] == DeviceID.RECOMPENSA.name)
        
#         # Obtener tiempos de sesión
#         session_events = self.event_logger.get_events(sessions=[session_id])
#         start_time = session_events['timestamp'].min()
#         end_time = session_events['timestamp'].max()
#         duration = end_time - start_time if not pd.isna(start_time) else pd.NaT
        
#         # Actualizar tabla
#         self.info_table.item(0, 1).setText(str(session_id))
#         self.info_table.item(1, 1).setText(str(start_time))
#         self.info_table.item(2, 1).setText(str(end_time))
#         self.info_table.item(3, 1).setText(str(duration))
#         self.info_table.item(4, 1).setText(str(lever_01))
#         self.info_table.item(5, 1).setText(str(lever_02))
#         self.info_table.item(6, 1).setText(str(rewards))
#         self.info_table.item(7, 1).setText("Completada" if not pd.isna(end_time) else "En progreso")

#     def generate_pdf_report(self):
#         """Genera un reporte PDF con los datos actuales"""
#         filename, _ = QFileDialog.getSaveFileName(
#             self, "Guardar Reporte PDF", 
#             "reporte_skinner.pdf", 
#             "PDF Files (*.pdf)")
        
#         if not filename:
#             return
            
#         if not filename.lower().endswith('.pdf'):
#             filename += '.pdf'
        
#         try:
#             pdf = PDFBuilder(
#                 title="Reporte de Sesión Skinner",
#                 author="Sistema de Monitoreo",
#                 page_size=A4
#             )
            
#             # Configuración básica
#             curr_date = QDateTime.currentDateTime().toString("dd/MM/yyyy - HH:mm:ss")
#             pdf.set_header(text=curr_date)
#             pdf.set_footer(text="Skinner v2.0 - Presitec")
            
#             # 1. Información general
#             pdf.add_title("Reporte de Sesión Experimental")
#             pdf.add_form_field("Fecha del Reporte", curr_date)
            
#             # 2. Datos de la sesión actual
#             selected_session = self.session_selector.current_session()
#             if selected_session:
#                 pdf.add_section(f"Datos de la Sesión {selected_session}")
#                 self._add_session_info_to_pdf(pdf, selected_session)
            
#             # 3. Gráfico
#             pdf.add_section("Gráfico de Comportamiento")
#             pdf.add_widget_as_image(
#                 self.plot_group.plot,
#                 width="16cm",
#                 height="8cm",
#                 caption="Comportamiento registrado durante la sesión"
#             )
            
#             # 4. Tabla de eventos
#             pdf.add_section("Resumen de Eventos")
#             self._add_events_table_to_pdf(pdf)
            
#             # 5. Observaciones
#             pdf.add_section("Observaciones")
#             pdf.add_text(self.log_box.logs_area.toPlainText() or "Sin observaciones registradas")
            
#             # Generar PDF
#             pdf.build(filename)
            
#             QMessageBox.information(
#                 self, "Éxito", 
#                 f"Reporte generado correctamente:\n{filename}")
                
#         except Exception as e:
#             QMessageBox.critical(
#                 self, "Error", 
#                 f"Error al generar PDF:\n{str(e)}")
#             self.logger.error(f"Error al generar PDF: {str(e)}")

#     def _add_session_info_to_pdf(self, pdf: PDFBuilder, session_id: int):
#         """Añade información detallada de la sesión al PDF"""
#         metadata = self.event_logger.get_session_metadata(session_id)
#         events = self.event_logger.get_events(sessions=[session_id])
        
#         # Datos básicos
#         pdf.add_form_field("ID Sesión", str(session_id))
#         pdf.add_form_field("Sujeto", metadata.get('subject', 'Desconocido'))
#         pdf.add_form_field("Condición", metadata.get('condition', 'No especificada'))
        
#         # Estadísticas
#         lever_01 = len(events[events['device_id'] == DeviceID.LEVER_01.name])
#         lever_02 = len(events[events['device_id'] == DeviceID.LEVER_02.name])
#         rewards = len(events[events['device_id'] == DeviceID.RECOMPENSA.name])
        
#         pdf.add_form_field("Presiones Palanca 01", str(lever_01))
#         pdf.add_form_field("Presiones Palanca 02", str(lever_02))
#         pdf.add_form_field("Recompensas entregadas", str(rewards))

#     def _add_events_table_to_pdf(self, pdf: PDFBuilder):
#         """Añade una tabla con los eventos al PDF"""
#         selected_session = self.session_selector.current_session()
#         if not selected_session:
#             return
            
#         events = self.event_logger.get_events(sessions=[selected_session])
        
#         # Preparar datos para la tabla
#         table_data = [["Hora", "Evento", "Dispositivo", "Valor"]]
        
#         for _, event in events.iterrows():
#             table_data.append([
#                 str(event['timestamp']),
#                 event['event_type'],
#                 event['device_id'],
#                 str(event['new_value'])
#             ])
        
#         # Añadir tabla al PDF
#         pdf.add_table(
#             data=table_data,
#             col_widths=["3cm", "4cm", "3cm", "2cm"],
#             style=[
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#005588')),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 8),
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey)
#             ]
#         )

#     def export_to_csv(self):
#         """Exporta los datos de la sesión actual a CSV"""
#         selected_session = self.session_selector.current_session()
#         if not selected_session:
#             QMessageBox.warning(self, "Advertencia", "No hay sesión seleccionada")
#             return
            
#         filename, _ = QFileDialog.getSaveFileName(
#             self, "Exportar datos CSV", 
#             f"sesion_{selected_session}_datos.csv", 
#             "CSV Files (*.csv)")
        
#         if filename:
#             try:
#                 self.event_logger.save_to_csv(filename)
#                 QMessageBox.information(
#                     self, "Éxito", 
#                     f"Datos exportados correctamente a:\n{filename}")
#             except Exception as e:
#                 QMessageBox.critical(
#                     self, "Error", 
#                     f"Error al exportar CSV:\n{str(e)}")
#                 self.logger.error(f"Error al exportar CSV: {str(e)}")

#     def refresh_data(self):
#         """Actualiza los datos mostrados en la vista"""
#         self.session_selector.refresh_sessions(self.event_logger.get_all_sessions())
#         if self.session_selector.current_session():
#             self.load_session_data(self.session_selector.current_session())