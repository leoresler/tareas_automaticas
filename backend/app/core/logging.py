"""
Configuración de logging para producción (Render)
Logs en formato JSON para mejor análisis
"""

import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging():
    """
    Configura logging JSON para producción en Render
    
    Formato JSON incluye:
    - timestamp
    - level (INFO, ERROR, etc)
    - message
    - module/function
    - extra fields si se agregan
    """
    logHandler = logging.StreamHandler(sys.stdout)
    
    # Formato JSON para producción
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s %(filename)s %(lineno)d',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logHandler.setFormatter(formatter)
    
    # Configurar logger raíz
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    
    # Nivel de log basado en DEBUG environment variable
    import os
    log_level = logging.INFO if os.getenv("DEBUG", "False").lower() == "false" else logging.DEBUG
    logger.setLevel(log_level)
    
    # Reducir verbosidad de librerías externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene logger configurado para producción
    
    Args:
        name: Nombre del módulo logger
        
    Returns:
        Logger configurado con formato JSON
    """
    return logging.getLogger(name)


# Auto-configurar al importar
if not logging.getLogger().handlers:
    setup_logging()