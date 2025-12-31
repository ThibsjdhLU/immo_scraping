import re
from typing import Optional

def clean_text(text: Optional[str]) -> str:
    """
    Nettoie un texte : supprime les espaces superflus, sauts de ligne, etc.

    Args:
        text (str): Texte brut.

    Returns:
        str: Texte nettoyé.
    """
    if not text:
        return ""
    # Remplace les séquences d'espaces/newlines par un espace simple
    return re.sub(r'\s+', ' ', str(text)).strip()

def extract_digits(text: str) -> Optional[int]:
    """
    Extrait les chiffres d'une chaîne et retourne un entier.
    Utile pour prix et surfaces.

    Args:
        text (str): Chaîne contenant des chiffres (ex: "1 200 €").

    Returns:
        int: La valeur entière ou None si échec.
    """
    if not text:
        return None
    # Garde seulement les chiffres
    digits = re.sub(r'[^\d]', '', str(text))
    if digits:
        return int(digits)
    return None

def normalize_price(price_raw: str) -> Optional[float]:
    """
    Convertit une chaîne de prix en float.
    """
    return float(extract_digits(price_raw)) if extract_digits(price_raw) is not None else None

def normalize_surface(surface_raw: str) -> Optional[float]:
    """
    Convertit une chaîne de surface en float.
    """
    # Parfois "20,5 m2", on remplace virgule par point
    if not surface_raw:
        return None
    clean = surface_raw.replace(',', '.').replace('m²', '').replace('m2', '')
    # Extraction plus fine pour garder les décimales
    match = re.search(r'(\d+(\.\d+)?)', clean)
    if match:
        return float(match.group(1))
    return None
