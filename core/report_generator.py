"""Generation de rapports de conformite -- VOC Complaints Analyzer."""

from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import streamlit as st

from core.llm_classifier import is_api_available


def generate_executive_summary(df: pd.DataFrame, lang: str = "fr") -> str:
    """Genere un resume executif des plaintes classifiees.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame des plaintes classifiees.
    lang : str
        Langue du rapport ('fr' ou 'en').

    Returns
    -------
    str
        Resume executif en markdown.
    """
    if df.empty:
        return "No data available." if lang == "en" else "Aucune donnee disponible."

    total = len(df)
    date_min = df["date"].min()
    date_max = df["date"].max()

    # Comptages de severite
    sev_counts = df["severity"].value_counts().to_dict() if "severity" in df.columns else {}
    n_critical = sev_counts.get("critical", 0)
    n_major = sev_counts.get("major", 0)
    n_minor = sev_counts.get("minor", 0)

    # Top defauts
    defect_counts = (
        df["defect_type"].value_counts().head(5).to_dict()
        if "defect_type" in df.columns
        else {}
    )

    # Top lignes de production
    line_counts = (
        df["production_line"].value_counts().head(3).to_dict()
        if "production_line" in df.columns
        else {}
    )

    if lang == "fr":
        period_str = (
            f"{date_min.strftime('%d/%m/%Y')} -- {date_max.strftime('%d/%m/%Y')}"
            if pd.notna(date_min)
            else "N/A"
        )
        report = f"""## Resume executif

**Periode :** {period_str}
**Total plaintes analysees :** {total}

### Distribution de la severite
| Severite | Nombre | % |
|----------|--------|---|
| Critique | {n_critical} | {n_critical/total*100:.0f}% |
| Majeure | {n_major} | {n_major/total*100:.0f}% |
| Mineure | {n_minor} | {n_minor/total*100:.0f}% |

### Top 5 types de defauts
"""
        for defect, count in defect_counts.items():
            report += f"- **{defect}** : {count} ({count/total*100:.0f}%)\n"

        report += "\n### Plaintes par ligne de production\n"
        for line, count in line_counts.items():
            if line:
                report += f"- **{line}** : {count} ({count/total*100:.0f}%)\n"

        if n_critical > 0:
            report += f"\n### Plaintes critiques ({n_critical})\n"
            critical = df[df["severity"] == "critical"]
            for _, row in critical.iterrows():
                summary = row.get("ai_summary", row.get("complaint_text", "")[:100])
                report += f"- **{row['complaint_id']}** ({row.get('product_line', 'N/A')}) : {summary}\n"

    else:
        period_str = (
            f"{date_min.strftime('%Y-%m-%d')} -- {date_max.strftime('%Y-%m-%d')}"
            if pd.notna(date_min)
            else "N/A"
        )
        report = f"""## Executive summary

**Period:** {period_str}
**Total complaints analyzed:** {total}

### Severity distribution
| Severity | Count | % |
|----------|-------|---|
| Critical | {n_critical} | {n_critical/total*100:.0f}% |
| Major | {n_major} | {n_major/total*100:.0f}% |
| Minor | {n_minor} | {n_minor/total*100:.0f}% |

### Top 5 defect types
"""
        for defect, count in defect_counts.items():
            report += f"- **{defect}**: {count} ({count/total*100:.0f}%)\n"

        report += "\n### Complaints by production line\n"
        for line, count in line_counts.items():
            if line:
                report += f"- **{line}**: {count} ({count/total*100:.0f}%)\n"

        if n_critical > 0:
            report += f"\n### Critical complaints ({n_critical})\n"
            critical = df[df["severity"] == "critical"]
            for _, row in critical.iterrows():
                summary = row.get("ai_summary", row.get("complaint_text", "")[:100])
                report += f"- **{row['complaint_id']}** ({row.get('product_line', 'N/A')}): {summary}\n"

    return report


def generate_mdr_report(df: pd.DataFrame, lang: str = "fr") -> str:
    """Genere un rapport type FDA MDR / vigilance.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame des plaintes classifiees.
    lang : str
        Langue du rapport.

    Returns
    -------
    str
        Rapport MDR en markdown.
    """
    if df.empty:
        return "No data." if lang == "en" else "Aucune donnee."

    # Si l'API est disponible, generer via LLM
    if is_api_available():
        return _generate_mdr_via_llm(df, lang)

    # Sinon, rapport structuree statique
    return _generate_mdr_static(df, lang)


