from typing import Dict, Any, List
from utils.text import clean_text, normalize_price, normalize_surface
from utils.dates import parse_relative_date

class Normalizer:
    """
    Classe responsable de la normalisation des données brutes des annonces.
    """

    def normalize(self, ad: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalise une annonce unique.

        Args:
            ad (dict): Annonce brute.

        Returns:
            dict: Annonce normalisée.
        """
        normalized = ad.copy()

        # Nettoyage textes
        normalized['title'] = clean_text(ad.get('title', ''))
        normalized['description'] = clean_text(ad.get('description', ''))
        normalized['location'] = clean_text(ad.get('location', ''))
        normalized['type'] = clean_text(ad.get('type', ''))

        # Normalisation numériques
        if isinstance(ad.get('price'), str):
            normalized['price'] = normalize_price(ad['price'])

        if isinstance(ad.get('surface'), str):
            normalized['surface'] = normalize_surface(ad['surface'])

        # Normalisation date
        if isinstance(ad.get('date'), str):
            normalized['date'] = parse_relative_date(ad['date'])

        return normalized

    def normalize_list(self, ads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalise une liste d'annonces."""
        return [self.normalize(ad) for ad in ads]
