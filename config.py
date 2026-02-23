"""Configuration globale de l'application -- VOC Complaints Analyzer."""

import os

import yaml

# --- Chemins ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_PATH = os.path.join(ROOT_DIR, "docs")
DATA_PATH = os.path.join(ROOT_DIR, "data")
ASSETS_PATH = os.path.join(ROOT_DIR, "assets")
CSS_PATH = os.path.join(ASSETS_PATH, "style.css")
CONFIG_YAML_PATH = os.path.join(ROOT_DIR, "config.yaml")
CATEGORIES_PATH = os.path.join(DATA_PATH, "categories.json")
SAMPLE_CSV_PATH = os.path.join(DATA_PATH, "sample_complaints.csv")

# --- Version ---
VERSION = "1.0.0"
VERSION_DATE = "Feb 2026"


def load_app_config() -> dict:
    """Charge la configuration YAML de l'application.

    Returns
    -------
    dict
        Configuration de l'application.
    """
    if os.path.exists(CONFIG_YAML_PATH):
        with open(CONFIG_YAML_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}
