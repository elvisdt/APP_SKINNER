from PyQt6.QtCore import QTimer
import pyqtgraph as pg
from pyqtgraph import mkPen, mkBrush
from typing import Dict, List, Optional, Tuple
import numpy as np

from PyQt6 import QtCore  # Para los estilos de línea
from pyqtgraph import mkPen  # Para crear el objeto Pen


class DynamicMultiPlot(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_plot()
        self.series: Dict[str, dict] = {}
        self.playback_speed = 1.0
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self._playback_step)
        self.current_frame = 0
        self.max_frames = 0
        self.is_playing = False

    def setup_plot(self):
        """Configuración inicial del gráfico"""
        self.setBackground("white")
        self.addLegend()
        self.showGrid(x=True, y=True, alpha=0.3)
        self.setLabel('left', 'Valores')
        self.setLabel('bottom', 'Tiempo')
        self.setTitle("Gráfico Dinámico Multi-Series")

    def add_series(self, name: str, color: str = '#3498db', 
                 line_style: str = 'solid', width: float = 1.5,
                 symbol: Optional[str] = None, symbol_size: int = 7,
                 visible: bool = True):
        """Añade una nueva serie al gráfico"""
        if name in self.series:
            return

        # Configurar estilo de línea
        line_styles = {
            'solid': QtCore.Qt.PenStyle.SolidLine,
            'dashed': QtCore.Qt.PenStyle.DashLine,
            'dotted': QtCore.Qt.PenStyle.DotLine,
            'dash-dot': QtCore.Qt.PenStyle.DashDotLine
        }

        pen = mkPen(
            color=color,
            width=width,
            style=line_styles.get(line_style, QtCore.Qt.PenStyle.SolidLine)
        )

        # Configurar símbolo si se especifica
        symbol_pen = mkPen(color=color, width=1)
        symbol_brush = mkBrush(color=color)

        # Crear curva
        curve = self.plot(
            [], [], 
            pen=pen,
            name=name,
            symbol=symbol,
            symbolSize=symbol_size,
            symbolPen=symbol_pen,
            symbolBrush=symbol_brush,
            visible=visible
        )

        self.series[name] = {
            'x_data': [],
            'y_data': [],
            'curve': curve,
            'visible': visible,
            'color': color,
            'line_style': line_style,
            'width': width,
            'symbol': symbol,
            'symbol_size': symbol_size
        }

    def update_series_style(self, name: str, **kwargs):
        """Actualiza el estilo de una serie existente"""
        if name not in self.series:
            raise ValueError(f"Serie {name} no existe")

        serie = self.series[name]
        
        # Actualizar propiedades si se proporcionan
        if 'color' in kwargs:
            serie['color'] = kwargs['color']
        if 'line_style' in kwargs:
            serie['line_style'] = kwargs['line_style']
        if 'width' in kwargs:
            serie['width'] = kwargs['width']
        if 'symbol' in kwargs:
            serie['symbol'] = kwargs['symbol']
        if 'symbol_size' in kwargs:
            serie['symbol_size'] = kwargs['symbol_size']
        
        # Recrear la curva con los nuevos estilos
        pen = mkPen(
            color=serie['color'],
            width=serie['width'],
            style=serie['line_style']
        )
        
        self.removeItem(serie['curve'])
        serie['curve'] = self.plot(
            serie['x_data'],
            serie['y_data'],
            pen=pen,
            name=name,
            symbol=serie['symbol'],
            symbolSize=serie['symbol_size'],
            symbolPen=mkPen(color=serie['color']),
            symbolBrush=mkBrush(color=serie['color']),
            visible=serie['visible']
        )

    def add_data(self, name: str, x: List[float], y: List[float]):
        """Añade datos a una serie existente"""
        if name not in self.series:
            raise ValueError(f"Serie {name} no existe")

        self.series[name]['x_data'].extend(x)
        self.series[name]['y_data'].extend(y)
        self._update_series_display(name)
        self._update_max_frames()

    def add_data_point(self, name: str, x: float, y: float):
        """Añade un punto de datos a una serie"""
        self.add_data(name, [x], [y])

    def set_series_visibility(self, name: str, visible: bool):
        """Muestra u oculta una serie"""
        if name not in self.series:
            raise ValueError(f"Serie {name} no existe")
        
        self.series[name]['visible'] = visible
        self.series[name]['curve'].setVisible(visible)

    def _update_series_display(self, name: str):
        """Actualiza la visualización de una serie"""
        serie = self.series[name]
        if serie['visible']:
            serie['curve'].setData(serie['x_data'], serie['y_data'])

    def _update_max_frames(self):
        """Actualiza el número máximo de frames basado en los datos"""
        self.max_frames = max(
            (len(serie['x_data']) for serie in self.series.values()),
            default=0
        )

    def reset_plot(self):
        """Limpia todos los datos del gráfico"""
        for serie in self.series.values():
            serie['x_data'].clear()
            serie['y_data'].clear()
            serie['curve'].setData([], [])
        self.current_frame = 0
        self.max_frames = 0

    def clear_series(self, name: str):
        """Limpia los datos de una serie específica"""
        if name not in self.series:
            raise ValueError(f"Serie {name} no existe")
        
        self.series[name]['x_data'].clear()
        self.series[name]['y_data'].clear()
        self.series[name]['curve'].setData([], [])
        self._update_max_frames()

    # Funcionalidad de reproducción (playback)
    def start_playback(self, speed: float = 1.0):
        """Inicia la reproducción animada de los datos"""
        self.playback_speed = speed
        self.current_frame = 0
        self.is_playing = True
        self.playback_timer.start(50)  # Actualizar cada 50ms

    def stop_playback(self):
        """Detiene la reproducción"""
        self.is_playing = False
        self.playback_timer.stop()

    def pause_playback(self):
        """Pausa la reproducción"""
        self.is_playing = False
        self.playback_timer.stop()

    def _playback_step(self):
        """Avanza un paso en la reproducción"""
        if not self.is_playing or self.current_frame >= self.max_frames:
            self.stop_playback()
            return

        for name, serie in self.series.items():
            if serie['visible'] and self.current_frame < len(serie['x_data']):
                # Mostrar datos hasta el frame actual
                x_data = serie['x_data'][:self.current_frame+1]
                y_data = serie['y_data'][:self.current_frame+1]
                serie['curve'].setData(x_data, y_data)

        self.current_frame += int(self.playback_speed)
        self.repaint()

    def set_current_frame(self, frame: int):
        """Establece el frame actual para visualización manual"""
        frame = max(0, min(frame, self.max_frames-1))
        self.current_frame = frame
        
        for name, serie in self.series.items():
            if serie['visible']:
                x_data = serie['x_data'][:frame+1]
                y_data = serie['y_data'][:frame+1]
                serie['curve'].setData(x_data, y_data)
        
        self.repaint()

    def export_to_csv(self, filename: str):
        """Exporta todos los datos a un archivo CSV"""
        import pandas as pd
        
        data = {}
        for name, serie in self.series.items():
            data[f"{name}_x"] = serie['x_data']
            data[f"{name}_y"] = serie['y_data']
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        
        
        
from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QComboBox, QSlider, QLabel, QSpinBox, QCheckBox)
from PyQt6.QtCore import Qt, QTimer
import pyqtgraph as pg
from pyqtgraph import mkPen, mkBrush
import numpy as np

