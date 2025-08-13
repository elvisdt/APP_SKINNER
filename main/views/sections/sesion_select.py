from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from main.styles.styles import AppStyles  # tu módulo de estilos

class SessionSelectorBox(QGroupBox):
    def __init__(self):
        super().__init__("Control de Sesiones")
        self.setStyleSheet(AppStyles.groupbox_style("#2ecc71"))
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Selección de sesión
        # layout.addWidget(QLabel("Sesión:"))
        lbl_01 = QLabel("Sesión:")
        lbl_01.setStyleSheet(AppStyles.LABEL_STYLE)
        lbl_01.setMinimumWidth(100)
        
        layout.addWidget(lbl_01)
        
        
        self.session_combo = QComboBox()
        self.session_combo.setStyleSheet(AppStyles.CMBOX_PLNC_STYLE)
        layout.addWidget(self.session_combo)

        # Selección de eventos
        
        lbl_02 = QLabel("Eventos:")
        lbl_02.setStyleSheet(AppStyles.LABEL_STYLE)
        lbl_02.setMinimumWidth(100)
        layout.addWidget(lbl_02)
         
        self.events_list = QListWidget()
        self.events_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.events_list.setStyleSheet(AppStyles.LIST_WIDGET_STYLE)
        layout.addWidget(self.events_list)


        # Botones de control
        btn_layout = QHBoxLayout()
        self.btn_play = QPushButton("▶ Reproducir")
        self.btn_play.setStyleSheet(AppStyles.BUTTON_PLAY_01)
        
        self.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_stop = QPushButton("⏹ Detener")
        self.btn_stop.setStyleSheet(AppStyles.BUTTON_STOP_01)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_layout.addWidget(self.btn_play)
        btn_layout.addWidget(self.btn_stop)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def add_session(self, session_name):
        self.session_combo.addItem(session_name)

    def add_event(self, event_name):
        item = QListWidgetItem(event_name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked)
        self.events_list.addItem(item)

    def get_selected_events(self):
        return [
            self.events_list.item(i).text()
            for i in range(self.events_list.count())
            if self.events_list.item(i).checkState() == Qt.CheckState.Checked
        ]
