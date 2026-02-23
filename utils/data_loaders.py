"""Chargement et validation des donnees -- VOC Complaints Analyzer."""

from __future__ import annotations

import json
import os
from io import BytesIO

import pandas as pd
import streamlit as st

from config import CATEGORIES_PATH, SAMPLE_CSV_PATH

# Colonnes attendues dans le fichier de plaintes
EXPECTED_COLUMNS: list[str] = [
    "complaint_id",
    "date",
    "product_line",
    "customer",
    "complaint_text",
    "severity",
    "defect_type",
    "lot_number",
    "production_line",
]

# Colonnes minimales obligatoires
REQUIRED_COLUMNS: list[str] = ["complaint_id", "complaint_text"]


@st.cache_data
def load_sample_data() -> pd.DataFrame:
    """Charge le fichier CSV d'exemple.

    Returns
    -------
    pd.DataFrame
        DataFrame des plaintes d'exemple.
    """
    if not os.path.exists(SAMPLE_CSV_PATH):
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    df = pd.read_csv(SAMPLE_CSV_PATH, parse_dates=["date"])
    return _normalize_dataframe(df)


@st.cache_data
def load_categories() -> dict:
    """Charge la taxonomie des defauts depuis categories.json.

    Returns
    -------
    dict
        Dictionnaire des types de defauts et niveaux de severite.
    """
    if not os.path.exists(CATEGORIES_PATH):
        return {"defect_types": {}, "severity_levels": {}}
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_uploaded_file(uploaded_file: st.runtime.uploaded_file_manager.UploadedFile) -> pd.DataFrame:
    """Charge un fichier uploade (CSV ou Excel).

    Parameters
    ----------
    uploaded_file : UploadedFile
        Fichier uploade via st.file_uploader.

    Returns
    -------
    pd.DataFrame
        DataFrame normalise.

    Raises
    ------
    ValueError
        Si le format n'est pas supporte ou les colonnes requises manquent.
    """
    name = uploaded_file.name.lower()

    if name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        raise ValueError(f"Format non supporte : {name}. Utilisez CSV ou Excel.")

    # Verifier les colonnes minimales
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes requises manquantes : {', '.join(missing)}")

    return _normalize_dataframe(df)


def parse_free_text(text: str, start_id: int = 1) -> pd.DataFrame:
    """Parse du texte libre en DataFrame de plaintes.

    Parameters
    ----------
    text : str
        Texte libre, une plainte par ligne.
    start_id : int
        Numero de depart pour les IDs.

    Returns
    -------
    pd.DataFrame
        DataFrame avec les plaintes extraites.
    """
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    if not lines:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    records = []
    for i, line in enumerate(lines, start=start_id):
        records.append(
            {
                "complaint_id": f"C-{i:03d}",
                "date": pd.Timestamp.now(),
                "product_line": "",
                "customer": "",
                "complaint_text": line,
                "severity": "",
                "defect_type": "",
                "lot_number": "",
                "production_line": "",
            }
        )
    return pd.DataFrame(records)


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise un DataFrame de plaintes.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame brut.

    Returns
    -------
    pd.DataFrame
        DataFrame avec colonnes standardisees.
    """
    # Ajouter les colonnes manquantes
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # Convertir la date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Remplir les NaN avec des chaines vides pour les colonnes texte
    text_cols = [
        "complaint_id", "product_line", "customer", "complaint_text",
        "severity", "defect_type", "lot_number", "production_line",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("")

    return df[EXPECTED_COLUMNS]


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convertit un DataFrame en bytes CSV pour telechargement.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame a convertir.

    Returns
    -------
    bytes
        Contenu CSV en bytes.
    """
    return df.to_csv(index=False).encode("utf-8")


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Convertit un DataFrame en bytes Excel pour telechargement.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame a convertir.

    Returns
    -------
    bytes
        Contenu Excel en bytes.
    """
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Complaints")
    return buffer.getvalue()