class DynamicPlotGroupBox(QGroupBox):
    def __init__(self, title="Gráfico Dinámico", parent=None):
        super().__init__(title, parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 20, 10, 10)
        
        # Crear el gráfico
        self.plot = DynamicMultiPlot()
        
        # Panel de controles
        control_panel = self.create_control_panel()
        
        # Añadir elementos al layout
        main_layout.addWidget(self.plot)
        main_layout.addLayout(control_panel)
        
        self.setLayout(main_layout)
        
        # Estilo del GroupBox
        self.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: #3498db;
            }
        """)
    
    def create_control_panel(self):
        """Crea el panel de controles debajo del gráfico"""
        controls = QHBoxLayout()
        
        # Botones de control de reproducción
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedWidth(40)
        self.play_btn.clicked.connect(self.toggle_playback)
        
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setFixedWidth(40)
        self.stop_btn.clicked.connect(self.plot.stop_playback)
        
        # Selector de velocidad
        speed_label = QLabel("Velocidad:")
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(1, 10)
        self.speed_spin.setValue(1)
        
        # Selector de series para mostrar/ocultar
        series_label = QLabel("Series:")
        self.series_combo = QComboBox()
        self.series_combo.currentTextChanged.connect(self.update_series_visibility)
        
        # Checkbox para visibilidad
        self.visibility_check = QCheckBox("Mostrar")
        self.visibility_check.setChecked(True)
        self.visibility_check.stateChanged.connect(self.toggle_current_series)
        
        # Slider para navegación manual
        self.frame_slider = QSlider(Qt.Orientation.Horizontal)
        self.frame_slider.setRange(0, 100)
        self.frame_slider.valueChanged.connect(self.plot.set_current_frame)
        
        # Añadir controles al layout
        controls.addWidget(self.play_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(speed_label)
        controls.addWidget(self.speed_spin)
        controls.addStretch()
        controls.addWidget(series_label)
        controls.addWidget(self.series_combo)
        controls.addWidget(self.visibility_check)
        controls.addStretch()
        controls.addWidget(self.frame_slider)
        
        return controls
    
    def toggle_playback(self):
        """Alterna entre reproducir/pausar"""
        if self.plot.is_playing:
            self.plot.pause_playback()
            self.play_btn.setText("▶")
        else:
            self.plot.start_playback(self.speed_spin.value())
            self.play_btn.setText("⏸")
    
    def update_series_visibility(self, series_name):
        """Actualiza el checkbox de visibilidad según la serie seleccionada"""
        if series_name in self.plot.series:
            visible = self.plot.series[series_name]['visible']
            self.visibility_check.setChecked(visible)
    
    def toggle_current_series(self, state):
        """Muestra/oculta la serie actualmente seleccionada"""
        series_name = self.series_combo.currentText()
        if series_name in self.plot.series:
            self.plot.set_series_visibility(series_name, state == Qt.CheckState.Checked)
    
    def add_series(self, name: str, **kwargs):
        """Añade una serie al gráfico y actualiza los controles"""
        self.plot.add_series(name, **kwargs)
        self.series_combo.addItem(name)
        
        # Actualizar el rango del slider si hay datos
        if len(self.plot.series[name]['x_data']) > self.frame_slider.maximum():
            self.frame_slider.setMaximum(len(self.plot.series[name]['x_data']))
    
    def add_data(self, name: str, x: List[float], y: List[float]):
        """Añade datos a una serie y actualiza controles"""
        self.plot.add_data(name, x, y)
        max_frames = max(len(self.plot.series[n]['x_data']) for n in self.plot.series)
        self.frame_slider.setMaximum(max_frames)