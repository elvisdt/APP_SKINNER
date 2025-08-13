import sys
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QSpinBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
import pyqtgraph as pg
from pyqtgraph import mkPen, mkBrush


class MultiSeriesPlotWidget(QWidget):
    sampling_rate_changed = pyqtSignal(int)  # Señal cuando cambia tasa de muestreo

    def __init__(self, title="Gráfico Multi-Serie", panel_title="Opciones", parent=None):
        super().__init__(parent)
        self.setObjectName("MultiSeriesPlotWidget")
        self.title = title
        self.panel_title = panel_title

        # Variables internas
        self.min_x = 0
        self.max_x = 30
        self.start_time = None
        self.data = {}
        self.max_points = 1000

        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)

        # Área de gráfico
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("transparent")
        self.plot_widget.setTitle(self.title, color="#2c3e50", size="14pt")
        self.plot_widget.setLabel("left", "Valores Y", color="#2c3e50", size="10pt")
        self.plot_widget.setLabel("bottom", "Valores X", color="#2c3e50", size="10pt")
        self.plot_widget.getAxis("left").setPen(mkPen(color="#7f8c8d", width=1.5))
        self.plot_widget.getAxis("bottom").setPen(mkPen(color="#7f8c8d", width=1.5))
        self.plot_widget.addLegend(offset=(10, 10), labelTextColor="#2c3e50", labelTextSize="9pt", frame=False)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.5)
        self.plot_widget.setXRange(self.min_x, self.max_x)
        self.plot_widget.setYRange(0, 10)
        self.plot_widget.setAntialiasing(True)
        main_layout.addWidget(self.plot_widget, stretch=4)

        # Panel lateral
        side_box = QGroupBox(self.panel_title)
        side_layout = QVBoxLayout(side_box)

        # Control tasa de muestreo
        form_layout = QFormLayout()
        self.sampling_spin = QSpinBox()
        self.sampling_spin.setRange(10, 5000)
        self.sampling_spin.setValue(1000)
        self.sampling_spin.setSingleStep(10)
        self.sampling_spin.valueChanged.connect(self.sampling_rate_changed.emit)
        form_layout.addRow(QLabel("Tasa (ms):"), self.sampling_spin)
        side_layout.addLayout(form_layout)

        # Contenedor para checkboxes
        self.series_checkboxes = {}
        self.checkboxes_layout = QVBoxLayout()
        side_layout.addLayout(self.checkboxes_layout)

        main_layout.addWidget(side_box, stretch=1)

    # ---------- Gestión de series ----------
    def add_series(self, name: str, color: str, style="line+scatter"):
        """Añade una nueva serie"""
        if name in self.data:
            return

        pen = mkPen(color, width=1.5)
        brush = mkBrush(color)

        curve = None
        scatter = None

        if style in ["line", "line+scatter"]:
            curve = self.plot_widget.plot([], [], name=name, pen=pen, antialias=True)
        if style in ["scatter", "line+scatter"]:
            scatter = pg.ScatterPlotItem([], [], symbol='o', size=8, brush=brush, pen=mkPen("#ffffff", width=1))
            self.plot_widget.addItem(scatter)

        self.data[name] = {
            "x": [], "y": [],
            "color": color, "style": style,
            "curve": curve, "scatter": scatter
        }

        # Checkbox para visibilidad
        checkbox = QCheckBox(name)
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(lambda state, sname=name: self.toggle_series_visibility(sname, state))
        self.series_checkboxes[name] = checkbox
        self.checkboxes_layout.addWidget(checkbox)

    def toggle_series_visibility(self, name, state):
        """Muestra u oculta una serie"""
        visible = state == 2
        serie = self.data.get(name)
        if serie["curve"]:
            serie["curve"].setVisible(visible)
        if serie["scatter"]:
            serie["scatter"].setVisible(visible)

    def show_all_series(self):
        """Muestra todas las series"""
        for name, cb in self.series_checkboxes.items():
            cb.setChecked(True)

    def hide_all_series(self):
        """Oculta todas las series"""
        for name, cb in self.series_checkboxes.items():
            cb.setChecked(False)

    # ---------- Agregado de datos ----------
    def add_data_point(self, name: str, x: float, y: float):
        if name not in self.data:
            raise ValueError(f"Serie '{name}' no existe.")
        serie = self.data[name]
        serie["x"].append(x)
        serie["y"].append(y)

        # Limitar tamaño
        if len(serie["x"]) > self.max_points:
            serie["x"] = serie["x"][-self.max_points:]
            serie["y"] = serie["y"][-self.max_points:]

        # Actualizar gráfico
        if serie["curve"]:
            serie["curve"].setData(serie["x"], serie["y"])
        if serie["scatter"]:
            serie["scatter"].setData(serie["x"], serie["y"])

        self._auto_adjust_ranges(x)

    def register_timed_point(self, name: str, y: float = None):
        if name not in self.data:
            raise ValueError(f"Serie '{name}' no existe.")
        if self.start_time is None:
            self.start_time = time.time()
        x = round(time.time() - self.start_time, 2)
        if y is None:
            y = len(self.data[name]["y"]) + 1
        self.add_data_point(name, x, y)

    # ---------- Utilidades ----------
    def _auto_adjust_ranges(self, current_x):
        all_y = [y for s in self.data.values() for y in s["y"]]
        max_y = max(all_y, default=5)
        y_margin = max(0.5, max_y * 0.1)
        self.max_x = max(current_x + 1, self.max_x)
        self.plot_widget.setYRange(0, max_y + y_margin)
        self.plot_widget.setXRange(self.min_x, self.max_x)

    def reset_plot(self):
        self.start_time = None
        self.min_x, self.max_x = 0, 30
        for serie in self.data.values():
            serie["x"].clear()
            serie["y"].clear()
            if serie["curve"]:
                serie["curve"].setData([], [])
            if serie["scatter"]:
                serie["scatter"].setData([], [])
        self.plot_widget.setYRange(0, 10)
        self.plot_widget.setXRange(self.min_x, self.max_x)

    def get_last_point(self, name: str):
        if name not in self.data or not self.data[name]["x"]:
            return None
        return self.data[name]["x"][-1], self.data[name]["y"][-1]

    def get_sampling_rate(self):
        return self.sampling_spin.value()
