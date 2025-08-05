from enum import Enum

class ModoLuz(Enum):
    APAGADO = "Apagado"
    ENCENDIDO = "Encendido"
    INTERMITENTE = "Intermitente"



class ModoPalanca(Enum):
    CRF = "CRF"
    FI = "FI"
    FR = "FR"
    VI = "VI"
    VR = "VR"
    EXTINCION = "EXTINCIÓN"
    INHABILITADO = "INHABILITADO"
