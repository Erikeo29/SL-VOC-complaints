"""Composant de generation de rapports -- VOC Complaints Analyzer."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.translations import t, get_language
from utils.data_loaders import dataframe_to_csv_bytes, dataframe_to_excel_bytes
from core.report_generator import generate_executive_summary, generate_mdr_report
from core.llm_classifier import is_api_available


def render_report_page() -> None:
    """Affiche la page de generation de rapports."""
    st.header(t("report_title"))

    # Verifier les donnees
    df = st.session_state.get("classified_df", pd.DataFrame())
    if df.empty:
        df = st.session_state.get("complaints_df", pd.DataFrame())
    if df.empty:
        st.warning(t("report_no_data"))
        return

    lang = get_language()

    # Metriques de la periode
    if "date" in df.columns:
        date_min = df["date"].min()
        date_max = df["date"].max()
        if pd.notna(date_min) and pd.notna(date_max):
            st.info(
                t("report_period", start=str(date_min.date()), end=str(date_max.date()))
                + " | "
                + t("report_total", n=str(len(df)))
            )

    tab_summary, tab_mdr, tab_export = st.tabs(
        [t("report_summary_title"), t("report_mdr_title"), "Export"]
    )

    # --- Onglet Resume executif ---
    with tab_summary:
        _render_executive_summary(df, lang)

    # --- Onglet Rapport MDR ---
    with tab_mdr:
        _render_mdr_report(df, lang)

    # --- Onglet Export ---
    with tab_export:
        _render_export(df)


def _render_executive_summary(df: pd.DataFrame, lang: str) -> None:
    """Affiche le resume executif.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame des plaintes.
    lang : str
        Langue du rapport.
    """
    if st.button(t("report_gen_btn"), type="primary", key="gen_summary"):
        with st.spinner("..."):
            summary = generate_executive_summary(df, lang=lang)
            st.session_state["exec_summary"] = summary

    summary = st.session_state.get("exec_summary", "")
    if summary:
        st.markdown(summary)
        st.divider()
        st.download_button(
            "Download Summary (Markdown)",
            data=summary.encode("utf-8"),
            file_name="executive_summary.md",
            mime="text/markdown",
        )


def _render_mdr_report(df: pd.DataFrame, lang: str) -> None:
    """Affiche le rapport MDR.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame des plaintes.
    lang : str
        Langue du rapport.
    """
    if not is_api_available():
        st.info(t("report_mdr_no_api"))

    if st.button(t("report_gen_mdr_btn"), type="primary", key="gen_mdr"):
        with st.spinner("..."):
            mdr = generate_mdr_report(df, lang=lang)
            st.session_state["mdr_report"] = mdr

    mdr = st.session_state.get("mdr_report", "")
    if mdr:
        st.markdown(mdr)
        st.divider()
        st.download_button(
            "Download MDR Report (Markdown)",
            data=mdr.encode("utf-8"),
            file_name="mdr_report.md",
            mime="text/markdown",
        )


def _render_export(df: pd.DataFrame) -> None:
    """Affiche les options d'export des donnees.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame des plaintes.
    """
    st.subheader("Export")

    col1, col2 = st.columns(2)

    with col1:
        csv_data = dataframe_to_csv_bytes(df)
        st.download_button(
            t("report_download_csv"),
            data=csv_data,
            file_name="complaints_classified.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        xlsx_data = dataframe_to_excel_bytes(df)
        st.download_button(
            t("report_download_xlsx"),
            data=xlsx_data,
            file_name="complaints_classified.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.divider()

    # Apercu des donnees exportees
    st.subheader(t("upload_preview"))
    st.dataframe(df, use_container_width=True, height=400)
