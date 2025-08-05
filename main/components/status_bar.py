from PyQt6.QtWidgets import QStatusBar, QLabel, QSizePolicy, QWidget, QHBoxLayout
from PyQt6.QtCore import QTimer, QDateTime, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

class CustomStatusBar(QStatusBar):
    def __init__(self, version="v1.0.0"):
        super().__init__()

        # Vista activa
        self.label_view = QLabel("Vista actual: Inicio")
        self.label_view.setStyleSheet("margin-right: 30px;")
        self.addPermanentWidget(self.label_view)

        # Versión del software
        self.label_version = QLabel(f"Versión {version}")
        self.label_version.setStyleSheet("margin-right: 30px;")
        self.addPermanentWidget(self.label_version)

        # Hora actual
        self.label_time = QLabel()
        self.label_time.setStyleSheet("margin-right: 30px;")
        self.addPermanentWidget(self.label_time)

        # Espaciador
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.addPermanentWidget(spacer)

        # Estado de conexión: widget compuesto
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(14, 14)

        self.status_text = QLabel("Desconectado")
        self.status_text.setStyleSheet("color: red; font-weight: bold; margin-right: 20px;")

        self.status_widget = QWidget()
        status_layout = QHBoxLayout(self.status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        #status_layout.setSpacing(5)
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_text)

        #self.status_widget.setFixedWidth(180)
        self.addPermanentWidget(self.status_widget)

        # Timer para hora
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

        # Estilos generales
        self.setStyleSheet("""
            QStatusBar {
                background-color: #1c1f26;
                color: white;
                padding: 6px 12px;
                font-weight: normal;
                font-size: 13px;
            }
            QStatusBar::item {
                border: none;
                margin-right: 12px;
            }
            QStatusBar QLabel {
                color: white;
            }
        """)

        # Inicial
        self.set_connection_status(False)

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.label_time.setText(now.toString("dd/MM/yyyy hh:mm:ss"))

    def set_connection_status(self, connected: bool):
        if connected:
            pixmap = self._circle_pixmap(QColor("green"))
            self.status_icon.setPixmap(pixmap)
            self.status_text.setText("Conectado")
            self.status_text.setStyleSheet("color: green; font-weight: bold; margin-right: 20px;")
        else:
            pixmap = self._circle_pixmap(QColor("red"))
            self.status_icon.setPixmap(pixmap)
            self.status_text.setText("Desconectado")
            self.status_text.setStyleSheet("color: red; font-weight: bold; margin-right: 20px;")

    def set_view_name(self, view_name: str):
        self.label_view.setText(f"Vista actual: {view_name}")

    def _circle_pixmap(self, color: QColor) -> QPixmap:
        """Devuelve un QPixmap circular de 12x12 con el color indicado"""
        size = QSize(12, 12)
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size.width(), size.height())
        painter.end()
        return pixmap
