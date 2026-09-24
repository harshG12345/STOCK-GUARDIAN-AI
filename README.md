# STOCK GUARDIAN AI

> **"Predict demand. Prevent stock-outs. Make smarter inventory decisions."**

Stock Guardian AI is a high-precision, data-driven inventory intelligence and demand forecasting platform developed for **PS-08: Inventory Demand Prediction**. It bridges the gap between predictive machine learning and actionable procurement by translating historical sales and inventory trends into verified forecasts, statistical stockout risks, and lead-time-aware reorder plans.

---

## Table of Contents

1. [Problem Statement & Impact](#1-problem-statement--impact)
2. [Solution Overview](#2-solution-overview)
3. [Architecture & Workflow](#3-architecture--workflow)
4. [Differentiating Features](#4-differentiating-features)
   - [What-If Inventory Simulator](#feature-1-what-if-inventory-simulator)
   - [Statistical Demand Shock Detector](#feature-2-statistical-demand-shock-detector)
   - [0–100 Multi-Factor Inventory Risk Score](#feature-3-0100-multi-factor-inventory-risk-score)
   - [Demand Trend Engine](#feature-4-demand-trend-engine)
   - [Smart Reorder Advisor](#feature-5-smart-reorder-advisor)
5. [Dataset & Ingestion](#5-dataset--ingestion)
6. [Data Preprocessing & Validation](#6-data-preprocessing--validation)
7. [Feature Engineering & Anti-Leakage Guarantee](#7-feature-engineering--anti-leakage-guarantee)
8. [Train / Test Strategy](#8-train--test-strategy)
9. [Predictive Models & Evaluation](#9-predictive-models--evaluation)
10. [Visual Design & UI Standards](#10-visual-design--ui-standards)
11. [Project Structure](#11-project-structure)
12. [Installation & Setup](#12-installation--setup)
13. [Step-by-Step Hackathon Demo](#13-step-by-step-hackathon-demo)
14. [Legal & Compliance](#14-legal--compliance)
15. [Limitations & Future Roadmap](#15-limitations--future-roadmap)

---

## 1. Problem Statement & Impact

Retailers and supply chain operators constantly battle two costly failures:
1. **Stockouts & Under-stocking:** Running out of high-demand items leads to immediate lost revenue, customer churn, and missed market opportunities.
2. **Overstocking & Stagnant Inventory:** Tying up working capital in low-demand goods leads to warehousing bloat, depreciation, and forced markdowns.

Traditional ERP systems rely on static threshold minimums that fail to anticipate demand seasonality, promotional surges, supplier lead time variability, and sudden demand shocks.

**Stock Guardian AI** transforms raw transactional sales data into a continuous decision-support engine answering:
- *What is the expected demand across each SKU for the upcoming horizon?*
- *Which products face imminent stockout risk?*
- *How many units should be ordered immediately to guarantee a 95% service level?*
- *What happens to inventory buffer if demand surges by +20% or +50%?*

---

## 2. Solution Overview

Stock Guardian AI delivers an end-to-end analytical pipeline:
- **Zero-fabrication ML**: Real models (`HistGradientBoostingRegressor` and `RandomForestRegressor`) trained on real historical partitions.
- **Anti-leakage feature engineering**: All lag and rolling features are shifted strictly backwards ($t-1$) to eliminate future lookahead bias.
- **Scientifically derived reorder plans**: Incorporates lead times, demand variance, and normal distribution $Z$-scores.
- **Real-time What-If scenario stress-testing**: Instant parameter manipulation with dynamic recalculation of shortages, stockout days, and adjusted replenishment orders.

---

## 3. Architecture & Workflow

```
[ Historical Sales & Inventory Data / CSV / Excel Upload ]
                           ↓
             [ Data Validation & Preprocessing ]
          (Date parsing, null handling, deduplication)
                           ↓
        [ Chronological Train / Test Split Strategy ]
         (Zero future leakage, rolling/lag feature safety)
                           ↓
              [ Feature Engineering Engine ]
        (Lags, rolling stats, calendar & business features)
                           ↓
        ┌──────────────────┴──────────────────┐
        ▼                                     ▼
  [ Baseline Model ]                  [ ML Demand Model ]
  (7D Moving Average)             (HistGradientBoosting / RF)
        └──────────────────┬──────────────────┘
                           ↓
        [ Model Evaluation & Metric Comparison ]
                     (MAE, RMSE, R²)
                           ↓
        [ Inventory Risk & Demand Shock Engine ]
      (Demand Gap, Risk Score 0-100, Shock Detection)
                           ↓
        [ Smart Reorder Advisor & What-If Simulator ]
   (Safety Buffer, Reorder Quantity, Real-time Simulation)
                           ↓
    [ Streamlit UI - Restrained, Flat, High-Contrast UI ]
```

---

## 4. Differentiating Features

### Feature 1: What-If Inventory Simulator
Allows inventory managers to dynamically test demand shocks and supply chain friction:
- **Interactive Controls**: Demand shift slider ($-50\%$ to $+100\%$), stock override, safety buffer multiplier ($0.5\times$ to $2.0\times$), and forecast horizon.
- **Instant Outputs**: Adjusted demand, projected stock balance, potential shortage, dynamic risk status, estimated days to stockout, and recalculated reorder units.

### Feature 2: Statistical Demand Shock Detector
Detects anomalies in recent demand relative to a 30-day baseline using standard deviation $Z$-scores and percentage deviation:
- `UNUSUAL INCREASE`: $Z \ge 2.0$ or $\Delta \ge +35\%$
- `NORMAL`: $-30\% \le \Delta < +35\%$
- `UNUSUAL DECREASE`: $Z \le -2.0$ or $\Delta \le -30\%$

### Feature 3: 0–100 Multi-Factor Inventory Risk Score
A composite scoring index combining 4 operational risk pillars:
$$\text{Risk Score} = 0.45 \cdot S_{\text{coverage}} + 0.20 \cdot S_{\text{trend}} + 0.20 \cdot S_{\text{volatility}} + 0.15 \cdot S_{\text{lead\_time}}$$
- **Categorization**: `CRITICAL` ($\ge 70$), `HIGH RISK` ($45-69$), `WATCH` ($25-44$), `SAFE` ($< 25$).

### Feature 4: Demand Trend Engine
Extracts normalized linear regression slopes and segment averages across historical windows to classify product trajectories as `INCREASING`, `STABLE`, or `DECREASING`.

### Feature 5: Smart Reorder Advisor
Provides transparent, auditable procurement recommendations:
$$\text{Safety Buffer } (SS) = Z_{\alpha} \times \sigma_{\text{daily demand}} \times \sqrt{\text{Lead Time Days}}$$
$$\text{Recommended Target Inventory} = \text{Forecasted Demand} + SS$$
$$\text{Recommended Order Quantity } (Q) = \max(0, \text{Target} - \text{Current Stock})$$

---

## 5. Dataset & Ingestion

1. **Curated Multi-Category Benchmark (`data/retail_inventory_history.csv`)**:
   - 12 distinct retail SKUs across Electronics, Apparel, Home & Kitchen, Health, and Groceries.
   - 540 days of daily transactions with authentic weekly seasonality, holiday spikes, price changes, promotional events, and realistic demand shocks.
2. **Custom CSV / Excel Ingestion**:
   - Automatic column matching using fuzzy keyword aliases (`sales`, `quantity`, `demand`, `stock`, `inventory`, `lead_time`, `date`).
   - Diagnostic validation report showing row counts, date ranges, null checks, and mapped schema.

---

## 6. Data Preprocessing & Validation

- **Date Standardization**: Enforces `datetime64[ns]` sorting and regular daily interval indexing.
- **Missing Value Handling**: Forward-fills inventory state, back-fills initial lags, and imputes zero sales for non-trading intervals.
- **Categorical & Numeric Sanity**: Positive value clamping ($\text{Sales} \ge 0$, $\text{Stock} \ge 0$, $\text{Lead Time} \ge 1$).

---

## 7. Feature Engineering & Anti-Leakage Guarantee

All features are strictly computed with a `shift(1)` backward lag:
- **Temporal Features**: `DayOfWeek`, `Month`, `Quarter`, `DayOfMonth`, `IsWeekend`.
- **Lag Features**: `Lag_1`, `Lag_7`, `Lag_14` (prior observed demand only).
- **Rolling Statistics**: `Rolling_Mean_7`, `Rolling_Mean_14`, `Rolling_Std_7` (historical moving velocity and volatility).
- **Business Predictors**: `Promotion_Active`, `Unit_Price`.

---

## 8. Train / Test Strategy

- **Strict Chronological Splitting**: 80% historical training window, 20% holdout test window.
- **Zero Lookahead**: Transformers and models are fitted exclusively on training timestamps, guaranteeing true out-of-time evaluation integrity.

---

## 9. Predictive Models & Evaluation

| Model | Technique | Strengths |
| :--- | :--- | :--- |
| **Model 1 (Baseline)** | 7-Day Moving Average / Naive | Fast, interpretable reference benchmark |
| **Model 2 (Production ML)** | `HistGradientBoostingRegressor` | Non-linear tree boosting, handles promotions & interactions |

### True Holdout Evaluation Metrics
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Squared Error)
- **$R^2$** (Coefficient of Determination)
- **Safe MAPE** (Zero-safe mean percentage error)

---

## 10. Visual Design & UI Standards

- **Warm Neutral Background**: `#F8F9FA` warm off-white.
- **Typography**: System font stack (`system-ui, -apple-system, Segoe UI, Roboto, sans-serif`).
- **Color Discipline**:
  - Restrained Navy Accent (`#1E3A8A`)
  - Status Indicators: Safe (`#15803D`), Watch (`#D97706`), High Risk (`#EA580C`), Critical (`#DC2626`).
- **Forbidden UI Exclusions**: **Zero gradients**, zero neon, zero purple-black dark mode, zero emoji UI, zero liquid glass, zero floating card clutter.

---

## 11. Project Structure

```
stock-guardian-ai/
├── app.py                         # Main Streamlit dashboard application
├── requirements.txt               # Dependencies
├── README.md                      # Documentation
├── data/
│   ├── dataset_generator.py       # Benchmark dataset generator
│   └── retail_inventory_history.csv # Benchmark dataset
├── preprocessing/
│   ├── data_loader.py             # Schema auto-detection & file parser
│   └── preprocessor.py            # Time series alignment & gap filler
├── forecasting/
│   ├── feature_engineering.py     # Anti-leakage lag & rolling features
│   └── time_splitter.py           # Chronological time splitter
├── models/
│   ├── baseline.py                # Moving average baseline model
│   ├── demand_model.py            # HistGradientBoosting / ML forecaster
│   └── evaluation.py              # MAE, RMSE, R2, Safe MAPE metrics
├── inventory/
│   ├── risk_engine.py             # 0-100 Risk score, shock detector, trends
│   └── reorder_advisor.py         # Lead-time safety stock & reorder plans
├── simulator/
│   └── what_if.py                 # Real-time What-If scenario engine
├── visualization/
│   ├── charts.py                  # Flat, high-contrast Plotly chart engines
│   └── styles.py                  # Custom CSS design system
└── tests/
    ├── test_pipeline.py           # Unit tests
    └── test_e2e_scenarios.py      # E2E scenario test runner
```

---

## 12. Installation & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.13.5)

### Quick Start
```bash
# 1. Clone or navigate to the project directory
cd "STOCK GUARDIAN AI"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate benchmark dataset (if not already present)
python data/dataset_generator.py

# 4. Run automated test suite
python -m pytest -v

# 5. Launch the Streamlit application
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 13. Step-by-Step Hackathon Demo

1. **Open Dashboard**: View KPI cards, portfolio stockout risks, and statistical demand shock alerts.
2. **Inspect Priority Table**: Review the **Products Requiring Attention** table sorted by Risk Score.
3. **Demand Forecast Drilldown**: Click Tab 2, select a product (e.g. *Performance Running Shoes Pro*), and inspect the 14-day ML forecast timeline and top feature drivers.
4. **Audit Reorder Recommendation**: Click Tab 3, review the safety buffer calculation, and expand the **"How is this calculated?"** transparent mathematical derivation.
5. **Interactive What-If Simulation**: Click Tab 4, select a product, click the **"+20% Demand Surge"** button, and watch the system dynamically recalculate the potential shortage, stockout timeline, and adjusted reorder units.
6. **Model Verification**: Click Tab 5 to verify the chronological 80/20 train/test methodology and inspect true holdout MAE and RMSE improvements.

---

## 14. Legal & Compliance

- **Draft Notice**: Terms of Service and Privacy Policy are provided in Tab 7 and marked **`[ DRAFT FOR REVIEW ]`**.
- **Data Privacy**: All data processing, model training, and simulation calculations execute entirely in-memory on the local instance. No data is transmitted externally.

---

## 15. Limitations & Future Roadmap

- **Multi-Echelon Warehousing**: Future releases will support multi-location warehouse routing and cross-depot balancing.
- **Supplier Volatility Modeling**: Incorporating stochastic supplier lead-time distributions alongside demand variance.
- **Automated Purchase Order Export**: Direct webhook integration into SAP, NetSuite, and Shopify inventory APIs.
