"""Classification des plaintes par LLM (Groq API) -- VOC Complaints Analyzer."""

from __future__ import annotations

import json
import os
import time
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd
import streamlit as st

# --------------------------------------------------------------------------- #
#  Types
# --------------------------------------------------------------------------- #

@dataclass
class ClassificationResult:
    """Resultat de classification d'une plainte."""

    defect_type: str = ""
    defect_subtype: str = ""
    severity: str = ""
    root_cause_hypothesis: str = ""
    sentiment: str = ""
    summary: str = ""
    error: str = ""


# --------------------------------------------------------------------------- #
#  Donnees de demonstration (fallback sans API)
# --------------------------------------------------------------------------- #

DEMO_CLASSIFICATIONS: dict[str, ClassificationResult] = {
    "C-001": ClassificationResult("solder_defect", "solder void", "major", "Incomplete reflow profile or paste deposition issue", "negative", "Solder voids on flex connector pads affecting 12% of units"),
    "C-002": ClassificationResult("dimensional", "out of tolerance", "major", "Electrode deposition process parameter drift", "negative", "Inconsistent biosensor electrode thickness outside spec range"),
    "C-003": ClassificationResult("mechanical", "bent pin", "minor", "Insufficient packaging protection during shipping", "negative", "Bent pins found on 4% of microconnectors after unpacking"),
    "C-004": ClassificationResult("dimensional", "out of tolerance", "critical", "Die cutting or etching process drift", "negative", "Flex circuit width 5.12 mm exceeds tolerance, entire lot rejected"),
    "C-005": ClassificationResult("electrical", "high resistance", "major", "Trace plating deficiency or micro-crack in conductor", "negative", "High resistance on PCB trace, 4.6x above specification limit"),
    "C-006": ClassificationResult("contamination", "foreign particle", "major", "Cleanroom process excursion or material contamination", "negative", "Metallic particle contamination on biosensor assemblies"),
    "C-007": ClassificationResult("solder_defect", "cold solder", "major", "Reflow temperature profile too low or solder paste issue", "negative", "Cold solder joints on flex connector, pull test failures"),
    "C-008": ClassificationResult("mechanical", "crack", "critical", "Material fatigue or molding defect in connector housing", "negative", "Connector housing crack at 150 vs 500 thermal cycles required"),
    "C-009": ClassificationResult("electrical", "short circuit", "major", "Etching defect or solder bridging between traces", "negative", "Short circuits on 5% of PCB modules at incoming inspection"),
    "C-010": ClassificationResult("biocompatibility", "cytotoxicity", "critical", "Material leachable or processing residue issue", "negative", "Cytotoxicity failure: cell viability 62% vs 80% min per ISO 10993"),
    "C-011": ClassificationResult("contamination", "oxidation", "minor", "Gold plating thickness insufficient or exposure to corrosive environment", "negative", "Surface oxidation on gold-plated contacts, 20% affected"),
    "C-012": ClassificationResult("packaging_delivery", "wrong quantity", "minor", "Counting or packaging error at shipment stage", "negative", "Quantity discrepancy: 4200 shipped vs 5000 ordered"),
    "C-013": ClassificationResult("mechanical", "delamination", "major", "Lamination pressure or temperature parameter issue", "negative", "PCB layer delamination after reflow on 15% of boards"),
    "C-014": ClassificationResult("dimensional", "warpage", "major", "Thermal stress during manufacturing or material CTE mismatch", "negative", "Flex connector warpage 3x above specification limit"),
    "C-015": ClassificationResult("packaging_delivery", "labeling error", "major", "Label printing or application process error", "negative", "Lot number mismatch between box and unit labels, traceability risk"),
    "C-016": ClassificationResult("dimensional", "misalignment", "major", "Stamping die wear or press alignment drift", "negative", "Pin pitch 0.52 mm vs 0.50 mm nominal, mating failure"),
    "C-017": ClassificationResult("solder_defect", "bridging", "major", "Solder paste excess or stencil aperture issue", "negative", "Solder bridging causing electrical shorts on flex connector"),
    "C-018": ClassificationResult("contamination", "residue", "major", "Cleaning process inadequacy or contaminated rinse water", "negative", "Ionic contamination 35% above specification limit on PCB"),
    "C-019": ClassificationResult("biocompatibility", "sensitization", "critical", "Material biocompatibility issue or adhesive reaction", "negative", "Patient skin sensitization reported near biosensor site"),
    "C-020": ClassificationResult("packaging_delivery", "damage in transit", "minor", "Inadequate packaging for shipping conditions", "negative", "Crushed packaging with bent leads on flex connectors"),
    "C-021": ClassificationResult("solder_defect", "solder void", "major", "Reflow profile issue on Line 2, possible temperature excursion", "negative", "Solder voids exceeding 25% pad area on Line 2 production"),
    "C-022": ClassificationResult("solder_defect", "cold solder", "major", "Line 2 reflow oven temperature profile degradation", "negative", "Cold solder joints on microconnectors from Line 2, 15% failure"),
    "C-023": ClassificationResult("solder_defect", "insufficient solder", "major", "Line 2 solder paste printer calibration drift", "negative", "Insufficient solder on flex connector, 40% below nominal volume"),
    "C-024": ClassificationResult("electrical", "open circuit", "major", "Solder reflow issue on Line 2 causing open traces", "negative", "Open circuits on PCB module from Line 2, 8% ICT failure rate"),
    "C-025": ClassificationResult("solder_defect", "bridging", "major", "Line 2 stencil misalignment or paste excess on fine pitch", "negative", "Solder bridging on fine-pitch flex connector pads from Line 2"),
    "C-026": ClassificationResult("mechanical", "delamination", "major", "Adhesion process parameter or surface preparation issue", "negative", "Electrode delamination on biosensor, peel strength 53% of spec"),
    "C-027": ClassificationResult("solder_defect", "cold solder", "major", "Ongoing Line 2 reflow temperature issue, pattern confirmed", "negative", "Cold solder on flex connector from Line 2, 22% visually defective"),
    "C-028": ClassificationResult("dimensional", "out of tolerance", "major", "Stamping or forming tool wear causing length variation", "negative", "Connector pin length variation 4x above specification tolerance"),
    "C-029": ClassificationResult("biocompatibility", "irritation", "critical", "Device material or adhesive causing skin irritation", "negative", "End user irritation at device contact, ISO 10993-10 retest needed"),
    "C-030": ClassificationResult("contamination", "foreign particle", "critical", "Foreign material inclusion during flex circuit lamination", "negative", "Embedded particle in flex circuit dielectric, production halted"),
}


