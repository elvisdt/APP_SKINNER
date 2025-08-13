from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QFont

from fpdf import FPDF
from PyQt6.QtCore import QTimer, QTime, QDateTime

from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QDateTime
import os
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

from main.core.serial_manager import SerialManager
from main.enums.program_enums import ModoLuz, ModoPalanca

from main.core.mean_generator import MeanTimeGeneratorMS, MeanTimeGeneratorSeconds, MeanTimeGeneratorInt


##-------------------------------------------------------------##


def seconds_to_hhmmss(total_seconds: int) -> str:
    """Convierte segundos a formato 'hh:mm:ss'.
    
    Args:
        total_seconds: Segundos a convertir (entero positivo o cero).
    
    Returns:
        str: Cadena en formato 'hh:mm:ss'.
    
    Ejemplos:
        >>> seconds_to_hhmmss(70)
        '00:01:10'
        >>> seconds_to_hhmmss(3665)
        '01:01:05'
    """
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class ProgramEngine:
    """
    Lógica principal del programa: estados, modos y procesamiento de comandos recibidos por UART.
    """
    def __init__(self, 
                 send_cmd_callback, 
                 check_event_palanc,
                 prog_section:ProgramControlBox,
                 info_group:IndicatorsSectionBox,
                 
                 logger):
        self.send_cmd = send_cmd_callback
        self.prog_section = prog_section
        self.info_group = info_group
        self.check_event_palanc = check_event_palanc
        self.logger = logger

            

    def process_uart_line(self, line):
        """
        Procesa un mensaje recibido por UART.
        """
        if self.prog_section.get_runing_state is False:
            return
        
        # Ejemplo básico de parseo
        parts = line.split()
        #self.logger.debug(f"[ProgramEngine] Process Line: {line}")
        
        for part in parts:
            self.logger.debug(f"[ProgramEngine] RX part: {part}")
            
            if part.startswith("L01:"):
                value = part.split(":")[1].strip()
                if value.isdigit():
                    self.info_group.update_value(IndicatorKey.LED_01_STATE, value, increment=False)
                
            elif part.startswith("L02:"):
                value = part.split(":")[1].strip()
                if value.isdigit():
                    self.info_group.update_value(IndicatorKey.LED_02_STATE, value, increment=False)
                
                # Aquí actualizas UI o estado interno
            elif part.startswith("P01:"):
                value = part.split(":")[1].strip()
                if value.isdigit():
                    self._handle_palanca(IndicatorKey.LEVER_01_COUNT, int(value))
                    
            elif part.startswith("P02:"):
                value = part.split(":")[1].strip()
                if value.isdigit():
                    self._handle_palanca(IndicatorKey.LEVER_02_COUNT, int(value))
                    
            elif part.startswith("IR1:"):
                value = part.split(":")[1].strip()
                if value.isdigit():
                    self._handle_recompensa_food(value)
                    
            else:
                self.logger.warning(f"unknow command: {part}")
                continue
                
        #----ACCIONES LUEGO DE PROCESAR ---------                
    def _handle_palanca(self,key,value):
        
        if key == IndicatorKey.LEVER_01_COUNT:            
 
            modo = self.prog_section.get_pal1_mode()   
            if modo in [ModoPalanca.CRF , ModoPalanca.FI, ModoPalanca.FR, ModoPalanca.VI, ModoPalanca.VR]:
                # self.plt_group.graph_left.register_pulse(self.name_plt_lf_l1)
                self.info_group.update_value(key, value, increment=True)
                
            if modo in [ModoPalanca.CRF, ModoPalanca.FR, ModoPalanca.VR]:
                self.check_event_palanc(1)
                
        elif key == IndicatorKey.LEVER_02_COUNT:            
 
            modo = self.prog_section.get_pal2_mode()   
            if modo in [ModoPalanca.CRF , ModoPalanca.FI, ModoPalanca.FR, ModoPalanca.VI, ModoPalanca.VR]:
                # self.plt_group.graph_left.register_pulse(self.name_plt_lf_l1)
                self.info_group.update_value(key, value, increment=True)
                
            if modo in [ModoPalanca.CRF, ModoPalanca.FR, ModoPalanca.VR]:
                self.check_event_palanc(2)

    
    def _handle_disp_food(self, value):
        #self.logger.info(f"Comando DISP recibido: {value}")
        if value.isdigit():
            self.info_group.update_value(IndicatorKey.DISPENSA_COUNT, value, increment=True)
            
            # Agregar más comandos aquí
    def _handle_recompensa_food(self, value):
        if value.isdigit():
            self.info_group.update_value(IndicatorKey.RECONPENSA_COUNT  , value, increment=True)

