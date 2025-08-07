from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt6.QtCore import QBuffer, QIODevice
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, 
    Image as RLImage, Table, TableStyle, 
    PageBreak, Frame, PageTemplate, 
    BaseDocTemplate, NextPageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm, inch, cm
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable
from datetime import datetime
import tempfile
import os
from PIL import Image
from io import BytesIO
from reportlab.lib.utils import ImageReader
import io
import sys

class PDFBuilder:
    def __init__(self, title="Reporte", author="Sistema", page_size=A4):
        """
        Inicializa el constructor de PDF
        
        Args:
            title (str): Título del documento
            author (str): Autor del documento
            page_size (tuple): Tamaño de página (letter, A4, etc.)
        """
        self.title = title
        self.author = author
        self.page_size = page_size
        self.elements = []
        self.styles = self._create_styles()
        self.header_content = None
        self.footer_content = None
        self.current_section = None
        self.watermark = None
        
    def _create_styles(self):
        """Crea estilos personalizados para el documento"""
        styles = getSampleStyleSheet()
        
        # Estilo de título principal
        styles.add(ParagraphStyle(
            name='MainTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#003366'),
            spaceAfter=14,
            alignment=1,  # Centrado
            fontName='Helvetica-Bold'
        ))
        
        # Estilo de sección
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#005588'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo de texto normal
        styles.add(ParagraphStyle(
            name='NormalText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
            leading=12
        ))
        
        # Estilo de nota
        styles.add(ParagraphStyle(
            name='NoteText',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            spaceAfter=6,
            leading=11,
            fontName='Helvetica-Oblique'
        ))
        
        styles.add(ParagraphStyle(
            name='FormField',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            leading=14,
            spaceAfter=6,
            leftIndent=10  # Sangría izquierda
        ))
        return styles
    
    def set_header(self, text=None, image_path=None):
        """Configura el contenido del encabezado"""
        self.header_content = {
            'text': text,
            'image': image_path
        }
    
    def set_footer(self, text=None, include_page_numbers=True):
        """Configura el contenido del pie de página"""
        self.footer_content = {
            'text': text,
            'page_numbers': include_page_numbers
        }
    
    def set_watermark(self, text=None, opacity=0.1):
        """Configura una marca de agua para el documento"""
        self.watermark = {
            'text': text,
            'opacity': opacity
        }
    
    def add_title(self, text, style='MainTitle'):
        """Añade un título principal al documento"""
        self.elements.append(Paragraph(text, self.styles[style]))
        self.elements.append(Spacer(1, 0.3*inch))
    
    def add_section(self, title, style='SectionTitle'):
        """Añade una nueva sección al documento"""
        self.current_section = title
        self.elements.append(Paragraph(title, self.styles[style]))
    
    def add_text(self, text, style='NormalText'):
        """Añade texto normal al documento"""
        self.elements.append(Paragraph(text, self.styles[style]))
    
    def add_note(self, text, style='NoteText'):
        """Añade texto de nota al documento"""
        self.elements.append(Paragraph(text, self.styles[style]))
    
    def add_spacer(self, height=0.2):
        """Añade espacio vertical"""
        # Asegurar que height sea numérico
        height = self._validate_measurement(height)
        self.elements.append(Spacer(1, height))
    
    def add_page_break(self):
        """Añade un salto de página"""
        self.elements.append(PageBreak())
    
    
    def _widget_to_image_data(self, widget):
        """Versión corregida para guardado de imágenes"""
        try:
            # Capturar el widget como QPixmap
            pixmap = widget.grab()
            
            # Crear QBuffer para guardar en memoria
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.ReadWrite)
            
            # Guardar la imagen en formato PNG
            qimage = pixmap.toImage()
            success = qimage.save(buffer, "PNG")
            
            if not success:
                raise RuntimeError("No se pudo guardar la imagen en el buffer")
            
            # Obtener los datos binarios
            buffer.seek(0)
            image_data = buffer.data()
            buffer.close()
            
            return image_data
            
        except Exception as e:
            print(f"Error al convertir widget a imagen: {str(e)}")
            raise

        
    def add_widget_as_image(self, widget, caption=None, width=6.0, height=None):
        """Método final corregido"""
        try:
            # Validar medidas
            width_pts = self._validate_measurement(width)
            height_pts = self._validate_measurement(height) if height else None
            
            # Obtener datos de imagen
            img_data = self._widget_to_image_data(widget)
            
            # Crear archivo temporal seguro
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Guardar en archivo temporal
            with open(temp_path, 'wb') as f:
                f.write(img_data)
            
            # Calcular altura si no se especifica
            if height_pts is None:
                with Image.open(temp_path) as img:
                    aspect_ratio = img.height / img.width
                    height_pts = width_pts * aspect_ratio
            
            # Añadir imagen al PDF
            img = RLImage(temp_path, width=width_pts, height=height_pts)
            self.elements.append(img)
            
            # Añadir caption si existe
            if caption:
                self.add_text(f"<i>{caption}</i>", 'NoteText')
                
            # Programar eliminación del temporal después de usarlo
            img._filename = temp_path
                
        except Exception as e:
            # Limpiar temporal si hubo error
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
            print(f"Error al añadir widget: {str(e)}")
            raise

    def _widget_to_temp_image(self, widget):
        """Convierte un widget a imagen temporal de manera robusta"""
        try:
            # Capturar el widget
            pixmap = widget.grab()
            
            # Crear archivo temporal
            temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_path = temp_img.name
            temp_img.close()
            
            # Guardar la imagen
            qimage = pixmap.toImage()
            qimage.save(temp_path, "PNG")
            
            return temp_path
            
        except Exception as e:
            print(f"Error al convertir widget a imagen: {str(e)}")
            raise

    
    def _validate_measurement(self, value):
        """Convierte cualquier medida a puntos (float)"""
        if value is None:
            return None
            
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Manejar unidades como "6inch", "15cm", "200mm"
            value = value.lower().replace(' ', '')
            
            if 'inch' in value:
                return float(value.replace('inch', '')) * inch
            elif 'cm' in value:
                return float(value.replace('cm', '')) * cm
            elif 'mm' in value:
                return float(value.replace('mm', '')) * mm
            else:
                # Asumir que está en pulgadas si no se especifica unidad
                try:
                    return float(value) * inch
                except ValueError:
                    raise ValueError(f"Formato de medida no válido: {value}")
        
        raise TypeError(f"Tipo de medida no soportado: {type(value)}")


    def add_table(self, data, col_widths=None, style=None):
        """
        Añade una tabla al documento
        
        Args:
            data: Lista de listas con los datos de la tabla
            col_widths: Lista con anchos de columnas (opcional)
            style: Estilo de tabla personalizado (opcional)
        """
        if style is None:
            style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#005588')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f8ff')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]
        
        # Validar anchos de columnas
        if col_widths is not None:
            col_widths = [self._validate_measurement(w) for w in col_widths]
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle(style))
        self.elements.append(table)
        
    def add_form_field(self, name, value, style='FormField', name_color='#005588', value_color='#333333'):
        """
        Versión con colores personalizables
        
        Args:
            name_color (str): Color hexadecimal para el nombre (ej. '#005588')
            value_color (str): Color hexadecimal para el valor (ej. '#333333')
        """
        text = (
            f"<font color='{name_color}'><b>{name}:</b></font> "
            f"<font color='{value_color}'>{value}</font>"
        )
        self.elements.append(Paragraph(text, self.styles[style]))
        
    def build(self, filename):
        """
        Genera el documento PDF
        
        Args:
            filename: Ruta del archivo PDF a generar
        """
        try:
            # Crear documento con márgenes
            doc = SimpleDocTemplate(
                filename,
                pagesize=self.page_size,
                title=self.title,
                author=self.author,
                leftMargin=15*mm,
                rightMargin=15*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # Construir el PDF
            doc.build(
                self.elements,
                onFirstPage=self._on_first_page,
                onLaterPages=self._on_later_page,
                canvasmaker=NumberedCanvas
            )
            
        except Exception as e:
            print(f"Error al generar PDF: {str(e)}")
            raise
        finally:
            # Limpiar archivos temporales
            self._clean_temp_files()
    
    def _on_first_page(self, canvas, doc):
        """Personaliza la primera página"""
        self._draw_header(canvas, doc)
        self._draw_footer(canvas, doc)
        self._draw_watermark(canvas, doc)
    
    def _on_later_page(self, canvas, doc):
        """Personaliza páginas subsiguientes"""
        self._draw_header(canvas, doc)
        self._draw_footer(canvas, doc)
        self._draw_watermark(canvas, doc)
    
    def _draw_header(self, canvas, doc):
        """Dibuja el encabezado"""
        if self.header_content is None:
            return
            
        canvas.saveState()
        
        width = doc.width
        y = doc.pagesize[1] - 15*mm
        
        # Imagen de encabezado
        if self.header_content.get('image'):
            try:
                img = RLImage(self.header_content['image'], width=2*inch, height=0.5*inch)
                img.drawOn(canvas, doc.leftMargin, y - 0.5*inch)
            except Exception as e:
                print(f"Error al dibujar imagen de encabezado: {str(e)}")
        
        # Texto de encabezado
        if self.header_content.get('text'):
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawRightString(doc.leftMargin + width, y, self.header_content['text'])
        
        canvas.restoreState()
    
    def _draw_footer(self, canvas, doc):
        """Dibuja el pie de página"""
        if self.footer_content is None:
            return
            
        canvas.saveState()
        
        width = doc.width
        y = 10*mm
        
        # Texto de pie de página
        if self.footer_content.get('text'):
            canvas.setFont("Helvetica", 8)
            canvas.drawString(doc.leftMargin, y, self.footer_content['text'])
        
        canvas.restoreState()
    
    def _draw_watermark(self, canvas, doc):
        """Dibuja la marca de agua"""
        if self.watermark is None:
            return
            
        canvas.saveState()
        canvas.setFillAlpha(self.watermark['opacity'])
        canvas.setFont("Helvetica-Bold", 60)
        canvas.setFillColor(colors.lightgrey)
        
        canvas.translate(doc.pagesize[0]/2, doc.pagesize[1]/3)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, self.watermark['text'])
        
        canvas.restoreState()
    
    def _clean_temp_files(self):
        """Limpia archivos temporales creados"""
        for element in self.elements:
            if isinstance(element, RLImage):
                if hasattr(element, '_filename') and os.path.exists(element._filename):
                    try:
                        os.unlink(element._filename)
                    except Exception as e:
                        print(f"Error al limpiar archivo temporal: {str(e)}")

class NumberedCanvas(canvas.Canvas):
    """Canvas personalizado para números de página"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        """Añade números de página"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_page_number(self, page_count):
        """Dibuja el número de página"""
        self.setFont("Helvetica", 8)
        self.drawRightString(
            200*mm, 10*mm,
            f"Página {self._pageNumber} de {page_count}"
        )
    
    