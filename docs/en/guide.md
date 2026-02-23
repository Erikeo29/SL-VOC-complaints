# User guide -- VOC Complaints Analyzer

## Overview

VOC Complaints Analyzer is an AI-powered customer complaint analysis tool
designed for the medtech and connector industry. It enables you to:

- Import complaints from CSV/Excel files or free text
- Automatically classify complaints by defect type, severity, and root cause
- Visualize trends and detect anomalies
- Generate compliance reports (FDA MDR, vigilance)
- Query data through an AI assistant

## Application pages

### 1. Import data

Load your complaints in three ways:

- **CSV/Excel file**: drag and drop or select a file.
  Expected columns: `complaint_id`, `date`, `product_line`, `customer`,
  `complaint_text`, `severity`, `defect_type`, `lot_number`, `production_line`.
- **Free text**: paste one complaint per line.
- **Sample data**: 30 realistic complaints to explore the application.

### 2. AI classification

Classification uses an LLM (Llama 3.3 via Groq) to analyze each complaint and return:

- **Defect type**: solder, dimensional, contamination, electrical, mechanical,
  biocompatibility, packaging/delivery
- **Severity**: critical, major, minor
- **Root cause hypothesis**
- **Sentiment**: negative, neutral, positive
- **One-line summary**

Without a Groq API key, pre-classified demo data is available.

### 3. Dashboard

Interactive visualizations:

- **KPIs**: total, critical, major, minor
- **Temporal trend** with moving average and anomaly threshold
- **Treemap** of defect types
- **Sunburst** of defects by production line
- **Anomaly detection** using z-score (configurable threshold)
- **Correlation matrix** production line vs. defect type
- **Sentiment analysis**

### 4. Reports

Generate reports:

- **Executive summary**: severity distribution, top defects, critical complaints
- **MDR/vigilance report**: reportable events, recommended actions
- **Export**: CSV or Excel

### 5. AI assistant

Chatbot specialized in complaint analysis. Example questions:

- "What are the most frequent defects this month?"
- "Is there a correlation between production line and defects?"
- "Summarize the critical complaints"
- "What corrective actions do you recommend?"

### 6. Guide

This page.

## Configuration

### Groq API key

For AI classification and chatbot, configure the Groq API key:

1. Create an account at [console.groq.com](https://console.groq.com)
2. Generate an API key
3. Add it to `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "gsk_your_key_here"
```

Or set the `GROQ_API_KEY` environment variable.

### Defect taxonomy

The `data/categories.json` file defines the defect taxonomy
and can be customized.

### General configuration

The `config.yaml` file contains application settings
(LLM model, anomaly thresholds, classification batch size).
