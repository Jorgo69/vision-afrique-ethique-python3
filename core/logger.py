import logging
from core.config import settings

def setup_logger(name: str) -> logging.Logger:
    """Configure un logger pour l'application."""
    logger = logging.getLogger(name)
    
    # Niveau selon l'environnement
    level = logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO
    logger.setLevel(level)
    
    # Format
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger