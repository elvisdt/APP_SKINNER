from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton,
    QFormLayout
)
from PyQt6.QtCore import Qt

from PySide6.QtCore import QDateTime, QTime, QTimer


from main.styles.styles import AppStyles
from main.enums.indicators_enum import IndicatorKey


class IndicatorsSectionBox(QGroupBox):
    def __init__(self):
        super().__init__("Indicadores de Sesión")
        self.setObjectName("IndicadoresBox")
        self.setStyleSheet(AppStyles.groupbox_style("#e67e22"))

        # Mapeo de claves a nombres mostrados y valores por defecto
        self.indicator_map = {
            IndicatorKey.SESSION_ID: ("ID de Sesión", "N/A"),
            IndicatorKey.START_TIME: ("Hora de Inicio", "--:--:--"),
            IndicatorKey.END_TIME: ("Hora de Fin", "--:--:--"),
            IndicatorKey.RUN_TIME: ("Duración", "00:00:00"),
            IndicatorKey.LATENCY: ("Latencia", "0 ms"),
            IndicatorKey.RESPONSE_RATE: ("Tasa de Respuesta", "0%"),
            IndicatorKey.LEVER_01_COUNT: ("Palanca 01", "0"),
            IndicatorKey.LEVER_02_COUNT: ("Palanca 02", "0"),
            IndicatorKey.LED_01_STATE: ("LED 01", "OFF"),
            IndicatorKey.LED_02_STATE: ("LED 02", "OFF"),
            IndicatorKey.FOOD_COUNT: ("Recompensas", "0"),
            IndicatorKey.TRIAL_COUNT: ("Intentos", "0")
        }

        self.labels = {}
        self._start_time = None
        self._end_time = None
        self.plc_01_count = 0
        
        self._init_ui()

    def _init_ui(self):
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.setHorizontalSpacing(3)
        form_layout.setVerticalSpacing(5)

        # Agregar todos los indicadores en una sola columna
        for key, (name, default) in self.indicator_map.items():
            self._add_indicator_row(form_layout, key, name, default)

        self.setLayout(form_layout)

    def _add_indicator_row(self, layout, key, name, default):
        key_label = QLabel(f"{name}:")
        key_label.setStyleSheet(AppStyles.LABEL_KEY_STYLE)
        key_label.setMinimumWidth(100)  # Un poco más ancho

        value_label = QLabel(default)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        value_label.setMinimumWidth(200)
    
        # Aplicar estilos específicos
        if key in [IndicatorKey.LED_01_STATE, IndicatorKey.LED_02_STATE]:
            style = AppStyles.LABEL_LED_ON_STYLE if default == "ON" else AppStyles.LABEL_LED_OFF_STYLE
            value_label.setStyleSheet(style)        
        else:
            value_label.setStyleSheet(AppStyles.LABEL_VALUE_STYLE)
            # value_label.setMinimumWidth(200)  # Ancho consistente

        layout.addRow(key_label, value_label)
        self.labels[key] = value_label

    def update_value(self, key: IndicatorKey, new_value):
        if key in self.labels:            
            # Actualizar estilo si es un LED
            if key in [IndicatorKey.LED_01_STATE, IndicatorKey.LED_02_STATE]:
                style = AppStyles.LABEL_LED_ON_STYLE if str(new_value).upper() == "ON" else AppStyles.LABEL_LED_OFF_STYLE
                self.labels[key].setText(new_value)
                self.labels[key].setStyleSheet(style)
                
            elif key in [IndicatorKey.LEVER_01_COUNT, IndicatorKey.LEVER_02_COUNT]:
                self.increment_value(key) 
            else:
                self.labels[key].setText(str(new_value))
                

    def set_start_time(self, dt: QDateTime):
        self._start_time = dt
        self.update_value(IndicatorKey.START_TIME, dt.toString("dd/MM/yyyy HH:mm:ss"))

    def set_end_time(self, dt: QDateTime):
        self._end_time = dt
        self.update_value(IndicatorKey.END_TIME, dt.toString("dd/MM/yyyy HH:mm:ss"))

    def update_run_time(self, time_str: str):
        self.update_value(IndicatorKey.RUN_TIME, time_str)



    def increment_value(self, key: IndicatorKey, step: int = 1):
        try:
            actual = int(self.labels[key].text())
        except ValueError:
            actual = 0
        #print(f"KEY:{key}, valor: {actual}")
        
        self.labels[key].setText(str(actual + step))

    def reset_all(self):
        for key, (_, default) in self.indicator_map.items():
            self.update_value(key, default)
        self._start_time = None
        self._end_time = None