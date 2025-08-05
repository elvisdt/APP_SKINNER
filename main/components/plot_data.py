import sys
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QColor
import pyqtgraph as pg
from pyqtgraph import mkPen, mkBrush

class PulseGraph(QWidget):
    def __init__(self, title="Eventos", parent=None):
        super().__init__(parent)
        self.setObjectName("PulseGraph")
        self.title = title
        
        # Crear el widget de gráfico directamente
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMouseEnabled(x=False, y=False)  # Desactiva zoom/arrastre
        # Desactiva menú contextual
        self.plot_widget.setMenuEnabled(False) 
        
        self.plot_widget.setMouseTracking(False)
        self.plot_widget.scene().sigMouseMoved.connect(self._block_mouse_events)
        
        # Variables para seguimiento del rango X
        self.min_x = 0
        self.max_x = 30  # Valor inicial
        
        self._ui_init()
        
    def _ui_init(self):
        # Estilo moderno con bordes redondeados
        self.setStyleSheet("""
            QWidget#PulseGraph {
                background-color: #ffffff;
                border-radius: 12px;
                border: 2px solid #bdc3c7;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

         

        # Configurar política de autoajuste
        self.plot_widget.enableAutoRange(axis='y')  # Autoajuste en ambos ejes
        

        layout.addWidget(self.plot_widget)
        
        # Configuración de fondo transparente para el área del gráfico
        self.plot_widget.setBackground("transparent")
        
        # Configurar título y etiquetas
        self.plot_widget.setTitle(self.title, color="#2c3e50", size="14pt")
        self.plot_widget.setLabel("left", "Eventos", color="#2c3e50", size="10pt")
        self.plot_widget.setLabel("bottom", "Tiempo (s)", color="#2c3e50", size="10pt")
        
        # Configurar ejes
        axis_pen = mkPen(color="#7f8c8d", width=1.5)
        self.plot_widget.getAxis("left").setPen(axis_pen)
        self.plot_widget.getAxis("bottom").setPen(axis_pen)
        
        # Configurar leyenda
        self.plot_widget.addLegend(
            offset=(10, 10),
            labelTextColor="#2c3e50",
            labelTextSize="9pt",
            frame=False
        )
        
        # Habilitar antialiasing para mejor calidad gráfica
        self.plot_widget.setAntialiasing(True)
        
        # Variables para el seguimiento de datos
        self.start_time = None
        self.data = {}
        self.max_points = 500
        
        # Configuración inicial de rangos
        self.plot_widget.setYRange(0, 10)
        self.plot_widget.setXRange(self.min_x, self.max_x)

        
        # Configurar grillas
        self.set_initial_limits()
        
        # Configurar grillas
        #self.set_grid_style()
        
    def add_series(self, name: str, color: str):
        """Añade una nueva serie de datos al gráfico"""
        if name in self.data:
            return

        pen = mkPen(color, width=2.5)
        brush = mkBrush(color)

        self.data[name] = {
            "x": [],
            "y": [],
            "count": 0,
            "color": color,
            "curve": self.plot_widget.plot(
                [], [],  # Inicializar con listas vacías
                name=name, 
                pen=pen,
                antialias=True
            ),
            "scatter": pg.ScatterPlotItem(
                [], [], 
                symbol='o', 
                size=8, 
                brush=brush,
                pen=mkPen(color="#ffffff", width=1)
            )
        }
        
        # Añadir el scatter plot al gráfico
        self.plot_widget.addItem(self.data[name]["scatter"])

    def register_pulse(self, name: str):
        """Registra un nuevo evento/pulso para una serie"""
        if name not in self.data:
            raise ValueError(f"Serie '{name}' no existe. Usa add_series() primero.")
        
        if self.start_time is None:
            raise RuntimeError("El tiempo base no ha sido iniciado. Llama a start_timer() primero.")

                
        elapsed = round(time.time() - self.start_time, 2)
        serie = self.data[name]
        
        # Incrementar contador
        serie["count"] += 1
        
        # Añadir nuevos puntos
        serie["x"].append(elapsed)
        serie["y"].append(serie["count"])
        
        # Limitar el número de puntos mostrados
        if len(serie["x"]) > self.max_points:
            serie["x"] = serie["x"][-self.max_points:]
            serie["y"] = serie["y"][-self.max_points:]
        
        # Actualizar gráfico
        serie["curve"].setData(serie["x"], serie["y"])
        serie["scatter"].setData(serie["x"], serie["y"])
        

        # Autoajustar rangos
        self._auto_adjust_ranges(elapsed)
        
    def _auto_adjust_ranges(self, current_time):
        """Ajusta los rangos mostrados"""
        # Calcular máximo Y con margen del 10%
        all_y = [y for s in self.data.values() for y in s["y"]]
        max_y = max(all_y, default=5)
        y_margin = max(0.5, max_y * 0.1)  # Mínimo 0.5 de margen
        
        # Ajustar eje X considerando los límites iniciales como mínimo
        if self.data:  # Si hay datos
            all_x = [x for s in self.data.values() for x in s["x"]]
            max_x = max(all_x) if all_x else current_time
            self.max_x = max(max_x + 1, self.max_x)  # Usar el mayor entre el cálculo y el valor inicial
        else:
            self.max_x = max(current_time + 1, self.max_x)

        # Aplicar rangos
        self.plot_widget.setYRange(0, max_y + y_margin)
        self.plot_widget.setXRange(self.min_x, self.max_x)
        
    def reset_graph(self):
        """Reinicia completamente el gráfico"""
        self.start_time = time.time()
        self.min_x = 0
        self.max_x = 30
        
        for serie in self.data.values():
            serie["x"].clear()
            serie["y"].clear()
            serie["count"] = 0
            serie["curve"].setData([], [])
            serie["scatter"].setData([], [])
        
        
        # Restablecer rangos iniciales
        self.plot_widget.setYRange(0, 10)
        self.plot_widget.setXRange(self.min_x, self.max_x)
    def start_timer(self):
        """Reinicia el tiempo base del gráfico"""
        self.start_time = time.time()

    def set_title(self, title: str):
        """Actualiza el título de la gráfica"""
        self.title = title
        self.plot_widget.setTitle(title, color="#2c3e50", size="14pt")
        
    def set_grid_style(self):
        """Configura las grillas con valores por defecto"""
        # Habilitar grillas con color y transparencia
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Configurar color de las grillas
        grid_pen = mkPen(color="#d5dbdb", width=0.8)
        self.plot_widget.getViewBox().setGridPen(grid_pen)
        
    def set_initial_limits(self, min_x=0, max_x=30):
        """Configura los límites iniciales del eje X"""
        self.min_x = min_x
        self.max_x = max_x
        self.plot_widget.setXRange(min_x, max_x)
    
    def _block_mouse_events(self, evt):
        """Bloquea eventos de mouse no deseados"""
        pass  # No hacer nada con los eventos de mouse
