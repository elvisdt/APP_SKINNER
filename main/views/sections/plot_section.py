from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QSpinBox
)
from PyQt6.QtCore import Qt
from main.styles.styles import AppStyles
from main.components.plot_data import PulseGraph
from main.components.cust_plot import CustomScatterPlot

class PlotGroupBox01(QGroupBox):
    def __init__(self, title="Gráficos en Tiempo Real", theme_color="#16a085"):
        super().__init__(title)
        self.setObjectName("PlotGroupBox")
        
        # Usar el estilo de la aplicación o un estilo personalizado
        if hasattr(AppStyles, 'groupbox_style'):
            self.setStyleSheet(AppStyles.groupbox_style(theme_color))
        else:
            self.setStyleSheet(f"""
                QGroupBox#PlotGroupBox {{
                    background-color: #f8f9fa;
                    border: 2px solid {theme_color};
                    border-radius: 14px;
                    margin-top: 10px;
                    padding-top: 15px;
                }}
                QGroupBox#PlotGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                    color: {theme_color};
                    font-weight: bold;
                }}
            """)
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(15)
        
        # Gráfico izquierdo con series predefinidas
        self.graph_left = PulseGraph("Palanca Izquierda")
        # self.graph_left.add_series("Presiones", "#3498db")  # Azul
        # self.graph_left.add_series("Recompensas", "#2ecc71")  # Verde
        
        # Gráfico derecho con series predefinidas
        self.graph_right = PulseGraph("Palanca Derecha")
        # self.graph_right.add_series("Presiones", "#e74c3c")  # Rojo
        # self.graph_right.add_series("Recompensas", "#f39c12")  # Naranja
        
        layout.addWidget(self.graph_left)
        layout.addWidget(self.graph_right)
        self.setLayout(layout)
    
    def register_left_pulse(self, series_name):
        """Registra un pulso en el gráfico izquierdo"""
        self.graph_left.register_pulse(series_name)
    
    def register_right_pulse(self, series_name):
        """Registra un pulso en el gráfico derecho"""
        self.graph_right.register_pulse(series_name)
    
    def reset_graphs(self):
        """Reinicia ambos gráficos"""
        self.graph_left.reset_graph()
        self.graph_right.reset_graph()


# # Versión alternativa con controles (eliminando PlotGroupBox01)
# class PlotGroupBoxWithControls(PlotGroupBox):
#     def __init__(self, title="Gráficos con Controles", theme_color="#16a085"):
#         super().__init__(title, theme_color)
#         self._add_controls()
    
#     def _add_controls(self):
#         # Crear controles
#         self.time_range_spin = QSpinBox()
#         self.time_range_spin.setRange(10, 120)
#         self.time_range_spin.setValue(30)
#         self.time_range_spin.setSuffix(" s")
        
#         self.reset_btn = QPushButton("Reiniciar")
#         self.reset_btn.clicked.connect(self.reset_graphs)
        
#         # Layout para controles
#         controls_layout = QHBoxLayout()
#         controls_layout.addWidget(QLabel("Rango de tiempo:"))
#         controls_layout.addWidget(self.time_range_spin)
#         controls_layout.addStretch()
#         controls_layout.addWidget(self.reset_btn)
        
#         # Layout principal vertical que incluye controles y gráficos
#         main_layout = QVBoxLayout()
#         main_layout.addLayout(controls_layout)
        
#         # Obtener el layout horizontal de gráficos de la clase padre
#         graphs_layout = self.layout()
#         self.setLayout(None)  # Eliminar el layout anterior
        
#         main_layout.addLayout(graphs_layout)
#         self.setLayout(main_layout)
        


class PlotGroupBox(QGroupBox):
    def __init__(self, title="Gráficos en Tiempo Real", theme_color="#16a085"):
        super().__init__(title)
        self.setObjectName("PlotGroupBox")
        
        # Usar el estilo de la aplicación o un estilo personalizado
        if hasattr(AppStyles, 'groupbox_style'):
            self.setStyleSheet(AppStyles.groupbox_style(theme_color))
        else:
            self.setStyleSheet(f"""
                QGroupBox#PlotGroupBox {{
                    background-color: #f8f9fa;
                    border: 2px solid {theme_color};
                    border-radius: 14px;
                    margin-top: 10px;
                    padding-top: 15px;
                }}
                QGroupBox#PlotGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                    color: {theme_color};
                    font-weight: bold;
                }}
            """)
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(15)
        
        # Gráfico izquierdo con series predefinidas
        self.graph_left = CustomScatterPlot("Palanca Izquierda")
        # self.graph_left.add_series("Presiones", "#3498db")  # Azul
        # self.graph_left.add_series("Recompensas", "#2ecc71")  # Verde
        
        # Gráfico derecho con series predefinidas
        self.graph_right = CustomScatterPlot("Palanca Derecha")
        # self.graph_right.add_series("Presiones", "#e74c3c")  # Rojo
        # self.graph_right.add_series("Recompensas", "#f39c12")  # Naranja
        
        layout.addWidget(self.graph_left)
        layout.addWidget(self.graph_right)
        self.setLayout(layout)
    
    def register_left_pulse(self, series_name, color: str ="#0000FF"):
        """Registra un pulso en el gráfico izquierdo"""
        self.graph_left.add_series(series_name,color)
        
    
    def register_right_pulse(self, series_name, color: str ="#0000FF"):
        """Registra un pulso en el gráfico derecho"""
        self.graph_right.add_series(series_name,color)
    
    def reset_graphs(self):
        """Reinicia ambos gráficos"""
        self.graph_left.reset_plot()
        self.graph_right.reset_plot()


