from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLabel
from PyQt6.QtCore import Qt, QDateTime
from main.styles.styles import AppStyles
from main.enums.indicators_enum import IndicatorKey

from main.core.event_logger import EventLogger, EventType, DeviceID

class IndicatorsSectionBox(QGroupBox, EventLogger):
    def __init__(self):
        QGroupBox.__init__(self, "Indicadores de Sesión")
        EventLogger.__init__(self)
        
        self.setStyleSheet(AppStyles.groupbox_style("#e67e22"))
        self.labels = {}
        self._init_ui()
        
        self.last_p01_event = False
        self.last_p02_event = False

    def _init_ui(self):
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.setHorizontalSpacing(3)
        form_layout.setVerticalSpacing(5)

        # Mapeo de indicadores a valores por defecto
        indicators = {
            IndicatorKey.SESSION_ID: "N/A",
            IndicatorKey.START_TIME: "--:--:--",
            IndicatorKey.END_TIME: "--:--:--",
            IndicatorKey.RUN_TIME: "00:00:00",
            IndicatorKey.LATENCY_VAL: "0",
            IndicatorKey.RESPONSE_RATE_VAL: "0",
            IndicatorKey.LEVER_01_COUNT: "0",
            IndicatorKey.LEVER_02_COUNT: "0",
            IndicatorKey.LED_01_STATE: "OFF",
            IndicatorKey.LED_02_STATE: "OFF",
            IndicatorKey.RECONPENSA_COUNT: "0",
            IndicatorKey.DISPENSA_COUNT: "0"
        }

        for key, default in indicators.items():
            self._add_indicator_row(form_layout, key, default)

        self.setLayout(form_layout)

    def _add_indicator_row(self, layout, key: IndicatorKey, default: str):
        label = QLabel(f"{key.value}:")
        label.setStyleSheet(AppStyles.LABEL_KEY_STYLE)
        label.setMinimumWidth(100)

        value_label = QLabel(default)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        value_label.setMinimumWidth(200)

        # Estilos especiales para LEDs
        if key in [IndicatorKey.LED_01_STATE, IndicatorKey.LED_02_STATE]:
            style = AppStyles.LABEL_LED_ON_STYLE if default == "ON" else AppStyles.LABEL_LED_OFF_STYLE
            value_label.setStyleSheet(style)
        else:
            value_label.setStyleSheet(AppStyles.LABEL_VALUE_STYLE)

        layout.addRow(label, value_label)
        self.labels[key] = value_label

    # def update_value(self, key: IndicatorKey, new_value=None, increment: bool = False):
    #     """Actualiza el valor del indicador, con opción de incremento"""
    #     if key not in self.labels:
    #         return

    #     # Para contadores (incrementar en 1)
    #     if increment and key in [IndicatorKey.LEVER_01_COUNT,
    #                              IndicatorKey.LEVER_02_COUNT,
    #                              IndicatorKey.FOOD_COUNT,
    #                              IndicatorKey.TRIAL_COUNT]:
    #         try:
    #             current = int(self.labels[key].text())
    #             new_value = current + 1
                
    #         except ValueError:
    #             new_value = 1  # Si no puede convertir a int, inicia en 1
    #             raise ValueError(f"Valor no válido para {key.name}: {self.labels[key].text()}")
            
    #     # Actualizar el label
    #     self.labels[key].setText(str(new_value))

    #     # Registrar el evento según el tipo de indicador
    #     if key == IndicatorKey.LED_01_STATE:
            
    #         self.log_event(EventType.LED_CHANGE, DeviceID.LED_01, new_value)
    #         style = AppStyles.LABEL_LED_ON_STYLE if str(new_value).upper() == "ON" else AppStyles.LABEL_LED_OFF_STYLE
    #         self.labels[key].setStyleSheet(style)
            
    #     elif key == IndicatorKey.LED_02_STATE:
    #         self.log_event(EventType.LED_CHANGE, DeviceID.LED_02, new_value)
    #         style = AppStyles.LABEL_LED_ON_STYLE if str(new_value).upper() == "ON" else AppStyles.LABEL_LED_OFF_STYLE
    #         self.labels[key].setStyleSheet(style)
            
    #     elif key == IndicatorKey.LEVER_01_COUNT:
    #         self.log_event(EventType.LEVER_PRESS, DeviceID.LEVER_01, new_value)
    #         self.last_p01_event = bool(new_value)

    #     elif key == IndicatorKey.LEVER_02_COUNT:
    #         self.log_event(EventType.LEVER_PRESS, DeviceID.LEVER_02, new_value)
    #         self.last_p02_event = bool(new_value)

            
    #     elif key == IndicatorKey.FOOD_COUNT:
    #         self.log_event(EventType.FOOD_DISPENSE, DeviceID.FOOD_DEVICE, new_value)
            
    #     else:  # Para otros indicadores (tiempos, ID, etc.)
    #         self.labels[key].setText(str(new_value))
    
    def update_value(self, key: IndicatorKey, new_value=None, increment: bool = False):
        """Actualiza el valor del indicador, con opción de incremento"""
        if key not in self.labels:
            return

        # Para contadores (incrementar en 1)
        if increment and key in [IndicatorKey.LEVER_01_COUNT,
                                IndicatorKey.LEVER_02_COUNT,
                                IndicatorKey.DISPENSA_COUNT,
                                IndicatorKey.RECONPENSA_COUNT]:
            try:
                current = int(self.labels[key].text())
                new_value = current + 1
            except ValueError:
                new_value = 1
                raise ValueError(f"Valor no válido para {key.name}: {self.labels[key].text()}")

        # LEDs → mostrar ON/OFF pero loggear 0 o 1
        if key in [IndicatorKey.LED_01_STATE, IndicatorKey.LED_02_STATE]:
            event_value = int(new_value)  # para el log
            display_value = "ON" if event_value == 1 else "OFF"  # para la UI
            self.labels[key].setText(display_value)

            # Cambiar estilo según estado
            style = AppStyles.LABEL_LED_ON_STYLE if event_value == 1 else AppStyles.LABEL_LED_OFF_STYLE
            self.labels[key].setStyleSheet(style)

            # Loggear con valor numérico
            device = DeviceID.LED_01 if key == IndicatorKey.LED_01_STATE else DeviceID.LED_02
            self.log_event(EventType.LED_CHANGE, device, event_value)

        elif key == IndicatorKey.LEVER_01_COUNT:
            self.labels[key].setText(str(new_value))
            self.log_event(EventType.LEVER_PRESS, DeviceID.LEVER_01, new_value)
            self.last_p01_event = bool(new_value)

        elif key == IndicatorKey.LEVER_02_COUNT:
            self.labels[key].setText(str(new_value))
            self.log_event(EventType.LEVER_PRESS, DeviceID.LEVER_02, new_value)
            self.last_p02_event = bool(new_value)

        elif key == IndicatorKey.DISPENSA_COUNT:
            self.labels[key].setText(str(new_value))
            self.log_event(EventType.FOOD_DISPENSE, DeviceID.DISPENSADOR, new_value)
            
        elif key == IndicatorKey.RECONPENSA_COUNT:
            self.labels[key].setText(str(new_value))
            self.log_event(EventType.FOOD_RECOMPENSE, DeviceID.RECOMPENSA, new_value)

        else:  # Otros indicadores
            self.labels[key].setText(str(new_value))


    def set_start_time(self, dt: QDateTime):
        self.start_session()  # Inicia una nueva sesión en el logger
        self.update_value(IndicatorKey.START_TIME, dt.toString("dd/MM/yyyy HH:mm:ss"))

    def set_end_time(self, dt: QDateTime):
        self.end_session()  # Finaliza la sesión en el logger
        self.update_value(IndicatorKey.END_TIME, dt.toString("dd/MM/yyyy HH:mm:ss"))
    
    def set_run_time(self, run_time: str):
        """Actualiza el tiempo de ejecución"""
        self.update_value(IndicatorKey.RUN_TIME, run_time)


    def reset_all(self):
        for key in self.labels:
            default = (
                "0" if ("COUNT" in key.name or "VAL" in key.name or "LED" in key.name)
                else "N/A" if key == IndicatorKey.SESSION_ID
                else "--:--:--"
            )
            self.update_value(key, default)
            
        self.last_p01_event = False
        self.last_p02_event = False
        
    #---------------------------------------------------------#
    def get_val_pal01_count(self):
        """Obtiene el conteo de palanca 01"""
        return int(self.labels[IndicatorKey.LEVER_01_COUNT].text())
    
    def get_val_pal02_count(self):
        """Obtiene el conteo de palanca 02"""
        return int(self.labels[IndicatorKey.LEVER_02_COUNT].text())
    
    def get_val_food_count(self):
        """Obtiene el conteo de comida dispensada"""
        return int(self.labels[IndicatorKey.FOOD_COUNT].text())
    
    def get_val_tryal_count(self):
        """Obtiene el conteo de intentos"""
        return int(self.labels[IndicatorKey.TRIAL_COUNT].text())
    
    def get_val_latency(self):
        """Obtiene el valor de latencia"""
        return int(self.labels[IndicatorKey.LATENCY_VAL].text())
    
    def get_val_response_rate(self):
        """Obtiene el valor de tasa de respuesta"""
        return float(self.labels[IndicatorKey.RESPONSE_RATE_VAL].text())
    def get_val_led01_state(self):
        """Obtiene el estado del LED 01"""
        return self.labels[IndicatorKey.LED_01_STATE].text()    
    def get_val_led02_state(self):
        """Obtiene el estado del LED 02"""
        return self.labels[IndicatorKey.LED_02_STATE].text()
    #---------------------------------------------------------#
    def get_last_p01_event(self):
        return self.last_p01_event
    def set_last_p01_event(self, state: bool):
        self.last_p01_event = state
    
    def get_last_p02_event(self):
        return self.last_p02_event
    
    def set_last_p02_event(self, state: bool):
        self.last_p02_event = state