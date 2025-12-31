from typing import List, Dict, Any
from playwright.sync_api import sync_playwright
import urllib.parse
from core.scraper_base import ScraperBase
from utils.http import get_random_user_agent

class LeBonCoinScraper(ScraperBase):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.site_name = "LeBonCoin"
        self.base_url = "https://www.leboncoin.fr/recherche"

    def build_url(self) -> str:
        """Construit l'URL de recherche."""
        params = {
            "category": "9",  # Immobilier
            "locations": self._get_locations_param(),
            "real_estate_type": self._get_types_param(),
            "price": self._get_price_param(),
            "square": self._get_surface_param(),
        }
        # Filtrer les params None/Empty
        params = {k: v for k, v in params.items() if v}
        return f"{self.base_url}?{urllib.parse.urlencode(params)}"

    def _get_locations_param(self):
        # Simplification: LBC utilise des codes insee ou des noms de ville.
        # Ici on prend juste la première ville configurée pour l'exemple
        locs = self.config.get('search', {}).get('locations', [])
        if locs:
            return locs[0].get('city')
        return "Paris"

    def _get_types_param(self):
        types = self.config.get('search', {}).get('types', [])
        mapped = []
        if "maison" in types: mapped.append("1")
        if "appartement" in types: mapped.append("2")
        return ",".join(mapped) if mapped else None

    def _get_price_param(self):
        p = self.config.get('search', {}).get('price', {})
        min_p = p.get('min')
        max_p = p.get('max')
        if min_p and max_p: return f"{min_p}-{max_p}"
        if min_p: return f"min-{min_p}"
        if max_p: return f"{max_p}-max"
        return None

    def _get_surface_param(self):
        s = self.config.get('search', {}).get('surface', {})
        min_s = s.get('min')
        if min_s: return f"min-{min_s}"
        return None

    def run(self) -> List[Dict[str, Any]]:
        self.logger.info(f"Démarrage du scraping {self.site_name}...")
        results = []

        try:
            with sync_playwright() as p:
                browser_args = []
                if self.config.get('scraping', {}).get('headless', True):
                    browser_args.append("--headless=new")

                browser = p.chromium.launch(
                    headless=self.config.get('scraping', {}).get('headless', True),
                    args=["--disable-blink-features=AutomationControlled"]
                )

                context = browser.new_context(
                    user_agent=get_random_user_agent(),
                    viewport={'width': 1280, 'height': 800}
                )

                # Injection pour masquer webdriver (basic)
                context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                page = context.new_page()

                url = self.build_url()
                self.logger.info(f"Navigation vers : {url}")

                try:
                    page.goto(url, timeout=60000, wait_until="domcontentloaded")
                except Exception as e:
                    self.logger.error(f"Timeout ou erreur de connexion : {e}")
                    return []

                self.sleep_random(2, 5)

                # Gestion cookies (Selector générique, peut changer)
                try:
                    accept_cookies = page.get_by_text("Tout accepter", exact=False)
                    if accept_cookies.is_visible():
                        accept_cookies.click()
                        self.sleep_random(1, 2)
                except:
                    pass

                # Sélecteurs (Note: LBC change souvent ses classes CSS obfusquées)
                # On essaie de viser des attributs stables ou la structure
                # Exemple hypothétique basé sur la structure courante (article ou a[data-test-id='ad'])

                # On attend que des annonces soient chargées
                if "captcha-delivery" in page.content() or "datadome" in page.content().lower():
                    self.logger.error("DETECTÉ COMME BOT (DataDome/Captcha). Impossible de scraper LeBonCoin.")
                    browser.close()
                    return []

                try:
                    page.wait_for_selector('a[data-test-id="ad"]', timeout=15000)
                except:
                    # Double check si on a été bloqué entre temps
                    if "captcha-delivery" in page.content():
                         self.logger.error("DETECTÉ COMME BOT (DataDome/Captcha).")
                         browser.close()
                         return []
                    self.logger.warning("Aucune annonce trouvée ou structure changée.")

                ads = page.query_selector_all('a[data-test-id="ad"]')
                self.logger.info(f"Annonces trouvées sur la page : {len(ads)}")

                for ad_elem in ads:
                    try:
                        link = ad_elem.get_attribute('href')
                        if link and not link.startswith('http'):
                            link = "https://www.leboncoin.fr" + link

                        # Extraction basique depuis la carte
                        text_content = ad_elem.inner_text()

                        # Parsing rudimentaire du texte de la carte
                        # Titre souvent en haut
                        # Prix avec €

                        price = "0"
                        lines = text_content.split('\n')
                        for line in lines:
                            if '€' in line:
                                price = line
                                break

                        # On pourrait cliquer sur chaque annonce pour le détail,
                        # mais pour cet exercice on reste sur la liste pour éviter le ban immédiat

                        results.append({
                            'site': self.site_name,
                            'title': lines[0] if lines else "Titre inconnu",
                            'price': price,
                            'location': self.config.get('search', {}).get('locations')[0].get('city'), # Approx
                            'url': link,
                            'description': text_content, # Contenu complet de la carte
                            'date': "Aujourd'hui" # Difficile à extraire sans ouvrir
                        })

                    except Exception as e:
                        self.log_error("Erreur parsing annonce", e)

                browser.close()

        except Exception as global_e:
            self.log_error("Erreur critique Playwright", global_e)

        return results
