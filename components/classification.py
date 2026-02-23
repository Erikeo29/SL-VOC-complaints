"""Composant de classification IA des plaintes -- VOC Complaints Analyzer."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.translations import t
from core.llm_classifier import (
    classify_batch,
    get_demo_classified_data,
    is_api_available,
)


def render_classification_page() -> None:
    """Affiche la page de classification IA."""
    st.header(t("classif_title"))
    st.markdown(t("classif_description"))

    # Verifier que des donnees sont chargees
    df = st.session_state.get("complaints_df", pd.DataFrame())
    if df.empty:
        st.warning(t("classif_no_data"))
        return

    api_available = is_api_available()

    if not api_available:
        st.info(t("classif_no_api"))

    st.divider()

    # --- Options de classification ---
    col_opts1, col_opts2 = st.columns(2)
    with col_opts1:
        batch_size = st.number_input(
            t("classif_batch_label"),
            min_value=1,
            max_value=50,
            value=5,
            step=1,
        )
    with col_opts2:
        st.markdown("")
        st.markdown("")
        classify_all = st.checkbox(t("classif_classify_all"), value=True)

    # --- Bouton de classification ---
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        run_classification = st.button(
            t("classif_run_btn"),
            type="primary",
            use_container_width=True,
        )

    with col_btn2:
        if not api_available:
            load_demo = st.button(
                t("classif_demo_label"),
                use_container_width=True,
            )
        else:
            load_demo = False

    # --- Lancer la classification ---
    if run_classification:
        _run_classification(df, api_available, classify_all, batch_size)

    # --- Charger les donnees demo ---
    if load_demo:
        demo_df = get_demo_classified_data(df)
        st.session_state["classified_df"] = demo_df
        st.session_state["complaints_df"] = demo_df
        st.success(t("classif_done", n=str(len(demo_df))))
        st.rerun()

    # --- Afficher les resultats ---
    _display_results()


@st.fragment
def _run_classification(
    df: pd.DataFrame,
    api_available: bool,
    classify_all: bool,
    batch_size: int,
) -> None:
    """Execute la classification (fragment pour mise a jour partielle).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame des plaintes.
    api_available : bool
        Si l'API Groq est disponible.
    classify_all : bool
        Classifier toutes les plaintes.
    batch_size : int
        Taille du lot.
    """
    if not api_available:
        # Utiliser les donnees demo
        demo_df = get_demo_classified_data(df)
        st.session_state["classified_df"] = demo_df
        st.session_state["complaints_df"] = demo_df
        st.info(t("classif_demo_info"))
        st.success(t("classif_done", n=str(len(demo_df))))
        return

    # Classification via API
    progress_bar = st.progress(0, text=t("classif_running"))

    def progress_callback(i: int, n: int, cid: str) -> None:
        progress_bar.progress(i / n, text=t("classif_progress", i=str(i), n=str(n), cid=cid))

    try:
        classified_df = classify_batch(df, progress_callback=progress_callback)
        st.session_state["classified_df"] = classified_df
        st.session_state["complaints_df"] = classified_df
        progress_bar.progress(1.0, text=t("classif_done", n=str(len(classified_df))))
    except Exception as e:
        st.error(t("classif_error", cid="batch", e=str(e)))


def _display_results() -> None:
    """Affiche les resultats de classification."""
    classified_df = st.session_state.get("classified_df", pd.DataFrame())
    if classified_df.empty:
        return

    st.divider()
    st.subheader(t("classif_results"))

    # Colonnes a afficher
    display_cols = [
        "complaint_id",
        "severity",
        "defect_type",
        "defect_subtype",
        "root_cause_hypothesis",
        "sentiment",
        "ai_summary",
    ]
    available_cols = [c for c in display_cols if c in classified_df.columns]

    if not available_cols:
        return

    # Metriques de classification
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        n_critical = (classified_df["severity"] == "critical").sum() if "severity" in classified_df.columns else 0
        st.metric(t("dash_kpi_critical"), n_critical)
    with col2:
        n_major = (classified_df["severity"] == "major").sum() if "severity" in classified_df.columns else 0
        st.metric(t("dash_kpi_major"), n_major)
    with col3:
        n_minor = (classified_df["severity"] == "minor").sum() if "severity" in classified_df.columns else 0
        st.metric(t("dash_kpi_minor"), n_minor)
    with col4:
        n_errors = (
            classified_df["classification_error"].notna()
            & (classified_df["classification_error"] != "")
        ).sum() if "classification_error" in classified_df.columns else 0
        st.metric("Errors", n_errors)

    # Tableau des resultats
    st.dataframe(
        classified_df[available_cols],
        use_container_width=True,
        height=500,
        column_config={
            "complaint_id": st.column_config.TextColumn(t("classif_col_id"), width="small"),
            "severity": st.column_config.TextColumn(t("classif_col_severity"), width="small"),
            "defect_type": st.column_config.TextColumn(t("classif_col_defect"), width="medium"),
            "defect_subtype": st.column_config.TextColumn(t("classif_col_subtype"), width="medium"),
            "root_cause_hypothesis": st.column_config.TextColumn(t("classif_col_root_cause"), width="large"),
            "sentiment": st.column_config.TextColumn(t("classif_col_sentiment"), width="small"),
            "ai_summary": st.column_config.TextColumn(t("classif_col_summary"), width="large"),
        },
    )

    # Detail par plainte (expandable)
    with st.expander("Detail des classifications", expanded=False):
        for _, row in classified_df.iterrows():
            severity = row.get("severity", "")
            badge_class = f"severity-{severity}" if severity in ("critical", "major", "minor") else ""

            st.markdown(
                f"""<div class="complaint-card">
<strong>{row.get('complaint_id', '')}</strong>
<span class="{badge_class}">{severity.upper() if severity else 'N/A'}</span><br>
<em>{row.get('ai_summary', row.get('complaint_text', '')[:100])}</em><br>
<small>Defect: {row.get('defect_type', 'N/A')} / {row.get('defect_subtype', 'N/A')} |
Root cause: {row.get('root_cause_hypothesis', 'N/A')}</small>
</div>""",
                unsafe_allow_html=True,
            )
