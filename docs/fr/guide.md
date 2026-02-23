# Guide d'utilisation -- VOC Complaints Analyzer

## Presentation

VOC Complaints Analyzer est un outil d'analyse IA des plaintes clients
concu pour l'industrie medtech et connecteurs. Il permet de :

- Importer des plaintes depuis des fichiers CSV/Excel ou du texte libre
- Classifier automatiquement les plaintes par type de defaut, severite et cause racine
- Visualiser les tendances et detecter les anomalies
- Generer des rapports de conformite (FDA MDR, vigilance)
- Interroger les donnees via un assistant IA

## Pages de l'application

### 1. Import donnees

Chargez vos plaintes de trois manieres :

- **Fichier CSV/Excel** : faites glisser ou selectionnez un fichier.
  Colonnes attendues : `complaint_id`, `date`, `product_line`, `customer`,
  `complaint_text`, `severity`, `defect_type`, `lot_number`, `production_line`.
- **Texte libre** : collez une plainte par ligne.
- **Donnees d'exemple** : 30 plaintes realistes pour decouvrir l'application.

### 2. Classification IA

La classification utilise un LLM (Llama 3.3 via Groq) pour analyser chaque plainte et retourner :

- **Type de defaut** : soudure, dimensionnel, contamination, electrique, mecanique,
  biocompatibilite, emballage/livraison
- **Severite** : critique, majeure, mineure
- **Hypothese de cause racine**
- **Sentiment** : negatif, neutre, positif
- **Resume** en une ligne

Sans cle API Groq, des donnees de demonstration pre-classifiees sont disponibles.

### 3. Tableau de bord

Visualisations interactives :

- **KPIs** : total, critiques, majeures, mineures
- **Tendance temporelle** avec moyenne mobile et seuil d'anomalie
- **Treemap** des types de defauts
- **Sunburst** des defauts par ligne de production
- **Detection d'anomalies** par z-score (seuil configurable)
- **Matrice de correlation** ligne de production / type de defaut
- **Analyse de sentiment**

### 4. Rapports

Generez des rapports :

- **Resume executif** : distribution de severite, top defauts, plaintes critiques
- **Rapport MDR/vigilance** : evenements a signaler, actions recommandees
- **Export** : CSV ou Excel

### 5. Assistant IA

Chatbot specialise dans l'analyse de plaintes. Exemples de questions :

- "Quels sont les defauts les plus frequents ce mois-ci ?"
- "Y a-t-il une correlation entre la ligne de production et les defauts ?"
- "Resume les plaintes critiques"
- "Quelles actions correctives recommandes-tu ?"

### 6. Guide

Cette page.

## Configuration

### Cle API Groq

Pour la classification IA et le chatbot, configurez la cle API Groq :

1. Creez un compte sur [console.groq.com](https://console.groq.com)
2. Generez une cle API
3. Ajoutez-la dans `.streamlit/secrets.toml` :

```toml
GROQ_API_KEY = "gsk_votre_cle_ici"
```

Ou definissez la variable d'environnement `GROQ_API_KEY`.

### Taxonomie des defauts

Le fichier `data/categories.json` definit la taxonomie des defauts
et peut etre personnalise.

### Configuration generale

Le fichier `config.yaml` contient les parametres de l'application
(modele LLM, seuils d'anomalie, taille des lots de classification).
