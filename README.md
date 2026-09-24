# STOCK GUARDIAN AI

> **"Predict demand. Prevent stock-outs. Make smarter inventory decisions."**

Stock Guardian AI is a high-precision, full-stack inventory intelligence and demand forecasting platform developed for **PS-08: Inventory Demand Prediction**. It bridges the gap between predictive machine learning and actionable procurement by translating historical sales and inventory trends into verified forecasts, multi-factor stockout risks, lead-time-aware reorder recommendations, and interactive What-If scenario simulations.

---

## 🌟 Key Highlights

- **Full-Stack Architecture**: React 19 + TypeScript frontend with a high-performance Python FastAPI backend.
- **Zero-Fabrication Supervised ML**: Real models (`RandomForestRegressor` and `HistGradientBoostingRegressor`) evaluated against a naive 7-day rolling average baseline.
- **Anti-Leakage Chronological Validation**: 80/20 out-of-time chronological partitioning with strictly backward-lagged features ($t-1$).
- **Statistical Demand Shock Detection**: Z-Score and percentage deviation anomaly detection against a 30-day baseline.
- **0–100 Multi-Factor Risk Scoring**: Actionable risk classification (`CRITICAL`, `HIGH RISK`, `WATCH`, `SAFE`) combining coverage deficit, trend acceleration, demand volatility, and lead time exposure.
- **Scientifically Derived Reorder Plans**: $Z$-score service level safety buffers ($90\%, 95\%, 99\%$) with step-by-step mathematical formulas.
- **Real-Time What-If Simulator**: Dynamic stress-testing of demand surges, supply shocks, and buffer multipliers.
- **Universal CSV / Excel Ingestion**: Intelligent column mapping with auto-detection for custom merchant datasets.

---

## 🏗️ Architecture & Workflow

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA INGESTION LAYER                           │
│  • Curated Retail Benchmark (12 SKUs, 540 Days)                        │
│  • Custom CSV / Excel Upload with Intelligent Auto-Column Mapping      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   PREPROCESSING & DATA INTEGRITY                       │
│  • DateTime alignment, zero-sales imputation, continuous daily grid    │
│  • Strict Chronological Split: 80% Train / 20% Holdout Test            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 FEATURE ENGINEERING & ANTI-LEAKAGE                     │
│  • Backward Lags (t-1, t-7, t-14), Rolling Stats (7D/14D Mean & Std)   │
│  • Calendar Signals (DayOfWeek, Month, IsWeekend), Business Predictors │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
┌───────────────────────────────────┐ ┌───────────────────────────────────┐
│          BASELINE MODEL           │ │         SUPERVISED ML           │
│  • 7-Day Moving Average           │ │  • Random Forest Regressor        │
│  • Naive rolling historical mean  │ │  • HistGradientBoostingRegressor  │
└─────────────────┬─────────────────┘ └─────────────────┬─────────────────┘
                  └─────────────────┬─────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  MODEL EVALUATION & BENCHMARKING                       │
│  • Holdout Metrics: MAE, RMSE, R² Score, Zero-Safe MAPE                │
│  • Head-to-Head Comparison Table & Test Set Alignment Visualizer       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               INVENTORY RISK & REORDER DECISION ENGINE                 │
│  • 0-100 Risk Scoring (Coverage + Trend + Volatility + Lead Time)      │
│  • Statistical Demand Shock Detection (Z-score >= 2.0 or Delta >= 35%) │
│  • Safety Stock Buffer: SS = Z * σ_daily * sqrt(LeadTime)              │
│  • Recommended Order Quantity = max(0, Target Stock - Current Stock)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     INTERACTIVE USER INTERFACE                         │
│  • Modern React 19 + TypeScript SPA (Vite, Recharts, Lucide Icons)     │
│  • High-performance FastAPI REST API with SPA fallback                 │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🧮 Mathematical & Algorithmic Formulations

