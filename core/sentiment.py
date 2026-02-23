"""Analyse de sentiment -- VOC Complaints Analyzer.

Utilise le LLM pour l'analyse de sentiment (pas de modele separe).
Fournit aussi des statistiques agregees de sentiment.
"""

from __future__ import annotations

import pandas as pd


def compute_sentiment_stats(df: pd.DataFrame) -> dict[str, int]:
    """Calcule les statistiques de sentiment sur le DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame avec une colonne 'sentiment'.

    Returns
    -------
    dict[str, int]
        Comptage par categorie de sentiment.
    """
    if "sentiment" not in df.columns:
        return {"negative": 0, "neutral": 0, "positive": 0}

    counts = df["sentiment"].value_counts().to_dict()
    return {
        "negative": counts.get("negative", 0),
        "neutral": counts.get("neutral", 0),
        "positive": counts.get("positive", 0),
    }


def compute_sentiment_by_product(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la distribution de sentiment par ligne de produit.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame avec colonnes 'product_line' et 'sentiment'.

    Returns
    -------
    pd.DataFrame
        Tableau croise sentiment x produit.
    """
    if "sentiment" not in df.columns or "product_line" not in df.columns:
        return pd.DataFrame()

    return pd.crosstab(
        df["product_line"],
        df["sentiment"],
        margins=True,
        margins_name="Total",
    )


def compute_sentiment_over_time(
    df: pd.DataFrame,
    freq: str = "M",
) -> pd.DataFrame:
    """Calcule l'evolution du sentiment dans le temps.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame avec colonnes 'date' et 'sentiment'.
    freq : str
        Frequence de regroupement ('M' pour mensuel, 'W' pour hebdomadaire).

    Returns
    -------
    pd.DataFrame
        Comptages de sentiment par periode.
    """
    if "sentiment" not in df.columns or "date" not in df.columns:
        return pd.DataFrame()

    df_valid = df.dropna(subset=["date"]).copy()
    if df_valid.empty:
        return pd.DataFrame()

    df_valid["period"] = df_valid["date"].dt.to_period(freq).dt.to_timestamp()

    result = (
        df_valid.groupby(["period", "sentiment"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    return result
