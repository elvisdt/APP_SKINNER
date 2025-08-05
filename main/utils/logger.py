import logging
import os

LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
LOG_LEVEL = logging.DEBUG  # Puedes cambiar a INFO o WARNING si prefieres menos verbosidad
LOG_FILE = "app.log"  # Puedes cambiar el nombre y ubicación si lo deseas

class Logger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:  # Para evitar múltiples handlers duplicados
            self.logger.setLevel(LOG_LEVEL)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(LOG_LEVEL)
            console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

            # File handler
            file_handler = logging.FileHandler(LOG_FILE, mode='a')
            file_handler.setLevel(LOG_LEVEL)
            file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
