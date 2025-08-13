from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal

from functools import partial

from main.components.menu_button import MenuButton
from main.styles.styles import AppStyles
from main.enums.menu_sections import MenuSection
from PyQt6.QtCore import QPropertyAnimation

class SideMenu(QWidget):
    """Menú lateral con 'Salir' anclado abajo"""

    menu_clicked = pyqtSignal(MenuSection)  # Emitimos el Enum

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = {}
        self.current_section = None
        self.setStyleSheet(AppStyles.SIDE_MENU)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Título
        title = QLabel("MENÚ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(AppStyles.MENU_TITLE)
        layout.addWidget(title)

        # Botones principales
        buttons_widget = QWidget()
        
        buttons_layout = QVBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(5)

        symbol_names = {
            MenuSection.HOME: "🏠 Inicio",
            MenuSection.CONTROL: "🎮 Panel de Control",
            MenuSection.REPORTS: "📊 Reportes",
            MenuSection.SETTINGS: "⚙️ Configuración",
            MenuSection.LOGOUT: "🔓 Salir"
        }
        
        main_sections = [
            MenuSection.HOME,
            MenuSection.CONTROL,
            MenuSection.REPORTS,
            MenuSection.SETTINGS,
        ]

        for section in main_sections:
            self._add_menu_button(buttons_layout, section, symbol_names[section])


        buttons_layout.addStretch()
        self._add_menu_button(buttons_layout, MenuSection.LOGOUT, symbol_names[MenuSection.LOGOUT])
        
        buttons_widget.setLayout(buttons_layout)
        layout.addWidget(buttons_widget)
        
        
        self.setLayout(layout)
        
        self.setFixedWidth(200)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(AppStyles.SIDE_MENU)
        self.select_section(MenuSection.HOME)

    def _add_menu_button(self, layout, section, text):
        btn = MenuButton(text)
        btn.setCheckable(True)
        btn.clicked.connect(partial(self.on_button_clicked, section))
        layout.addWidget(btn)
        self.buttons[section] = btn
        
        # Ocultar el botón de reportes por defecto
        if section == MenuSection.REPORTS:
            btn.setVisible(False)

        if section == MenuSection.SETTINGS:
            btn.setVisible(False)
    
    def on_button_clicked(self, section_enum: MenuSection):
        self.select_section(section_enum)
        self.menu_clicked.emit(section_enum)  # Emitimos el enum directamente
        # print(f"emit secction : {section_enum}")
    
    def select_section(self, section_enum: MenuSection):
        # print(f"select secction : {section_enum}")
        for btn in self.buttons.values():
            btn.setChecked(False)
        if section_enum in self.buttons:
            self.buttons[section_enum].setChecked(True)
            self.current_section = section_enum


    def set_section_enabled(self, section: MenuSection, enabled: bool):
        """Habilita o deshabilita una sección del menú"""
        if section in self.buttons:
            self.buttons[section].setEnabled(enabled)
            
            # Si lo deshabilitamos y está seleccionado, seleccionamos Home en su lugar
            if not enabled and self.current_section == section:
                self.select_section(MenuSection.HOME)
                self.menu_clicked.emit(MenuSection.HOME)
    
    def is_section_enabled(self, section: MenuSection) -> bool:
        """Verifica si una sección está habilitada"""
        return self.buttons[section].isEnabled() if section in self.buttons else False
    
    

    def set_section_visible(self, section: MenuSection, visible: bool):
        """Muestra u oculta una sección del menú"""
        if section in self.buttons:
            self.buttons[section].setVisible(visible)
            
            # Si lo ocultamos y está seleccionado, seleccionamos Home en su lugar
            if not visible and self.current_section == section:
                self.select_section(MenuSection.HOME)
                self.menu_clicked.emit(MenuSection.HOME)

    def is_section_visible(self, section: MenuSection) -> bool:
        """Verifica si una sección está visible"""
        return self.buttons[section].isVisible() if section in self.buttons else False
    

    

    def set_section_visible(self, section: MenuSection, visible: bool, animated=True):
        """Muestra u oculta una sección del menú con animación opcional"""
        if section not in self.buttons:
            return

        btn = self.buttons[section]
        
        if not animated:
            btn.setVisible(visible)
            return
            
        anim = QPropertyAnimation(btn, b"maximumHeight")
        anim.setDuration(300)
        
        if visible:
            btn.setVisible(True)
            anim.setStartValue(0)
            anim.setEndValue(btn.sizeHint().height())
        else:
            anim.setStartValue(btn.height())
            anim.setEndValue(0)
            anim.finished.connect(lambda: btn.setVisible(False))
        
        anim.start()
    
# from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
# from PyQt6.QtCore import Qt, pyqtSignal

# from functools import partial

# from main.components.menu_button import MenuButton
# from main.styles.styles import AppStyles
# from main.enums.menu_sections import MenuSection

# class SideMenu(QWidget):
#     def __init__(self, on_section_changed):
#         super().__init__()
#         self.on_section_changed = on_section_changed
#         self.buttons = {}
#         self.current_selected = None
        
#         self.initUI()
#         #self.select_section(MenuSection.HOME)
        
#     def initUI(self):
        
#         layout = QVBoxLayout()
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(5)

#         # Título del menú
#         title = QLabel("SK SYSTEM")
#         title.setStyleSheet(AppStyles.MENU_TITLE)
#         title.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         layout.addWidget(title)


#         symbol_names = {
#             MenuSection.HOME: "🏠 Inicio",
#             MenuSection.CONTROL: "🎮 Control",
#             MenuSection.REPORTS: "📊 Reportes",
#             MenuSection.SETTINGS: "⚙️ Configuración",
#             MenuSection.CALIBRATION: "🧪 Calibración",
#             MenuSection.LOGOUT: "🔓 Salir"
#         }

#         # Secciones principales
#         main_sections = [
#             MenuSection.HOME,
#             MenuSection.CONTROL,
#             MenuSection.REPORTS,
#             MenuSection.SETTINGS,
#             MenuSection.CALIBRATION,
#         ]
#         for section in main_sections:
#             self._add_menu_button(layout, section, symbol_names[section])

#         # Espaciador para empujar logout abajo
#         layout.addStretch()


#         self._add_menu_button(layout, MenuSection.LOGOUT, symbol_names[MenuSection.LOGOUT])
#         self.setLayout(layout)
        
#         self.setFixedWidth(180)
#         self.setObjectName("SideMenu") 
#         # print("SideMenu objectName:", self.objectName())  # Debería imprimir: SideMenu
           
#         self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        
#         self.setStyleSheet("""
#             QWidget {
#                 background-color: #EB3A17;
#             }
#         """)



        
        
#     def _add_menu_button(self, layout, section, text):
#         btn = MenuButton(text)
#         btn.setCheckable(True)
#         btn.clicked.connect(partial(self.select_section, section))
#         layout.addWidget(btn)
#         self.buttons[section] = btn


#     def select_section(self, section: MenuSection):
#         if section == self.current_selected:
#             return  # Ya seleccionado, evita llamar callback

#         if self.current_selected:
#             self.buttons[self.current_selected].setChecked(False)

#         self.buttons[section].setChecked(True)
#         self.current_selected = section
#         self.on_section_changed(section)

