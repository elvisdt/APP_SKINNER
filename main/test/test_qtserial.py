from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtCore import QIODevice, pyqtSignal, QObject, QTimer
from typing import List, Optional, Dict, Any

# class SerialManager(QObject):
#     """
#     Gestor avanzado de comunicación serial usando QtSerialPort.
#     """
#     data_received = pyqtSignal(bytes, str)  # datos, puerto
#     data_sent = pyqtSignal(bytes, str)      # datos, puerto
#     error_occurred = pyqtSignal(str, str)   # mensaje, puerto
#     connection_changed = pyqtSignal(bool, str)  # estado, puerto
#     ports_updated = pyqtSignal(list)        # lista de puertos
    
#     # Configuración por defecto
#     DEFAULT_SETTINGS = {
#         'baud_rate': QSerialPort.BaudRate.Baud115200,
#         'data_bits': QSerialPort.DataBits.Data8,
#         'parity': QSerialPort.Parity.NoParity,
#         'stop_bits': QSerialPort.StopBits.OneStop,
#         'flow_control': QSerialPort.FlowControl.NoFlowControl
#     }

#     def __init__(self):
#         super().__init__()
#         self.serial: Optional[QSerialPort] = None
#         self.port_name: str = ""
#         self._scan_timer = QTimer()
#         self._scan_timer.timeout.connect(self.scan_ports)
#         self._scan_timer.start(2000)  # Escanear puertos cada 2 segundos
        
#     def scan_ports(self):
#         """Escanear puertos disponibles y emitir señal si cambian."""
#         ports = [port.portName() for port in QSerialPortInfo.availablePorts()]
#         self.ports_updated.emit(ports)
        
#     def get_port_info(self, port_name: str) -> Dict[str, Any]:
#         """Obtener información detallada de un puerto."""
#         for port in QSerialPortInfo.availablePorts():
#             if port.portName() == port_name:
#                 return {
#                     'description': port.description(),
#                     'manufacturer': port.manufacturer(),
#                     'serial_number': port.serialNumber(),
#                     'vendor_id': port.vendorIdentifier(),
#                     'product_id': port.productIdentifier(),
#                     'system_location': port.systemLocation()
#                 }
#         return {}
        
#     def connect_serial(self, port_name: str, settings: Optional[Dict] = None):
#         """Conectar al puerto serial con configuración."""
#         if self.serial and self.serial.isOpen():
#             self.disconnect_serial()
            
#         self.serial = QSerialPort(port_name)
#         self.port_name = port_name
        
#         # Aplicar configuración
#         config = {**self.DEFAULT_SETTINGS, **(settings or {})}
#         self.serial.setBaudRate(config['baud_rate'])
#         self.serial.setDataBits(config['data_bits'])
#         self.serial.setParity(config['parity'])
#         self.serial.setStopBits(config['stop_bits'])
#         self.serial.setFlowControl(config['flow_control'])
        
#         # Conectar señales
#         self.serial.readyRead.connect(self._handle_ready_read)
#         self.serial.errorOccurred.connect(self._handle_error)
        
#         if self.serial.open(QIODevice.OpenModeFlag.ReadWrite):
#             self.connection_changed.emit(True, port_name)
#         else:
#             self.error_occurred.emit(f"Error al abrir {port_name}", port_name)
#             self.serial = None
            
#     def disconnect_serial(self):
#         """Desconectar el puerto serial."""
#         if self.serial and self.serial.isOpen():
#             port_name = self.port_name
#             self.serial.close()
#             self.serial = None
#             self.port_name = ""
#             self.connection_changed.emit(False, port_name)
            
#     def send_data(self, data: bytes):
#         """Enviar datos por el puerto serial."""
#         if self.serial and self.serial.isOpen():
#             bytes_written = self.serial.write(data)
#             if bytes_written == len(data):
#                 self.data_sent.emit(data, self.port_name)
#             else:
#                 self.error_occurred.emit(
#                     f"Error al enviar datos (enviados {bytes_written}/{len(data)} bytes)",
#                     self.port_name
#                 )
                
#     def _handle_ready_read(self):
#         """Manejar datos recibidos."""
#         if self.serial and self.serial.isOpen():
#             data = self.serial.readAll()
#             self.data_received.emit(data.data(), self.port_name)
            
