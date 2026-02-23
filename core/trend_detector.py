"""Detection de tendances et anomalies -- VOC Complaints Analyzer.

Methodes statistiques simples : moyenne mobile, z-score pour anomalies.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class AnomalyResult:
    """Resultat de detection d'anomalie."""

    is_anomaly: bool
    description: str
    period: str
    z_score: float
    count: int
    mean: float
    std: float


def compute_complaint_trend(
    df: pd.DataFrame,
    freq: str = "W",
) -> pd.DataFrame:
    """Calcule la tendance temporelle des plaintes.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame avec colonne 'date'.
    freq : str
        Frequence de regroupement ('W' hebdomadaire, 'M' mensuel).

    Returns
    -------
    pd.DataFrame
        Comptages par periode avec moyenne mobile.
    """
    if "date" not in df.columns:
        return pd.DataFrame()

    df_valid = df.dropna(subset=["date"]).copy()
    if df_valid.empty:
        return pd.DataFrame()

    df_valid["period"] = df_valid["date"].dt.to_period(freq).dt.to_timestamp()

    counts = (
        df_valid.groupby("period")
        .size()
        .reset_index(name="count")
        .sort_values("period")
    )

    # Moyenne mobile sur 4 periodes
    counts["rolling_mean"] = counts["count"].rolling(window=4, min_periods=1).mean()
    counts["rolling_std"] = counts["count"].rolling(window=4, min_periods=2).std().fillna(0)

    return counts


def compute_defect_trend(
    df: pd.DataFrame,
    freq: str = "M",
) -> pd.DataFrame:
    """Calcule la tendance par type de defaut dans le temps.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame avec colonnes 'date' et 'defect_type'.
    freq : str
        Frequence de regroupement.

    Returns
    -------
    pd.DataFrame
        Comptages par periode et type de defaut.
    """
    if "date" not in df.columns or "defect_type" not in df.columns:
        return pd.DataFrame()

    df_valid = df.dropna(subset=["date"]).copy()
    df_valid = df_valid[df_valid["defect_type"] != ""]
    if df_valid.empty:
        return pd.DataFrame()

    df_valid["period"] = df_valid["date"].dt.to_period(freq).dt.to_timestamp()

    return (
        df_valid.groupby(["period", "defect_type"])
        .size()
        .reset_index(name="count")
        .sort_values("period")
    )


def detect_anomalies(
    df: pd.DataFrame,
    z_threshold: float = 2.0,
    freq: str = "M",
) -> list[AnomalyResult]:
    """Detecte les anomalies dans les tendances de plaintes.

    Utilise le z-score sur les comptages mensuels pour identifier
    les periodes avec un nombre anormalement eleve de plaintes.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame avec colonne 'date'.
    z_threshold : float
        Seuil de z-score pour considerer une anomalie.
    freq : str
        Frequence de regroupement.

    Returns
    -------
    list[AnomalyResult]
        Liste des anomalies detectees.
    """
    if "date" not in df.columns:
        return []

    df_valid = df.dropna(subset=["date"]).copy()
    if df_valid.empty or len(df_valid) < 3:
        return []

    df_valid["period"] = df_valid["date"].dt.to_period(freq).dt.to_timestamp()
    counts = df_valid.groupby("period").size()

    if len(counts) < 3:
        return []

    mean_val = counts.mean()
    std_val = counts.std()

    if std_val == 0:
        return []

    anomalies = []
    for period, count in counts.items():
        z = (count - mean_val) / std_val
        if z > z_threshold:
            anomalies.append(
                AnomalyResult(
                    is_anomaly=True,
                    description=f"{count} complaints in {period.strftime('%b %Y')} (z={z:.1f})",
                    period=period.strftime("%Y-%m"),
                    z_score=round(z, 2),
                    count=int(count),
                    mean=round(mean_val, 1),
                    std=round(std_val, 1),
                )
            )

    return anomalies


def detect_production_line_anomalies(
    df: pd.DataFrame,
    z_threshold: float = 2.0,
    freq: str = "M",
) -> list[AnomalyResult]:
    """Detecte les anomalies par ligne de production.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame avec colonnes 'date', 'production_line', 'defect_type'.
    z_threshold : float
        Seuil de z-score.
    freq : str
        Frequence de regroupement.

    Returns
    -------
    list[AnomalyResult]
        Anomalies detectees par ligne de production.
    """
    required = {"date", "production_line", "defect_type"}
    if not required.issubset(df.columns):
        return []

    df_valid = df.dropna(subset=["date"]).copy()
    df_valid = df_valid[
        (df_valid["production_line"] != "") & (df_valid["defect_type"] != "")
    ]
    if df_valid.empty:
        return []

    df_valid["period"] = df_valid["date"].dt.to_period(freq).dt.to_timestamp()

    anomalies = []
    for line in df_valid["production_line"].unique():
        line_data = df_valid[df_valid["production_line"] == line]
        counts = line_data.groupby("period").size()

        if len(counts) < 3:
            continue

        mean_val = counts.mean()
        std_val = counts.std()
        if std_val == 0:
            continue

        for period, count in counts.items():
            z = (count - mean_val) / std_val
            if z > z_threshold:
                # Identifier le defaut dominant sur cette periode
                period_data = line_data[line_data["period"] == period]
                top_defect = period_data["defect_type"].mode()
                top_defect_str = top_defect.iloc[0] if len(top_defect) > 0 else "N/A"

                anomalies.append(
                    AnomalyResult(
                        is_anomaly=True,
                        description=(
                            f"{line}: {count} complaints in {period.strftime('%b %Y')} "
                            f"(z={z:.1f}), dominant defect: {top_defect_str}"
                        ),
                        period=period.strftime("%Y-%m"),
                        z_score=round(z, 2),
                        count=int(count),
                        mean=round(mean_val, 1),
                        std=round(std_val, 1),
                    )
                )

    return anomalies


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la matrice de correlation ligne de production / type de defaut.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame avec colonnes 'production_line' et 'defect_type'.

    Returns
    -------
    pd.DataFrame
        Tableau croise production_line x defect_type.
    """
    if "production_line" not in df.columns or "defect_type" not in df.columns:
        return pd.DataFrame()

    df_valid = df[
        (df["production_line"] != "") & (df["defect_type"] != "")
    ]
    if df_valid.empty:
        return pd.DataFrame()

    return pd.crosstab(
        df_valid["production_line"],
        df_valid["defect_type"],
        margins=True,
        margins_name="Total",
    )
