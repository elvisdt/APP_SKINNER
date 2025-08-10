

from enum import Enum, auto

# class IndicatorKey(Enum):
#     START_TIME = auto()
#     END_TIME = auto()
#     RUN_TIME = auto()
#     LATENCY = auto()
#     RESPONSE_RATE = auto()
#     LEVER_01_COUNT = auto()
#     LEVER_02_COUNT = auto()
#     LED_01_STATE = auto()
#     LED_02_STATE = auto()
#     FOOD_COUNT = auto()
#     SESSION_ID = auto()
#     TRIAL_COUNT = auto()
    


class IndicatorKey(Enum):
    SESSION_ID = "ID de Sesión"
    START_TIME = "Hora de Inicio"
    END_TIME = "Hora de Fin"
    RUN_TIME = "Duración"
    LATENCY_VAL = "Latencia (ms)"
    RESPONSE_RATE_VAL = "Tasa de Respuesta (%)"
    LEVER_01_COUNT = "Palanca 01"
    LEVER_02_COUNT = "Palanca 02"
    LED_01_STATE = "LED 01"
    LED_02_STATE = "LED 02"
    RECONPENSA_COUNT = "Recompensas"
    DISPENSA_COUNT = "Dispensador"