#     def _handle_error(self, error):
#         """Manejar errores del puerto serial."""
#         if error == QSerialPort.SerialPortError.NoError:
#             return
            
#         error_map = {
#             QSerialPort.SerialPortError.DeviceNotFoundError: "Dispositivo no encontrado",
#             QSerialPort.SerialPortError.PermissionError: "Permiso denegado",
#             QSerialPort.SerialPortError.OpenError: "Error al abrir puerto",
#             QSerialPort.SerialPortError.WriteError: "Error de escritura",
#             QSerialPort.SerialPortError.ReadError: "Error de lectura",
#             QSerialPort.SerialPortError.ResourceError: "Recurso no disponible",
#             QSerialPort.SerialPortError.UnsupportedOperationError: "Operación no soportada",
#             QSerialPort.SerialPortError.TimeoutError: "Timeout",
#             QSerialPort.SerialPortError.NotOpenError: "Dispositivo no abierto"
#         }
        
#         error_msg = error_map.get(error, f"Error desconocido ({error})")
#         self.error_occurred.emit(error_msg, self.port_name)
        
#     def is_connected(self) -> bool:
#         """Verificar si hay conexión activa."""
#         return self.serial is not None and self.serial.isOpen()
        
#     def get_current_settings(self) -> Dict[str, Any]:
#         """Obtener configuración actual del puerto."""
#         if not self.is_connected():
#             return {}
            
#         return {
#             'baud_rate': self.serial.baudRate(),
#             'data_bits': self.serial.dataBits(),
#             'parity': self.serial.parity(),
#             'stop_bits': self.serial.stopBits(),
#             'flow_control': self.serial.flowControl()
#         }
        


# from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
#                             QComboBox, QPushButton, QTextEdit, QLineEdit,
#                             QLabel, QGroupBox, QFormLayout, QStatusBar)
# from PyQt6.QtCore import Qt, pyqtSlot
# # from qtserial_manager import SerialManager

# class SerialInterface(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.serial_manager = SerialManager()
#         self.init_ui()
#         self.connect_signals()
#         self.setWindowTitle("Interfaz Serial Avanzada")
#         self.resize(800, 600)
        
#     def init_ui(self):
#         """Inicializar componentes de la interfaz."""
#         main_widget = QWidget()
#         layout = QVBoxLayout()
        
#         # Grupo de conexión
#         connection_group = QGroupBox("Configuración de Conexión")
#         connection_layout = QFormLayout()
        
#         self.port_combo = QComboBox()
#         self.refresh_ports_btn = QPushButton("Actualizar Puertos")
#         self.baud_combo = QComboBox()
#         self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        
#         self.connect_btn = QPushButton("Conectar")
#         self.disconnect_btn = QPushButton("Desconectar")
#         self.disconnect_btn.setEnabled(False)
        
#         connection_layout.addRow("Puerto:", self.port_combo)
#         connection_layout.addRow("", self.refresh_ports_btn)
#         connection_layout.addRow("Baudrate:", self.baud_combo)
#         connection_layout.addRow(self.connect_btn)
#         connection_layout.addRow(self.disconnect_btn)
#         connection_group.setLayout(connection_layout)
        
#         # Grupo de información
#         info_group = QGroupBox("Información del Puerto")
#         info_layout = QFormLayout()
        
#         self.port_info_label = QLabel("No conectado")
#         self.port_info_label.setWordWrap(True)
#         info_layout.addRow(self.port_info_label)
#         info_group.setLayout(info_layout)
        
#         # Grupo de comunicación
#         comm_group = QGroupBox("Comunicación Serial")
#         comm_layout = QVBoxLayout()
        
#         self.received_text = QTextEdit()
#         self.received_text.setReadOnly(True)
#         self.received_text.setPlaceholderText("Datos recibidos aparecerán aquí...")
        
#         self.send_text = QLineEdit()
#         self.send_text.setPlaceholderText("Escriba datos para enviar...")
#         self.send_btn = QPushButton("Enviar")
        
#         comm_layout.addWidget(self.received_text)
#         comm_layout.addWidget(self.send_text)
#         comm_layout.addWidget(self.send_btn)
#         comm_group.setLayout(comm_layout)
        
#         # Ensamblar layout principal
#         layout.addWidget(connection_group)
#         layout.addWidget(info_group)
#         layout.addWidget(comm_group)
#         main_widget.setLayout(layout)
        
