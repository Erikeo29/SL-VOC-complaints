"""Composant tableau de bord -- VOC Complaints Analyzer."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.translations import t
from core.trend_detector import (
    compute_complaint_trend,
    compute_defect_trend,
    detect_anomalies,
    detect_production_line_anomalies,
    compute_correlation_matrix,
)
from core.sentiment import (
    compute_sentiment_stats,
    compute_sentiment_by_product,
)

# Palette navy
COLORS = {
    "navy": "#004b87",
    "dark_navy": "#003366",
    "light_blue": "#5b9bd5",
    "orange": "#e67e22",
    "red": "#e74c3c",
    "green": "#27ae60",
    "purple": "#8e44ad",
    "teal": "#1abc9c",
    "gray": "#95a5a6",
}

SEVERITY_COLORS = {
    "critical": "#e74c3c",
    "major": "#e67e22",
    "minor": "#3498db",
    "": "#95a5a6",
}

DEFECT_COLORS = {
    "solder_defect": "#e74c3c",
    "dimensional": "#e67e22",
    "contamination": "#f39c12",
    "electrical": "#3498db",
    "mechanical": "#8e44ad",
    "biocompatibility": "#1abc9c",
    "packaging_delivery": "#95a5a6",
}


def render_dashboard_page() -> None:
    """Affiche le tableau de bord."""
    st.header(t("dash_title"))

    # Verifier les donnees
    df = st.session_state.get("classified_df", pd.DataFrame())
    if df.empty:
        # Fallback sur les donnees non classifiees
        df = st.session_state.get("complaints_df", pd.DataFrame())
    if df.empty:
        st.warning(t("dash_no_data"))
        return

    # --- Filtres ---
    _render_filters(df)

    # Appliquer les filtres
    df_filtered = _apply_filters(df)

    # --- KPIs ---
    _render_kpis(df_filtered)

    st.divider()

    # --- Tendance temporelle ---
    _render_trend_chart(df_filtered)

    # --- Detection d'anomalies ---
    _render_anomaly_alerts(df_filtered)

    st.divider()

    # --- Graphiques en colonnes ---
    col_left, col_right = st.columns(2)

    with col_left:
        _render_treemap(df_filtered)
        st.markdown("")
        _render_severity_chart(df_filtered)

    with col_right:
        _render_sunburst(df_filtered)
        st.markdown("")
        _render_product_chart(df_filtered)

    st.divider()

    # --- Correlation ---
    _render_correlation(df_filtered)

    # --- Sentiment ---
    _render_sentiment(df_filtered)


def _render_filters(df: pd.DataFrame) -> None:
    """Affiche les filtres du tableau de bord.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame complet.
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        if "date" in df.columns:
            date_min = df["date"].min()
            date_max = df["date"].max()
            if pd.notna(date_min) and pd.notna(date_max):
                date_range = st.date_input(
                    t("dash_filter_period"),
                    value=(date_min.date(), date_max.date()),
                    min_value=date_min.date(),
                    max_value=date_max.date(),
                    key="dash_date_range",
                )
                st.session_state["dash_date_filter"] = date_range

    with col2:
        products = [t("dash_filter_all")]
        if "product_line" in df.columns:
            products += sorted(df["product_line"].unique().tolist())
        st.selectbox(
            t("dash_filter_product"),
            products,
            key="dash_product_filter",
        )

    with col3:
        severities = [t("dash_filter_all"), "critical", "major", "minor"]
        st.selectbox(
            t("dash_filter_severity"),
            severities,
            key="dash_severity_filter",
        )


