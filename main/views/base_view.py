"""
Vista base para heredar en todas las vistas
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal
from main.utils.logger import Logger  # Asegúrate de que exista este archivo

from main.core.serial_manager import SerialManager  # Asegúrate de que exista este archivo

class BaseView(QWidget):
    """Clase base para todas las vistas"""
    
    # Señales comunes
    data_changed = pyqtSignal(dict)
    action_requested = pyqtSignal(str, dict)
    
    def __init__(self, serial_manager: SerialManager = None, parent=None):
        super().__init__(parent)
        
        #logger
        self.logger = Logger(self.__class__.__name__)
        
        # Serial manager opcional
        self.serial_manager = serial_manager
        self.layout = QVBoxLayout(self)
        
        self.setup_ui()

    def setup_ui(self):
        """Método para ser sobrescrito por las vistas hijas"""
        pass
    
    def refresh_data(self):
        """Actualiza los datos de la vista"""
        pass
    
    def clear_view(self):
        """Limpia la vista"""
        pass
