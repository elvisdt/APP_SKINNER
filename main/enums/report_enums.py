from enum import Enum, auto
from datetime import datetime
from typing import Optional, List, Dict, Union
import pandas as pd
import json

class EventType(Enum):
    LED_CHANGE = auto()
    LEVER_PRESS = auto()
    FOOD_DISPENSE = auto()
    SESSION_START = auto()
    SESSION_END = auto()
    CUSTOM_EVENT = auto()

class DeviceID(Enum):
    LED_01 = "LED_01"
    LED_02 = "LED_02"
    LEVER_01 = "PAL_01"
    LEVER_02 = "PAL_02"
    FOOD_DEVICE = "DISP_FOOD"
    SYSTEM = "SYSTEM"