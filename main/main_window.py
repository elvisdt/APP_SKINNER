
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QSizePolicy, QMessageBox
)
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt

from main.utils.logger import Logger
from main.styles.styles import AppStyles
from main.components.side_menu import SideMenu
from main.components.status_bar import CustomStatusBar
from main.views.inicio_view import InicioView
from main.views.pnl_ctrl import PanelControlView
from main.views.reporte_view import ReporteView
from main.enums.menu_sections import MenuSection

from main.core.serial_port_model import SerialPortModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = Logger("MainWindow")

        self.serial_model = SerialPortModel()
         
        self.views = {}
        self.view_titles = {
            MenuSection.HOME: "Inicio",
            MenuSection.CONTROL: "Panel de Control",
            MenuSection.SETTINGS: "Configuración",
            MenuSection.REPORTS: "Reportes",
            MenuSection.LOGOUT: "Cerrar sesión",
        }
        
        self._init_ui()
        self._configure_window()
        self._init_views()
        self._connect_signals()
        
        self._connect_serial_signals()
        

    def _configure_window(self):
        
        screen = QGuiApplication.primaryScreen().availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # Dimensiones ideales para evitar advertencias
        target_width = min(1400, screen_width)
        target_height = min(800, screen_height)

        self.resize(int(target_width*0.8), int(target_height*0.8))

        # Centrar la ventana
        center_x = (screen_width - target_width) // 2
        center_y = (screen_height - target_height) // 2
        self.move(center_x, center_y)

        self.setWindowFlags(Qt.WindowType.Window)
        self.show()

    def _init_ui(self):
        self.setWindowTitle("Serial viwer Skinner")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        
        # Menú lateral
        self.side_menu = SideMenu()
        self.side_menu.menu_clicked.connect(self.change_view)
        self.side_menu.setMaximumWidth(200)
        

        # Contenido principal
        content_container = QWidget()
        
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Contenedor de vistas
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        # Barra de estado
        self.status_bar = CustomStatusBar(version="1.0.0")
        self.status_bar.setMaximumHeight(30)
        content_layout.addWidget(self.status_bar)
        
        
        main_layout.addWidget(self.side_menu)
        main_layout.addWidget(content_container)
        self.stacked_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def _init_views(self):
        self.views = {
            MenuSection.HOME: InicioView(),
            MenuSection.CONTROL: PanelControlView(self.serial_model),
            MenuSection.REPORTS: ReporteView(),
        }

        for view in self.views.values():
            self.stacked_widget.addWidget(view)

        self.change_view(MenuSection.HOME)

    def _connect_signals(self):
        for section, view in self.views.items():
            view.action_requested.connect(
                lambda action, data, s=section: self.handle_view_action(s, action, data)
            )

    def change_view(self, section: MenuSection):
        if section in self.views:
            view = self.views[section]
            self.stacked_widget.setCurrentWidget(view)

            if hasattr(view, "refresh_data"):
                view.refresh_data()

            title = self.view_titles.get(section, "Sin título")
            self.status_bar.set_view_name(title)
        else:
            self.logger.warning(f"[WARN] Vista no implementada: {section}")
            self.status_bar.set_view_name("Vista no disponible")

    def handle_view_action(self, section: MenuSection, action: str, data: dict):
        self.logger.info(f"[{section.name}] Acción solicitada: {action}")
        self.logger.debug(f"Datos recibidos: {data}")

    def _connect_serial_signals(self):
        """Conectar señales del modelo serial"""
        self.serial_model.connection_state_changed.connect(self._handle_serial_connection_change)
        self.serial_model.ports_list_updated.connect(self._update_serial_ports)
        self.serial_model.data_received.connect(self._handle_serial_data)
        self.serial_model.error_occurred.connect(self._handle_serial_error)
        self.serial_model.port_disconnected.connect(self._handle_port_disconnection)

    def _handle_serial_connection_change(self, connected: bool):
        """Manejar cambios en el estado de conexión"""
        self.status_bar.set_connection_status(connected)
        
        # Actualizar todas las vistas que muestren estado de conexión
        for view in self.views.values():
            if hasattr(view, 'update_connection_status'):
                view.update_connection_status(connected)

    def _update_serial_ports(self, ports: list):
        """Actualizar lista de puertos disponibles"""
        
        for view in self.views.values():
            if hasattr(view, 'update_ports_list'):
                view.update_ports_list(ports)

    def _handle_serial_data(self, data: str):
        """Manejar datos recibidos del puerto serial"""
        # Puedes enviar los datos a la vista activa o a todas
        self.logger.debug(f"data RX: {data}")
        # current_view = self.stacked_widget.currentWidget()
        # if hasattr(current_view, 'handle_serial_data'):
        #     current_view.handle_serial_data(data)

    def _handle_serial_error(self, error_msg: str):
        """Manejar errores del puerto serial"""
        
        self.logger.error(error_msg)
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Error-Serial Port")
        msg_box.setText(error_msg)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setStyleSheet(AppStyles.MESSAGEBOX_STYLE)
        msg_box.exec()
        

    def _handle_port_disconnection(self, port_name: str):
        """Manejar desconexión inesperada"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Desconexión")
        msg_box.setText(f"<b>El puerto {port_name} se ha desconectado </b>")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStyleSheet(AppStyles.MESSAGEBOX_STYLE)
        msg_box.exec()
        self._handle_serial_connection_change(False)