#         self.setCentralWidget(main_widget)
#         self.status_bar = QStatusBar()
#         self.setStatusBar(self.status_bar)
        
#         # Actualizar puertos al iniciar
#         self.update_ports()
        
#     def connect_signals(self):
#         """Conectar señales y slots."""
#         self.refresh_ports_btn.clicked.connect(self.update_ports)
#         self.connect_btn.clicked.connect(self.connect_to_port)
#         self.disconnect_btn.clicked.connect(self.serial_manager.disconnect_serial)
#         self.send_btn.clicked.connect(self.send_data)
        
#         # Señales del SerialManager
#         self.serial_manager.ports_updated.connect(self.update_port_combo)
#         self.serial_manager.data_received.connect(self.display_received_data)
#         self.serial_manager.data_sent.connect(self.display_sent_data)
#         self.serial_manager.error_occurred.connect(self.display_error)
#         self.serial_manager.connection_changed.connect(self.handle_connection_change)
        
#     def update_ports(self):
#         """Actualizar lista de puertos disponibles."""
#         self.serial_manager.scan_ports()
        
#     @pyqtSlot(list)
#     def update_port_combo(self, ports):
#         """Actualizar combo box con puertos disponibles."""
#         current = self.port_combo.currentText()
#         self.port_combo.clear()
#         self.port_combo.addItems(ports)
        
#         if current in ports:
#             self.port_combo.setCurrentText(current)
            
#     def connect_to_port(self):
#         """Conectar al puerto seleccionado."""
#         port = self.port_combo.currentText()
#         baud = int(self.baud_combo.currentText())
        
#         if not port:
#             self.status_bar.showMessage("Seleccione un puerto válido", 3000)
#             return
            
#         settings = {
#             'baud_rate': baud,
#             # Puedes añadir más configuraciones aquí si necesitas
#         }
        
#         self.serial_manager.connect_serial(port, settings)
        
#     @pyqtSlot(bytes, str)
#     def display_received_data(self, data, port):
#         """Mostrar datos recibidos."""
#         try:
#             text = data.decode('utf-8').strip()
#             self.received_text.append(f"[{port} RECV]: {text}")
#             self.serial_manager.send_data(text.encode('utf-8'))
#         except UnicodeDecodeError:
#             self.received_text.append(f"[{port} RECV HEX]: {data.hex()}")
            
#     @pyqtSlot(bytes, str)
#     def display_sent_data(self, data, port):
#         """Mostrar datos enviados."""
#         try:
#             text = data.decode('utf-8').strip()
#             self.received_text.append(f"[{port} SENT]: {text}")
#         except UnicodeDecodeError:
#             self.received_text.append(f"[{port} SENT HEX]: {data.hex()}")
            
#     @pyqtSlot(str, str)
#     def display_error(self, error, port):
#         """Mostrar errores."""
#         self.received_text.append(f"[{port} ERROR]: {error}")
#         self.status_bar.showMessage(f"Error: {error}", 5000)
        
#     @pyqtSlot(bool, str)
#     def handle_connection_change(self, connected, port):
#         """Manejar cambios en el estado de conexión."""
#         self.connect_btn.setEnabled(not connected)
#         self.disconnect_btn.setEnabled(connected)
#         self.send_btn.setEnabled(connected)
        
#         if connected:
#             info = self.serial_manager.get_port_info(port)
#             info_text = f"Conectado a {port}\n"
#             info_text += f"\nDescripción: {info.get('description', 'N/A')}"
#             info_text += f"\nFabricante: {info.get('manufacturer', 'N/A')}"
#             info_text += f"\nSerial: {info.get('serial_number', 'N/A')}"
#             self.port_info_label.setText(info_text)
#             self.status_bar.showMessage(f"Conectado a {port}", 3000)
#         else:
#             self.port_info_label.setText("No conectado")
#             self.status_bar.showMessage(f"Desconectado de {port}", 3000)
            
#     def send_data(self):
#         """Enviar datos a través del puerto serial."""
#         text = self.send_text.text().strip()
#         if text:
#             self.serial_manager.send_data(text.encode('utf-8'))
#             self.send_text.clear()
            
#     def closeEvent(self, event):
#         """Manejar cierre de la ventana."""
#         self.serial_manager.disconnect_serial()
#         event.accept()


