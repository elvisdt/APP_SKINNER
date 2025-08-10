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
        self.close_port()
        self._scan_timer.stop()

    def scan_ports(self):
        ports = [port.portName() for port in QSerialPortInfo.availablePorts()]
        if ports != self._last_ports:
            self._last_ports = ports
            self.ports_updated.emit(ports)
            
    def get_list_ports(self) -> list:
        """Devuelve una lista de puertos seriales disponibles."""
        return [port.portName() for port in QSerialPortInfo.availablePorts()]

        
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

    def open_port(self, port_name: str, settings: Optional[Dict] = None):
        if self.serial is None:
            self.serial = QSerialPort()
            self.serial.readyRead.connect(self._handle_ready_read)
            self.serial.errorOccurred.connect(self._handle_error)

        if self.serial.isOpen():
            self.close_port()

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

    def close_port(self):
        if self.serial and self.serial.isOpen():
            port_name = self.port_name
            self.serial.close()
            self.port_name = ""
            self.connection_changed.emit(False, port_name)
            self._scan_timer.start(2000)

    # def send_data(self, data: bytes):
    #     if self.serial and self.serial.isOpen():
    #         bytes_written = self.serial.write(data)
    #         if bytes_written == -1:
    #             self.error_occurred.emit("Error al escribir datos", self.port_name)
    #         elif bytes_written == len(data):
    #             self.data_sent.emit(data, self.port_name)
    #         else:
    #             self.error_occurred.emit(
    #                 f"Datos enviados parcialmente ({bytes_written}/{len(data)})",
    #                 self.port_name
    #             )
    def send_data_str(self, data: str) -> None:
        """Envía un string con salto de línea automático (\\n) por el puerto serial."""
        if not self.serial or not self.serial.isOpen():
            return

        if not data.endswith('\n'):
            data += '\n'  # Añade salto de línea si no existe
        
        self.send_data_bytes(data.encode('utf-8'))  # Reutiliza el método de bytes

    def send_data_bytes(self, data: bytes) -> None:
        """Envía datos en formato bytes (sin modificación) por el puerto serial."""
        if not self.serial or not self.serial.isOpen():
            return

        bytes_written = self.serial.write(data)
        
        if bytes_written == -1:
            self.error_occurred.emit("Error al escribir datos", self.port_name)
        elif bytes_written == len(data):
            # Emite bytes o str según el método llamado
            if isinstance(data, bytes):
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

    # def _handle_error(self, error):
    #     if error == QSerialPort.SerialPortError.NoError:
    #         return
    #     self.error_occurred.emit(
    #         self.ERROR_MAP.get(error, f"Error desconocido ({error})"),
    #         self.port_name
    #     )
    def _handle_error(self, error):
        if error == QSerialPort.SerialPortError.NoError:
            return
        
        error_msg = self.ERROR_MAP.get(error, f"Error desconocido ({error})")
        self.error_occurred.emit(error_msg, self.port_name)
        
        # Cerrar automáticamente en errores críticos
        if error in (QSerialPort.SerialPortError.ResourceError,
                    QSerialPort.SerialPortError.DeviceNotFoundError):
            self.close_port()
        
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
