import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QPushButton, QMessageBox, QFileDialog
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor
from datetime import datetime

from reportlab.lib.units import inch, mm  # Añade esto con los otros imports
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
# Importa tus clases (asegúrate de tenerlas en el mismo directorio o en PYTHONPATH)
from main.components.plot_data import PulseGraph  # Tu clase original
from main.components.pdf_builder import PDFBuilder  # La clase que te proporcioné

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba de Generación de PDF")
        self.setGeometry(100, 100, 800, 600)
        
        # Crear widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Crear instancia de PulseGraph
        self.pulse_graph = PulseGraph("Eventos de Prueba")
        
        # Añadir series de datos
        self.pulse_graph.add_series("Serie 1", "#FF5733")  # Rojo/naranja
        self.pulse_graph.add_series("Serie 2", "#33A1FF")  # Azul
        self.pulse_graph.add_series("Serie 3", "#33FF57")  # Verde
        
        # Botones de control
        self.btn_start = QPushButton("Iniciar Simulación")
        self.btn_start.clicked.connect(self.start_simulation)
        
        self.btn_stop = QPushButton("Detener Simulación")
        self.btn_stop.clicked.connect(self.stop_simulation)
        self.btn_stop.setEnabled(False)
        
        self.btn_generate_pdf = QPushButton("Generar PDF")
        self.btn_generate_pdf.clicked.connect(self.generate_pdf_report)
        
        # Timer para simulación
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.simulate_data)
        self.simulation_active = False
        
        # Añadir widgets al layout
        layout.addWidget(self.pulse_graph)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_generate_pdf)
        
        central_widget.setLayout(layout)
        
        # Iniciar el timer base
        self.pulse_graph.start_timer()
    
    def start_simulation(self):
        """Inicia la simulación de datos aleatorios"""
        self.simulation_active = True
        self.simulation_timer.start(1000)  # 1 segundo
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.pulse_graph.reset_graph()
    
    def stop_simulation(self):
        """Detiene la simulación de datos"""
        self.simulation_active = False
        self.simulation_timer.stop()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
    
    def simulate_data(self):
        """Genera datos aleatorios para la simulación"""
        if not self.simulation_active:
            return
            
        # Registrar pulsos aleatorios en las series
        if random.random() > 0.6:  # 40% de probabilidad
            self.pulse_graph.register_pulse("Serie 1")
        
        if random.random() > 0.7:  # 30% de probabilidad
            self.pulse_graph.register_pulse("Serie 2")
        
        if random.random() > 0.8:  # 20% de probabilidad
            self.pulse_graph.register_pulse("Serie 3")
    
    def generate_pdf_report(self):
        """Versión mejorada del generador de PDF"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte PDF", 
            "reporte_eventos.pdf", 
            "PDF Files (*.pdf)")
        
        if not filename:
            return
            
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        try:
            pdf = PDFBuilder(
                title="Reporte de Eventos",
                author="Sistema de Monitoreo",
                page_size=A4
            )
            
            # Configuración básica
            pdf.set_header(text="Reporte de Eventos")
            pdf.set_footer(text="Generado automáticamente")
            
            # Contenido del reporte
            pdf.add_title("Reporte de Eventos del Sistema")
            pdf.add_spacer(0.5*inch)
            
            # Añadir gráfico (versión en memoria)
            pdf.add_section("Gráfico de Eventos")
            pdf.add_widget_as_image(
                self.pulse_graph,
                width="10cm",  
                height="10cm",
                caption="Gráfico generado en tiempo real"
            )
            
            # Generar PDF
            pdf.build(filename)
            
            QMessageBox.information(
                self, "Éxito", 
                f"PDF generado correctamente:\n{filename}")
                
        except Exception as e:
            QMessageBox.critical(
                self, "Error", 
                f"Error al generar PDF:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Estilo moderno opcional
    app.setStyle('Fusion')
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())