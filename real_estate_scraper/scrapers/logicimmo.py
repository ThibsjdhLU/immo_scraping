from typing import List, Dict, Any
from playwright.sync_api import sync_playwright
from core.scraper_base import ScraperBase
from utils.http import get_random_user_agent
import urllib.parse

class LogicImmoScraper(ScraperBase):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.site_name = "LogicImmo"
        self.base_url = "https://www.logic-immo.com/recherche-immobiliere.php"

    def run(self) -> List[Dict[str, Any]]:
        self.logger.info(f"Démarrage du scraping {self.site_name} (Playwright)...")
        results = []

        # Construction URL (simplifiée pour LogicImmo)
        # Ex: https://www.logic-immo.com/vente-immobilier-paris-75001,100_1.html
        loc = self.config.get('search', {}).get('locations', [])[0]
        zip_code = loc.get('zip_code')
        city = loc.get('city').lower().replace(' ', '-')

        target_url = f"https://www.logic-immo.com/vente-immobilier-{city}-{zip_code},100_1.html"

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=self.config.get('scraping', {}).get('headless', True),
                    args=["--disable-blink-features=AutomationControlled"]
                )
                context = browser.new_context(user_agent=get_random_user_agent())
                context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                page = context.new_page()
                self.logger.info(f"Navigation vers : {target_url}")

                try:
                    page.goto(target_url, timeout=60000, wait_until="domcontentloaded")
                except Exception as e:
                    self.logger.error(f"Erreur de navigation LogicImmo : {e}")
                    return []

                self.sleep_random(3, 5)

                # Check Anti-Bot
                if "captcha" in page.content().lower() or "datadome" in page.url or "403 Forbidden" in page.title():
                    self.logger.error("DETECTÉ COMME BOT (Captcha/403) sur LogicImmo.")
                    self.logger.info("Conseil : Tentez de mettre 'headless: false' dans config.yaml pour intervenir manuellement.")
                    browser.close()
                    return []

                # Gestion Cookies
                try:
                    page.get_by_text("Accepter", exact=False).first.click(timeout=3000)
                except:
                    pass

                # Sélecteurs
                # LogicImmo a une structure changeante, on vise les classes génériques
                try:
                    # Attente d'un élément d'annonce
                    page.wait_for_selector('div[class*="PropertyCard"]', timeout=15000)
                except:
                     if "captcha" in page.content().lower():
                         self.logger.error("DETECTÉ COMME BOT (Captcha) pendant le chargement.")
                         self.logger.info("Conseil : Tentez de mettre 'headless: false' dans config.yaml pour intervenir manuellement.")
                         browser.close()
                         return []
                     self.logger.warning("Pas d'annonces trouvées (structure ?)")

                cards = page.query_selector_all('div[class*="PropertyCard"]') # Selecteur générique React
                if not cards:
                    cards = page.query_selector_all('.offer-list-item') # Vieux selecteur fallback

                self.logger.info(f"Annonces trouvées sur la page : {len(cards)}")

                for card in cards:
                    try:
                        # Extraction
                        price_elem = card.query_selector('[class*="price"]')
                        price = price_elem.inner_text() if price_elem else "0"

                        link_elem = card.query_selector('a')
                        link = link_elem.get_attribute('href') if link_elem else ""

                        # LogicImmo met souvent tout dans le lien

                        results.append({
                            'site': self.site_name,
                            'title': "Annonce LogicImmo",
                            'price': price,
                            'location': city,
                            'url': link,
                            'description': card.inner_text(),
                            'date': "Aujourd'hui"
                        })
                    except:
                        pass

                browser.close()

        except Exception as e:
            self.log_error("Erreur critique LogicImmo", e)

        return results