# --------------------------------------------------------------------------- #
#  Groq client
# --------------------------------------------------------------------------- #

def _get_api_key() -> str | None:
    """Recupere la cle API Groq depuis l'environnement ou st.secrets.

    Returns
    -------
    str or None
        Cle API ou None si non disponible.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GROQ_API_KEY", None)
        except Exception:
            pass
    return api_key


def is_api_available() -> bool:
    """Verifie si l'API Groq est disponible.

    Returns
    -------
    bool
        True si la cle API est configuree.
    """
    return bool(_get_api_key())


def _get_groq_client():
    """Retourne une instance du client Groq.

    Returns
    -------
    groq.Groq or None
        Client Groq ou None si non disponible.
    """
    api_key = _get_api_key()
    if not api_key:
        return None
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except ImportError:
        return None


# --------------------------------------------------------------------------- #
#  Prompt de classification
# --------------------------------------------------------------------------- #

CLASSIFICATION_PROMPT = """You are an expert quality engineer at a medtech/connector manufacturer.
Analyze the following customer complaint and classify it.

Complaint ID: {complaint_id}
Product line: {product_line}
Complaint text: {complaint_text}
Lot number: {lot_number}
Production line: {production_line}

Classify using these defect types:
- solder_defect (subtypes: solder void, cold solder, bridging, insufficient solder)
- dimensional (subtypes: out of tolerance, warpage, misalignment)
- contamination (subtypes: foreign particle, residue, oxidation)
- electrical (subtypes: open circuit, short circuit, high resistance)
- mechanical (subtypes: bent pin, crack, delamination)
- biocompatibility (subtypes: cytotoxicity, sensitization, irritation)
- packaging_delivery (subtypes: damage in transit, wrong quantity, labeling error)

Severity levels:
- critical: Safety risk or regulatory impact, immediate action required
- major: Significant functional impact, corrective action needed
- minor: Cosmetic or minor functional impact, monitoring

