import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, QIODeviceBase
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                            QTableWidget, QStackedWidget)
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo

class SerialHandler(QObject):
    """
    Manejador de comunicación serial (versión corregida sin Singleton)
    """
    data_ready = pyqtSignal(bytes, str)  # data, source_port
    status_changed = pyqtSignal(dict)    # {connected: bool, port: str, error: str}
    ports_updated = pyqtSignal(list)     # Lista de puertos disponibles
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._serial = QSerialPort()
        self._current_port = ""
        self._setup_connections()
        
    def _setup_connections(self):
        """Configura las conexiones de señales internas"""
        self._serial.readyRead.connect(self._on_data_ready)
        self._serial.errorOccurred.connect(self._on_error)
        
        # Timer para escanear puertos
        self._scan_timer = QTimer(self)
        self._scan_timer.timeout.connect(self.refresh_ports)
        self._scan_timer.start(3000)  # Escanear cada 3 segundos
    
    @pyqtSlot()
    def refresh_ports(self):
        """Actualiza lista de puertos disponibles"""
        ports = [port.portName() for port in QSerialPortInfo.availablePorts()]
        self.ports_updated.emit(ports)
    
    def connect_to_port(self, port: str, config: Dict[str, Any]):
        """Establece conexión serial con configuración"""
        if self._serial.isOpen():
            self.disconnect()
        
        self._serial.setPortName(port)
        self._serial.setBaudRate(config.get('baud_rate', QSerialPort.BaudRate.Baud9600))
        
        if self._serial.open(QIODeviceBase.OpenModeFlag.ReadWrite):
            self._current_port = port
            self.status_changed.emit({
                'connected': True,
                'port': port,
                'error': None
            })
            return True
        else:
            self._on_error(self._serial.error())
            return False
    
    def disconnect(self):
        """Cierra la conexión serial"""
        if self._serial.isOpen():
            port = self._current_port
            self._serial.close()
            self._current_port = ""
            self.status_changed.emit({
                'connected': False,
                'port': port,
                'error': None
            })
    
    @pyqtSlot()
    def _on_data_ready(self):
        """Maneja datos entrantes del puerto serial"""
        if self._serial.bytesAvailable():
            data = self._serial.readAll()
            self.data_ready.emit(data.data(), self._current_port)
    
    @pyqtSlot(QSerialPort.SerialPortError)
    def _on_error(self, error):
        """Maneja errores de conexión serial"""
        error_msg = {
            QSerialPort.SerialPortError.NoError: "",
            QSerialPort.SerialPortError.DeviceNotFoundError: "Dispositivo no encontrado",
            QSerialPort.SerialPortError.PermissionError: "Permiso denegado",
            QSerialPort.SerialPortError.OpenError: "Error al abrir puerto",
            QSerialPort.SerialPortError.NotOpenError: "Puerto no abierto",
        }.get(error, "Error desconocido")
        
        self.status_changed.emit({
            'connected': False,
            'port': self._current_port,
            'error': error_msg
        })
    
    def send_data(self, data: bytes):
        """Envía datos por el puerto serial"""
        if self._serial.isOpen():
            self._serial.write(data)

class SerialView(QWidget):
    """
    Vista base para todas las vistas que necesitan comunicación serial
    """
    def __init__(self, view_name: str, handler: SerialHandler, parent=None):
        super().__init__(parent)
        self._view_name = view_name
        self._handler = handler
        self._setup_serial_connections()
        self._setup_ui()
    
    def _setup_serial_connections(self):
        """Configura conexiones seriales comunes"""
        self._handler.data_ready.connect(self._process_incoming_data)
        self._handler.status_changed.connect(self._update_connection_status)
        self._handler.ports_updated.connect(self._update_ports_list)
    
    def _setup_ui(self):
        """Configura la interfaz de usuario (debe implementarse en subclases)"""
        pass
    
    def _process_incoming_data(self, data: bytes, port: str):
        """Procesa datos entrantes (debe implementarse en subclases)"""
        pass
    
    def _update_connection_status(self, status: dict):
        """Actualiza estado de conexión (debe implementarse en subclases)"""
        pass
    
    def _update_ports_list(self, ports: list):
        """Actualiza lista de puertos (debe implementarse en subclases)"""
        pass
    
    def send_command(self, command: str):
        """Envía un comando por el puerto serial"""
        self._handler.send_data(command.encode())
    
    def view_name(self) -> str:
        """Devuelve el nombre de la vista"""
        return self._view_name

