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
from main.views.sections.program_section import ProgramControlBox
from main.views.sections.uart_section import UartSection

from main.components.header_view import HeaderWidget
from main.utils.resource_path import get_resource_path
from main.utils.logger import Logger


#--------------------------------------------------------------##
led_keys = {
    "L01": IndicatorKey.LED_01_STATE,
    "L02": IndicatorKey.LED_02_STATE,
}


value_led_map = {
    "1": "ON",
    "0": "OFF",
    "ON": "ON",
    "OFF": "OFF"
}

palanca_keys = {
    "P01": IndicatorKey.LEVER_01_COUNT,
    "P02": IndicatorKey.LEVER_02_COUNT,
}


from PyQt6.QtCore import QThread, pyqtSignal

class SerialDataWorker(QThread):
    """Hilo para procesamiento pesado de datos seriales"""
    processed_data = pyqtSignal(dict)  # Emite datos procesados
    
    def __init__(self, raw_data: str, parent=None):
        super().__init__(parent)
        self.raw_data = raw_data
        
    def run(self):
        """Procesa los datos en el hilo secundario"""
        try:
            # Normalización de delimitadores
            normalized_data = self.raw_data.replace('\r\n', '\n').replace('\r', '\n')
            
            # Procesamiento inicial (puede ser costoso)
            result = {
                'blocks': [block.strip() for block in normalized_data.split('\n') if block.strip()],
                'timestamp': QDateTime.currentDateTime().toString('hh:mm:ss.zzz')
            }
            
            self.processed_data.emit(result)
            
        except Exception as e:
            self.processed_data.emit({'error': str(e)})
            