Return ONLY a valid JSON object (no markdown, no explanation):
{{
  "defect_type": "type",
  "defect_subtype": "subtype",
  "severity": "critical|major|minor",
  "root_cause_hypothesis": "brief hypothesis",
  "sentiment": "negative|neutral|positive",
  "summary": "one-line summary"
}}"""


# --------------------------------------------------------------------------- #
#  Classification
# --------------------------------------------------------------------------- #

def classify_complaint(
    complaint_id: str,
    complaint_text: str,
    product_line: str = "",
    lot_number: str = "",
    production_line: str = "",
    max_retries: int = 3,
) -> ClassificationResult:
    """Classifie une plainte individuelle via Groq LLM.

    Parameters
    ----------
    complaint_id : str
        Identifiant de la plainte.
    complaint_text : str
        Texte de la plainte.
    product_line : str
        Ligne de produit.
    lot_number : str
        Numero de lot.
    production_line : str
        Ligne de production.
    max_retries : int
        Nombre maximum de tentatives.

    Returns
    -------
    ClassificationResult
        Resultat de la classification.
    """
    client = _get_groq_client()
    if client is None:
        # Fallback sur les donnees demo
        return DEMO_CLASSIFICATIONS.get(
            complaint_id,
            ClassificationResult(error="API non disponible"),
        )

    prompt = CLASSIFICATION_PROMPT.format(
        complaint_id=complaint_id,
        product_line=product_line or "N/A",
        complaint_text=complaint_text,
        lot_number=lot_number or "N/A",
        production_line=production_line or "N/A",
    )

    from config import load_app_config
    config = load_app_config()
    llm_config = config.get("llm", {})

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=llm_config.get("model", "llama-3.3-70b-versatile"),
                messages=[
                    {"role": "system", "content": "You are a quality engineer. Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=llm_config.get("temperature", 0.1),
                max_tokens=llm_config.get("max_tokens", 1024),
            )

            raw = response.choices[0].message.content.strip()

            # Nettoyer le JSON (retirer d'eventuels blocs markdown)
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()

            data = json.loads(raw)

            return ClassificationResult(
                defect_type=data.get("defect_type", ""),
                defect_subtype=data.get("defect_subtype", ""),
                severity=data.get("severity", ""),
                root_cause_hypothesis=data.get("root_cause_hypothesis", ""),
                sentiment=data.get("sentiment", ""),
                summary=data.get("summary", ""),
            )

        except json.JSONDecodeError:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return ClassificationResult(error=f"JSON parsing failed after {max_retries} attempts")

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return ClassificationResult(error=str(e)[:100])

    return ClassificationResult(error="Max retries exceeded")


def classify_batch(
    df: pd.DataFrame,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> pd.DataFrame:
    """Classifie un lot de plaintes.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame des plaintes.
    progress_callback : callable or None
        Fonction de callback (i, n, complaint_id) pour le suivi.

    Returns
    -------
    pd.DataFrame
        DataFrame enrichi avec les colonnes de classification.
    """
    results = []
    n = len(df)

    for i, (_, row) in enumerate(df.iterrows()):
        cid = str(row.get("complaint_id", f"C-{i+1:03d}"))

        if progress_callback:
            progress_callback(i + 1, n, cid)

        result = classify_complaint(
            complaint_id=cid,
            complaint_text=str(row.get("complaint_text", "")),
            product_line=str(row.get("product_line", "")),
            lot_number=str(row.get("lot_number", "")),
            production_line=str(row.get("production_line", "")),
        )

        results.append(
            {
                "complaint_id": cid,
                "severity": result.severity,
                "defect_type": result.defect_type,
                "defect_subtype": result.defect_subtype,
                "root_cause_hypothesis": result.root_cause_hypothesis,
                "sentiment": result.sentiment,
                "ai_summary": result.summary,
                "classification_error": result.error,
            }
        )

    results_df = pd.DataFrame(results)

    # Fusionner avec le DataFrame original
    df_out = df.copy()
    for col in ["severity", "defect_type"]:
        if col in results_df.columns:
            df_out[col] = results_df[col].values

    # Ajouter les nouvelles colonnes
    for col in ["defect_subtype", "root_cause_hypothesis", "sentiment", "ai_summary", "classification_error"]:
        if col in results_df.columns:
            df_out[col] = results_df[col].values

    return df_out


def get_demo_classified_data(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne les donnees de demonstration pre-classifiees.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame des plaintes.

    Returns
    -------
    pd.DataFrame
        DataFrame enrichi avec les classifications demo.
    """
    df_out = df.copy()
    severities = []
    defect_types = []
    defect_subtypes = []
    root_causes = []
    sentiments = []
    summaries = []

    for _, row in df_out.iterrows():
        cid = str(row.get("complaint_id", ""))
        demo = DEMO_CLASSIFICATIONS.get(cid, ClassificationResult())
        severities.append(demo.severity)
        defect_types.append(demo.defect_type)
        defect_subtypes.append(demo.defect_subtype)
        root_causes.append(demo.root_cause_hypothesis)
        sentiments.append(demo.sentiment)
        summaries.append(demo.summary)

    df_out["severity"] = severities
    df_out["defect_type"] = defect_types
    df_out["defect_subtype"] = defect_subtypes
    df_out["root_cause_hypothesis"] = root_causes
    df_out["sentiment"] = sentiments
    df_out["ai_summary"] = summaries
    df_out["classification_error"] = ""

    return df_out
