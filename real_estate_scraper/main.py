import sys
import yaml
import logging
import os
from pathlib import Path
from typing import List

# Ajout du dossier courant au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.logger import setup_logger
from core.normalizer import Normalizer
from core.filters import FilterEngine
from core.deduplicator import Deduplicator
from core.exporter_excel import ExcelExporter

from scrapers.leboncoin import LeBonCoinScraper
from scrapers.seloger import SeLogerScraper
from scrapers.logicimmo import LogicImmoScraper

def load_config(path: str = "config.yaml") -> dict:
    if not os.path.exists(path):
        print(f"Erreur: Fichier de configuration {path} introuvable.")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    # 1. Chargement Config
    config = load_config("real_estate_scraper/config.yaml") if os.path.exists("real_estate_scraper/config.yaml") else load_config("config.yaml")

    # 2. Setup Logger
    logger = setup_logger(log_file="real_estate_scraper/scraper.log")
    logger.info("=== Démarrage du Real Estate Scraper ===")

    # 3. Initialisation des composants
    normalizer = Normalizer()
    filter_engine = FilterEngine(config, logger)
    deduplicator = Deduplicator()
    exporter = ExcelExporter(config, logger)

    scrapers = []
    sites_cfg = config.get('scraping', {}).get('sites', {})

    if sites_cfg.get('leboncoin'):
        scrapers.append(LeBonCoinScraper(config, logger))
    if sites_cfg.get('seloger'):
        scrapers.append(SeLogerScraper(config, logger))
    if sites_cfg.get('logicimmo'):
        scrapers.append(LogicImmoScraper(config, logger))

    all_ads = []

    # 4. Exécution du Scraping
    for scraper in scrapers:
        try:
            site_ads = scraper.run()
            logger.info(f"Récupéré {len(site_ads)} annonces sur {scraper.site_name}")
            all_ads.extend(site_ads)
        except Exception as e:
            logger.error(f"Erreur critique sur {scraper.site_name}: {e}")

    if not all_ads:
        logger.warning("Aucune annonce récupérée sur l'ensemble des sites.")
        # On continue quand même pour générer un fichier vide ou vérifier le backup

    # 5. Traitement des données
    logger.info("Début du traitement des données...")

    # Normalisation
    normalized_ads = normalizer.normalize_list(all_ads)

    # Filtrage
    filtered_ads = filter_engine.apply_filters(normalized_ads)

    # Déduplication
    unique_ads = deduplicator.deduplicate(filtered_ads)

    logger.info(f"Total final après traitements : {len(unique_ads)} annonces (sur {len(all_ads)} brutes).")

    # 6. Export
    stats = {
        'date_execution': logging.Formatter('%(asctime)s').format(logging.LogRecord('',0,'',0,'','',None)),
        'total_scraped': len(all_ads),
        'total_filtered': len(filtered_ads),
        'total_final': len(unique_ads),
        'rejected_count': len(filter_engine.rejected_log)
    }

    exporter.export(unique_ads, stats)
    logger.info("=== Fin du programme ===")

if __name__ == "__main__":
    main()