### 1. Safety Buffer & Reorder Point Formulation
$$\text{Safety Buffer } (SS) = Z_{\alpha} \times \sigma_{\text{daily demand}} \times \sqrt{\text{Lead Time Days}}$$
$$\text{Recommended Target Inventory} = \text{Forecasted Demand} + SS$$
$$\text{Recommended Order Quantity } (Q) = \max(0, \text{Recommended Target Inventory} - \text{Current Stock})$$

*Where $Z_{\alpha} = 1.645$ for $95\%$ Service Level ($1.282$ for $90\%$, $2.326$ for $99\%$).*

### 2. Multi-Factor 0–100 Inventory Risk Score
$$\text{Risk Score} = 0.45 \cdot S_{\text{coverage}} + 0.20 \cdot S_{\text{trend}} + 0.20 \cdot S_{\text{volatility}} + 0.15 \cdot S_{\text{lead\_time}}$$

- **Coverage Deficit ($S_{\text{coverage}}$)**: Measures severity of potential stockout based on $\frac{\text{Current Stock}}{\text{Predicted Demand}}$.
- **Trend Acceleration ($S_{\text{trend}}$)**: Evaluates demand surge velocity from linear slope.
- **Demand Volatility ($S_{\text{volatility}}$)**: Coefficient of variation ($\text{CV} = \frac{\sigma}{\mu}$).
- **Lead Time Exposure ($S_{\text{lead\_time}}$)**: Supply chain replenishment delay factor.

**Classification**:
- `CRITICAL` ($\ge 70$): Immediate stockout risk; place purchase order now.
- `HIGH RISK` ($45 - 69$): Vulnerable stock levels; buffer deficit.
- `WATCH` ($25 - 44$): Adequate inventory; monitor demand trends.
- `SAFE` ($< 25$): Healthy buffer; no replenishment required.

### 3. Statistical Demand Shock Detection
$$Z = \frac{\mu_{\text{recent 7d}} - \mu_{\text{baseline 30d}}}{\sigma_{\text{baseline 30d}} + \epsilon}, \quad \Delta = \frac{\mu_{\text{recent}} - \mu_{\text{baseline}}}{\mu_{\text{baseline}} + \epsilon} \times 100\%$$

- **Unusual Surge**: $Z \ge 2.0$ or $\Delta \ge +35\%$
- **Normal Range**: $-30\% \le \Delta < +35\%$
- **Unusual Drop**: $Z \le -2.0$ or $\Delta \le -30\%$

---

## 💻 Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite 6, Recharts, Lucide React, CSS3 Design Tokens |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, Pydantic |
| **Machine Learning** | Scikit-Learn (`RandomForestRegressor`, `HistGradientBoostingRegressor`, `LinearRegression`), NumPy, Pandas |
| **Testing** | Pytest, End-to-End Scenario Runners |

---

## 📁 Project Structure

```
STOCK GUARDIAN AI/
├── data/
│   ├── dataset_generator.py         # 12-SKU realistic benchmark generator
│   └── retail_inventory_history.csv # Curated 540-day retail dataset
├── forecasting/
│   ├── feature_engineering.py       # Anti-leakage backward lag & rolling transforms
│   └── time_splitter.py             # Strict 80/20 chronological time splitter
├── frontend/
│   ├── dist/                        # Compiled production SPA assets
│   ├── src/
│   │   ├── api/client.ts            # Axios REST API client
│   │   ├── components/              # Reusable UI components (Header, MetricCard, Modals)
│   │   ├── pages/                   # Application Views (Overview, Forecast, Risk, Reorder, etc.)
│   │   ├── types/                   # TypeScript schemas & interfaces
│   │   ├── App.tsx                  # Core app router & layout
│   │   └── main.tsx                 # Entrypoint with ErrorBoundary
│   ├── package.json                 # Frontend dependencies & build scripts
│   └── vite.config.ts               # Vite configuration with API proxy
├── inventory/
│   ├── reorder_advisor.py           # Safety stock & reorder calculation engine
│   └── risk_engine.py               # 0-100 Risk score, shock detection, trend analysis
├── models/
│   ├── baseline.py                  # 7-day moving average baseline model
│   ├── demand_model.py              # Supervised ML regression & recursive forecaster
│   └── evaluation.py                # MAE, RMSE, R², Safe MAPE evaluator
├── preprocessing/
│   ├── data_loader.py               # Smart CSV/Excel reader & fuzzy column matcher
│   └── preprocessor.py              # Time series regularizer & metadata builder
├── simulator/
│   └── what_if.py                   # Real-time What-If scenario simulation engine
├── tests/
│   ├── test_pipeline.py             # Unit tests for ML & inventory engines
│   └── test_e2e_scenarios.py        # End-to-end integration test scenarios
├── sample_test_inventory.csv        # 1,300-row sample CSV for custom test uploads
├── server.py                        # FastAPI unified backend & SPA host
├── requirements.txt                 # Python dependencies
└── README.md                        # Documentation
```

