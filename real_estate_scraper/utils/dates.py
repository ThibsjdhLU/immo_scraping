from datetime import datetime, timedelta
import re

def parse_relative_date(date_str: str) -> str:
    """
    Tente de convertir une date relative (ex: "Hier", "Il y a 2 jours")
    en format ISO (YYYY-MM-DD).

    Args:
        date_str (str): Chaîne de date brute.

    Returns:
        str: Date au format YYYY-MM-DD ou la chaîne originale si échec.
    """
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")

    date_str = date_str.lower().strip()
    now = datetime.now()

    if "aujourd'hui" in date_str or "minutes" in date_str or "heures" in date_str:
        return now.strftime("%Y-%m-%d")

    if "hier" in date_str:
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")

    # Pattern "Il y a X jours"
    match = re.search(r'il y a (\d+) jour', date_str)
    if match:
        days = int(match.group(1))
        return (now - timedelta(days=days)).strftime("%Y-%m-%d")

    # Si c'est déjà une date type dd/mm/yyyy
    match_date = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
    if match_date:
        day, month, year = match_date.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    return now.strftime("%Y-%m-%d")
