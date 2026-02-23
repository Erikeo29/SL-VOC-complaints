"""Composant d'upload de fichiers et apercu des donnees -- VOC Complaints Analyzer."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.translations import t
from utils.data_loaders import (
    load_sample_data,
    load_uploaded_file,
    parse_free_text,
    EXPECTED_COLUMNS,
)


def render_upload_page() -> None:
    """Affiche la page d'import des donnees."""
    st.header(t("upload_title"))

    # --- Section : charger un fichier ---
    st.subheader(t("upload_file_label"))

    uploaded_file = st.file_uploader(
        t("upload_file_label"),
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        try:
            df = load_uploaded_file(uploaded_file)
            st.session_state["complaints_df"] = df
            st.success(t("upload_success", n=str(len(df))))
        except ValueError as e:
            st.error(t("upload_error", e=str(e)))
        except Exception as e:
            st.error(t("upload_error", e=str(e)))

    # --- Section : coller du texte libre ---
    st.subheader(t("upload_paste_label"))

    text_input = st.text_area(
        t("upload_paste_help"),
        height=150,
        placeholder="Solder defects found on batch LOT-2026-042...\nConnector pins bent on arrival...",
    )

    col_paste, col_sample, col_clear = st.columns([1, 1, 1])

    with col_paste:
        if st.button(t("upload_paste_btn"), type="primary", use_container_width=True):
            if text_input.strip():
                # Determiner l'ID de depart
                existing = st.session_state.get("complaints_df", pd.DataFrame())
                start_id = len(existing) + 1 if not existing.empty else 1

                new_df = parse_free_text(text_input, start_id=start_id)

                if not existing.empty:
                    combined = pd.concat([existing, new_df], ignore_index=True)
                else:
                    combined = new_df

                st.session_state["complaints_df"] = combined
                st.success(t("upload_paste_success", n=str(len(new_df))))
                st.rerun()

    with col_sample:
        if st.button(
            t("upload_sample_btn"),
            help=t("upload_sample_help"),
            use_container_width=True,
        ):
            sample_df = load_sample_data()
            if not sample_df.empty:
                st.session_state["complaints_df"] = sample_df
                st.success(t("upload_success", n=str(len(sample_df))))
                st.rerun()

    with col_clear:
        if st.button(t("upload_clear_btn"), use_container_width=True):
            st.session_state["complaints_df"] = pd.DataFrame(columns=EXPECTED_COLUMNS)
            # Nettoyer les resultats de classification
            if "classified_df" in st.session_state:
                del st.session_state["classified_df"]
            st.info(t("upload_cleared"))
            st.rerun()

    # --- Apercu des donnees ---
    df = st.session_state.get("complaints_df", pd.DataFrame())
    if not df.empty:
        st.divider()
        st.subheader(t("upload_preview"))

        # Metriques rapides
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t("sidebar_nb_complaints"), len(df))
        with col2:
            products = df["product_line"].nunique() if "product_line" in df.columns else 0
            st.metric("Produits" if t("lang_label") == "Langue" else "Products", products)
        with col3:
            customers = df["customer"].nunique() if "customer" in df.columns else 0
            st.metric("Clients" if t("lang_label") == "Langue" else "Customers", customers)
        with col4:
            has_severity = (
                df["severity"].notna() & (df["severity"] != "")
            ).sum() if "severity" in df.columns else 0
            st.metric(t("sidebar_nb_classified"), has_severity)

        # Tableau de donnees
        st.dataframe(
            df,
            use_container_width=True,
            height=400,
            column_config={
                "complaint_id": st.column_config.TextColumn("ID", width="small"),
                "date": st.column_config.DateColumn("Date", width="small"),
                "product_line": st.column_config.TextColumn("Product", width="medium"),
                "customer": st.column_config.TextColumn("Customer", width="small"),
                "complaint_text": st.column_config.TextColumn("Complaint", width="large"),
                "severity": st.column_config.TextColumn("Severity", width="small"),
                "defect_type": st.column_config.TextColumn("Defect", width="medium"),
                "lot_number": st.column_config.TextColumn("Lot", width="small"),
                "production_line": st.column_config.TextColumn("Line", width="small"),
            },
        )