# if __name__ == "__main__":
#     from PyQt6.QtWidgets import QApplication
#     import sys
    
#     app = QApplication(sys.argv)
#     window = SerialInterface()
#     window.show()
#     sys.exit(app.exec())


from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QIODevice
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo

from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QIODevice
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo

class SerialManager(QObject):
    """
    Gestor avanzado de comunicación serial usando QtSerialPort.
    Optimizado para minimizar uso de CPU y memoria.
    """
    data_received = pyqtSignal(bytes, str)   # datos, puerto
    data_sent = pyqtSignal(bytes, str)       # datos, puerto
    error_occurred = pyqtSignal(str, str)    # mensaje, puerto
    connection_changed = pyqtSignal(bool, str)  # estado, puerto
    ports_updated = pyqtSignal(list)         # lista de puertos

    # Configuración por defecto (formato correcto para PyQt6)
    DEFAULT_SETTINGS = {
        'baud_rate': 115200,  # int
        'data_bits': QSerialPort.DataBits.Data8,
        'parity': QSerialPort.Parity.NoParity,
        'stop_bits': QSerialPort.StopBits.OneStop,
        'flow_control': QSerialPort.FlowControl.NoFlowControl
    }

    ERROR_MAP = {
        QSerialPort.SerialPortError.DeviceNotFoundError: "Dispositivo no encontrado",
        QSerialPort.SerialPortError.PermissionError: "Permiso denegado",
        QSerialPort.SerialPortError.OpenError: "Error al abrir puerto",
        QSerialPort.SerialPortError.WriteError: "Error de escritura",
        QSerialPort.SerialPortError.ReadError: "Error de lectura",
        QSerialPort.SerialPortError.ResourceError: "Recurso no disponible",
        QSerialPort.SerialPortError.UnsupportedOperationError: "Operación no soportada",
        QSerialPort.SerialPortError.TimeoutError: "Timeout",
        QSerialPort.SerialPortError.NotOpenError: "Dispositivo no abierto"
    }

    def __init__(self):
        super().__init__()
        self.serial: Optional[QSerialPort] = None
        self.port_name: str = ""
        self._last_ports = []

        self._scan_timer = QTimer()
        self._scan_timer.timeout.connect(self.scan_ports)
        self._scan_timer.start(2000)

    def __del__(self):
        self.disconnect_serial()
        self._scan_timer.stop()

    def scan_ports(self):
        ports = [port.portName() for port in QSerialPortInfo.availablePorts()]
        if ports != self._last_ports:
            self._last_ports = ports
            self.ports_updated.emit(ports)

    def get_port_info(self, port_name: str) -> Dict[str, Any]:
        for port in QSerialPortInfo.availablePorts():
            if port.portName() == port_name:
                return {
                    'description': port.description(),
                    'manufacturer': port.manufacturer(),
                    'serial_number': port.serialNumber(),
                    'vendor_id': port.vendorIdentifier(),
                    'product_id': port.productIdentifier(),
                    'system_location': port.systemLocation()
                }
        return {}

    def connect_serial(self, port_name: str, settings: Optional[Dict] = None):
        if self.serial is None:
            self.serial = QSerialPort()
            self.serial.readyRead.connect(self._handle_ready_read)
            self.serial.errorOccurred.connect(self._handle_error)

        if self.serial.isOpen():
            self.disconnect_serial()

        self.serial.setPortName(port_name)
        self.port_name = port_name

        config = {**self.DEFAULT_SETTINGS, **(settings or {})}

        # Aplicar configuración correctamente para PyQt6
        self.serial.setBaudRate(config['baud_rate'])       # int
        self.serial.setDataBits(config['data_bits'])       # enum
        self.serial.setParity(config['parity'])            # enum
        self.serial.setStopBits(config['stop_bits'])       # enum
        self.serial.setFlowControl(config['flow_control']) # enum

        if self.serial.open(QIODevice.OpenModeFlag.ReadWrite):
            self.connection_changed.emit(True, port_name)
            self._scan_timer.stop()
        else:
            self.error_occurred.emit(f"Error al abrir {port_name}", port_name)
            self.serial.close()

    def disconnect_serial(self):
        if self.serial and self.serial.isOpen():
            port_name = self.port_name
            self.serial.close()
            self.port_name = ""
            self.connection_changed.emit(False, port_name)
            self._scan_timer.start(2000)

    def send_data(self, data: bytes):
        if self.serial and self.serial.isOpen():
            bytes_written = self.serial.write(data)
            if bytes_written == -1:
                self.error_occurred.emit("Error al escribir datos", self.port_name)
            elif bytes_written == len(data):
                self.data_sent.emit(data, self.port_name)
            else:
                self.error_occurred.emit(
                    f"Datos enviados parcialmente ({bytes_written}/{len(data)})",
                    self.port_name
                )

    def _handle_ready_read(self):
        if self.serial and self.serial.isOpen():
            data = bytes(self.serial.readAll())
            self.data_received.emit(data, self.port_name)

    def _handle_error(self, error):
        if error == QSerialPort.SerialPortError.NoError:
            return
        self.error_occurred.emit(
            self.ERROR_MAP.get(error, f"Error desconocido ({error})"),
            self.port_name
        )

    def is_connected(self) -> bool:
        return self.serial is not None and self.serial.isOpen()

    def get_current_settings(self) -> Dict[str, Any]:
        if not self.is_connected():
            return {}
        return {
            'baud_rate': self.serial.baudRate(),
            'data_bits': self.serial.dataBits(),
            'parity': self.serial.parity(),
            'stop_bits': self.serial.stopBits(),
            'flow_control': self.serial.flowControl()
        }