##-------------------------------------------------------------##
class PanelControlView(BaseView):
    def __init__(self, serial_model: SerialPortModel, parent=None):
        super().__init__(parent)
        self.logger = Logger(__name__)
        self.serial_model = serial_model
        self.is_prog_running = False
        
        self.worker_thread = None
        self.pending_data = []

        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._actualizar_duracion)
        self.start_time = None
        self.end_time = None    
        self._setup_connections()
        
        self.name_plt_rh_l1="Presiones"
        self.name_plt_lf_l1="Presiones"
        
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
                    title="PANEL DE CONTROL - SKINNER",
                    logo_path=logo_path,
                    logo_url="https://presitec.pe/index.php/nosotros/",
                    title_font_size=20,
                    parent=self
                )
            else:
                self.header = HeaderWidget(
                    title="PANEL DE CONTROL - SKINNER",
                    title_font_size=20,
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
        
            # ───── TOP LAYOUT ─────
            top_layout = QHBoxLayout()
            top_layout.setContentsMargins(0, 0, 0, 0)
            top_layout.setSpacing(5)
            
            self.uart_section = UartSection()
            self.prog_section = ProgramControlBox()
            self.actions_group = AcctionsSectionBox()

            top_layout.addWidget(self.uart_section)
            top_layout.addWidget(self.prog_section)
            top_layout.addWidget(self.actions_group)
            
            # Asignar proporciones 2:3:1
            top_layout.setStretch(0, 1)  # UART
            top_layout.setStretch(1, 4)  # Programa
            top_layout.setStretch(2, 1)  # Acciones

            # ───── BUTTON LAYOUT ─────
            bot_layout = QHBoxLayout()
            bot_layout.setContentsMargins(0, 0, 0, 0)
            bot_layout.setSpacing(5)
            
            self.info_group = IndicatorsSectionBox()
            self.plt_group = PlotGroupBox()

            bot_layout.addWidget(self.info_group)
            bot_layout.addWidget(self.plt_group)
            
            
            # Asignar proporciones 2:3:1
            bot_layout.setStretch(0, 1)  # INFO
            bot_layout.setStretch(1, 3)  # PLOT
        
            
            
            top_container = QWidget()
            top_container.setLayout(top_layout)
            
            bot_container = QWidget()
            bot_container.setLayout(bot_layout)
            
            self.layout.addWidget(top_container)
            self.layout.addWidget(bot_container)
            
            # Asignar proporciones 1:3
            self.layout.setStretch(0, 1)  # top_container
            self.layout.setStretch(1, 3)  # bot_container

        except Exception as e:
                self.logger.error(f"Error al configurar contenido: {str(e)}")
                raise
    
         
    def update_uart_status(self, connected: bool):
        """Actualiza la UI según el estado de conexión"""
        self.logger.info(f"status uart Panel: {connected}")
        self.uart_section.update_uart_status(connected)
        
        if connected:
            self.prog_section.btn_start.setEnabled(True)   
        else :
            self.stop_program()
            
            self.prog_section.btn_start.setEnabled(False) 
            list_ports = self.serial_model.get_port_names()
            self.uart_section.update_list_port(list_ports)
            
    
    def _setup_connections(self):
        """Conectar señales internas del widget"""
        self.uart_section.connect_btn.clicked.connect(self._handle_connect_btn_uart)
        
        # Conectar señales del serial model
        self.serial_model.ports_list_updated.connect(self.uart_section.update_list_port)
        self.serial_model.connection_state_changed.connect(self.update_uart_status)
        self.serial_model.data_received.connect(self.handle_serial_data)

        self.prog_section.btn_start.clicked.connect(self.start_program)
        self.prog_section.btn_stop.clicked.connect(self.stop_program)

        
        self.prog_section.btn_start.setEnabled(False)
        self.prog_section.btn_stop.setEnabled(False)
        
    def _handle_connect_btn_uart(self):
        """Manejar clic en el botón de conexión"""
        text = self.uart_section.connect_btn.text().lower()
        self.logger.info(text)
        if "desconectar" == text:
            self.serial_model.close_port()
        else:
            port = self.uart_section.port_input.currentText()
            if port:
                 config = {
                    'port_name': port,
                    'baud_rate': 115200,
                    'data_bits': QSerialPort.DataBits.Data8,
                    'parity': QSerialPort.Parity.NoParity,
                    'stop_bits': QSerialPort.StopBits.OneStop,
                    'flow_control': QSerialPort.FlowControl.NoFlowControl
                 }
                 self.serial_model.configure_port(config)
                 
    #--------------------------------------------------------
    def start_program(self):
        if self.is_prog_running:
            return  # Ya está en ejecución

        # LIMPIAR LABELS
        self.info_group.reset_all()
        self.plt_group.graph_left.reset_graph()
        self.plt_group.graph_right.reset_graph()
        
        #--- AGREGAR SERIES ---
        self.plt_group.graph_right.add_series(self.name_plt_rh_l1, "#3498db")
        self.plt_group.graph_left.add_series(self.name_plt_lf_l1, "#2ecc71")
        
        #--- INICIAR GRAFICA
        self.plt_group.graph_left.start_timer()
        self.plt_group.graph_right.start_timer()
        
        # INICIAR TIMER DE CONTEO
        self.is_prog_running = True
        self.start_time = QDateTime.currentDateTime()
        
        self.info_group.set_start_time(self.start_time)
        
        
        # Actualiza el campo de hora de inicio (si lo tienes)
        self.logger.info(f"Programa iniciado a las {self.start_time.toString('hh:mm:ss')}")
        self.timer.start(1000)  # Actualizar cada 1 segundo
        
        self.prog_section.btn_start.setEnabled(False)
        self.prog_section.btn_stop.setEnabled(True)
        
        # PEDIR INFORMACION DE LOS LEDS
        #self.serial_model.write_data("LED-STATUS")
        self.send_command_with_delay("LED-STATUS",500)
        # self.serial_model.write_data("IR-STATUS")

    def stop_program(self):
        if not self.is_prog_running:
            return  # Ya está detenido
        self.is_prog_running = False
        self.end_time = QDateTime.currentDateTime()
        self.info_group.set_end_time(self.end_time)
        
        self.logger.info(f"Programa detenido a las {self.end_time.toString('hh:mm:ss')}")

        self.timer.stop()
        self._actualizar_duracion(final=True)

        self.prog_section.btn_start.setEnabled(True)
        self.prog_section.btn_stop.setEnabled(False)

    def _actualizar_duracion(self, final=False):
        if self.start_time:
            now = self.end_time if final else QDateTime.currentDateTime()
            elapsed = self.start_time.secsTo(now)

            horas = elapsed // 3600
            minutos = (elapsed % 3600) // 60
            segundos = elapsed % 60

            time_str = f"{horas:02}:{minutos:02}:{segundos:02}"
            # self.logger.info(time_str)
            self.info_group.update_run_time(time_str)
    
    def send_command_with_delay(self, command: str, delay_ms: int = 100):
        """Envía un comando con un delay mínimo"""
        self.logger.debug(f"TX: {command} -> {delay_ms}")
        
        if not self.serial_model.is_connected():
            return
            
        QTimer.singleShot(delay_ms, lambda: self.serial_model.write_data(command))
        
    def handle_serial_data(self, data: str):
        """Inicia el procesamiento en otro hilo"""
        self.logger.debug(f"RX (crudo): {repr(data)}")
        
        # Si hay un hilo trabajando, guarda los datos para después
        if self.worker_thread and self.worker_thread.isRunning():
            self.pending_data.append(data)
            return
            
        # Crea y configura el worker
        self.worker_thread = SerialDataWorker(data)
        self.worker_thread.processed_data.connect(self._on_data_processed)
        self.worker_thread.finished.connect(self._check_pending_data)
        self.worker_thread.start()
        
    def _process_single_line(self, line: str):
        """Procesa una línea individual de datos"""
        try:
            if 'OK:' in line or 'ERROR:' in line:
                self._process_response(line)
            else:
                self._process_command_block(line)
        except Exception as e:
            self.logger.error(f"Error procesando línea '{line}': {str(e)}")
            
    def _on_data_processed(self, result: dict):
        """Recibe los datos procesados desde el hilo"""
        if 'error' in result:
            self.logger.error(f"Error en worker: {result['error']}")
            return
            
        for block in result['blocks']:
            try:
                if 'OK:' in block or 'ERROR:' in block:
                    self._process_response(block)
                else:
                    self._process_command_block(block)
            except Exception as e:
                self.logger.error(f"Error process block: {str(e)}")
                
    def _check_pending_data(self):
        """Verifica si hay datos pendientes por procesar"""
        if self.pending_data:
            next_data = self.pending_data.pop(0)
            self.handle_serial_data(next_data)
            
            
    def _process_command_block(self, block: str):
        """Procesa bloques de comandos como 'L01:1,L02:0'"""
        items = [item.strip() for item in block.split(',') if item.strip()]
        self.logger.debug(f"cmd blok: {items}")
        
        for item in items:
            try:
                if ':' not in item:
                    self.logger.warning(f"Format invalid cmd: {item}")
                    continue
                    
                key, value = item.split(':', 1)
                key = key.strip().upper()
                value = value.strip()
                
                # Aquí tu lógica existente para LEDs y palancas
                if key in led_keys:
                    self._control_led(key, value)
                elif key in palanca_keys:
                    self._handle_palanca(key, value)
                    
            except Exception as e:
                self.logger.error(f"Error procesando comando '{item}': {str(e)}")

    def _process_response(self, response: str):
        """Procesa respuestas como 'OK:LED-STATUS'"""
        try:
            _, content = response.split(':', 1)
            content = content.strip()
            
            if content == 'LED-STATUS':
                self.logger.info("Solicitud de estado de LEDs")
                # Aquí implementa la lógica para responder el estado
            elif content == 'IR-STATUS':
                self.logger.info("Solicitud de estado IR recibida")
                # Lógica para estado IR
            
        except Exception as e:
            self.logger.error(f"Error procesando respuesta '{response}': {str(e)}")
        
    
    
    #----ACCIONES LUEGO DE PROCESAR ---------
    
    def _control_led(self,key,value):
        if key in led_keys:
            value = value_led_map.get(value.strip().upper(), value)
            if value in ["ON", "OFF"]:
                self.info_group.update_value(led_keys[key], value)
                
    def _handle_palanca(self,key,value):
        if key in palanca_keys:            
            if key == "P01":
                if value.isdigit():
                    self.plt_group.graph_right.register_pulse(self.name_plt_lf_l1)
                    self.info_group.update_value(palanca_keys[key], value)
                    
            elif key == "P02":
                if value.isdigit():
                    self.plt_group.graph_left.register_pulse(self.name_plt_rh_l1)
                    self.info_group.update_value(palanca_keys[key], value)