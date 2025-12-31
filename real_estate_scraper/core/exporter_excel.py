import pandas as pd
import logging
from typing import List, Dict, Any
import os
from datetime import datetime
import shutil

class ExcelExporter:
    """
    Gère l'export des données vers Excel avec formatage.
    """

    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.filepath = config.get('export', {}).get('filepath', 'output/annonces.xlsx')
        self.backup_dir = config.get('export', {}).get('backup_dir', 'output/backups')

    def _backup_existing_file(self):
        """Crée une copie de sauvegarde si le fichier existe."""
        if os.path.exists(self.filepath):
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(self.filepath)
            backup_path = os.path.join(self.backup_dir, f"{filename}_{timestamp}.bak")

            try:
                shutil.copy2(self.filepath, backup_path)
                self.logger.info(f"Backup créé : {backup_path}")
            except Exception as e:
                self.logger.error(f"Echec du backup : {e}")

    def export(self, ads: List[Dict[str, Any]], stats: Dict[str, Any] = None):
        """
        Exporte les annonces vers Excel.

        Args:
            ads (list): Liste des annonces.
            stats (dict, optional): Statistiques de scraping à inclure dans une autre feuille.
        """
        if not ads:
            self.logger.warning("Aucune donnée à exporter.")
            return

        self._backup_existing_file()

        # Création du DataFrame
        df = pd.DataFrame(ads)

        # Réorganisation des colonnes si possible
        cols_order = ['date', 'site', 'price', 'surface', 'location', 'type', 'title', 'url', 'description']
        existing_cols = [c for c in cols_order if c in df.columns]
        other_cols = [c for c in df.columns if c not in cols_order]
        df = df[existing_cols + other_cols]

        try:
            # Création du dossier parent si inexistant
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

            with pd.ExcelWriter(self.filepath, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Annonces', index=False)

                # Feuille Stats
                if stats:
                    df_stats = pd.DataFrame([stats])
                    df_stats.to_excel(writer, sheet_name='Stats', index=False)

                workbook = writer.book
                worksheet = writer.sheets['Annonces']

                # Formatage
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })

                # Appliquer le format aux en-têtes
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                # Auto-ajustement basique des colonnes (largeur estimée)
                for i, col in enumerate(df.columns):
                    max_len = max(
                        df[col].astype(str).map(len).max(),
                        len(str(col))
                    )
                    # Limite la largeur pour pas avoir des colonnes géantes (ex: description)
                    final_len = min(max_len + 2, 50)
                    worksheet.set_column(i, i, final_len)

                # Figer les volets (première ligne)
                worksheet.freeze_panes(1, 0)

                # Ajouter le filtre automatique
                worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

            self.logger.info(f"Export réussi vers {self.filepath}")

        except Exception as e:
            self.logger.error(f"Erreur lors de l'export Excel : {e}")
