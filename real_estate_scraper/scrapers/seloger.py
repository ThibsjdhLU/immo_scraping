from typing import List, Dict, Any
from playwright.sync_api import sync_playwright
import urllib.parse
from core.scraper_base import ScraperBase
from utils.http import get_random_user_agent

class SeLogerScraper(ScraperBase):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.site_name = "SeLoger"
        # URL de base fictive car SeLoger utilise une structure complexe
        # On passe souvent par /list.htm
        self.base_url = "https://www.seloger.com/list.htm"

    def build_url(self) -> str:
        # Construction très simplifiée des paramètres GET de SeLoger
        # types: 1=Appart, 2=Maison (approx)
        # projects: 2=Vente, 1=Location
        params = {
            "projects": "2,8", # Vente
            "types": "1,2",    # Appart/Maison
            "places": f"[{self._get_zip_code()}]",
            "price": f"NaN/{self._get_max_price()}",
            "surface": f"{self._get_min_surface()}/NaN",
            "enterprise": "0",
            "qsVersion": "1.0"
        }
        return f"{self.base_url}?{urllib.parse.urlencode(params)}"

    def _get_zip_code(self):
        # Nécessite souvent un ID interne, mais le code postal passe parfois
        # Ou alors il faut interroger l'API autocomplete.
        # Pour le script, on tente le CP direct.
        locs = self.config.get('search', {}).get('locations', [])
        if locs:
            # SeLoger utilise souvent CP + insee, ici on tente juste CP
            return f"{{ci:{locs[0].get('zip_code')}}}"
        return ""

    def _get_max_price(self):
        return self.config.get('search', {}).get('price', {}).get('max', '')

    def _get_min_surface(self):
        return self.config.get('search', {}).get('surface', {}).get('min', '')

    def run(self) -> List[Dict[str, Any]]:
        self.logger.info(f"Démarrage du scraping {self.site_name}...")
        results = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=self.config.get('scraping', {}).get('headless', True)
                )
                context = browser.new_context(user_agent=get_random_user_agent())

                # Masquage antibot basique
                context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                page = context.new_page()
                url = self.build_url()
                self.logger.info(f"Navigation vers : {url}")

                try:
                    page.goto(url, timeout=60000, wait_until="domcontentloaded")
                except:
                    self.logger.error("Erreur chargement page SeLoger")
                    return []

                self.sleep_random(3, 6)

                # Cookies
                try:
                    page.get_by_text("Accepter", exact=False).first.click(timeout=5000)
                except:
                    pass

                # Attente des cartes (classe souvent changeante, on vise 'div[data-test="sl.card-container"]')
                # SeLoger est très agressif sur les bots (Captcha Datadome).
                # Si Captcha, le script échouera ou devra s'arrêter.

                if "captcha" in page.content().lower() or "datadome" in page.url:
                    self.logger.error("DETECTÉ COMME BOT (Captcha/Datadome). Arrêt.")
                    self.logger.info("Conseil : Tentez de mettre 'headless: false' dans config.yaml pour intervenir manuellement.")
                    browser.close()
                    return []

                try:
                    page.wait_for_selector('div[data-testid="gsl.uikit.card.content"]', timeout=10000)
                except:
                    self.logger.warning("Pas d'annonces détectées (sélecteurs obsolètes ou blocage).")

                cards = page.query_selector_all('div[data-testid="gsl.uikit.card.content"]')

                for card in cards:
                    try:
                        price_elem = card.query_selector('div[data-test="price"]')
                        price = price_elem.inner_text() if price_elem else "0"

                        # Le lien est souvent sur un parent ou via JS
                        # On cherche un tag <a> parent ou interne
                        link_elem = card.xpath('..').query_selector('a')
                        # Ou parfois le container lui-même est cliquable

                        url_suffix = link_elem.get_attribute('href') if link_elem else ""
                        full_url = url_suffix # Souvent absolu sur SeLoger, sinon concatener

                        # Infos
                        details = card.inner_text()

                        results.append({
                            'site': self.site_name,
                            'title': "Annonce SeLoger",
                            'price': price,
                            'location': self.config.get('search', {}).get('locations')[0].get('city'),
                            'url': full_url,
                            'description': details,
                            'date': "Aujourd'hui"
                        })

                    except Exception as e:
                        pass

                browser.close()

        except Exception as e:
            self.log_error("Erreur scraping SeLoger", e)

        return results
