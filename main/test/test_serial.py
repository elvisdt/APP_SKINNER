




import serial
import serial.tools.list_ports
from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
from typing import Optional, List


class SerialWorker(QObject):
    """
    Worker para manejar la comunicación serial en un hilo separado.
    """
    data_received = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)
    connection_status = pyqtSignal(bool)

    def __init__(self, port: str, baudrate: int = 9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial_connection: Optional[serial.Serial] = None
        self._is_running = False

    def open_connection(self) -> bool:
        """Abre la conexión serial."""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            self._is_running = True
            self.connection_status.emit(True)
            return True
        except serial.SerialException as e:
            self.error_occurred.emit(f"Error al abrir puerto: {str(e)}")
            self.connection_status.emit(False)
            return False

    def close_connection(self):
        """Cierra la conexión serial."""
        if self.serial_connection and self.serial_connection.is_open:
            self._is_running = False
            self.serial_connection.close()
        self.connection_status.emit(False)

    def send_data(self, data: str):
        """Envía datos por el puerto serial."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(data.encode('utf-8'))
            except serial.SerialException as e:
                self.error_occurred.emit(f"Error al enviar datos: {str(e)}")

    @pyqtSlot()
    def read_data(self):
        """Lee datos del puerto serial continuamente."""
        while self._is_running and self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.read(self.serial_connection.in_waiting)
                    self.data_received.emit(data)
            except serial.SerialException as e:
                self.error_occurred.emit(f"Error al leer datos: {str(e)}")
                self.close_connection()


class SerialManager(QObject):
    """
    Gestiona la comunicación serial y proporciona una interfaz para la UI.
    """
    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    connection_status = pyqtSignal(bool)
    available_ports_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.serial_worker: Optional[SerialWorker] = None
        self.worker_thread: Optional[QThread] = None

    def get_available_ports(self) -> List[str]:
        """Devuelve una lista de puertos seriales disponibles."""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.available_ports_updated.emit(ports)
        return ports

    def connect_serial(self, port: str, baudrate: int = 9600):
        """Inicia la conexión serial en un hilo separado."""
        if self.serial_worker is not None:
            self.disconnect_serial()

        self.worker_thread = QThread()
        self.serial_worker = SerialWorker(port, baudrate)

        # Mover worker al hilo
        self.serial_worker.moveToThread(self.worker_thread)

        # Conectar señales
        self.serial_worker.data_received.connect(self._handle_received_data)
        self.serial_worker.error_occurred.connect(self.error_occurred.emit)
        self.serial_worker.connection_status.connect(self.connection_status.emit)

        # Conectar señales del hilo
        self.worker_thread.started.connect(self.serial_worker.read_data)
        self.worker_thread.finished.connect(self.serial_worker.deleteLater)

        # Iniciar hilo
        self.worker_thread.start()

        # Intentar abrir conexión
        self.serial_worker.open_connection()

    def disconnect_serial(self):
        """Cierra la conexión serial y limpia los recursos."""
        if self.serial_worker is not None:
            self.serial_worker.close_connection()
            self.serial_worker = None

        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None

        self.connection_status.emit(False)

    def send_data(self, data: str):
        """Envía datos a través del puerto serial."""
        if self.serial_worker is not None:
            self.serial_worker.send_data(data)

    def _handle_received_data(self, data: bytes):
        """Procesa los datos recibidos del puerto serial."""
        try:
            decoded_data = data.decode('utf-8').strip()
            self.data_received.emit(decoded_data)
        except UnicodeDecodeError:
            self.error_occurred.emit("Error al decodificar los datos recibidos")



from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox, QTextEdit, QLineEdit
from PyQt6.QtCore import Qt


class SerialApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_manager = SerialManager()
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.setWindowTitle("Serial Communication")
        self.setGeometry(100, 100, 600, 400)

        # Widgets
        self.port_combo = QComboBox()
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.connect_btn = QPushButton("Conectar")
        self.disconnect_btn = QPushButton("Desconectar")
        self.disconnect_btn.setEnabled(False)
        self.refresh_btn = QPushButton("Actualizar Puertos")
        
        self.send_input = QLineEdit()
        self.send_btn = QPushButton("Enviar")
        
        self.received_data = QTextEdit()
        self.received_data.setReadOnly(True)
        
        # Layout
        layout = QVBoxLayout()
        
        control_layout = QVBoxLayout()
        control_layout.addWidget(self.refresh_btn)
        control_layout.addWidget(self.port_combo)
        control_layout.addWidget(self.baudrate_combo)
        control_layout.addWidget(self.connect_btn)
        control_layout.addWidget(self.disconnect_btn)
        
        send_layout = QVBoxLayout()
        send_layout.addWidget(self.send_input)
        send_layout.addWidget(self.send_btn)
        
        layout.addLayout(control_layout)
        layout.addWidget(self.received_data)
        layout.addLayout(send_layout)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Actualizar puertos al iniciar
        self.refresh_ports()

    def connect_signals(self):
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.connect_btn.clicked.connect(self.connect_serial)
        self.disconnect_btn.clicked.connect(self.disconnect_serial)
        self.send_btn.clicked.connect(self.send_data)
        
        self.serial_manager.data_received.connect(self.update_received_data)
        self.serial_manager.error_occurred.connect(self.show_error)
        self.serial_manager.connection_status.connect(self.update_connection_status)
        self.serial_manager.available_ports_updated.connect(self.update_ports_combo)

    def refresh_ports(self):
        self.serial_manager.get_available_ports()

    def update_ports_combo(self, ports):
        self.port_combo.clear()
        self.port_combo.addItems(ports)

    def connect_serial(self):
        port = self.port_combo.currentText()
        baudrate = int(self.baudrate_combo.currentText())
        self.serial_manager.connect_serial(port, baudrate)

    def disconnect_serial(self):
        self.serial_manager.disconnect_serial()

    def send_data(self):
        data = self.send_input.text()
        if data:
            self.serial_manager.send_data(data)
            self.send_input.clear()

    def update_received_data(self, data):
        self.received_data.append(f"Recibido: {data}")

    def show_error(self, error_msg):
        self.received_data.append(f"Error: {error_msg}")

    def update_connection_status(self, connected):
        self.connect_btn.setEnabled(not connected)
        self.disconnect_btn.setEnabled(connected)
        self.send_btn.setEnabled(connected)
        status = "Conectado" if connected else "Desconectado"
        self.statusBar().showMessage(f"Estado: {status}")


if __name__ == "__main__":
    app = QApplication([])
    window = SerialApp()
    window.show()
    app.exec()