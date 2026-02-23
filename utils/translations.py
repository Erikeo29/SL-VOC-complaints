"""Traductions et gestion de la langue -- VOC Complaints Analyzer."""

import streamlit as st

TRANSLATIONS: dict[str, dict[str, str]] = {
    "fr": {
        # --- App ---
        "app_title": "VOC Complaints Analyzer",
        "app_subtitle": "Analyse IA des plaintes clients",
        "sidebar_title": "VOC Complaints",
        "version_info": (
            "**Version {version}** -- {date}\n\n"
            "Analyse IA des plaintes clients pour l'industrie medtech."
        ),
        # --- Language ---
        "lang_fr": "FR",
        "lang_en": "EN",
        "lang_label": "Langue",
        # --- Navigation ---
        "nav_upload": "Import donnees",
        "nav_classification": "Classification IA",
        "nav_dashboard": "Tableau de bord",
        "nav_reports": "Rapports",
        "nav_chatbot": "Assistant IA",
        "nav_guide": "Guide",
        # --- Sidebar stats ---
        "sidebar_data_stats": "Donnees chargees",
        "sidebar_nb_complaints": "Plaintes",
        "sidebar_nb_classified": "Classifiees",
        "sidebar_nb_unclassified": "Non classifiees",
        "sidebar_no_data": "Aucune donnee chargee",
        # --- Upload page ---
        "upload_title": "Import des donnees",
        "upload_file_label": "Charger un fichier (CSV, Excel)",
        "upload_paste_label": "Ou coller du texte libre",
        "upload_paste_help": "Une plainte par ligne",
        "upload_paste_btn": "Ajouter les plaintes",
        "upload_sample_btn": "Charger les donnees d'exemple",
        "upload_sample_help": "30 plaintes realistes (medtech/connecteurs)",
        "upload_preview": "Apercu des donnees",
        "upload_success": "{n} plaintes chargees avec succes.",
        "upload_error": "Erreur lors du chargement : {e}",
        "upload_paste_success": "{n} plaintes ajoutees depuis le texte.",
        "upload_columns_warning": "Colonnes attendues manquantes : {cols}",
        "upload_clear_btn": "Effacer les donnees",
        "upload_cleared": "Donnees effacees.",
        # --- Classification page ---
        "classif_title": "Classification IA",
        "classif_description": (
            "Classification automatique des plaintes par LLM : type de defaut, "
            "severite, hypothese de cause racine et sentiment."
        ),
        "classif_no_data": "Aucune donnee chargee. Allez dans **Import donnees**.",
        "classif_no_api": (
            "Cle API Groq non configuree. Mode demonstration avec donnees pre-classifiees."
        ),
        "classif_run_btn": "Lancer la classification",
        "classif_running": "Classification en cours...",
        "classif_progress": "Plainte {i}/{n} : {cid}",
        "classif_done": "Classification terminee : {n} plaintes traitees.",
        "classif_error": "Erreur pour {cid} : {e}",
        "classif_results": "Resultats de la classification",
        "classif_col_id": "ID",
        "classif_col_severity": "Severite",
        "classif_col_defect": "Type de defaut",
        "classif_col_subtype": "Sous-type",
        "classif_col_root_cause": "Hypothese cause racine",
        "classif_col_sentiment": "Sentiment",
        "classif_col_summary": "Resume",
        "classif_demo_label": "Donnees de demonstration",
        "classif_demo_info": (
            "Les resultats ci-dessous sont des donnees de demonstration pre-classifiees. "
            "Configurez GROQ_API_KEY pour la classification IA en temps reel."
        ),
        "classif_batch_label": "Taille du lot",
        "classif_classify_all": "Classifier toutes les plaintes",
        "classif_classify_selected": "Classifier la selection",
        # --- Dashboard page ---
        "dash_title": "Tableau de bord",
        "dash_no_data": "Aucune donnee classifiee. Lancez la **Classification IA** d'abord.",
        "dash_kpi_total": "Total plaintes",
        "dash_kpi_critical": "Critiques",
        "dash_kpi_major": "Majeures",
        "dash_kpi_minor": "Mineures",
        "dash_kpi_unclassified": "Non classifiees",
        "dash_trend_title": "Tendance temporelle des plaintes",
        "dash_treemap_title": "Repartition par type de defaut",
        "dash_sunburst_title": "Defauts par ligne de production",
        "dash_severity_title": "Distribution de la severite",
        "dash_product_title": "Plaintes par ligne de produit",
        "dash_anomaly_title": "Detection d'anomalies",
        "dash_anomaly_alert": (
            "ALERTE : tendance anormale detectee -- {details}"
        ),
        "dash_no_anomaly": "Aucune anomalie detectee sur la periode.",
        "dash_correlation_title": "Correlation ligne de production / defauts",
        "dash_filter_period": "Periode",
        "dash_filter_product": "Ligne de produit",
        "dash_filter_severity": "Severite",
        "dash_filter_all": "Toutes",
        "dash_sentiment_title": "Analyse de sentiment",
        # --- Report page ---
        "report_title": "Generation de rapports",
        "report_no_data": "Aucune donnee classifiee disponible.",
        "report_summary_title": "Resume executif",
        "report_gen_btn": "Generer le rapport",
        "report_download_csv": "Telecharger CSV",
        "report_download_xlsx": "Telecharger Excel",
        "report_mdr_title": "Rapport type FDA MDR / vigilance",
        "report_gen_mdr_btn": "Generer le rapport MDR",
        "report_mdr_no_api": (
            "Cle API Groq requise pour la generation du rapport MDR."
        ),
        "report_period": "Periode : {start} -- {end}",
        "report_total": "Total plaintes analysees : {n}",
        # --- Chatbot page ---
        "chat_title": "Assistant IA",
        "chat_welcome": (
            "Bonjour ! Je suis votre assistant pour analyser les plaintes clients. "
            "Posez-moi vos questions sur les tendances, les correlations ou les defauts."
        ),
        "chat_placeholder": "Posez votre question...",
        "chat_error": "Erreur de connexion a l'API.",
        "chat_clear": "Effacer la conversation",
        "chat_api_missing": "Cle API Groq non configuree. Le chatbot n'est pas disponible.",
        "chat_no_data": "Aucune donnee chargee. Importez des plaintes d'abord.",
        "chat_data_context": (
            "Donnees chargees : {n} plaintes, {nc} classifiees. "
            "Produits : {products}. Periode : {period}."
        ),
        # --- Guide page ---
        "guide_title": "Guide d'utilisation",
        "guide_not_found": "Le fichier guide n'a pas ete trouve.",
    },
    "en": {
        # --- App ---
        "app_title": "VOC Complaints Analyzer",
        "app_subtitle": "AI-powered customer complaint analysis",
        "sidebar_title": "VOC Complaints",
        "version_info": (
            "**Version {version}** -- {date}\n\n"
            "AI-powered customer complaint analysis for medtech industry."
        ),
        # --- Language ---
        "lang_fr": "FR",
        "lang_en": "EN",
        "lang_label": "Language",
        # --- Navigation ---
        "nav_upload": "Import data",
        "nav_classification": "AI classification",
        "nav_dashboard": "Dashboard",
        "nav_reports": "Reports",
        "nav_chatbot": "AI assistant",
        "nav_guide": "Guide",
        # --- Sidebar stats ---
        "sidebar_data_stats": "Loaded data",
        "sidebar_nb_complaints": "Complaints",
        "sidebar_nb_classified": "Classified",
        "sidebar_nb_unclassified": "Unclassified",
        "sidebar_no_data": "No data loaded",
        # --- Upload page ---
        "upload_title": "Data import",
        "upload_file_label": "Upload a file (CSV, Excel)",
        "upload_paste_label": "Or paste free text",
        "upload_paste_help": "One complaint per line",
        "upload_paste_btn": "Add complaints",
        "upload_sample_btn": "Load sample data",
        "upload_sample_help": "30 realistic complaints (medtech/connectors)",
        "upload_preview": "Data preview",
        "upload_success": "{n} complaints loaded successfully.",
        "upload_error": "Error loading file: {e}",
        "upload_paste_success": "{n} complaints added from text.",
        "upload_columns_warning": "Expected columns missing: {cols}",
        "upload_clear_btn": "Clear data",
        "upload_cleared": "Data cleared.",
        # --- Classification page ---
        "classif_title": "AI classification",
        "classif_description": (
            "Automatic complaint classification via LLM: defect type, "
            "severity, root cause hypothesis, and sentiment."
        ),
        "classif_no_data": "No data loaded. Go to **Import data**.",
        "classif_no_api": (
            "Groq API key not configured. Demo mode with pre-classified data."
        ),
        "classif_run_btn": "Run classification",
        "classif_running": "Classification in progress...",
        "classif_progress": "Complaint {i}/{n}: {cid}",
        "classif_done": "Classification complete: {n} complaints processed.",
        "classif_error": "Error for {cid}: {e}",
        "classif_results": "Classification results",
        "classif_col_id": "ID",
        "classif_col_severity": "Severity",
        "classif_col_defect": "Defect type",
        "classif_col_subtype": "Subtype",
        "classif_col_root_cause": "Root cause hypothesis",
        "classif_col_sentiment": "Sentiment",
        "classif_col_summary": "Summary",
        "classif_demo_label": "Demo data",
        "classif_demo_info": (
            "Results below are pre-classified demo data. "
            "Set GROQ_API_KEY for real-time AI classification."
        ),
        "classif_batch_label": "Batch size",
        "classif_classify_all": "Classify all complaints",
        "classif_classify_selected": "Classify selection",
        # --- Dashboard page ---
        "dash_title": "Dashboard",
        "dash_no_data": "No classified data. Run **AI classification** first.",
        "dash_kpi_total": "Total complaints",
        "dash_kpi_critical": "Critical",
        "dash_kpi_major": "Major",
        "dash_kpi_minor": "Minor",
        "dash_kpi_unclassified": "Unclassified",
        "dash_trend_title": "Complaint temporal trend",
        "dash_treemap_title": "Distribution by defect type",
        "dash_sunburst_title": "Defects by production line",
        "dash_severity_title": "Severity distribution",
        "dash_product_title": "Complaints by product line",
        "dash_anomaly_title": "Anomaly detection",
        "dash_anomaly_alert": (
            "ALERT: abnormal trend detected -- {details}"
        ),
        "dash_no_anomaly": "No anomaly detected for the period.",
        "dash_correlation_title": "Production line / defect correlation",
        "dash_filter_period": "Period",
        "dash_filter_product": "Product line",
        "dash_filter_severity": "Severity",
        "dash_filter_all": "All",
        "dash_sentiment_title": "Sentiment analysis",
        # --- Report page ---
        "report_title": "Report generation",
        "report_no_data": "No classified data available.",
        "report_summary_title": "Executive summary",
        "report_gen_btn": "Generate report",
        "report_download_csv": "Download CSV",
        "report_download_xlsx": "Download Excel",
        "report_mdr_title": "FDA MDR / vigilance report template",
        "report_gen_mdr_btn": "Generate MDR report",
        "report_mdr_no_api": (
            "Groq API key required for MDR report generation."
        ),
        "report_period": "Period: {start} -- {end}",
        "report_total": "Total complaints analyzed: {n}",
        # --- Chatbot page ---
        "chat_title": "AI assistant",
        "chat_welcome": (
            "Hello! I'm your assistant for analyzing customer complaints. "
            "Ask me about trends, correlations, or defect patterns."
        ),
        "chat_placeholder": "Ask your question...",
        "chat_error": "API connection error.",
        "chat_clear": "Clear conversation",
        "chat_api_missing": "Groq API key not configured. Chatbot is unavailable.",
        "chat_no_data": "No data loaded. Import complaints first.",
        "chat_data_context": (
            "Loaded data: {n} complaints, {nc} classified. "
            "Products: {products}. Period: {period}."
        ),
        # --- Guide page ---
        "guide_title": "User guide",
        "guide_not_found": "Guide file not found.",
    },
}


def get_language() -> str:
    """Retourne la langue courante depuis session_state.

    Returns
    -------
    str
        Code langue ('fr' ou 'en').
    """
    return st.session_state.get("lang", "fr")


def t(key: str, **kwargs: str) -> str:
    """Traduit une cle selon la langue courante.

    Parameters
    ----------
    key : str
        Cle de traduction.
    **kwargs : str
        Variables de substitution pour str.format().

    Returns
    -------
    str
        Texte traduit.
    """
    lang = get_language()
    text = TRANSLATIONS.get(lang, TRANSLATIONS["fr"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
