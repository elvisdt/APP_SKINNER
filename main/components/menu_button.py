"""
Componente de botón personalizado para el menú
"""

from PyQt6.QtWidgets import QPushButton
from main.styles.styles import AppStyles


class MenuButton(QPushButton):
    """Botón personalizado para el menú lateral"""
    
    def __init__(self, text, icon="", parent=None):
        super().__init__(text, parent)
        self.icon = icon
        self.setCheckable(True)
        self.setFixedHeight(50)
        self.setStyleSheet(AppStyles.MENU_BUTTON)
        
        if icon:
            self.setText(f"{icon} {text}")