import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QComboBox, QLineEdit, QLabel
from PyQt6.QtCore import Qt
# from serial_manager import SerialManager  # tu clase optimizada

class SerialTestUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Manager Test")
        self.resize(500, 400)

        layout = QVBoxLayout(self)

        # Lista de puertos
        self.port_label = QLabel("Puerto:")
        self.port_combo = QComboBox()
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_combo)

        # Botón conectar
        self.btn_connect = QPushButton("Conectar")
        layout.addWidget(self.btn_connect)

        # Área de recepción de datos
        self.text_received = QTextEdit()
        self.text_received.setReadOnly(True)
        layout.addWidget(self.text_received)

        # Campo de envío
        self.input_send = QLineEdit()
        self.input_send.setPlaceholderText("Escribe algo para enviar...")
        layout.addWidget(self.input_send)

        # Botón enviar
        self.btn_send = QPushButton("Enviar")
        layout.addWidget(self.btn_send)

        # Instancia del SerialManager
        self.serial_manager = SerialManager()

        # Conexión de señales
        self.serial_manager.ports_updated.connect(self.update_ports)
        self.serial_manager.data_received.connect(self.on_data_received)
        self.serial_manager.data_sent.connect(self.on_data_sent)
        self.serial_manager.error_occurred.connect(self.on_error)
        self.serial_manager.connection_changed.connect(self.on_connection_changed)

        # Eventos UI
        self.btn_connect.clicked.connect(self.toggle_connection)
        self.btn_send.clicked.connect(self.send_data)

    def update_ports(self, ports):
        """Actualizar lista de puertos en el combo."""
        self.port_combo.clear()
        self.port_combo.addItems(ports)

    def toggle_connection(self):
        """Conectar o desconectar según el estado."""
        if self.serial_manager.is_connected():
            self.serial_manager.disconnect_serial()
        else:
            port = self.port_combo.currentText()
            if port:
                self.serial_manager.connect_serial(port)

    def send_data(self):
        """Enviar datos escritos por el usuario."""
        text = self.input_send.text().strip()
        if text and self.serial_manager.is_connected():
            self.serial_manager.send_data(text.encode("utf-8"))

    def on_data_received(self, data: bytes, port: str):
        """Mostrar datos recibidos."""
        self.text_received.append(f"< {data.decode(errors='ignore')}")

    def on_data_sent(self, data: bytes, port: str):
        """Confirmar datos enviados."""
        self.text_received.append(f"> {data.decode(errors='ignore')}")

    def on_error(self, message: str, port: str):
        """Mostrar errores."""
        self.text_received.append(f"[ERROR] {message}")

    def on_connection_changed(self, connected: bool, port: str):
        """Actualizar botón y estado."""
        if connected:
            self.btn_connect.setText("Desconectar")
            self.text_received.append(f"[INFO] Conectado a {port}")
        else:
            self.btn_connect.setText("Conectar")
            self.text_received.append(f"[INFO] Desconectado de {port}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SerialTestUI()
    win.show()
    sys.exit(app.exec())