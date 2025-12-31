import logging
import sys
from pathlib import Path

def setup_logger(name: str = "RealEstateScraper", log_file: str = "scraper.log", level: int = logging.INFO) -> logging.Logger:
    """
    Configure et retourne un logger.

    Args:
        name (str): Nom du logger.
        log_file (str): Chemin du fichier de log.
        level (int): Niveau de log (ex: logging.INFO).

    Returns:
        logging.Logger: Instance de logger configurée.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Eviter d'ajouter des handlers multiples si le logger existe déjà
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler fichier
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
