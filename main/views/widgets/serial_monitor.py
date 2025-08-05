from PyQt6.QtCore import QTimer, QObject, pyqtSignal

from main.core.serial_model import SerialPortModel

class SerialMonitor(QObject):
    ports_updated = pyqtSignal(list)
    status_changed = pyqtSignal(bool)

    def __init__(self, serial_model:SerialPortModel, interval_ms=2000):
        super().__init__()
        self.serial_model = serial_model
        self.timer = QTimer()
        self.timer.timeout.connect(self.scan_ports)
        self.timer.start(interval_ms)
        self.last_ports = []

    def scan_ports(self):
        ports = self.serial_model.get_port_names()
        if ports != self.last_ports:
            self.last_ports = ports
            self.ports_updated.emit(ports)

    def connect(self, port_name):
        success = self.serial_model.connect(port_name)
        self.status_changed.emit(success)
        return success

    def disconnect(self):
        self.serial_model.disconnect()
        self.status_changed.emit(False)
