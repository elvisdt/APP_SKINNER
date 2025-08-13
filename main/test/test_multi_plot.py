import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QTimer

# Importamos tus clases
# Aquí pondrías: from tu_modulo import CustomMultiPlot
from PyQt6.QtWidgets import QLabel, QGroupBox, QComboBox, QPushButton, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import mkPen, mkBrush


class SessionSelectorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        group = QGroupBox("Control de Sesiones")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f7f9fa;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                color: #2c3e50;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)

        layout = QVBoxLayout()

        # Selección de sesión
        layout.addWidget(QLabel("Sesión:"))
        self.session_combo = QComboBox()
        layout.addWidget(self.session_combo)

        # Selección de eventos
        layout.addWidget(QLabel("Eventos:"))
        self.events_list = QListWidget()
        self.events_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.events_list)

        # Botones de control
        self.btn_play = QPushButton("▶ Reproducir")
        self.btn_stop = QPushButton("⏹ Detener")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_play)
        btn_layout.addWidget(self.btn_stop)
        layout.addLayout(btn_layout)

        group.setLayout(layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(group)
        self.setLayout(main_layout)

    def add_session(self, session_name):
        self.session_combo.addItem(session_name)

    def add_event(self, event_name):
        item = QListWidgetItem(event_name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked)
        self.events_list.addItem(item)

    def get_selected_events(self):
        return [self.events_list.item(i).text() for i in range(self.events_list.count())
                if self.events_list.item(i).checkState() == Qt.CheckState.Checked]


class CustomMultiPlot(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackground("white")
        self.addLegend()
        self.series = {}

    def add_series(self, name, color):
        if name in self.series:
            return
        pen = mkPen(color, width=1.5)
        curve = self.plot([], [], pen=pen, name=name)
        self.series[name] = {"x": [], "y": [], "curve": curve}

    def add_data_point(self, name, x, y):
        if name not in self.series:
            raise ValueError(f"Serie {name} no existe")
        self.series[name]["x"].append(x)
        self.series[name]["y"].append(y)
        self.series[name]["curve"].setData(self.series[name]["x"], self.series[name]["y"])

    def reset_plot(self):
        for serie in self.series.values():
            serie["x"].clear()
            serie["y"].clear()
            serie["curve"].setData([], [])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualización de Sesiones")
        self.resize(900, 500)

        # Widgets
        self.selector = SessionSelectorWidget()
        self.plot = CustomMultiPlot()

        # Layout principal
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(self.selector, 1)
        layout.addWidget(self.plot, 3)
        self.setCentralWidget(container)

        # Datos simulados
        self._load_mock_data()

        # Conectar botones
        self.selector.btn_play.clicked.connect(self.start_playback)
        self.selector.btn_stop.clicked.connect(self.stop_playback)

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_playback)
        self.play_index = 0
        self.play_events = []

    def _load_mock_data(self):
        # Simular 2 sesiones con eventos
        self.selector.add_session("Sesión 1")
        self.selector.add_session("Sesión 2")

        events = ["Sensor A", "Sensor B", "Motor 1"]
        for e in events:
            self.selector.add_event(e)
            self.plot.add_series(e, pg.intColor(len(self.plot.series)))

        # Generar datos aleatorios
        self.data_sessions = {
            "Sesión 1": {e: [(i, random.uniform(0, 10)) for i in range(30)] for e in events},
            "Sesión 2": {e: [(i, random.uniform(0, 10)) for i in range(20)] for e in events},
        }

    def start_playback(self):
        self.plot.reset_plot()
        session = self.selector.session_combo.currentText()
        self.play_events = self.selector.get_selected_events()
        self.play_data = self.data_sessions[session]
        self.play_index = 0
        self.timer.start(100)  # velocidad de reproducción

    def stop_playback(self):
        self.timer.stop()

    def _update_playback(self):
        if not self.play_events:
            self.stop_playback()
            return
        if self.play_index >= len(next(iter(self.play_data.values()))):
            self.stop_playback()
            return
        for event in self.play_events:
            x, y = self.play_data[event][self.play_index]
            self.plot.add_data_point(event, x, y)
        self.play_index += 1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
