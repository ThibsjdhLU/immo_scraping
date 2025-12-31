import hashlib
from typing import List, Dict, Any

class Deduplicator:
    """
    Détecte et supprime les doublons basés sur l'URL ou un hash du contenu.
    """

    def __init__(self):
        self.seen_urls = set()
        self.seen_hashes = set()

    def is_duplicate(self, ad: Dict[str, Any]) -> bool:
        """
        Vérifie si une annonce est un doublon.

        Args:
            ad (dict): L'annonce à vérifier.

        Returns:
            bool: True si doublon, False sinon.
        """
        url = ad.get('url')
        if url and url in self.seen_urls:
            return True

        # Création d'un hash basé sur titre + prix + surface + lieu pour détecter les doublons cross-sites ou républiés
        # On évite la description car elle peut varier légèrement
        content_id = f"{ad.get('title')}{ad.get('price')}{ad.get('surface')}{ad.get('location')}"
        content_hash = hashlib.md5(content_id.encode('utf-8')).hexdigest()

        if content_hash in self.seen_hashes:
            return True

        if url:
            self.seen_urls.add(url)
        self.seen_hashes.add(content_hash)
        return False

    def deduplicate(self, ads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Retourne la liste sans doublons.
        """
        unique_ads = []
        for ad in ads:
            if not self.is_duplicate(ad):
                unique_ads.append(ad)
        return unique_ads
