import sys
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QColor
import pyqtgraph as pg
from pyqtgraph import mkPen, mkBrush

class CustomScatterPlot(QWidget):
    def __init__(self, title="Gráfico de Puntos", parent=None):
        super().__init__(parent)
        self.setObjectName("CustomScatterPlot")
        self.title = title
        
        # Crear el widget de gráfico
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.setMouseTracking(False)
        self.plot_widget.scene().sigMouseMoved.connect(self._block_mouse_events)
        
        # Variables para seguimiento del rango
        self.min_x = 0
        self.max_x = 30
        self._ui_init()
        
    def _ui_init(self):
        self.setStyleSheet("""
            QWidget#CustomScatterPlot {
                background-color: #ffffff;
                border-radius: 12px;
                border: 2px solid #bdc3c7;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        layout.addWidget(self.plot_widget)
        
        # Configuración del gráfico
        self.plot_widget.setBackground("transparent")
        self.plot_widget.setTitle(self.title, color="#2c3e50", size="14pt")
        self.plot_widget.setLabel("left", "Valores Y", color="#2c3e50", size="10pt")
        self.plot_widget.setLabel("bottom", "Valores X", color="#2c3e50", size="10pt")
        
        # Estilo de ejes
        axis_pen = mkPen(color="#7f8c8d", width=1.5)
        self.plot_widget.getAxis("left").setPen(axis_pen)
        self.plot_widget.getAxis("bottom").setPen(axis_pen)
        
        # Leyenda
        self.plot_widget.addLegend(offset=(10, 10), labelTextColor="#2c3e50", labelTextSize="9pt", frame=False)
        self.plot_widget.setAntialiasing(True)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.5)
        
        # Datos y configuración
        self.start_time = None
        self.data = {}
        self.max_points = 1000
        self.plot_widget.setYRange(0, 10)
        self.plot_widget.setXRange(self.min_x, self.max_x)
        self.set_initial_limits()
    
    def add_series(self, name: str, color: str):
        """Añade una nueva serie de datos al gráfico"""
        if name in self.data:
            return

        pen = mkPen(color, width=1.5)
        brush = mkBrush(color)

        self.data[name] = {
            "x": [],
            "y": [],
            "color": color,
            "curve": self.plot_widget.plot([], [], name=name, pen=pen, antialias=True),
            "scatter": pg.ScatterPlotItem([], [], symbol='o', size=8, brush=brush, pen=mkPen("#ffffff", width=1))
        }
        self.plot_widget.addItem(self.data[name]["scatter"])

    def add_data_point(self, name: str, x: float, y: float):
        """
        Agrega un punto con coordenadas específicas
        Args:
            name: Nombre de la serie
            x: Coordenada X del punto
            y: Coordenada Y del punto
        """
        if name not in self.data:
            raise ValueError(f"Serie '{name}' no existe. Primero debe agregarla con add_series()")
            
        serie = self.data[name]
        serie["x"].append(x)
        serie["y"].append(y)
        
        # Limitar puntos máximos
        if len(serie["x"]) > self.max_points:
            serie["x"] = serie["x"][-self.max_points:]
            serie["y"] = serie["y"][-self.max_points:]
        
        # Actualizar gráfico
        serie["curve"].setData(serie["x"], serie["y"])
        serie["scatter"].setData(serie["x"], serie["y"])
        self._auto_adjust_ranges(max(serie["x"]) if serie["x"] else x)

    def register_timed_point(self, name: str, y: float = None):
        """
        Registra un punto usando el tiempo actual como coordenada X
        Args:
            name: Nombre de la serie
            y: Valor Y (opcional, si no se provee se autoincrementa)
        """
        if name not in self.data:
            raise ValueError(f"Serie '{name}' no existe")
            
        if self.start_time is None:
            self.start_time = time.time()
            
        x = round(time.time() - self.start_time, 2)
        serie = self.data[name]
        
        # Si no se especifica Y, usar conteo autoincremental
        if y is None:
            y = len(serie["y"]) + 1 if serie["y"] else 1
        
        self.add_data_point(name, x, y)

    def _auto_adjust_ranges(self, current_x):
        """Ajusta automáticamente los rangos del gráfico"""
        # Ajuste eje Y
        all_y = [y for s in self.data.values() for y in s["y"]]
        max_y = max(all_y, default=5)
        y_margin = max(0.5, max_y * 0.1)
        
        # Ajuste eje X
        if self.data:
            all_x = [x for s in self.data.values() for x in s["x"]]
            max_x = max(all_x) if all_x else current_x
            self.max_x = max(max_x + 1, self.max_x)

        self.plot_widget.setYRange(0, max_y + y_margin)
        self.plot_widget.setXRange(self.min_x, self.max_x)

    def reset_plot(self):
        """Reinicia completamente el gráfico"""
        self.start_time = None
        self.min_x = 0
        self.max_x = 30
        
        for serie in self.data.values():
            serie["x"].clear()
            serie["y"].clear()
            serie["curve"].setData([], [])
            serie["scatter"].setData([], [])
        
        self.plot_widget.setYRange(0, 10)
        self.plot_widget.setXRange(self.min_x, self.max_x)

    def set_title(self, title: str):
        """Actualiza el título del gráfico"""
        self.title = title
        self.plot_widget.setTitle(title, color="#2c3e50", size="14pt")
        
    def set_grid_style(self, visible=True, color="#d5dbdb", alpha=0.3):
        """Configura el estilo de la grilla"""
        self.plot_widget.showGrid(x=visible, y=visible, alpha=alpha)
        self.plot_widget.getViewBox().setGridPen(mkPen(color, width=0.8))
    
    def set_initial_limits(self, min_x=0, max_x=30):
        """Configura los límites iniciales de los ejes"""
        self.min_x = min_x
        self.max_x = max_x
        self.plot_widget.setXRange(min_x, max_x)
    
    
    def get_last_point(self, name: str):
        """
        Devuelve el último punto (x, y) añadido a la serie indicada.
        """
        if name not in self.data:
            raise ValueError(f"La serie '{name}' no existe")
        
        if not self.data[name]["x"]:
            return None  # La serie está vacía
        
        return (
            self.data[name]["x"][-1],
            self.data[name]["y"][-1]
        )


    def _block_mouse_events(self, evt):
        """Bloquea eventos de mouse no deseados"""
        pass


    