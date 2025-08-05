

from enum import Enum, auto

class IndicatorKey(Enum):
    START_TIME = auto()
    END_TIME = auto()
    RUN_TIME = auto()
    LATENCY = auto()
    RESPONSE_RATE = auto()
    LEVER_01_COUNT = auto()
    LEVER_02_COUNT = auto()
    LED_01_STATE = auto()
    LED_02_STATE = auto()
    FOOD_COUNT = auto()
    SESSION_ID = auto()
    TRIAL_COUNT = auto()