"""Composant chatbot IA -- VOC Complaints Analyzer."""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from utils.translations import t, get_language


SYSTEM_PROMPT_FR = """Tu es un assistant expert en qualite et analyse de plaintes clients pour un fabricant de dispositifs medicaux et connecteurs (medtech).

Tu connais parfaitement :
1. Les types de defauts : soudure (voids, cold solder, bridging), dimensionnel, contamination, electrique, mecanique, biocompatibilite, emballage/livraison
2. Les niveaux de severite : critique (risque securite/reglementaire), majeur (impact fonctionnel), mineur (cosmetique)
3. Les normes applicables : ISO 13485, ISO 10993, FDA 21 CFR 820, MDR
4. L'analyse de tendances et la detection d'anomalies dans les plaintes
5. Les methodologies CAPA (Corrective and Preventive Actions)

{data_context}

Reponds de maniere concise, structuree et actionnable.
Utilise des tableaux markdown quand c'est pertinent.
Si tu ne connais pas la reponse, dis-le honnetement.
Reponds en francais.
"""

SYSTEM_PROMPT_EN = """You are an expert assistant in quality management and customer complaint analysis for a medical device and connector manufacturer (medtech).

You have deep knowledge of:
1. Defect types: solder (voids, cold solder, bridging), dimensional, contamination, electrical, mechanical, biocompatibility, packaging/delivery
2. Severity levels: critical (safety/regulatory risk), major (functional impact), minor (cosmetic)
3. Applicable standards: ISO 13485, ISO 10993, FDA 21 CFR 820, MDR
4. Trend analysis and anomaly detection in complaint data
5. CAPA (Corrective and Preventive Actions) methodology

{data_context}

Respond concisely, with structured and actionable insights.
Use markdown tables when relevant.
If you don't know the answer, say so honestly.
Respond in English.
"""


def _get_api_key() -> str | None:
    """Recupere la cle API Groq.

    Returns
    -------
    str or None
        Cle API ou None.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GROQ_API_KEY", None)
        except Exception:
            pass
    return api_key


def _get_data_context() -> str:
    """Construit le contexte des donnees pour le chatbot.

    Returns
    -------
    str
        Description textuelle des donnees chargees.
    """
    df = st.session_state.get("classified_df", pd.DataFrame())
    if df.empty:
        df = st.session_state.get("complaints_df", pd.DataFrame())
    if df.empty:
        return "No complaint data currently loaded."

    n = len(df)

    # Produits
    products = (
        ", ".join(df["product_line"].unique().tolist())
        if "product_line" in df.columns
        else "N/A"
    )

    # Periode
    if "date" in df.columns:
        date_min = df["date"].min()
        date_max = df["date"].max()
        period = (
            f"{date_min.strftime('%Y-%m-%d')} to {date_max.strftime('%Y-%m-%d')}"
            if pd.notna(date_min)
            else "N/A"
        )
    else:
        period = "N/A"

    # Severite
    sev_info = ""
    if "severity" in df.columns:
        sev_counts = df["severity"].value_counts().to_dict()
        sev_parts = [f"{k}: {v}" for k, v in sev_counts.items() if k]
        sev_info = f"Severity distribution: {', '.join(sev_parts)}"

    # Defauts
    defect_info = ""
    if "defect_type" in df.columns:
        defect_counts = df["defect_type"].value_counts().head(5).to_dict()
        defect_parts = [f"{k}: {v}" for k, v in defect_counts.items() if k]
        defect_info = f"Top defect types: {', '.join(defect_parts)}"

    # Lignes de production
    line_info = ""
    if "production_line" in df.columns:
        line_counts = df["production_line"].value_counts().to_dict()
        line_parts = [f"{k}: {v}" for k, v in line_counts.items() if k]
        line_info = f"Production lines: {', '.join(line_parts)}"

    context = f"""Current complaint data context:
- Total complaints: {n}
- Products: {products}
- Period: {period}
- {sev_info}
- {defect_info}
- {line_info}"""

    # Ajouter les plaintes critiques
    if "severity" in df.columns:
        critical = df[df["severity"] == "critical"]
        if not critical.empty:
            context += f"\n- Critical complaints ({len(critical)}):"
            for _, row in critical.iterrows():
                text = row.get("ai_summary", row.get("complaint_text", ""))[:100]
                context += f"\n  - {row.get('complaint_id', 'N/A')}: {text}"

    return context


def _stream_groq_response(user_message: str):
    """Genere la reponse Groq en streaming.

    Parameters
    ----------
    user_message : str
        Message de l'utilisateur.

    Yields
    ------
    str
        Fragments de la reponse.
    """
    api_key = _get_api_key()
    if not api_key:
        yield t("chat_api_missing")
        return

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
    except ImportError:
        yield "Groq library not installed. Run: pip install groq"
        return

    st.session_state.chat_messages.append({"role": "user", "content": user_message})

    # System prompt avec contexte des donnees
    lang = get_language()
    data_context = _get_data_context()
    system_prompt = (
        SYSTEM_PROMPT_FR.format(data_context=data_context)
        if lang == "fr"
        else SYSTEM_PROMPT_EN.format(data_context=data_context)
    )

    try:
        from config import load_app_config
        config = load_app_config()
        llm_config = config.get("llm", {})

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(st.session_state.chat_messages)

        stream = client.chat.completions.create(
            model=llm_config.get("model", "llama-3.3-70b-versatile"),
            messages=messages,
            max_tokens=llm_config.get("max_tokens", 1024),
            stream=True,
        )

        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                yield text

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": full_response}
        )

    except Exception as e:
        yield f"{t('chat_error')} ({str(e)[:80]}...)"


def render_chatbot_page() -> None:
    """Affiche la page du chatbot."""
    st.header(t("chat_title"))

    api_key = _get_api_key()

    # Initialiser l'historique
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Afficher le contexte des donnees
    df = st.session_state.get("complaints_df", pd.DataFrame())
    if not df.empty:
        n = len(df)
        nc = len(st.session_state.get("classified_df", pd.DataFrame()))
        products = (
            ", ".join(df["product_line"].unique().tolist())
            if "product_line" in df.columns
            else "N/A"
        )
        if "date" in df.columns:
            dmin = df["date"].min()
            dmax = df["date"].max()
            period = (
                f"{dmin.strftime('%Y-%m-%d')} -- {dmax.strftime('%Y-%m-%d')}"
                if pd.notna(dmin)
                else "N/A"
            )
        else:
            period = "N/A"
        st.info(
            t("chat_data_context", n=str(n), nc=str(nc), products=products, period=period)
        )
    else:
        st.warning(t("chat_no_data"))

    if not api_key:
        st.warning(t("chat_api_missing"))

    # Bouton effacer
    if st.button(t("chat_clear"), use_container_width=False):
        st.session_state.chat_messages = []
        st.rerun()

    st.divider()

    # Message d'accueil
    if not st.session_state.chat_messages:
        with st.chat_message("assistant"):
            st.markdown(t("chat_welcome"))

    # Historique des messages
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input(t("chat_placeholder")):
        with st.chat_message("user"):
            st.markdown(prompt)

        if api_key:
            with st.chat_message("assistant"):
                st.write_stream(_stream_groq_response(prompt))
        else:
            with st.chat_message("assistant"):
                st.markdown(t("chat_api_missing"))
