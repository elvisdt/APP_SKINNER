import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QSpinBox, QDoubleSpinBox, QLabel, 
                             QComboBox, QGroupBox)
from PyQt6.QtCore import Qt
import random

from main.components.cust_plot import CustomScatterPlot

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba de CustomScatterPlot")
        self.setGeometry(100, 100, 1000, 700)
        
        # Crear el gráfico
        self.plot = CustomScatterPlot("Gráfico de Prueba")
        self.plot.add_series("Serie 1", "#FF0000")  # Rojo
        self.plot.add_series("Serie 2", "#00FF00")  # Verde
        self.plot.add_series("Serie 3", "#0000FF")  # Azul
        
        # Controles de prueba
        self._setup_controls()
        
        # Layout principal
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        
        # Panel de controles a la izquierda
        control_panel = QGroupBox("Controles")
        control_panel.setFixedWidth(300)
        control_panel.setLayout(QVBoxLayout())
        control_panel.layout().addWidget(self.control_widget)
        control_panel.layout().addStretch()
        
        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.plot)
        
        self.setCentralWidget(central_widget)
        
    def _setup_controls(self):
        self.control_widget = QWidget()
        layout = QVBoxLayout(self.control_widget)
        
        # Selector de serie
        self.series_combo = QComboBox()
        self.series_combo.addItems(["Serie 1", "Serie 2", "Serie 3"])
        layout.addWidget(QLabel("Serie:"))
        layout.addWidget(self.series_combo)
        
        # Controles para agregar puntos
        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(-100, 100)
        self.x_spin.setValue(0)
        
        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(-100, 100)
        self.y_spin.setValue(1)
        
        add_point_btn = QPushButton("Agregar Punto (X,Y)")
        add_point_btn.clicked.connect(self._add_point)
        
        layout.addWidget(QLabel("Coordenada X:"))
        layout.addWidget(self.x_spin)
        layout.addWidget(QLabel("Coordenada Y:"))
        layout.addWidget(self.y_spin)
        layout.addWidget(add_point_btn)
        
        # Botón para punto con tiempo automático
        timed_point_btn = QPushButton("Agregar Punto Temporal")
        timed_point_btn.clicked.connect(self._add_timed_point)
        layout.addWidget(timed_point_btn)
        
        # Botón para punto aleatorio
        random_point_btn = QPushButton("Agregar Punto Aleatorio")
        random_point_btn.clicked.connect(self._add_random_point)
        layout.addWidget(random_point_btn)
        
        # Controles de configuración
        config_group = QGroupBox("Configuración")
        config_group.setLayout(QVBoxLayout())
        
        self.max_points_spin = QSpinBox()
        self.max_points_spin.setRange(10, 5000)
        self.max_points_spin.setValue(500)
        self.max_points_spin.valueChanged.connect(self._change_max_points)
        
        reset_btn = QPushButton("Reiniciar Gráfico")
        reset_btn.clicked.connect(self.plot.reset_plot)
        
        config_group.layout().addWidget(QLabel("Máx. puntos:"))
        config_group.layout().addWidget(self.max_points_spin)
        config_group.layout().addWidget(reset_btn)
        
        layout.addWidget(config_group)
        
        # Botón para probar autoajuste
        stress_test_btn = QPushButton("Prueba de Estrés (50 pts)")
        stress_test_btn.clicked.connect(self._run_stress_test)
        layout.addWidget(stress_test_btn)
        
    def _add_point(self):
        serie = self.series_combo.currentText()
        x = self.x_spin.value()
        y = self.y_spin.value()
        self.plot.add_data_point(serie, x, y)
        
    def _add_timed_point(self):
        serie = self.series_combo.currentText()
        self.plot.register_timed_point(serie)
        
    def _add_random_point(self):
        serie = self.series_combo.currentText()
        x = random.uniform(0, 20)
        y = random.uniform(1, 10)
        self.plot.add_data_point(serie, x, y)
        
    def _change_max_points(self):
        self.plot.max_points = self.max_points_spin.value()
        
    def _run_stress_test(self):
        serie = self.series_combo.currentText()
        for _ in range(50):
            x = random.uniform(0, 100)
            y = random.uniform(0, 50)
            self.plot.add_data_point(serie, x, y)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     app.setStyle("Fusion")  # Mejor aspecto visual
    
#     window = TestWindow()
#     window.show()
    
#     sys.exit(app.exec())
    
    
    
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets

# # Create application and window
# app = QtWidgets.QApplication([])
# win = pg.GraphicsLayoutWidget(show=True, title="PyQtGraph Grid Example")

# # Add a plot
# plot = win.addPlot(title="Plot with Grid")
# plot.showGrid(x=True, y=True)  # Enable grid for both axes

# # Add some data
# x = [1, 2, 3, 4, 5]
# y = [10, 20, 15, 30, 25]
# plot.plot(x, y, pen='b', symbol='o')

# # Start the application
# app.exec()




from PyQt6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

