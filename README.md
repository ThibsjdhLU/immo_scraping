# Real Estate Scraper

Ce projet est un outil d'extraction de données immobilières (Web Scraping) pour les sites **LeBonCoin**, **SeLoger**, et **Logic-Immo**. Il est conçu pour être modulaire, configurable et robuste.

## Fonctionnalités

*   **Multi-sites** : Supporte LeBonCoin, SeLoger et Logic-Immo.
*   **Configurable** : Tous les critères (ville, prix, surface, type) sont dans `config.yaml`.
*   **Export Excel** : Génère un fichier `.xlsx` formaté avec gestion des backups.
*   **Anti-Doublons** : Détection intelligente des annonces déjà scrapées.
*   **Robustesse** : Gestion des erreurs, logs détaillés et détection des blocages anti-bot.

## Prérequis

*   Python 3.11+
*   Navigateur Chromium (installé via Playwright)

## Installation

1.  **Installer les dépendances Python :**
    ```bash
    pip install -r real_estate_scraper/requirements.txt
    ```

2.  **Installer les navigateurs Playwright :**
    ```bash
    playwright install chromium
    ```

## Configuration

Modifiez le fichier `real_estate_scraper/config.yaml` selon vos besoins :

```yaml
scraping:
  sites:
    leboncoin: true
    seloger: true
    logicimmo: true
  headless: true  # Mettre à 'false' pour voir le navigateur (utile si bloqué)

search:
  locations:
    - city: "Paris"
      zip_code: "75001"
  price:
    min: 100000
    max: 500000
  # ...
```

## Utilisation

Lancer le script principal :

```bash
python real_estate_scraper/main.py
```

Les résultats seront enregistrés dans le dossier `output/`.

## Note sur les protections Anti-Bot (Captchas)

Ces sites immobiliers sont protégés par des systèmes avancés (DataDome, PerimeterX, etc.).

*   **Symptôme** : Le log affiche `ERROR - DETECTÉ COMME BOT (DataDome/Captcha)`.
*   **Solution locale** :
    1.  Ouvrez `real_estate_scraper/config.yaml`.
    2.  Changez `headless: true` en `headless: false`.
    3.  Relancez le script. Une fenêtre de navigateur s'ouvrira.
    4.  Si un captcha apparaît, résolvez-le manuellement. Le script continuera une fois la page chargée.

*Note : Ce projet respecte les interdictions de contournement automatisé des sécurités. Il ne contient pas de solveur de captcha.*
