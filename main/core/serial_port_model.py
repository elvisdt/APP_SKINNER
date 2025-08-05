
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtCore import QIODevice


from datetime import datetime
from typing import List, Dict, Optional
from queue import Queue


class SerialPortModel(QObject):
    """Modelo mejorado para operaciones de puerto serial usando PyQt6."""
    
    # Señales
    connection_state_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    data_received = pyqtSignal(str)
    port_status_changed = pyqtSignal(dict)  # Nueva señal para estado detallado
    
    # Nuevas señales para monitoreo
    ports_list_updated = pyqtSignal(list)  # Emite lista de puertos disponibles
    connection_attempt_started = pyqtSignal(str)  # Emite cuando intenta conectarse
    port_disconnected = pyqtSignal(str)  # Emite cuando se desconecta
    
    def __init__(self):
        super().__init__()
        self.serial_port = QSerialPort()
        self.write_queue = Queue()
        self.connection_attempts = 0
        self.max_reconnect_attempts = 3
        self._last_error = ""  
        
        
        # Timer para monitoreo de conexión
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._monitor_connection)
        
        # Configuración por defecto
        self.default_config = {
            'port_name': 'COM3',
            'baud_rate': 115200,
            'data_bits': QSerialPort.DataBits.Data8,
            'parity': QSerialPort.Parity.NoParity,
            'stop_bits': QSerialPort.StopBits.OneStop,
            'flow_control': QSerialPort.FlowControl.NoFlowControl
        }
        
        # Conectar señales
        self.serial_port.errorOccurred.connect(self.handle_port_error)
        self.serial_port.readyRead.connect(self._handle_ready_read)
        
        
        # Timer para verificar puertos disponibles
        self.ports_check_timer = QTimer()
        self.ports_check_timer.timeout.connect(self.check_available_ports)
        self.ports_check_timer.start(1000)  # Verificar cada 1 segundos
        
        # Guardar última lista de puertos conocidos
        self.last_known_ports = []
        
        # Emitir estado inicial
        QTimer.singleShot(100, self._emit_initial_status)
        
        

    
    def _emit_initial_status(self):
        """Emite el estado inicial del puerto"""
        self.connection_state_changed.emit(False)
        self._update_port_status()
    
    def _monitor_connection(self):
        """Monitorea la conexión del puerto serial"""
        if self.serial_port.isOpen():
            # Verificar si el puerto sigue siendo válido
            current_port = self.serial_port.portName()
            available_ports = self.get_port_names()
            if current_port not in available_ports:
                self.handle_port_error(QSerialPort.SerialPortError.ResourceError)
        
        self._update_port_status()
    
    def _update_port_status(self):
        """Actualiza y emite el estado detallado del puerto"""
        status = {
            'connected': self.is_connected(),
            'port_name': self.serial_port.portName() if self.serial_port.portName() else "None",
            'baud_rate': self.serial_port.baudRate(),
            'bytes_available': self.serial_port.bytesAvailable() if self.is_connected() else 0,
            'error_string': self.serial_port.errorString(),
            'last_error': self._last_error
        }
        self.port_status_changed.emit(status)
    
    def _handle_ready_read(self):
        """Maneja los datos entrantes cuando están disponibles"""
        try:
            data = self.read_data()
            if data:
                self.data_received.emit(data)
        except Exception as e:
            self.error_occurred.emit(f"Error reading data: {str(e)}")
    

            
    def handle_port_error(self, error: 'QSerialPort.SerialPortError'):
        """Maneja errores del puerto serial con mensajes detallados"""
        error_messages = {
            QSerialPort.SerialPortError.NoError: "",
            QSerialPort.SerialPortError.DeviceNotFoundError: "Dispositivo no encontrado",
            QSerialPort.SerialPortError.PermissionError: "Permisos denegados - puerto ocupado",
            QSerialPort.SerialPortError.OpenError: "Error al abrir puerto",
            QSerialPort.SerialPortError.ResourceError: "Dispositivo desconectado",
            QSerialPort.SerialPortError.WriteError: "Error de escritura",
            QSerialPort.SerialPortError.ReadError: "Error de lectura",
            QSerialPort.SerialPortError.UnknownError: "Error desconocido",
            QSerialPort.SerialPortError.TimeoutError: "Timeout de operación",
            QSerialPort.SerialPortError.UnsupportedOperationError: "Operación no soportada"
        }
        
        message = error_messages.get(error, f"Error no manejado: {error}")
        self._last_error = message
        
        if message:
            self.error_occurred.emit(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
        # Manejo especial para desconexión
        if error == QSerialPort.SerialPortError.ResourceError:
            was_open = self.serial_port.isOpen()
            self.serial_port.close()
            if was_open:
                self.connection_state_changed.emit(False)
                self.error_occurred.emit("Puerto desconectado inesperadamente")

    def get_available_ports(self) -> List[Dict]:
        """Obtiene lista de puertos seriales disponibles con información detallada"""
        ports = []
        for port_info in QSerialPortInfo.availablePorts():
            port_data = {
                'name': port_info.portName(),
                'description': port_info.description(),
                'manufacturer': port_info.manufacturer(),
                'system_location': port_info.systemLocation(),
                'vendor_id': port_info.vendorIdentifier(),
                'product_id': port_info.productIdentifier()
            }
            ports.append(port_data)
        return ports
    
    def get_port_names(self) -> List[str]:
        """Obtiene solo los nombres de los puertos disponibles"""
        return [port.portName() for port in QSerialPortInfo.availablePorts()]
    
    def get_ports_info(self) -> List[dict]:
        """Obtiene información detallada de todos los puertos disponibles"""
        ports_info = []
        for port in QSerialPortInfo.availablePorts():
            info = {
                'name': port.portName(),
                'description': port.description(),
                'manufacturer': port.manufacturer(),
                'serial_number': port.serialNumber(),
                'vendor_id': port.vendorIdentifier(),
                'product_id': port.productIdentifier(),
                'system_location': port.systemLocation()
            }
            ports_info.append(info)
        return ports_info
    
    def get_port_details(self, port_name: str) -> dict:
        """Obtiene información detallada de un puerto específico"""
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
    
    def configure_port(self, config: Optional[Dict] = None) -> bool:
        """Configura el puerto serial con los ajustes dados"""
        if config is None:
            config = self.default_config.copy()
        
        self.connection_attempt_started.emit(config['port_name'])
        
        try:
            # Cerrar puerto si está abierto
            if self.serial_port.isOpen():
                self.serial_port.close()
            
            # Configurar puerto
            self.serial_port.setPortName(config['port_name'])
            
            # Configurar baud rate
            if isinstance(config['baud_rate'], QSerialPort.BaudRate):
                self.serial_port.setBaudRate(config['baud_rate'])
            else:
                self.serial_port.setBaudRate(int(config['baud_rate']))
            
            # Configuraciones del puerto
            self.serial_port.setDataBits(config.get('data_bits', QSerialPort.DataBits.Data8))
            self.serial_port.setParity(config.get('parity', QSerialPort.Parity.NoParity))
            self.serial_port.setStopBits(config.get('stop_bits', QSerialPort.StopBits.OneStop))
            self.serial_port.setFlowControl(config.get('flow_control', QSerialPort.FlowControl.NoFlowControl))
            
            # Intentar abrir puerto
            if self.serial_port.open(QIODevice.OpenModeFlag.ReadWrite):
                self.connection_state_changed.emit(True)
                self.connection_attempts = 0
                self._last_error = ""
                
                # Iniciar monitoreo
                self.monitor_timer.start(2000)  # Cada 2 segundos
                
                return True
            else:
                error_msg = f"Failed to open {config['port_name']}: {self.serial_port.errorString()}"
                self.error_occurred.emit(error_msg)
                self._last_error = error_msg
                return False
        
        except Exception as e:
            error_msg = f"Configuration error: {str(e)}"
            self.connection_state_changed.emit(False)
            self.error_occurred.emit(error_msg)
            self._last_error = error_msg
            return False
    
    def connect_default(self) -> bool:
        """Conecta usando la configuración por defecto (COM3, 115200)"""
        return self.configure_port(self.default_config)
    
    def auto_connect(self) -> bool:
        """Intenta conectarse automáticamente al primer puerto disponible"""     
        available_ports = self.get_port_names()
        if not available_ports:
            self.error_occurred.emit("No hay puertos seriales disponibles")
            return False
        
        for port in available_ports:
            port_details = self.get_port_details(port)
            # print(f"PORT: {port} with details: {port_details}")
            description = port_details.get('description', '')
            if description.lower() == 'dispositivo serie usb':
                config = self.default_config.copy()
                config['port_name'] = port  
                if self.configure_port(config):
                    return True
            
        # Si no, intentar con el primer puerto disponible
        # config = self.default_config.copy()
        # config['port_name'] = available_ports[0]
        # return self.configure_port(config)
        return False
    
    # Modificar el método close_port para emitir señales
    def close_port(self) -> None:
        """Cierra el puerto serial si está abierto"""
        port_name = self.serial_port.portName() if self.is_connected() else ""
        
        self.monitor_timer.stop()
        if self.serial_port.isOpen():
            self.serial_port.close()
            self.connection_state_changed.emit(False)
            self._last_error = ""
            if port_name:
                self.port_disconnected.emit(port_name)
                
                
    def write_data(self, data: str, add_newline: bool = True) -> bool:
        """Escribe datos al puerto serial"""
        if not self.serial_port.isOpen():
            self.error_occurred.emit("Puerto no conectado")
            return False
        
        try:
            if add_newline and not data.endswith('\n'):
                data += '\n'
            
            bytes_written = self.serial_port.write(data.encode('utf-8'))
            if bytes_written == -1:
                self.error_occurred.emit("Error al escribir datos")
                return False
            
            # Esperar a que se escriban los datos
            if not self.serial_port.waitForBytesWritten(3000):
                self.error_occurred.emit("Timeout escribiendo datos")
                return False
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Write error: {str(e)}")
            return False
    
    def read_data(self) -> Optional[str]:
        """Lee datos del puerto serial si están disponibles"""
        try:
            if self.serial_port.isOpen() and self.serial_port.bytesAvailable() > 0:
                raw_data = self.serial_port.readAll()
                if raw_data.isEmpty():
                    return None
                
                data = raw_data.data().decode('utf-8', errors='ignore')
                return data if data else None
            return None
            
        except Exception as e:
            self.error_occurred.emit(f"Read error: {str(e)}")
            return None
    
    def read_line(self) -> Optional[str]:
        """Lee una línea completa del puerto serial"""
        try:
            if self.serial_port.isOpen() and self.serial_port.canReadLine():
                line = self.serial_port.readLine().data().decode('utf-8', errors='ignore').strip()
                return line if line else None
            return None
        except Exception as e:
            self.error_occurred.emit(f"ReadLine error: {str(e)}")
            return None

    def is_connected(self) -> bool:
        """Verifica si el puerto está actualmente abierto"""
        return self.serial_port.isOpen()

    def flush_buffers(self) -> None:
        """Limpia los buffers del puerto serial"""
        if self.serial_port.isOpen():
            self.serial_port.clear(QSerialPort.Direction.AllDirections)
    
    def get_port_info(self) -> Dict:
        """Obtiene información detallada del puerto actual"""
        if not self.is_connected():
            return {}
        
        return {
            'port_name': self.serial_port.portName(),
            'baud_rate': self.serial_port.baudRate(),
            'data_bits': self.serial_port.dataBits(),
            'parity': self.serial_port.parity(),
            'stop_bits': self.serial_port.stopBits(),
            'flow_control': self.serial_port.flowControl(),
            'bytes_available': self.serial_port.bytesAvailable(),
            'is_sequential': self.serial_port.isSequential(),
            'error_string': self.serial_port.errorString()
        }
        
    def check_available_ports(self):
        """Verifica los puertos disponibles y emite señales si hay cambios"""
        current_ports = self.get_port_names()
        
        # Si hay cambios en la lista de puertos
        if current_ports != self.last_known_ports:
            self.last_known_ports = current_ports
            self.ports_list_updated.emit(current_ports)
            
            # Si el puerto actualmente conectado desapareció
            if (self.is_connected() and 
                self.serial_port.portName() not in current_ports):
                self.close_port()
                self.port_disconnected.emit(self.serial_port.portName())
                