class CustomPlotWidget(QtWidgets.QWidget):
    def __init__(self, title="Gráfico", x_label="Eje X", y_label="Eje Y", parent=None):
        super().__init__(parent)
        
        # Configuración del layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear el widget de gráfico
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        
        # Configuración básica del gráfico
        self.plot_widget.setBackground("w")
        self.plot_widget.setTitle(title, color="b", size="20pt")
        
        styles = {"color": "black", "font-size": "14px"}
        self.plot_widget.setLabel("left", y_label, **styles)
        self.plot_widget.setLabel("bottom", x_label, **styles)
        
        # Configurar la leyenda
        self.plot_widget.addLegend()
        
        # Configurar la grilla (método compatible con todas versiones)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.5)
        
        # Almacenar las series
        self.series = {}
        
        # Configuración inicial de los ejes
        self.x_range = (0, 10)
        self.y_range = (0, 100)
        self.plot_widget.setXRange(*self.x_range)
        self.plot_widget.setYRange(*self.y_range)
    
    def add_series(self, name, color="b", symbol="o", line_style=QtCore.Qt.PenStyle.SolidLine, line_width=2):
        """Añade una nueva serie al gráfico"""
        if name in self.series:
            raise ValueError(f"Ya existe una serie con el nombre '{name}'")
            
        pen = pg.mkPen(color=color, style=line_style, width=line_width)
        self.series[name] = {
            "x_data": [],
            "y_data": [],
            "pen": pen,
            "symbol": symbol,
            "color": color,
            "plot_item": None
        }
    
    def add_points(self, series_name, x_list, y_list):
        """Añade múltiples puntos a una serie existente"""
        if series_name not in self.series:
            raise ValueError(f"No existe la serie '{series_name}'")
            
        series = self.series[series_name]
        series["x_data"].extend(x_list)
        series["y_data"].extend(y_list)
        
        self._update_series_plot(series_name)
        self._adjust_ranges()
    
    def add_point(self, series_name, x, y):
        """Añade un punto a una serie existente"""
        self.add_points(series_name, [x], [y])
    
    def _update_series_plot(self, series_name):
        """Actualiza el gráfico de una serie específica"""
        series = self.series[series_name]
        
        # Eliminar el plot existente si hay uno
        if series["plot_item"] is not None:
            self.plot_widget.removeItem(series["plot_item"])
        
        # Crear nuevo plot si hay datos
        if series["x_data"] and series["y_data"]:
            series["plot_item"] = self.plot_widget.plot(
                series["x_data"],
                series["y_data"],
                name=series_name,
                pen=series["pen"],
                symbol=series["symbol"],
                symbolSize=8,
                symbolBrush=series["color"],
                symbolPen=series["pen"]
            )
    
    def _adjust_ranges(self):
        """Ajusta los rangos de los ejes automáticamente"""
        all_x = []
        all_y = []
        
        for series in self.series.values():
            if series["x_data"]:
                all_x.extend(series["x_data"])
            if series["y_data"]:
                all_y.extend(series["y_data"])
        
        if all_x:
            min_x, max_x = min(all_x), max(all_x)
            padding_x = max((max_x - min_x) * 0.1, 0.1)  # Mínimo 0.1 de padding
            self.plot_widget.setXRange(min_x - padding_x, max_x + padding_x)
        
        if all_y:
            min_y, max_y = min(all_y), max(all_y)
            padding_y = max((max_y - min_y) * 0.1, 0.1)  # Mínimo 0.1 de padding
            self.plot_widget.setYRange(min_y - padding_y, max_y + padding_y)
    
    def clear_series(self, series_name=None):
        """Limpia los datos de una serie específica o de todas las series"""
        if series_name is None:
            for name in list(self.series.keys()):
                self.clear_series(name)
        elif series_name in self.series:
            self.series[series_name]["x_data"] = []
            self.series[series_name]["y_data"] = []
            self._update_series_plot(series_name)
            self._adjust_ranges()
    
    def set_ranges(self, x_range=None, y_range=None):
        """Establece los rangos de los ejes manualmente"""
        if x_range is not None:
            self.x_range = x_range
            self.plot_widget.setXRange(*self.x_range)
        if y_range is not None:
            self.y_range = y_range
            self.plot_widget.setYRange(*self.y_range)
    
    def get_series_data(self, series_name):
        """Obtiene los datos de una serie específica"""
        if series_name not in self.series:
            raise ValueError(f"No existe la serie '{series_name}'")
        return self.series[series_name]["x_data"], self.series[series_name]["y_data"]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gráfico de Temperatura")
        self.resize(800, 600)
        
        # Crear widget personalizado
        self.plot = CustomPlotWidget(
            title="Temperature vs Time",
            x_label="Time (min)",
            y_label="Temperature (°C)"
        )
        self.setCentralWidget(self.plot)
        
        # Añadir series con diferentes estilos
        self.plot.add_series(
            "Sensor 1", 
            color="#3498db",  # Azul
            symbol="o",
            line_style=QtCore.Qt.PenStyle.SolidLine,
            line_width=2
        )
        
        self.plot.add_series(
            "Sensor 2", 
            color="#e74c3c",  # Rojo
            symbol="s",
            line_style=QtCore.Qt.PenStyle.DashLine,
            line_width=2
        )
        
        # Datos de ejemplo
        minutes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature_1 = [30, 32, 34, 32, 33, 31, 29, 32, 35, 30]
        temperature_2 = [32, 35, 40, 22, 38, 32, 27, 38, 32, 38]
        
        # Añadir todos los puntos de una vez (más eficiente)
        self.plot.add_points("Sensor 1", minutes, temperature_1)
        self.plot.add_points("Sensor 2", minutes, temperature_2)
        
        # Opcional: establecer rangos manuales
        # self.plot.set_ranges(x_range=(0, 15), y_range=(20, 45))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    
    # Establecer estilo visual
    app.setStyle("Fusion")
    
    # Configurar paleta de colores
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(240, 240, 240))
    app.setPalette(palette)
    
    main = MainWindow()
    main.show()
    app.exec()