def _apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Applique les filtres selectionnes.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame complet.

    Returns
    -------
    pd.DataFrame
        DataFrame filtre.
    """
    df_filtered = df.copy()

    # Filtre de date
    date_range = st.session_state.get("dash_date_filter")
    if date_range and len(date_range) == 2 and "date" in df_filtered.columns:
        start, end = date_range
        mask = (df_filtered["date"].dt.date >= start) & (df_filtered["date"].dt.date <= end)
        df_filtered = df_filtered[mask]

    # Filtre produit
    product = st.session_state.get("dash_product_filter", t("dash_filter_all"))
    if product != t("dash_filter_all") and "product_line" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["product_line"] == product]

    # Filtre severite
    severity = st.session_state.get("dash_severity_filter", t("dash_filter_all"))
    if severity != t("dash_filter_all") and "severity" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["severity"] == severity]

    return df_filtered


def _render_kpis(df: pd.DataFrame) -> None:
    """Affiche les KPIs principaux.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame filtre.
    """
    col1, col2, col3, col4, col5 = st.columns(5)

    total = len(df)
    has_severity = "severity" in df.columns

    with col1:
        st.metric(t("dash_kpi_total"), total)
    with col2:
        n = (df["severity"] == "critical").sum() if has_severity else 0
        st.metric(t("dash_kpi_critical"), n)
    with col3:
        n = (df["severity"] == "major").sum() if has_severity else 0
        st.metric(t("dash_kpi_major"), n)
    with col4:
        n = (df["severity"] == "minor").sum() if has_severity else 0
        st.metric(t("dash_kpi_minor"), n)
    with col5:
        n = ((df["severity"] == "") | df["severity"].isna()).sum() if has_severity else total
        st.metric(t("dash_kpi_unclassified"), n)


def _render_trend_chart(df: pd.DataFrame) -> None:
    """Affiche le graphique de tendance temporelle.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame filtre.
    """
    st.subheader(t("dash_trend_title"))

    trend = compute_complaint_trend(df, freq="M")
    if trend.empty:
        st.info("No temporal data available.")
        return

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=trend["period"],
            y=trend["count"],
            name="Complaints",
            marker_color=COLORS["navy"],
            opacity=0.7,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=trend["period"],
            y=trend["rolling_mean"],
            name="Moving average",
            line=dict(color=COLORS["orange"], width=3),
            mode="lines+markers",
        )
    )

    # Zone d'anomalie (mean + 2*std)
    if "rolling_std" in trend.columns:
        upper_bound = trend["rolling_mean"] + 2 * trend["rolling_std"]
        fig.add_trace(
            go.Scatter(
                x=trend["period"],
                y=upper_bound,
                name="Anomaly threshold",
                line=dict(color=COLORS["red"], width=1, dash="dash"),
                mode="lines",
            )
        )

    fig.update_layout(
        xaxis_title="",
        yaxis_title="Complaints",
        template="plotly_white",
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tendance par defaut
    defect_trend = compute_defect_trend(df, freq="M")
    if not defect_trend.empty:
        fig_defect = px.line(
            defect_trend,
            x="period",
            y="count",
            color="defect_type",
            color_discrete_map=DEFECT_COLORS,
            markers=True,
            height=300,
        )
        fig_defect.update_layout(
            xaxis_title="",
            yaxis_title="Count",
            template="plotly_white",
            legend_title="",
        )
        st.plotly_chart(fig_defect, use_container_width=True)


def _render_anomaly_alerts(df: pd.DataFrame) -> None:
    """Affiche les alertes d'anomalies.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame filtre.
    """
    st.subheader(t("dash_anomaly_title"))

    # Anomalies globales
    anomalies = detect_anomalies(df, z_threshold=2.0)

    # Anomalies par ligne de production
    line_anomalies = detect_production_line_anomalies(df, z_threshold=1.5)

    all_anomalies = anomalies + line_anomalies

    if all_anomalies:
        for anomaly in all_anomalies:
            st.error(t("dash_anomaly_alert", details=anomaly.description))
    else:
        st.success(t("dash_no_anomaly"))


def _render_treemap(df: pd.DataFrame) -> None:
    """Affiche le treemap des types de defaut.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame filtre.
    """
    st.subheader(t("dash_treemap_title"))

    if "defect_type" not in df.columns:
        return

    df_valid = df[df["defect_type"] != ""].copy()
    if df_valid.empty:
        st.info("No classified data.")
        return

    # Compter par type et sous-type
    if "defect_subtype" in df_valid.columns:
        counts = (
            df_valid.groupby(["defect_type", "defect_subtype"])
            .size()
            .reset_index(name="count")
        )
        fig = px.treemap(
            counts,
            path=["defect_type", "defect_subtype"],
            values="count",
            color="defect_type",
            color_discrete_map=DEFECT_COLORS,
            height=400,
        )
    else:
        counts = df_valid["defect_type"].value_counts().reset_index()
        counts.columns = ["defect_type", "count"]
        fig = px.treemap(
            counts,
            path=["defect_type"],
            values="count",
            color="defect_type",
            color_discrete_map=DEFECT_COLORS,
            height=400,
        )

    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)


def _render_sunburst(df: pd.DataFrame) -> None:
    """Affiche le sunburst defauts par ligne de production.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame filtre.
    """
    st.subheader(t("dash_sunburst_title"))

    required_cols = {"production_line", "defect_type"}
    if not required_cols.issubset(df.columns):
        return

    df_valid = df[(df["production_line"] != "") & (df["defect_type"] != "")].copy()
    if df_valid.empty:
        st.info("No data with production line info.")
        return

    counts = (
        df_valid.groupby(["production_line", "defect_type"])
        .size()
        .reset_index(name="count")
    )

    fig = px.sunburst(
        counts,
        path=["production_line", "defect_type"],
        values="count",
        color="defect_type",
        color_discrete_map=DEFECT_COLORS,
        height=400,
    )
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)


def _render_severity_chart(df: pd.DataFrame) -> None:
    """Affiche la distribution de severite.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame filtre.
    """
    st.subheader(t("dash_severity_title"))

    if "severity" not in df.columns:
        return

    counts = df["severity"].value_counts().reset_index()
    counts.columns = ["severity", "count"]
    counts = counts[counts["severity"] != ""]

    if counts.empty:
        return

    fig = px.pie(
        counts,
        values="count",
        names="severity",
        color="severity",
        color_discrete_map=SEVERITY_COLORS,
        hole=0.4,
        height=300,
    )
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        margin=dict(t=10, l=10, r=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_product_chart(df: pd.DataFrame) -> None:
    """Affiche les plaintes par ligne de produit.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame filtre.
    """
    st.subheader(t("dash_product_title"))

    if "product_line" not in df.columns:
        return

    counts = df["product_line"].value_counts().reset_index()
    counts.columns = ["product_line", "count"]
    counts = counts[counts["product_line"] != ""]

    if counts.empty:
        return

    fig = px.bar(
        counts,
        x="product_line",
        y="count",
        color="count",
        color_continuous_scale=["#5b9bd5", "#004b87"],
        height=300,
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Count",
        template="plotly_white",
        showlegend=False,
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_correlation(df: pd.DataFrame) -> None:
    """Affiche la matrice de correlation ligne / defaut.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame filtre.
    """
    st.subheader(t("dash_correlation_title"))

    corr = compute_correlation_matrix(df)
    if corr.empty:
        st.info("No data for correlation analysis.")
        return

    # Heatmap
    fig = px.imshow(
        corr.iloc[:-1, :-1],  # Exclure les totaux
        color_continuous_scale=["#f8f9fa", "#004b87"],
        text_auto=True,
        height=300,
        aspect="auto",
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        template="plotly_white",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tableau
    st.dataframe(corr, use_container_width=True)


def _render_sentiment(df: pd.DataFrame) -> None:
    """Affiche l'analyse de sentiment.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame filtre.
    """
    st.subheader(t("dash_sentiment_title"))

    stats = compute_sentiment_stats(df)
    total = sum(stats.values())

    if total == 0:
        st.info("No sentiment data available.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Negative", stats["negative"])
    with col2:
        st.metric("Neutral", stats["neutral"])
    with col3:
        st.metric("Positive", stats["positive"])

    # Par produit
    sent_by_product = compute_sentiment_by_product(df)
    if not sent_by_product.empty:
        st.dataframe(sent_by_product, use_container_width=True)
