from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLabel
from PyQt6.QtCore import Qt, QDateTime
from main.styles.styles import AppStyles

from enum import Enum, auto

class ResumenKey(Enum):
    SESSION_ID = "ID de Sesión"
    START_TIME = "Hora de Inicio"
    END_TIME = "Hora de Fin"
    RUN_TIME = "Duración"
    LATENCY_VAL = "Latencia (s)"
    RESPONSE_RATE_VAL = "Tasa de RPM"
    
    LEVER_01_COUNT = "Palanca 01"
    LEVER_02_COUNT = "Palanca 02"
    
    LED_01_STATE = "LED 01"
    LED_02_STATE = "LED 02"
    RECONPENSA_COUNT = "Recompensas"
    DISPENSA_COUNT = "Dispensador"
    
    
    
class ResumenSectionBox(QGroupBox):
    def __init__(self):
        super().__init__("Resumen de Sesión")
        

        self.setStyleSheet(AppStyles.groupbox_style("#e67e22"))
        self.labels = {}
        self._init_ui()

    def _init_ui(self):
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.setHorizontalSpacing(3)
        form_layout.setVerticalSpacing(5)

        indicators = {
            ResumenKey.SESSION_ID: "N/A",
            ResumenKey.START_TIME: "--:--:--",
            ResumenKey.END_TIME: "--:--:--",
            ResumenKey.RUN_TIME: "00:00:00",
            ResumenKey.LATENCY_VAL: "0",
            ResumenKey.RESPONSE_RATE_VAL: "0",
            ResumenKey.LEVER_01_COUNT: "0",
            ResumenKey.LEVER_02_COUNT: "0",
            ResumenKey.LED_01_STATE: "OFF",
            ResumenKey.LED_02_STATE: "OFF",
            ResumenKey.RECONPENSA_COUNT: "0",
            ResumenKey.DISPENSA_COUNT: "0"
        }

        for key, default in indicators.items():
            self._add_indicator_row(form_layout, key, default)

        self.setLayout(form_layout)

    def _add_indicator_row(self, layout, key: ResumenKey, default: str):
        label = QLabel(f"{key.value}:")
        label.setStyleSheet(AppStyles.LABEL_KEY_STYLE)
        label.setMinimumWidth(100)

        value_label = QLabel(default)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        value_label.setMinimumWidth(200)

        if key in [ResumenKey.LED_01_STATE, ResumenKey.LED_02_STATE]:
            style = AppStyles.LABEL_LED_ON_STYLE if default == "ON" else AppStyles.LABEL_LED_OFF_STYLE
            value_label.setStyleSheet(style)
        else:
            value_label.setStyleSheet(AppStyles.LABEL_VALUE_STYLE)

        layout.addRow(label, value_label)
        self.labels[key] = value_label
    
    def update_value(self, key: ResumenKey, new_value=None, increment: bool = False):
        if key not in self.labels:
            return

        if increment and key in [ResumenKey.LEVER_01_COUNT,
                                ResumenKey.LEVER_02_COUNT,
                                ResumenKey.DISPENSA_COUNT,
                                ResumenKey.RECONPENSA_COUNT]:
            try:
                current = int(self.labels[key].text())
                new_value = current + 1
            except ValueError:
                new_value = 1

        if key in [ResumenKey.LED_01_STATE, ResumenKey.LED_02_STATE]:
            event_value = int(new_value)
            display_value = "ON" if event_value == 1 else "OFF"
            self.labels[key].setText(display_value)

            style = AppStyles.LABEL_LED_ON_STYLE if event_value == 1 else AppStyles.LABEL_LED_OFF_STYLE
            self.labels[key].setStyleSheet(style)


        elif key == ResumenKey.LEVER_01_COUNT:
            self.labels[key].setText(str(new_value))

        elif key == ResumenKey.LEVER_02_COUNT:
            self.labels[key].setText(str(new_value))
            
            self.last_p02_event = bool(new_value)

        elif key == ResumenKey.DISPENSA_COUNT:
            self.labels[key].setText(str(new_value))
            
        elif key == ResumenKey.RECONPENSA_COUNT:
            self.labels[key].setText(str(new_value))
            
        else:
            self.labels[key].setText(str(new_value))

    
    def reset_all(self):
        for key in self.labels:
            default = (
                "0" if ("COUNT" in key.name or "VAL" in key.name or "LED" in key.name)
                else "N/A" if key == ResumenKey.SESSION_ID
                else "--:--:--"
            )
            self.update_value(key, default, log=False)

    # Métodos de acceso (getters)
    def get_val_pal01_count(self):
        return int(self.labels[ResumenKey.LEVER_01_COUNT].text())
    
    def get_val_pal02_count(self):
        return int(self.labels[ResumenKey.LEVER_02_COUNT].text())
    
    def get_val_food_count(self):
        return int(self.labels[ResumenKey.RECONPENSA_COUNT].text())
    
    def get_val_latency(self):
        return float(self.labels[ResumenKey.LATENCY_VAL].text())
    
    def get_val_response_rate(self):
        return float(self.labels[ResumenKey.RESPONSE_RATE_VAL].text())
    
    def get_val_led01_state(self):
        return self.labels[ResumenKey.LED_01_STATE].text()    
    
    def get_val_led02_state(self):
        return self.labels[ResumenKey.LED_02_STATE].text()