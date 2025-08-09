# frontend/styles/styles.py
from main.resources.compiled_resources import qInitResources
qInitResources()


class AppStyles:
    # Colores principales
    PRIMARY_COLOR = "#2c3e50"
    PRIMARY_HOVER = "#34495e"
    ACCENT_COLOR = "#3498db"
    BACKGROUND_COLOR = "#f5f5f5"
    SECONDARY_BG = "#ecf0f1"
    TEXT_COLOR = "#2c3e50"
    TEXT_SECONDARY = "#7f8c8d"

    # Estilos del menú
    MENU_BUTTON = """
        QPushButton {
            background-color: #2c3e50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: left;
            font-size: 14px;
            font-weight: 500;
            border-left: 2px solid transparent;
        }
        QPushButton:hover {
            background-color: #34495e;
            border-left: 2px solid #3498db;
        }
        QPushButton:checked {
            background-color: #4A6794;
            font-weight: bold;
            border-left: 2px solid #3498db;
        }
    """

    SIDE_MENU = """
        QWidget{
            background-color: #2c3e50;
        }
    """



    MENU_TITLE = """
        QLabel {
            background-color: #1a252f;
            color: white;
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
        }
    """

    # # Estilos de vistas
    # VIEW_TITLE = """
    #     QLabel {
    #         font-size: 20px;
    #         font-weight: bold;
    #         color: #2c3e50;
    #         padding: 10px;
    #     }
    # """

    CONTENT_FRAME = """
        QFrame {
            background-color: #ecf0f1;
            border-radius: 10px;
            padding: 20px;
        }
    """

    ACTION_BUTTON = """
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 10px;
            border-radius: 5px;
            font-size: 12px;
            font-weight: demibold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:disabled {
            background-color: #95a5a6;  /* Un azul grisáceo */
            color: #ecf0f1;
        }
    """


    OPTION_BUTTON = """
        QPushButton {
            background-color: white;
            border: 1px solid #bdc3c7;
            padding: 15px;
            margin: 5px;
            border-radius: 5px;
            text-align: left;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #ecf0f1;
            border: 1px solid #3498db;
        }
    """

    VIEW_TITLE = """
        QLabel {
            color: #2c3e50;
            padding: 5px;
        }
    """
    
    SHORT_DESCRIPTION = """
        QLabel {
            color: #34495e;
            font-size: 14px;
            padding: 10px;
        }
    """
    
    LABEL_STYLE = """
        QLabel {
            color: #2c3e50;
            font-size: 13px;
        }
    """


    # Estilo para valores (VALUE)
    # Estilos para los estados de LED
    LABEL_LED_ON_STYLE = """
        QLabel {
            color: #ffffff;
            font-weight: bold;
            background-color: #2ecc71;  /* Verde para ON */
            border-radius: 8px;
            padding: 3px 8px;
            min-width: 60px;
            text-align: center;
        }
    """

    LABEL_LED_OFF_STYLE = """
        QLabel {
            color: #ffffff;
            font-weight: bold;
            background-color: #e74c3c;  /* Rojo para OFF */
            border-radius: 8px;
            padding: 3px 8px;
            min-width: 60px;
            text-align: center;
        }
    """

    # Modifica el estilo normal para que coincida
    LABEL_VALUE_STYLE = """
        QLabel {
            color: #2c3e50;
            font-weight: normal;
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
            padding: 3px 8px;
            min-width: 80px;
            text-align: right;
        }
    """
        
        # Estilo para claves (KEY)
    LABEL_KEY_STYLE = """
        QLabel {
            font-size: 14px;
            color: #2c3e50;
            font-weight: 500;
        }
    """
    LINK_LABEL_STYLE = """
    QLabel {
            font-size: 14px;
            color: #2c3e50;
            font-weight: 500;
        }
        a {
            color: #1e90ff;             /* Azul llamativo */
            text-decoration: underline;
            font-weight: bold;
        }
        a:hover {
            color: #104e8b;             /* Azul más oscuro al pasar el mouse */
        }
    """

    INPUT_STYLE = """
        QSpinBox, QSlider {
            font-size: 14px;
            padding: 4px;
        }
    """

    # Nuevos estilos agregados
    INPUT_FIELD_STYLE = """
        QLineEdit {
            background-color: #2c3e50;
            color: white;
            border: 1px solid #7f8c8d;
            padding: 6px;
            border-radius: 4px;
        }
        QLineEdit:focus {
            border: 1px solid #3498db;
        }
    """
    CMBOX_UART_STYLE = """
        QComboBox {
            background-color: #2c3e50;
            color: white;
            border: 1px solid #2980b9;
            border-radius: 4px;
            padding: 5px 10px;
            min-width: 100px;
        }
        QComboBox QAbstractItemView {
            background-color: #34495e;
            color: white;
            selection-background-color: #1abc9c;
            selection-color: black;
        }
    """
    
    CMBOX_PLNC_STYLE = """
        QComboBox {
            background-color: #2c3e50;
            color: white;
            border: 1px solid #2980b9;
            border-radius: 6px;
            padding: 4px 4px;
            width: 100px;
            font-size: 12px;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #2980b9;
            border-left-style: solid;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            background-color: #34495e;
        }

        QComboBox::down-arrow {
            image: url(:/icons/fill-down);
            width: 12px;
            height: 12px;
        }

        QComboBox QAbstractItemView {
            background-color: #34495e;
            color: white;
            selection-background-color: #1abc9c;
            selection-color: black;
            border: 1px solid #2980b9;
            outline: 0;
            padding: 4px;
            margin: 0;
        }

        QComboBox:hover {
            border-color: #1abc9c;
        }

        QComboBox::drop-down:hover {
            background-color: #3d566e;
        }

    """

        # ESTILO DESHABILITADO (GRISES)
    CMBOX_STYLE_DISABLED = """
        QComboBox {
            background-color: #ecf0f1;
            color: #95a5a6;
            border: 1px solid #A1A1A1;
            border-radius: 6px;
            padding: 4px 4px;
            width: 100px;
            font-size: 12px;
        }
        QComboBox::drop-down {
            background-color: #A1A1A1;
            border-left-color: #A1A1A1;
        }
    """
    
    LABEL_SECONDARY_STYLE = """
        QLabel {
            font-size: 14px;
            color: #7f8c8d;  
            font-weight: 400;
        }
    """
    
    # SPINBOX_STYLE = f"""
    #     QSpinBox {{
    #         background-color: {PRIMARY_COLOR};
    #         color: white;
    #         border: 1px solid {ACCENT_COLOR};
    #         border-radius: 4px;
    #         padding: 1px 4px 1px 4px;  
    #         font-size: 12px;            
    #         min-width: 65px;            
    #         min-height: 20px;               
    #     }}

    #     QSpinBox::up-button {{
    #         width: 12px;
    #         height: 10px;                
    #         subcontrol-position: top right;
    #         margin-right: 1px;          
    #         image: url(:/icons/up-png);
    #         border-left: 1px solid {ACCENT_COLOR};
    #         border-bottom: 1px solid {ACCENT_COLOR};
    #         background-color: transparent;  
    #     }}

    #     QSpinBox::down-button {{
    #         width: 12px;
    #         height: 10px;
    #         subcontrol-position: bottom right;
    #         margin-right: 1px;
    #         image: url(:/icons/down-png);
    #         border-top: 1px solid {ACCENT_COLOR};
    #         border-left: 1px solid {ACCENT_COLOR};
    #         background-color: transparent;
    #     }}

    #     QSpinBox::up-button:hover, 
    #     QSpinBox::down-button:hover {{
    #         background-color: rgba(255, 255, 255, 0.2);
    #     }}


    #     QSpinBox::up-button:pressed, 
    #     QSpinBox::down-button:pressed {{
    #         background-color: {ACCENT_COLOR};
    #         border-left: 1px solid {PRIMARY_HOVER};
    #         border-bottom: 1px solid {PRIMARY_HOVER};
    #     }}

    #     QSpinBox::text {{
    #         padding-top: 1px;
    #         padding-bottom: 1px;
    #     }}
    # """

    SPINBOX_STYLE = f"""
        /* Estilo base */
        QSpinBox {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: 1px solid {ACCENT_COLOR};
            border-radius: 4px;
            padding: 1px 4px 1px 4px;
            font-size: 12px;
            min-width: 65px;
            min-height: 20px;
        }}
        
        /* Estilo cuando está deshabilitado */
        QSpinBox:disabled {{
            background-color: {SECONDARY_BG};  /* Usar tu color secundario o un gris */
            color: #c0c0c0;                      /* Texto gris claro */
            border: 1px solid #606060;
        }}
        
        /* Botón de incremento - estado normal */
        QSpinBox::up-button {{
            width: 12px;
            height: 10px;
            subcontrol-position: top right;
            margin-right: 1px;
            image: url(:/icons/up-png);
            border-left: 1px solid {ACCENT_COLOR};
            border-bottom: 1px solid {ACCENT_COLOR};
            background-color: transparent;
        }}
        
        /* Botón de incremento - estado deshabilitado */
        QSpinBox::up-button:disabled {{
            image: url(:/icons/up-disabled.png);  /* Icono alternativo para deshabilitado */
            border-left: 1px solid #606060;
            border-bottom: 1px solid #606060;
        }}
        
        /* Botón de decremento - estado normal */
        QSpinBox::down-button {{
            width: 12px;
            height: 10px;
            subcontrol-position: bottom right;
            margin-right: 1px;
            image: url(:/icons/down-png);
            border-top: 1px solid {ACCENT_COLOR};
            border-left: 1px solid {ACCENT_COLOR};
            background-color: transparent;
        }}
        
        /* Botón de decremento - estado deshabilitado */
        QSpinBox::down-button:disabled {{
            image: url(:/icons/down-disabled.png);  /* Icono alternativo para deshabilitado */
            border-top: 1px solid #606060;
            border-left: 1px solid #606060;
        }}
        
        /* Efectos hover (solo cuando está habilitado) */
        QSpinBox::up-button:hover:enabled, 
        QSpinBox::down-button:hover:enabled {{
            background-color: rgba(255, 255, 255, 0.2);
        }}
        
        /* Efectos pressed (solo cuando está habilitado) */
        QSpinBox::up-button:pressed:enabled, 
        QSpinBox::down-button:pressed:enabled {{
            background-color: {ACCENT_COLOR};
            border-left: 1px solid {PRIMARY_HOVER};
            border-bottom: 1px solid {PRIMARY_HOVER};
        }}
        
        /* Estilo del texto */
        QSpinBox::text {{
            padding-top: 1px;
            padding-bottom: 1px;
        }}
        
        /* Texto cuando está deshabilitado */
        QSpinBox:disabled::text {{
            color: #a0a0a0;
        }}
    """
    BUTTON_STYLE = """
        QPushButton {
            background-color: #2c3e50;
            color: white;
            padding: 8px 12px;
            border: 1px solid #7f8c8d;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #34495e;
        }
    """
    BUTTON_STYLE_MODERN = """
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #3498db, stop:1 #2980b9);
            color: white;
            padding: 10px 20px;
            border: 1px solid #3498db;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            min-width: 140px;
            margin: 4px;
        }
        QPushButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #3aa3ff, stop:1 #2c8fd8);
            border-color: #3aa3ff;
        }
        QPushButton:pressed {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #2980b9, stop:1 #1a6ca3);
        }
        QPushButton:disabled {
            background-color: #e9ecef;
            color: #6c757d;
            border: 1px solid #ced4da;
        }
    """

    BUTTON_STYLE_ALT = """
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #2ecc71, stop:1 #27ae60);
            color: white;
            padding: 10px 20px;
            border: 1px solid #2ecc71;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            min-width: 140px;
            margin: 4px;
        }
        QPushButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #31d673, stop:1 #2ab563);
            border-color: #31d673;
        }
        QPushButton:pressed {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #27ae60, stop:1 #1e995b);
        }
        QPushButton:disabled {
            background-color: #e9ecef;
            color: #6c757d;
            border: 1px solid #ced4da;
        }
    """

    STOP_BUTTON_STYLE = """
        QPushButton {
            background-color: #e74c3c;
            color: white;
            padding: 10px 20px;
            font-weight: bold;
            border-radius: 5px;
            border: none;
        }
        QPushButton:hover {
            background-color: #c0392b;
        }
    """

    LOG_AREA_STYLE = """
        QTextEdit {
            background-color: #2c3e50;
            color: #ecf0f1;
            font-family: Consolas, monospace;
            padding: 10px;
            border: 1px solid #7f8c8d;
            border-radius: 5px;
        }
    """

    SLIDER_STYLE = """
        QSlider::groove:horizontal {
            height: 6px;
            background: #bdc3c7;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            width: 14px;
            background: #3498db;
            border-radius: 7px;
            margin: -5px 0;
        }
    """

    CHECKBOX_STYLE = """
        QCheckBox {
            font-size: 14px;
            color: #2c3e50;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        QCheckBox::indicator:checked {
            background-color: #3498db;
            border: 1px solid #2980b9;
        }
    """

    GPIO_INPUT_LABEL_STYLE = """
        QLabel {
            background-color: #ffffff;
            color: #2c3e50;
            border: 1px solid #bdc3c7;
            padding: 5px;
            border-radius: 5px;
            font-weight: bold;
            text-align: center;
        }
    """

    # frontend/styles/styles.py
    TAB_STYLE = """
        QTabWidget::pane {
            border: 1px solid #bdc3c7;
            background-color: #f9f9f9;
            border-radius: 4px;
        }
        QTabBar::tab {
            background: #ecf0f1;
            color: #2c3e50;
            padding: 8px 18px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            margin-right: 4px;
        }
        QTabBar::tab:selected {
            background: #3498db;
            color: white;
        }
        QTabBar::tab:hover {
            background: #2980b9;
            color: white;
        }
    """

    PROGRESS_STYLE = """
        QProgressBar {
            border: 1px solid #ccc;
            border-radius: 5px;
            text-align: center;
            height: 20px;
            background-color: #2c3e50;
            color: white;
        }
        QProgressBar::chunk {
            background-color: #3498db;
            width: 20px;
        }
        """

    # SHORT_DESCRIPTION = """
    #     QLabel {
    #         font-size: 16px;
    #         color: #7f8c8d;
    #         font-style: italic;
    #         font-weight: 500;
    #         padding-bottom: 10px;
    #     }
    # """
    BUTTON_CONNECTED_UART ="""
        QPushButton {
            background-color: #e74c3c;
            color: white;
            padding: 6px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #c0392b;
        }
    """
    BUTTON_DISCONNECTED_UART = """
        QPushButton {
            background-color: #2ecc71;
            color: white;
            padding: 6px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #27ae60;
        }
    """
    BUTTON_DISABLED_UART = """
        QPushButton {
            background-color: #bdc3c7;
            color: #ecf0f1;
            padding: 6px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #95a5a6;
        }
    """
    # Estilo para botón de Iniciar
    BUTTON_START = """
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #27ae60, stop:1 #2ecc71);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 7px 10px;
            font-weight: bold;
            font-size: 13px;
            min-width: 120px;
            margin: 4px;
        }
        QPushButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #2ecc71, stop:1 #27ae60);
        }
        QPushButton:pressed {
            background-color: #219653;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #737373;
        }
    """

    # Estilo para botón de Detener
    BUTTON_STOP = """
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #e74c3c, stop:1 #c0392b);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 7px 10px;
            font-weight: bold;
            font-size: 13px;
            min-width: 120px;
            margin: 4px;
        }
        QPushButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #c0392b, stop:1 #e74c3c);
        }
        QPushButton:pressed {
            background-color: #a53125;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #737373;
        }
    """
    MESSAGEBOX_STYLE = """
            QMessageBox {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QLabel {
                color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
    
    @staticmethod
    def groupbox_style(border_color):
        return f"""
            QGroupBox {{
                border: 1px solid {border_color};
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: {border_color};
                color: white;
                border-radius: 5px;
            }}
        """
    @staticmethod
    def groupbox_style_ori(border_color):
        return f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {border_color};
                border-radius: 8px;
                margin-top: 20px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: {border_color};
                color: white;
                border-radius: 5px;
            }}
        """