# SerialReceiver.py
from queue import Queue

class SerialReceiver:
    """
    Se encarga de recibir datos crudos de UART y guardarlos en una cola para su posterior procesamiento.
    """
    def __init__(self, logger=None):
        self.queue = Queue()
        self.logger = logger

    def on_data_received(self, data: bytes, port_name: str = ""):
        """
        Llamado cuando llega data desde el puerto serial.
        """
        try:
            if self.logger:
                self.logger.debug(f"Data RX {port_name}: {data}")
                
            line = data.decode(errors='ignore').strip()
            if line:
                self.queue.put(line)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al decodificar datos: {e}")
                
# DataProcessor.py
class DataProcessor:
    """
    Extrae mensajes de la cola y los envía al motor del programa para su interpretación.
    """
    def __init__(self, program_engine: ProgramEngine, logger=None):
        self.engine = program_engine
        self.logger = logger

    def process_pending(self, queue):
        """
        Procesa todos los mensajes que haya en la cola.
        """
        while not queue.empty():
            try:
                line = queue.get_nowait()
                self.engine.process_uart_line(line)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error process line: {e}")
                # print(f"[DataProcessor] Error procesando línea: {e}")
                
##-------------------------------------------------------------##
from PyQt6.QtCore import QThread, pyqtSignal, QObject 

from PyQt6.QtCore import (
    QObject, 
    QThread, 
    QMetaObject, 
    Qt, 
    pyqtSignal, 
    Q_ARG
)

from PyQt6.QtCore import QObject, QThread, pyqtSignal, QMutex, pyqtSlot

class GeneratorManager(QObject):
    value_ready = pyqtSignal(int, int)  # palanca_num, value
    
    def __init__(self):
        super().__init__()
        self.generators = {
            1: MeanTimeGeneratorInt(),
            2: MeanTimeGeneratorInt()
        }
        self.mutex = QMutex()
        self.current_values = {1: 0, 2: 0}
        
    def get_value(self, palanca_num):
        """Obtiene el último valor generado (thread-safe)"""
        self.mutex.lock()
        value = self.current_values[palanca_num]
        self.mutex.unlock()
        return value
    
    @pyqtSlot(int, result=int)
    def get_total_value(self, palanca_num):
        self.mutex.lock()
        try:
            return self.generators[palanca_num].get_total_value()
        finally:
            self.mutex.unlock()
    
    @pyqtSlot(int)  # <-- Añade este decorador
    def generate_next(self, palanca_num):
        """Genera el siguiente valor (ejecutar en hilo secundario)"""
        self.mutex.lock()
        new_value = self.generators[palanca_num].next_value()
        self.current_values[palanca_num] = new_value
        self.mutex.unlock()
        self.value_ready.emit(palanca_num, new_value)

    @pyqtSlot(int, int)  # <-- Añade este decorador
    def reset_generator(self, palanca_num, target):
        """Reinicia el generador (thread-safe)"""
        self.mutex.lock()
        self.generators[palanca_num].reset(target, 50, 1)
        self.mutex.unlock()
        
    @pyqtSlot(int, int, int, int)  # palanca_num, target, range_pct, precision_s
    def reset_generator(self, palanca_num, target, range_pct=50, precision_s=1):
        """Reinicia el generador de manera thread-safe"""
        self.mutex.lock()
        try:
            self.generators[palanca_num].reset(
                target_s=target,
                range_pct=range_pct,
                precision_s=precision_s
            )
            # Generar un valor inicial inmediato
            initial_value = self.generators[palanca_num].next_value()
            self.current_values[palanca_num] = initial_value
            self.value_ready.emit(palanca_num, initial_value)
        finally:
            self.mutex.unlock()
            
