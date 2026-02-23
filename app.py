"""VOC Complaints Analyzer -- Streamlit Application.

AI-powered customer complaint analysis for medtech/connector industry.
"""

import os

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# --- Configuration de la page (DOIT etre en premier) ---
st.set_page_config(
    page_title="VOC Complaints Analyzer",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Authentification ---
_cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
with open(_cfg_path) as _f:
    _auth_config = yaml.load(_f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    _auth_config["credentials"],
    _auth_config["cookie"]["name"],
    _auth_config["cookie"]["key"],
    _auth_config["cookie"]["expiry_days"],
)

authenticator.login()

if not st.session_state.get("authentication_status"):
    if st.session_state.get("authentication_status") is False:
        st.error("Identifiants incorrects / Invalid credentials")
    else:
        st.info("Entrez vos identifiants / Enter your credentials")
    st.stop()

# --- Imports locaux ---
from config import ASSETS_PATH, CSS_PATH, DOC_PATH, VERSION, VERSION_DATE
from utils.translations import TRANSLATIONS, get_language, t
from components.file_upload import render_upload_page
from components.classification import render_classification_page
from components.dashboard import render_dashboard_page
from components.report import render_report_page
from components.chatbot import render_chatbot_page


# ─── CSS ─────────────────────────────────────────────────────────────────────


def load_custom_css() -> str:
    """Charge le CSS personnalise et les boutons de navigation.

    Returns
    -------
    str
        HTML avec le CSS et les boutons.
    """
    css_content = ""
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()

    nav_buttons_html = """
<a href="#top" class="nav-button back-to-top" title="Retour en haut / Back to top">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
        <path d="M12 4l-8 8h5v8h6v-8h5z"/>
    </svg>
</a>
<a href="#bottom" class="nav-button scroll-to-bottom" title="Aller en bas / Go to bottom">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
        <path d="M12 20l8-8h-5V4h-6v8H4z"/>
    </svg>
</a>
<div id="top"></div>
"""
    return f"<style>{css_content}</style>{nav_buttons_html}"


st.markdown(load_custom_css(), unsafe_allow_html=True)


# ─── Initialisation du session_state ─────────────────────────────────────────

if "lang" not in st.session_state:
    st.session_state["lang"] = "fr"

if "complaints_df" not in st.session_state:
    st.session_state["complaints_df"] = pd.DataFrame()

if "classified_df" not in st.session_state:
    st.session_state["classified_df"] = pd.DataFrame()

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []


# ─── Pages ───────────────────────────────────────────────────────────────────


def page_upload() -> None:
    """Page d'import des donnees."""
    render_upload_page()


def page_classification() -> None:
    """Page de classification IA."""
    render_classification_page()


def page_dashboard() -> None:
    """Page tableau de bord."""
    render_dashboard_page()


def page_reports() -> None:
    """Page de generation de rapports."""
    render_report_page()


def page_chatbot() -> None:
    """Page assistant IA."""
    render_chatbot_page()


def page_guide() -> None:
    """Page guide d'utilisation."""
    st.header(t("guide_title"))

    lang = get_language()
    guide_path = os.path.join(DOC_PATH, lang, "guide.md")

    if os.path.exists(guide_path):
        with open(guide_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(content)
    else:
        st.warning(t("guide_not_found"))


# ─── Navigation ──────────────────────────────────────────────────────────────


def build_navigation() -> None:
    """Construit la navigation multipage avec st.navigation."""
    pages = {
        "VOC Complaints Analyzer": [
            st.Page(page_upload, title=t("nav_upload"), icon="📂"),
            st.Page(page_classification, title=t("nav_classification"), icon="🤖"),
            st.Page(page_dashboard, title=t("nav_dashboard"), icon="📊"),
            st.Page(page_reports, title=t("nav_reports"), icon="📄"),
            st.Page(page_chatbot, title=t("nav_chatbot"), icon="💬"),
            st.Page(page_guide, title=t("nav_guide"), icon="📖"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()


# ─── Sidebar ─────────────────────────────────────────────────────────────────


def render_sidebar() -> None:
    """Affiche la sidebar avec titre, langue et statistiques."""
    with st.sidebar:
        st.title(t("sidebar_title"))
        authenticator.logout(location="sidebar")
        st.caption(t("app_subtitle"))

        st.divider()

        # Selecteur de langue
        lang_options = ["FR", "EN"]
        lang_map = {"FR": "fr", "EN": "en"}

        current_lang = get_language()
        current_idx = 0 if current_lang == "fr" else 1

        selected = st.radio(
            t("lang_label"),
            lang_options,
            index=current_idx,
            horizontal=True,
            key="lang_selector",
        )

        new_lang = lang_map.get(selected, "fr")
        if new_lang != st.session_state.get("lang"):
            st.session_state["lang"] = new_lang
            st.rerun()

        st.divider()

        # Statistiques des donnees
        df = st.session_state.get("complaints_df", pd.DataFrame())
        if not df.empty:
            st.subheader(t("sidebar_data_stats"))
            st.metric(t("sidebar_nb_complaints"), len(df))

            # Nombre classifiees
            classified_df = st.session_state.get("classified_df", pd.DataFrame())
            if not classified_df.empty:
                n_classified = (
                    classified_df["severity"].notna()
                    & (classified_df["severity"] != "")
                ).sum() if "severity" in classified_df.columns else 0
                st.metric(t("sidebar_nb_classified"), n_classified)
                st.metric(
                    t("sidebar_nb_unclassified"),
                    len(classified_df) - n_classified,
                )
        else:
            st.info(t("sidebar_no_data"))

        st.divider()

        # Version
        st.caption(
            t("version_info", version=VERSION, date=VERSION_DATE)
        )


# ─── Main ────────────────────────────────────────────────────────────────────


def main() -> None:
    """Point d'entree principal de l'application."""
    render_sidebar()
    build_navigation()


# Streamlit execute le script directement (pas d'import conditionnel)
main()
