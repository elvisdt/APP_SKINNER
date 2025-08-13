from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QDateTime

from main.styles.styles import AppStyles
from main.enums.program_enums import ModoLuz, ModoPalanca




class ProgramControlBox(QGroupBox):
    def __init__(self, uart_connected: bool = False, isrunig: bool = False):
        super().__init__("Modo de operación:")
        self.setStyleSheet(AppStyles.groupbox_style("#2c3e50"))        
        self._init_ui()
        self.is_runing = isrunig
        
        self.set_runing_state(isrunig)
        self.update_uart_status(uart_connected)
        
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Crear y agregar secciones
        self.lbl_mode_l1, self.cmb_mode_l1, self.lbl_spbox_l1, self.spbox_l1 = self._crear_seccion_led("Led-01", "Tiempo(s)-L01")
        self.lbl_mode_l2, self.cmb_mode_l2, self.lbl_spbox_l2, self.spbox_l2 = self._crear_seccion_led("Led-02", "Tiempo(s)-L02")
        self.lbl_mode_p1, self.cmb_mode_p1, self.lbl_spbox_p1, self.spbox_p1 = self._crear_seccion_pln("Palanca-01", "Tiempo(s)-P01")
        self.lbl_mode_p2, self.cmb_mode_p2, self.lbl_spbox_p2, self.spbox_p2 = self._crear_seccion_pln("Palanca-02", "Tiempo(s)-P02")

        # crear Boton de inicio o detenido
        self.btn_start = QPushButton("Iniciar Pragrama")
        self.btn_start.setStyleSheet(AppStyles.BUTTON_START)
        self.btn_start.setMinimumWidth(120)
        self.btn_start.setMaximumWidth(200)
        
        self.btn_stop = QPushButton("Detener Programa")
        self.btn_stop.setStyleSheet(AppStyles.BUTTON_STOP)
        self.btn_stop.setMinimumWidth(120)
        self.btn_stop.setMaximumWidth(200)
        
        layout_btn = QHBoxLayout()
        layout_btn.setContentsMargins(0, 5, 0, 0)
        layout_btn.setSpacing(50)
        
        layout_btn.addStretch()
        layout_btn.addWidget(self.btn_start)
        layout_btn.addWidget(self.btn_stop)
        layout_btn.addStretch()
        
        
        # Conectar señales
        self.cmb_mode_l1.currentTextChanged.connect(lambda: self._actualizar_visibilidad_tiempo(self.spbox_l1, self.lbl_spbox_l1, self.cmb_mode_l1, True))
        self.cmb_mode_l2.currentTextChanged.connect(lambda: self._actualizar_visibilidad_tiempo(self.spbox_l2, self.lbl_spbox_l2, self.cmb_mode_l2, True))
        self.cmb_mode_p1.currentTextChanged.connect(lambda: self._actualizar_visibilidad_tiempo(self.spbox_p1, self.lbl_spbox_p1, self.cmb_mode_p1, False))
        self.cmb_mode_p2.currentTextChanged.connect(lambda: self._actualizar_visibilidad_tiempo(self.spbox_p2, self.lbl_spbox_p2, self.cmb_mode_p2, False))



        # Añadir widgets al layout
        layout.addLayout(self._crear_layout_fila(self.lbl_mode_l1, self.cmb_mode_l1, self.lbl_spbox_l1, self.spbox_l1))
        layout.addLayout(self._crear_layout_fila(self.lbl_mode_l2, self.cmb_mode_l2, self.lbl_spbox_l2, self.spbox_l2))
        layout.addLayout(self._crear_layout_fila(self.lbl_mode_p1, self.cmb_mode_p1, self.lbl_spbox_p1, self.spbox_p1))
        layout.addLayout(self._crear_layout_fila(self.lbl_mode_p2, self.cmb_mode_p2, self.lbl_spbox_p2, self.spbox_p2))
        layout.addLayout(layout_btn)
        self.setLayout(layout)

        # Actualizar visibilidad inicial
        self._actualizar_visibilidad_tiempo(self.spbox_l1, self.lbl_spbox_l1, self.cmb_mode_l1, True)
        self._actualizar_visibilidad_tiempo(self.spbox_l2, self.lbl_spbox_l2, self.cmb_mode_l2, True)
        self._actualizar_visibilidad_tiempo(self.spbox_p1, self.lbl_spbox_p1, self.cmb_mode_p1, False)
        self._actualizar_visibilidad_tiempo(self.spbox_p2, self.lbl_spbox_p2, self.cmb_mode_p2, False)
    
    

    def _actualizar_visibilidad_tiempo(self, spinbox, label, combobox, es_luz):
        """Actualiza la visibilidad de los controles de tiempo según el modo seleccionado
        y modifica el texto del label para VI/FI si es palanca"""
        modo = combobox.currentText()
        
        if es_luz:
            # Para luces: mostrar solo en modo intermitente
            mostrar = (modo == ModoLuz.INTERMITENTE.value)
            # Mantener el texto original del label para luces
            nuevo_texto = label.text()  # Conservamos el texto original
        else:
            # Para palancas: mostrar solo en VI, VR, FI, FR
            mostrar = (modo in {ModoPalanca.VI.value, ModoPalanca.VR.value, 
                            ModoPalanca.FI.value, ModoPalanca.FR.value})
            
            # Obtener el identificador (P01 o P02)
            texto_original = label.text()
            identificador = "P01:" if "P01:" in texto_original else "P02:"
            
            # Cambiar el texto del label según el modo
            if modo == ModoPalanca.VI.value:
                nuevo_texto = f"Tiempo(s).VI-{identificador}"
            elif modo == ModoPalanca.FI.value:
                nuevo_texto = f"Tiempo(s).FI-{identificador}"
            elif modo == ModoPalanca.VR.value:
                nuevo_texto = f"Cantidad(u).VR-{identificador}"
            elif modo == ModoPalanca.FR.value:
                nuevo_texto = f"Cantidad(u).FR-{identificador}"
            else:
                nuevo_texto = f"Tiempo(s)-{identificador}"
        
        spinbox.setVisible(mostrar)
        label.setVisible(mostrar)
        label.setText(nuevo_texto)

    def _crear_seccion_led(self, nombre_lbl_01: str, nombre_lbl_02: str):
        lbl_01 = QLabel(f"{nombre_lbl_01}:")
        lbl_01.setStyleSheet(AppStyles.LABEL_STYLE)
        lbl_01.setMinimumWidth(100)
        
        cmb = QComboBox()
        cmb.addItems([modo.value for modo in ModoLuz])
        cmb.setStyleSheet(AppStyles.CMBOX_PLNC_STYLE)
        # cmb.setMinimumWidth(80)

        lbl_02 = QLabel(f"{nombre_lbl_02}:")
        lbl_02.setStyleSheet(AppStyles.LABEL_STYLE)
        lbl_02.setMinimumWidth(120)

        spbox = QSpinBox()
        spbox.setStyleSheet(AppStyles.SPINBOX_STYLE)
        spbox.setRange(1, 999)
        # spbox.setSuffix(" s")
        spbox.setFixedWidth(100)

        return lbl_01, cmb, lbl_02, spbox
    
    def _crear_seccion_pln(self, nombre_lbl_01: str, nombre_lbl_02: str):
        lbl_01 = QLabel(f"{nombre_lbl_01}:")
        lbl_01.setStyleSheet(AppStyles.LABEL_STYLE)
        lbl_01.setMinimumWidth(100)
        
        cmb = QComboBox()
        cmb.addItems([modo.value for modo in ModoPalanca])
        cmb.setStyleSheet(AppStyles.CMBOX_PLNC_STYLE)
        # cmb.setMinimumWidth(80)

        lbl_02 = QLabel(f"{nombre_lbl_02}:")
        lbl_02.setStyleSheet(AppStyles.LABEL_STYLE)
        lbl_02.setMinimumWidth(120)

        spbox = QSpinBox()
        spbox.setStyleSheet(AppStyles.SPINBOX_STYLE)
        spbox.setRange(3, 999)
        spbox.setFixedWidth(100)

        return lbl_01, cmb, lbl_02, spbox

    def _crear_layout_fila(self, lbl_01, cmbox, lbl_02, spbox):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(lbl_01, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(cmbox, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(50)
        layout.addWidget(lbl_02)
        layout.addWidget(spbox,alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        return layout

    def update_uart_status(self, connected: bool):
        """Actualiza el estado de conexión UART"""
        if connected:
            self.enable_config()
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
        else:
            self.disable_config()
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(False)
            
    def set_runing_state(self, is_running: bool):
        """Actualiza el estado de ejecución del programa."""
        self.is_runing = is_running
        if is_running:
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.disable_config()
        else:
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.enable_config()
            
    def get_runing_state(self) -> bool:
        """Obtiene el estado de ejecución del programa."""
        return self.is_runing
            
    def disable_config(self):
        """Deshabilita todos los controles de configuración."""
        self.cmb_mode_l1.setEnabled(False)
        self.cmb_mode_l1.setStyleSheet(AppStyles.CMBOX_STYLE_DISABLED)
        
        self.spbox_l1.setEnabled(False)
        
        self.cmb_mode_l2.setEnabled(False)
        self.cmb_mode_l2.setStyleSheet(AppStyles.CMBOX_STYLE_DISABLED)
        
        self.spbox_l2.setEnabled(False)
        
        self.cmb_mode_p1.setEnabled(False)
        self.cmb_mode_p1.setStyleSheet(AppStyles.CMBOX_STYLE_DISABLED)
        
        self.spbox_p1.setEnabled(False)
        
        self.cmb_mode_p2.setEnabled(False)
        self.cmb_mode_p2.setStyleSheet(AppStyles.CMBOX_STYLE_DISABLED)
        
        self.spbox_p2.setEnabled(False)
    
    def enable_config(self):
        """Habilita todos los controles de configuración."""
        self.cmb_mode_l1.setEnabled(True)
        self.cmb_mode_l1.setStyleSheet(AppStyles.CMBOX_PLNC_STYLE)
        
        self.spbox_l1.setEnabled(True)
        self.cmb_mode_l2.setEnabled(True)
        self.cmb_mode_l2.setStyleSheet(AppStyles.CMBOX_PLNC_STYLE)
        
        self.spbox_l2.setEnabled(True)
        
        self.cmb_mode_p1.setEnabled(True)
        self.cmb_mode_p1.setStyleSheet(AppStyles.CMBOX_PLNC_STYLE)
        
        self.spbox_p1.setEnabled(True)
        
        self.cmb_mode_p2.setEnabled(True)
        self.cmb_mode_p2.setStyleSheet(AppStyles.CMBOX_PLNC_STYLE)
        
        self.spbox_p2.setEnabled(True)
    
    
    def get_led1_mode(self) -> ModoLuz:
        """Obtiene el modo seleccionado para el Led-01 como Enum"""
        current_text = self.cmb_mode_l1.currentText()
        return ModoLuz(current_text)

    def get_led2_mode(self) -> ModoLuz:
        """Obtiene el modo seleccionado para el Led-02 como Enum"""
        current_text = self.cmb_mode_l2.currentText()
        return ModoLuz(current_text)

    def get_pal1_mode(self) -> ModoPalanca:
        """Obtiene el modo seleccionado para la Palanca-01 como Enum"""
        current_text = self.cmb_mode_p1.currentText()
        return ModoPalanca(current_text)

    def get_pal2_mode(self) -> ModoPalanca:
        """Obtiene el modo seleccionado para la Palanca-02 como Enum"""
        current_text = self.cmb_mode_p2.currentText()
        return ModoPalanca(current_text)

    #---------------------------------------------------------#
    def get_led1_time(self) -> int:
        """Obtiene el tiempo configurado para el Led-01"""
        return self.spbox_l1.value()

    def get_led2_time(self) -> int:
        """Obtiene el tiempo configurado para el Led-02"""
        return self.spbox_l2.value()

    def get_pal1_time(self) -> int:
        """Obtiene el tiempo/configuración para la Palanca-01"""
        return self.spbox_p1.value()

    def get_pal2_time(self) -> int:
        """Obtiene el tiempo/configuración para la Palanca-02"""
        return self.spbox_p2.value()
    
    def get_program_config(self) -> dict:
        """Devuelve toda la configuración actual como diccionario."""
        return {
            'experiment': 'Skinnerv01',
            'time': QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss"),
            'led_1c': self.get_led1_mode().value,
            'led_1v': self.get_led1_time(),
            'led_2c': self.get_led2_mode().value,
            'led_2v': self.get_led2_time(),
            'pal_1c': self.get_pal1_mode().value,
            'pal_1v': self.get_pal1_time(),
            'pal_2c': self.get_pal2_mode().value,
            'pal_2v': self.get_pal2_time()
        }