##-------------------------------------------------------------#
from main.core.event_logger import EventType, EventLogger, DeviceID

class PanelControlView(BaseView):
    def __init__(self, serial_manager: SerialManager = None, event_logger: EventLogger = None, parent=None):
        super().__init__(serial_manager=serial_manager, event_logger=event_logger, parent=parent)

        

        # 2. Configuración de temporizadores
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer_events)
        self.start_time = None
        self.end_time = None    
        self.elapsed = 0
        
        self.name_plt_rh_l1="Presiones"
        self.name_plt_lf_l1="Presiones"
        
        self.gen_pal01 = MeanTimeGeneratorInt()
        self.gen_pal02 = MeanTimeGeneratorInt()
        
         # 1️ Inicializar motor del programa
        self.engine = ProgramEngine(
            send_cmd_callback=self.send_uart_cmd,
            check_event_palanc = self.check_palanca_num,
            prog_section=self.prog_section,
            info_group=self.info_group,
            logger=self.logger
        )
        
        
        

         # 2️ Inicializar receptor de UART
        self.receiver = SerialReceiver(logger=self.logger)

        # 3️ Inicializar procesador de datos
        self.processor = DataProcessor(self.engine, logger=self.logger)

        # 4️ Configurar el serial manager
        self._setup_connections()
    

        # 5 Timer para procesar datos UART (cada 100 ms)
        self.timer_uart = QTimer()
        self.timer_uart.timeout.connect(lambda: self.processor.process_pending(self.receiver.queue))
        self.timer_uart.start(100)
        
         # Crear worker y thread
        self.setup_generators()
        
    def refresh_data(self, session_id: int):
        """Actualiza todos los datos de la vista con la sesión especificada"""
        pass
    
    # En tu PanelControlView
    def setup_generators(self):
        self.gen_manager = GeneratorManager()
        self.gen_thread = QThread()

        # Mover el manager al hilo secundario
        self.gen_manager.moveToThread(self.gen_thread)

        # Conectar señales
        self.gen_manager.value_ready.connect(self.handle_generated_value)

        # Iniciar el hilo
        self.gen_thread.start()

        # Generar valores iniciales
        QMetaObject.invokeMethod(self.gen_manager, "generate_next", 
                                Qt.ConnectionType.QueuedConnection,
                                Q_ARG(int, 1))
        
        QMetaObject.invokeMethod(self.gen_manager, "generate_next", 
                                Qt.ConnectionType.QueuedConnection,
                                Q_ARG(int, 2))

    def handle_generated_value(self, palanca_num, value):
        """Maneja los valores generados (se ejecuta en el hilo principal)"""
        self.logger.info(f"gen 01: {palanca_num}: {value}")
            
        

    def reset_generators_config(self):
        """Reinicia ambos generadores con la configuración actual"""
        # Configuración palanca 1
        if self.prog_section.get_pal1_mode() in [ModoPalanca.VI, ModoPalanca.VR]:
            target = self.prog_section.get_pal1_time()
            QMetaObject.invokeMethod(
                self.gen_manager,
                "reset_generator",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(int, 1),
                Q_ARG(int, target),
                Q_ARG(int, 50),  # range_pct
                Q_ARG(int, 1)    # precision_s
            )
        
        # Configuración palanca 2
        if self.prog_section.get_pal2_mode() in [ModoPalanca.VI, ModoPalanca.VR]:
            target = self.prog_section.get_pal2_time()
            QMetaObject.invokeMethod(
                self.gen_manager,
                "reset_generator",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(int, 2),
                Q_ARG(int, target),
                Q_ARG(int, 50),  # range_pct
                Q_ARG(int, 1)    # precision_s
            )
            
    def request_new_value(self, palanca_num):
        """Solicita un nuevo valor de manera thread-safe"""
        try:
            QMetaObject.invokeMethod(
                self.gen_manager,
                "generate_next",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(int, palanca_num)
            )
        except RuntimeError as e:
            print(f"Error al invocar generate_next: {e}")
            # Puedes agregar aquí un fallback síncrono si es necesario
            return self.gen_manager.get_value(palanca_num)
            
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
            
            self.uart_section = UartSection(self.serial_manager.get_list_ports())
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
            
            # Pasar el event_logger al IndicatorsSectionBox
            # Usa self.event_logger que ahora está inicializado
            self.info_group = IndicatorsSectionBox(event_logger=self.event_logger)
        
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
    
            
    
    def _setup_connections(self):
        """Conectar señales internas del widget"""
        self.uart_section.connect_btn.clicked.connect(self._toggle_uart)
        self.prog_section.btn_start.clicked.connect(self.start_program)
        self.prog_section.btn_stop.clicked.connect(self.stop_program)
        self.actions_group.btn_export.clicked.connect(self._btn_export_csv)
        
        # Conectar señales del serial manager
        self.serial_manager.ports_updated.connect(self._on_ports_updated)
        self.serial_manager.data_received.connect(self.receiver.on_data_received)
        
        self.serial_manager.connection_changed.connect(self.update_uart_status)
        self.serial_manager.data_sent.connect(self.handle_serial_dsent)
        self.serial_manager.error_occurred.connect(self._handle_error_uart)
    
    def _btn_export_csv(self):
        
        
        
        timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
        suggested_name = f"sesion_{timestamp}.csv"

        # Carpeta base donde quieres que empiece
        base_dir = os.getcwd()  # O tu carpeta de exportación preferida

        # Cuadro de diálogo para elegir dónde guardar
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo CSV",
            os.path.join(base_dir, suggested_name),  # Ruta sugerida
            "Archivos CSV (*.csv)"
        )

        # Si el usuario no canceló
        if file_path:
            self.event_logger.save_to_csv(file_path)
            self.logger.info(f"Registro guardado en {file_path}")
    #--------------------------------------------------------
    def update_uart_status(self, connected: bool, port_name: str = ""):
        """Actualiza la UI según el estado de conexión"""
        self.logger.info(f"status uart Panel: {connected}")
        self.uart_section.update_uart_status(connected)
        self.prog_section.update_uart_status(connected)
        
        if not connected:
            self.stop_program()
            self.uart_section.update_list_port(self.serial_manager.get_list_ports())
    
    def _toggle_uart(self):
        """Manejar clic en el botón de conexión"""
        if self.serial_manager.is_connected():
            self.serial_manager.close_port()
            self.uart_section.update_uart_status(False)
        else:
            port = self.uart_section.port_input.currentText()
            if port:
                self.serial_manager.open_port(port)
                self.uart_section.update_uart_status(True)
                
    def _on_ports_updated(self, ports: list[str]):
        """Actualiza la lista de puertos en la UI."""
        self.logger.info(f"Puertos actualizados: {ports}")
        self.uart_section.update_list_port(ports)
        
    def _handle_error_uart(self, error: str, port_name: str = ""):
        """Maneja errores de conexión UART"""
        self.logger.error(f"Error UART: {error}")
        
        
    def _send_current_config(self):
        #------------------------------------#
        
        # config led 01 mode
        led_01_tx = self.prog_section.get_led1_mode()
        if led_01_tx == ModoLuz.APAGADO:
            self.send_uart_cmd("LED1:OFF",50)
        elif led_01_tx == ModoLuz.ENCENDIDO:
            self.send_uart_cmd("LED1:ON",50)
        elif led_01_tx == ModoLuz.INTERMITENTE:
            l01_time = self.prog_section.get_led1_time()
            pass
        
        #config led 02 mode
        led_02_tx = self.prog_section.get_led2_mode()
        if led_02_tx == ModoLuz.APAGADO:
            self.send_uart_cmd("LED2:OFF",100)
        elif led_02_tx == ModoLuz.ENCENDIDO:
            self.send_uart_cmd("LED2:ON",100)
        elif led_02_tx == ModoLuz.INTERMITENTE:
            l02_time = self.prog_section.get_led2_time()
            pass
        
        #config palanca 01 mode
        self.reset_generators_config() 
        self.logger.info(f"Config Led-01: {led_01_tx}, Led-02: {led_02_tx}")
        

    def start_program(self):
        if self.serial_manager.is_connected() is False:
            return
        
        if self.prog_section.get_runing_state():
            return  # Ya está en ejecución

        # Limpia todo antes de iniciar sesión
        self.info_group.reset_all()

        # Inicia la sesión
        #self.info_group.start_session(self.prog_section.get_program_config())
        self.event_logger.start_session(self.prog_section.get_program_config())
        
        self.elapsed = 0
        self.logger.info("Iniciando programa...")

        # Limpia gráficas pero sin resetear indicadores (para no cerrar sesión)
        self.plt_group.reset_graphs()
        
        mode_p1 = self.prog_section.get_pal1_mode()
        if mode_p1 in [ModoPalanca.CRF , ModoPalanca.FI, ModoPalanca.FR, ModoPalanca.VI, ModoPalanca.VR]:
            self.plt_group.graph_left.add_series(self.name_plt_lf_l1, "#2ecc71")
            self.plt_group.graph_left.add_data_point(self.name_plt_lf_l1,0,0)
        
        mode_p2 = self.prog_section.get_pal2_mode()
        if mode_p2 in [ModoPalanca.CRF , ModoPalanca.FI, ModoPalanca.FR, ModoPalanca.VI, ModoPalanca.VR]:
            self.plt_group.graph_right.add_series(self.name_plt_rh_l1, "#3498db")
            self.plt_group.graph_right.add_data_point(self.name_plt_rh_l1,0,0)
            
        # Inicia temporizador
        self.prog_section.set_runing_state(True)
        self.start_time = QDateTime.currentDateTime()
        self.info_group.set_start_time(self.start_time)
        
        self.logger.info(f"Programa iniciado a las {self.start_time.toString('hh:mm:ss')}")
        self.timer.start(1000)
        
        self.prog_section.btn_start.setEnabled(False)
        self.prog_section.btn_stop.setEnabled(True)
        self._send_current_config()

  
        if self.event_logger.is_session_active():
            sesion_id = self.event_logger.get_current_session_id()
            val_id_txt = f"{sesion_id:03d}"
            # Aquí usamos setText directamente para no loguear nada
            self.info_group.labels[IndicatorKey.SESSION_ID].setText(val_id_txt)

    
    def stop_program(self):
        if not self.prog_section.get_runing_state():
            return  # Ya está detenido
        
        
        
        self.prog_section.set_runing_state(False)
        self.end_time = QDateTime.currentDateTime()
        self.info_group.set_end_time(self.end_time)
        
        self.logger.info(f"Program stop -> {self.end_time.toString('hh:mm:ss')}")        
        # Cierra la sesión si está activa
        if self.event_logger.is_session_active():
            self.event_logger.end_session()
            
            
        self.timer.stop()
        self._update_timer_events(final=True)
        self.prog_section.update_uart_status(self.serial_manager.is_connected())
        
        if self.elapsed < 60:
            val_in_rpm = self.info_group.get_val_response_rate()
            val_cp1 = self.info_group.get_val_pal01_count()
            val_cp2 = self.info_group.get_val_pal02_count()
            value_end_RPM = (val_cp1 + val_cp2) - val_in_rpm
            self.info_group.update_value(IndicatorKey.RESPONSE_RATE_VAL, int(value_end_RPM))
        
        self.send_uart_cmd("LED1:OFF", 0)
        self.send_uart_cmd("LED2:OFF", 20)

       

    def _update_timer_events(self, final=False):
        """Actualiza eventos basados en tiempo cada segundo"""
        if self.start_time:
            now = self.end_time if final else QDateTime.currentDateTime()
            self.elapsed = self.start_time.secsTo(now)
            self.info_group.set_run_time(seconds_to_hhmmss(self.elapsed))
            
            
            if self.elapsed % 60==0:
                val_in_rpm = self.info_group.get_val_response_rate()
                val_cp1 = self.info_group.get_val_pal01_count()
                val_cp2 = self.info_group.get_val_pal02_count()
                
                value_end_RPM = (val_cp1 + val_cp2) - val_in_rpm
                self.info_group.update_value(IndicatorKey.RESPONSE_RATE_VAL, int(value_end_RPM))
                 
            # #--------------------------------------------------------
            mode_pal1 = self.prog_section.get_pal1_mode()
            mode_pal2 = self.prog_section.get_pal2_mode()
            
            if mode_pal1 in [ModoPalanca.FI, ModoPalanca.VI]:
                self.check_palanca_num(1)
                    
            if mode_pal2 in [ModoPalanca.FI, ModoPalanca.VI]:
                self.check_palanca_num(2)
            
    
    def send_uart_cmd(self, command: str, delay_ms: int = 50):
        """Envía un comando con un delay mínimo"""
        if not self.serial_manager or not self.serial_manager.is_connected():
            return
        QTimer.singleShot(delay_ms, lambda: self.serial_manager.send_data_str(command))

        
    
    def handle_serial_dsent(self, data: bytes, port_name: str):
        """Maneja los datos enviados (solo para logging)"""
        self.logger.debug(f"TX {port_name}-> {data}")
        data_tx =  data.decode(errors='ignore').strip()
        if not data_tx:
            self.logger.warning(f"Data null en: {port_name}")
            return
        
        if not self.prog_section.get_runing_state():
            self.logger.warning("Program not runing, ignore all data")
            return
        # Procesar datos en un hilo separado
        palabras = data_tx.split()
        
        # Procesar cada palabra
        for palabra in palabras:
            
            if 'DISP:' in palabra:
                try:
                    _, value = palabra.split(':', 1)
                    value = value.strip()
                    if value.isdigit():
                        self.engine._handle_disp_food(value)
                except Exception as e:
                    self.logger.error(f"Error procesando DISP: {str(e)}")
  
    
    def check_palanca_num(self, num: int):
        # Solicitar generación de nuevo valor
        
        if num not in [1,2]:
            return
        
        # Obtener el último valor disponible (puede ser el anterior hasta que se actualice)
        if num==1:
            self.actions_palanca_01()
        else:
            self.actions_palanca_02()
                    
    def actions_palanca_01(self):
        
        if self.prog_section.get_runing_state() is False:
            return
        
        mode_fun  =  self.prog_section.get_pal1_mode()
        last_event = self.info_group.get_last_p01_event()
        
        last_count_val = self.info_group.get_val_pal01_count()
        last_point = self.plt_group.graph_left.get_last_point(self.name_plt_lf_l1)

        if last_point is None or last_count_val != last_point[1]:
            if last_event and mode_fun in [
                ModoPalanca.CRF,
                ModoPalanca.FI,
                ModoPalanca.FR,
                ModoPalanca.VI,
                ModoPalanca.VR
            ]:
                self.plt_group.graph_left.add_data_point(
                    self.name_plt_lf_l1,
                    self.elapsed,
                    last_count_val
                )
                self.logger.info(f"PLOT NEW DATA P1: {self.elapsed},{last_count_val}")
                
                val_latency = self.info_group.get_val_latency()
                if val_latency<=0:
                    now = QDateTime.currentDateTime()
                    pas_time_ms = self.start_time.msecsTo(now)
                    past_time_sec_txt = f"{pas_time_ms/1000:.2f}" 
                    self.info_group.update_value(IndicatorKey.LATENCY_VAL, past_time_sec_txt)
                    
                
        match mode_fun:
            case ModoPalanca.CRF:
                if last_event:
                    self.send_uart_cmd(f"DISP:1", 10)
                    self.info_group.set_last_p01_event(False)
            
            case ModoPalanca.FI:
                interval = self.prog_section.get_pal1_time()
                count_val = self.elapsed
                if last_event and ( count_val % interval == 0) and count_val != 0:
                    self.send_uart_cmd("DISP:1", 10)
                    self.info_group.set_last_p01_event(False)
            
            case ModoPalanca.FR:
                interval = self.prog_section.get_pal1_time()
                count_val = self.info_group.get_val_pal01_count()
                if last_event and (count_val % interval == 0) and count_val != 0:
                    self.send_uart_cmd("DISP:1", 10)
                    self.info_group.set_last_p01_event(False)
            
            case ModoPalanca.VI:
                interval = self.gen_manager.get_value(1) 
                count_val = self.elapsed
                           
                if count_val > interval:
                    self.gen_manager.generate_next(1)
                else:
                    if last_event and (count_val % interval == 0) and count_val != 0:
                        self.send_uart_cmd("DISP:1", 10)
                        self.info_group.set_last_p01_event(False)
                        
            case ModoPalanca.VR:
                interval = self.gen_manager.get_value(1) 
                count_val = self.info_group.get_val_pal01_count()
                            
                if count_val > interval:
                    self.gen_manager.generate_next(1)
                else:
                    if last_event and (count_val % interval == 0) and count_val != 0:
                        self.send_uart_cmd("DISP:1", 10)
                        self.info_group.set_last_p01_event(False)
                        
            case _:
                self.logger.warning(f"Mode not found {mode_fun} -> state:{last_event}")  
                
    def actions_palanca_02(self):
        if self.prog_section.get_runing_state() is False:
            return
        
        mode_fun  =  self.prog_section.get_pal2_mode()
        last_event = self.info_group.get_last_p02_event()
        
        last_count_val = self.info_group.get_val_pal02_count()
        last_point = self.plt_group.graph_right.get_last_point(self.name_plt_rh_l1)

        if last_point is None or last_count_val != last_point[1]:
            if last_event and mode_fun in [
                ModoPalanca.CRF,
                ModoPalanca.FI,
                ModoPalanca.FR,
                ModoPalanca.VI,
                ModoPalanca.VR
            ]:
                self.plt_group.graph_right.add_data_point(
                    self.name_plt_rh_l1,
                    self.elapsed,
                    last_count_val
                )
                self.logger.info(f"PLOT NEW DATA P2: {self.elapsed},{last_count_val}")
                
                val_latency = self.info_group.get_val_latency()
                if val_latency<=0:
                    now = QDateTime.currentDateTime()
                    pas_time_ms = self.start_time.msecsTo(now)
                    self.info_group.update_value(IndicatorKey.LATENCY_VAL, pas_time_ms)
                
        
        match mode_fun:
            case ModoPalanca.CRF:
                if last_event:
                    self.send_uart_cmd(f"DISP:1", 10)
                    self.info_group.set_last_p02_event(False)
            
            case ModoPalanca.FI:
                interval = self.prog_section.get_pal2_time()
                count_val = self.elapsed
                
                if last_event and ( count_val % interval == 0) and count_val != 0:
                    self.send_uart_cmd("DISP:1", 10)
                    self.info_group.set_last_p02_event(False)
            
            case ModoPalanca.FR:
                interval = self.prog_section.get_pal2_time()
                count_val = self.info_group.get_val_pal02_count()
                if last_event and (count_val % interval == 0) and count_val != 0:
                    self.send_uart_cmd("DISP:1", 10)
                    self.info_group.set_last_p02_event(False)
            
            case ModoPalanca.VI:
                interval = self.gen_manager.get_value(2) 
                count_val = self.elapsed
                           
                if count_val > interval:
                    self.gen_manager.generate_next(2)
                else:
                    if last_event and (count_val % interval == 0) and count_val != 0:
                        self.send_uart_cmd("DISP:1", 10)
                        self.info_group.set_last_p02_event(False)
                        
            case ModoPalanca.VR:
                interval = self.gen_manager.get_value(2) 
                count_val = self.info_group.get_val_pal02_count()
                            
                if count_val > interval:
                    self.gen_manager.generate_next(2)
                else:
                    if last_event and (count_val % interval == 0) and count_val != 0:
                        self.send_uart_cmd("DISP:1", 10)
                        self.info_group.set_last_p02_event(False)    
            case _:
                self.logger.warning(f"Mode not found {mode_fun} -> state:{last_event}")         
          
    