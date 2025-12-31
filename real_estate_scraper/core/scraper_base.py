from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging
import time
import random

class ScraperBase(ABC):
    """
    Classe abstraite définissant l'interface pour tous les scrapers.
    """

    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialise le scraper.

        Args:
            config (dict): Configuration globale (contient filtres, localisations, etc.).
            logger (logging.Logger): Logger partagé.
        """
        self.config = config
        self.logger = logger
        self.site_name = "unknown"
        self.results: List[Dict[str, Any]] = []

    @abstractmethod
    def run(self) -> List[Dict[str, Any]]:
        """
        Exécute le scraping. Doit être implémenté par les sous-classes.

        Returns:
            List[Dict]: Liste d'annonces brutes extraites.
        """
        pass

    def sleep_random(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Pause aléatoire pour simuler un comportement humain."""
        sleep_time = random.uniform(min_seconds, max_seconds)
        self.logger.debug(f"Pause de {sleep_time:.2f}s...")
        time.sleep(sleep_time)

    def log_error(self, message: str, exception: Exception = None):
        """Log une erreur avec contexte optionnel."""
        if exception:
            self.logger.error(f"[{self.site_name}] {message}: {str(exception)}")
        else:
            self.logger.error(f"[{self.site_name}] {message}")
