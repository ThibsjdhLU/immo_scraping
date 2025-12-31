import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from core.scraper_base import ScraperBase
from utils.http import get_default_headers

class LogicImmoScraper(ScraperBase):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.site_name = "LogicImmo"
        self.base_url = "https://www.logic-immo.com/recherche-immobiliere.php"

    def run(self) -> List[Dict[str, Any]]:
        # LogicImmo est aussi protégé, mais tentons une approche requests simple
        # Si ça échoue, c'est "normal" pour des sites immo majeurs sans proxy résidenciel

        self.logger.info(f"Démarrage du scraping {self.site_name} (Requests)...")
        results = []

        # Mapping paramètres
        # LogicImmo utilise des URLs spécifiques souvent (ex: /vente-immobilier-paris-75001,...)
        # Pour faire simple, on simule une requête sur une URL construite ou on avertit

        # Pour cet exercice, on va simuler une réponse car LogicImmo requiert des headers complexes et cookies
        # Mais je vais coder la logique comme si l'accès était ouvert.

        # Construction URL (fictive fonctionnelle)
        # https://www.logic-immo.com/vente-immobilier-paris-75001,100_1.html

        loc = self.config.get('search', {}).get('locations', [])[0]
        zip_code = loc.get('zip_code')
        city = loc.get('city').lower()

        target_url = f"https://www.logic-immo.com/vente-immobilier-{city}-{zip_code},100_1.html"

        try:
            headers = get_default_headers()
            self.sleep_random(1, 2)

            # Note: LogicImmo bloque souvent requests sans cookies/JS valide (Datadome/Akamai)
            # En cas de blocage, on retourne vide.

            response = requests.get(target_url, headers=headers, timeout=10)

            if response.status_code != 200:
                self.logger.warning(f"Statut HTTP {response.status_code} sur LogicImmo")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # Selecteurs (sujets à changement)
            annonces = soup.select('.offer-list-item') # Ancienne classe
            # LogicImmo a migré vers une structure React très similaire à SeLoger (même groupe)

            if not annonces:
                # Tentative autre selecteur
                annonces = soup.select('div[class*="PropertyCard"]')

            self.logger.info(f"Annonces trouvées : {len(annonces)}")

            for ann in annonces:
                try:
                    link_tag = ann.select_one('a')
                    url = link_tag['href'] if link_tag else ""

                    price_tag = ann.select_one('[class*="price"]')
                    price = price_tag.get_text(strip=True) if price_tag else "0"

                    title = "Annonce LogicImmo"

                    results.append({
                        'site': self.site_name,
                        'title': title,
                        'price': price,
                        'location': city,
                        'url': url,
                        'description': ann.get_text(strip=True),
                        'date': "Aujourd'hui"
                    })
                except:
                    pass

        except Exception as e:
            self.log_error("Erreur Requests LogicImmo", e)

        return results
