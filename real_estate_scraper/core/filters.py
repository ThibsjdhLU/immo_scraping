from typing import List, Dict, Any
import logging

class FilterEngine:
    """
    Applique les filtres définis dans la configuration.
    """

    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.rejected_log = []

    def apply_filters(self, ads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtre la liste des annonces.

        Args:
            ads (list): Liste d'annonces normalisées.

        Returns:
            list: Liste filtrée.
        """
        filtered_ads = []
        criteria = self.config.get('search', {})
        price_cfg = criteria.get('price', {})
        surface_cfg = criteria.get('surface', {})
        keywords = criteria.get('keywords', {})

        min_price = price_cfg.get('min')
        max_price = price_cfg.get('max')
        min_surface = surface_cfg.get('min')

        incl_kw = [k.lower() for k in keywords.get('include', [])]
        excl_kw = [k.lower() for k in keywords.get('exclude', [])]

        for ad in ads:
            reason = None

            # Filtre Prix
            price = ad.get('price')
            if price is not None:
                if min_price and price < min_price:
                    reason = f"Prix trop bas ({price} < {min_price})"
                elif max_price and price > max_price:
                    reason = f"Prix trop haut ({price} > {max_price})"

            # Filtre Surface
            if not reason:
                surface = ad.get('surface')
                if surface is not None:
                    if min_surface and surface < min_surface:
                        reason = f"Surface trop petite ({surface} < {min_surface})"

            # Filtre Mots-clés
            if not reason:
                text_content = (str(ad.get('title', '')) + " " + str(ad.get('description', ''))).lower()

                # Exclusion prioritaire
                for kw in excl_kw:
                    if kw in text_content:
                        reason = f"Mot-clé exclu trouvé: {kw}"
                        break

                # Inclusion (si liste non vide)
                if not reason and incl_kw:
                    found = False
                    for kw in incl_kw:
                        if kw in text_content:
                            found = True
                            break
                    if not found:
                        reason = "Aucun mot-clé inclus trouvé"

            if reason:
                self.logger.debug(f"Annonce rejetée ({ad.get('url')}): {reason}")
                self.rejected_log.append({'url': ad.get('url'), 'reason': reason})
            else:
                filtered_ads.append(ad)

        self.logger.info(f"{len(filtered_ads)} annonces retenues sur {len(ads)}.")
        return filtered_ads