def _generate_mdr_static(df: pd.DataFrame, lang: str = "fr") -> str:
    """Genere un rapport MDR statique (sans LLM).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame des plaintes classifiees.
    lang : str
        Langue du rapport.

    Returns
    -------
    str
        Rapport MDR statique.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = len(df)

    critical = df[df.get("severity", pd.Series(dtype=str)) == "critical"] if "severity" in df.columns else pd.DataFrame()

    if lang == "fr":
        report = f"""## Rapport de vigilance / MDR

**Date de generation :** {now}
**Nombre total de plaintes :** {total}
**Plaintes critiques :** {len(critical)}

---

### 1. Evenements a signaler

"""
        if not critical.empty:
            for _, row in critical.iterrows():
                report += f"""#### {row['complaint_id']}
- **Produit :** {row.get('product_line', 'N/A')}
- **Lot :** {row.get('lot_number', 'N/A')}
- **Ligne :** {row.get('production_line', 'N/A')}
- **Date :** {row.get('date', 'N/A')}
- **Description :** {row.get('complaint_text', 'N/A')}
- **Type de defaut :** {row.get('defect_type', 'N/A')} / {row.get('defect_subtype', 'N/A')}
- **Cause racine probable :** {row.get('root_cause_hypothesis', 'A determiner')}

"""
        else:
            report += "Aucun evenement critique a signaler.\n\n"

        report += """### 2. Actions recommandees

- Evaluer le besoin de rappel produit pour les lots critiques.
- Investiguer les causes racines identifiees.
- Mettre a jour le CAPA correspondant.
- Verifier la conformite aux exigences ISO 13485.

### 3. Suivi

Ce rapport doit etre revu par le responsable qualite et le responsable reglementaire.
"""

    else:
        report = f"""## Vigilance / MDR report

**Generation date:** {now}
**Total complaints:** {total}
**Critical complaints:** {len(critical)}

---

### 1. Reportable events

"""
        if not critical.empty:
            for _, row in critical.iterrows():
                report += f"""#### {row['complaint_id']}
- **Product:** {row.get('product_line', 'N/A')}
- **Lot:** {row.get('lot_number', 'N/A')}
- **Line:** {row.get('production_line', 'N/A')}
- **Date:** {row.get('date', 'N/A')}
- **Description:** {row.get('complaint_text', 'N/A')}
- **Defect type:** {row.get('defect_type', 'N/A')} / {row.get('defect_subtype', 'N/A')}
- **Probable root cause:** {row.get('root_cause_hypothesis', 'To be determined')}

"""
        else:
            report += "No critical events to report.\n\n"

        report += """### 2. Recommended actions

- Assess need for product recall for critical lots.
- Investigate identified root causes.
- Update corresponding CAPA.
- Verify compliance with ISO 13485 requirements.

### 3. Follow-up

This report must be reviewed by Quality Manager and Regulatory Affairs Manager.
"""

    return report


def _generate_mdr_via_llm(df: pd.DataFrame, lang: str = "fr") -> str:
    """Genere un rapport MDR via LLM (Groq).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame des plaintes classifiees.
    lang : str
        Langue du rapport.

    Returns
    -------
    str
        Rapport MDR genere par LLM.
    """
    try:
        from core.llm_classifier import _get_groq_client
        from config import load_app_config

        client = _get_groq_client()
        if client is None:
            return _generate_mdr_static(df, lang)

        config = load_app_config()
        llm_config = config.get("llm", {})

        # Preparer le resume des donnees pour le LLM
        critical = df[df["severity"] == "critical"] if "severity" in df.columns else pd.DataFrame()
        summary_data = []
        for _, row in critical.iterrows():
            summary_data.append(
                f"- {row['complaint_id']}: {row.get('complaint_text', '')[:150]} "
                f"(Product: {row.get('product_line', 'N/A')}, "
                f"Lot: {row.get('lot_number', 'N/A')}, "
                f"Defect: {row.get('defect_type', 'N/A')})"
            )

        lang_str = "French" if lang == "fr" else "English"
        prompt = f"""Generate a medical device vigilance / FDA MDR-style report in {lang_str} based on these critical complaints:

Total complaints: {len(df)}
Critical complaints: {len(critical)}

Critical complaint details:
{chr(10).join(summary_data) if summary_data else 'None'}

Include sections for:
1. Reportable events summary
2. Risk assessment
3. Root cause analysis summary
4. Recommended corrective actions
5. Timeline for follow-up

Format in markdown. Be concise and professional."""

        response = client.chat.completions.create(
            model=llm_config.get("model", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": "You are a medical device regulatory affairs expert."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2048,
        )

        return response.choices[0].message.content

    except Exception as e:
        # Fallback sur le rapport statique
        return _generate_mdr_static(df, lang)