class MonitorView(SerialView):
    """Vista para monitoreo en tiempo real"""
    def __init__(self, handler: SerialHandler):
        super().__init__("Monitor", handler)
        self._data_buffer = []
    
    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        
        self.status_label = QLabel("Estado: Desconectado")
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.data_display)
    
    def _process_incoming_data(self, data: bytes, port: str):
        try:
            text = data.decode('utf-8').strip()
            self._data_buffer.append(text)
            if len(self._data_buffer) > 100:
                self._data_buffer.pop(0)
            
            self.data_display.append(f"[{port}] {text}")
        except UnicodeDecodeError:
            self.data_display.append(f"[{port}] Datos binarios: {data.hex()}")
    
    def _update_connection_status(self, status: dict):
        state = "Conectado" if status['connected'] else "Desconectado"
        self.status_label.setText(f"Estado: {state} | Puerto: {status.get('port', 'N/A')}")
        if status['error']:
            self.data_display.append(f"ERROR: {status['error']}")

class ReportView(SerialView):
    """Vista para generación de reportes"""
    def __init__(self, handler: SerialHandler):
        super().__init__("Reportes", handler)
        self._report_data = []
    
    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        
        self.generate_btn = QPushButton("Generar Reporte")
        self.generate_btn.clicked.connect(self._generate_report)
        
        self.report_table = QTableWidget(0, 3)
        self.report_table.setHorizontalHeaderLabels(["Timestamp", "Puerto", "Datos"])
        
        self.layout.addWidget(self.generate_btn)
        self.layout.addWidget(self.report_table)
    
    def _process_incoming_data(self, data: bytes, port: str):
        self._report_data.append({
            'timestamp': datetime.now(),
            'port': port,
            'data': data
        })
    
    def _generate_report(self):
        self.report_table.setRowCount(len(self._report_data))
        for row, entry in enumerate(self._report_data):
            # Implementar llenado de tabla aquí
            pass

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Comunicación Serial")
        self.resize(1024, 768)
        
        # Crear el manejador serial
        self.serial_handler = SerialHandler(self)
        
        # Configurar interfaz
        self._setup_ui()
    
    def _setup_ui(self):
        # Configuración principal
        self.stack = QStackedWidget()
        
        # Crear vistas
        self._views = {
            'monitor': MonitorView(self.serial_handler),
            'reports': ReportView(self.serial_handler)
        }
        
        # Añadir vistas al stack
        for view in self._views.values():
            self.stack.addWidget(view)
        
        # Barra de navegación
        nav_bar = QWidget()
        nav_layout = QHBoxLayout()
        
        for view_name, view in self._views.items():
            btn = QPushButton(view.view_name())
            btn.clicked.connect(lambda _, v=view_name: self._switch_view(v))
            nav_layout.addWidget(btn)
        
        nav_bar.setLayout(nav_layout)
        
        # Layout principal
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(nav_bar)
        main_layout.addWidget(self.stack)
        main_widget.setLayout(main_layout)
        
        self.setCentralWidget(main_widget)
        
        # Mostrar vista inicial
        self._switch_view('monitor')
    
    def _switch_view(self, view_name: str):
        """Cambia a la vista especificada"""
        if view_name in self._views:
            self.stack.setCurrentWidget(self._views[view_name])

def main():
    """Función principal de la aplicación"""
    app = QApplication(sys.argv)
    
    # Configurar estilo (opcional)
    app.setStyle('Fusion')
    
    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()
    
    # Ejecutar bucle de aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()