---

## 🚀 Installation & Running

### 1. Prerequisites
- Python 3.10 or higher
- Node.js 18+ (for frontend development)

### 2. Backend Setup
```powershell
# Navigate to the project directory
cd "d:\STOCK GUARDIAN AI"

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup (Optional for Development)
```powershell
cd frontend
npm install
npm run build
cd ..
```

### 4. Run the Application
Start the unified application (FastAPI serves both the API and the React SPA on a single port):

```powershell
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

Open your browser at:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

*(For live hot-reloading frontend development, run `npm run dev` in `frontend/` and access `http://127.0.0.1:5173/`).*

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/health` | `GET` | Service status, product count, and active configuration |
| `/api/v1/dashboard/summary` | `GET` | Portfolio KPIs, critical stockout alerts, demand shock list |
| `/api/v1/products` | `GET` | List all SKUs with current stock, risk level, and demand stats |
| `/api/v1/products/{id}/forecast` | `GET` | 14-day daily forecast breakdown, history, and feature importances |
| `/api/v1/products/{id}/risk` | `GET` | Multi-factor risk breakdown, component scores, and reorder plan |
| `/api/v1/models/performance` | `GET` | Holdout evaluation metrics (MAE, RMSE, R²) vs. Baseline model |
| `/api/v1/simulator/what-if` | `POST` | Dynamic scenario simulation (demand shifts, inventory overrides) |
| `/api/v1/models/train` | `POST` | Trigger model retraining across custom horizon & model architecture |
| `/api/v1/data/upload` | `POST` | Upload custom CSV/Excel with automatic validation and schema detection |
| `/api/v1/data/map-columns` | `POST` | Apply manual column mappings for non-standard merchant datasets |
| `/api/v1/data/load-benchmark` | `POST` | Reset back to the 12-SKU benchmark dataset |

---

## 🧪 Testing with the Sample Dataset

A sample test file [sample_test_inventory.csv](file:///d:/STOCK%20GUARDIAN%20AI/sample_test_inventory.csv) (1,300 rows across 5 products) is included to test all system capabilities:

1. Click **Data Studio** in the navigation bar.
2. Drag and drop [sample_test_inventory.csv](file:///d:/STOCK%20GUARDIAN%20AI/sample_test_inventory.csv) into the upload box.
3. The platform validates columns, parses dates, computes time-series splits, trains ML models, and updates all dashboards in real-time.
4. Test scenarios represented in the sample file:
   - **Critical Stockout Risk**: `SKU-COF-01` (Coffee Beans)
   - **Statistical Demand Shock**: `SKU-SNK-02` (Running Shoes)
   - **Safe Stock Level**: `SKU-KEY-03` (Mechanical Keyboard)
   - **Watchlist Trajectory**: `SKU-OIL-05` (Olive Oil)

---

## 🛡️ Validation & Automated Tests

Run the complete test suite:
```powershell
python -m pytest tests/ -v
```

---

## 📄 License & Compliance

- **Draft Notice**: Terms of Service and Privacy Policy are embedded within the application and marked `[ DRAFT FOR REVIEW ]`.
- **Data Privacy**: All data ingestion, model fitting, and risk calculations run locally in-memory. Zero merchant data is sent to external cloud APIs.
