from enum import Enum, auto

class MenuSection(Enum):
    HOME = auto()
    CONTROL = auto()
    SETTINGS = auto()
    REPORTS = auto()
    LOGOUT = auto()
    CALIBRATION = auto()

    def __str__(self):
        labels = {
            MenuSection.HOME: "Inicio",
            MenuSection.CONTROL: "Control",
            MenuSection.SETTINGS: "Configuración",
            MenuSection.REPORTS: "Reportes",
            MenuSection.LOGOUT: "Cerrar sesión",
            MenuSection.CALIBRATION: "Calibración"
        }
        return labels[self]

