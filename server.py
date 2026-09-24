import os
import io
import math
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

from preprocessing.data_loader import DataLoader
from preprocessing.preprocessor import DataPreprocessor
from forecasting.time_splitter import ChronologicalTimeSplitter
from forecasting.feature_engineering import FeatureEngineer
from models.baseline import BaselineDemandModel
from models.demand_model import MLDemandModel
from models.evaluation import ModelEvaluator
from inventory.risk_engine import InventoryRiskEngine
from inventory.reorder_advisor import SmartReorderAdvisor
from simulator.what_if import WhatIfSimulator
from data.dataset_generator import generate_benchmark_dataset

app = FastAPI(
    title="Stock Guardian AI API",
    description="REST API for Demand Intelligence, Inventory Risk Engine, and Reorder Planning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BENCHMARK_PATH = os.path.join(os.path.dirname(__file__), "data", "retail_inventory_history.csv")

# In-memory application state
class AppState:
    def __init__(self):
        self.raw_df: Optional[pd.DataFrame] = None
        self.diagnostics: Dict[str, Any] = {}
        self.product_metadata: List[Dict[str, Any]] = []
        self.forecast_horizon_days: int = 14
        self.service_level_target: str = "95%"
        self.model_type: str = "RandomForest"
        self.portfolio_results: List[Dict[str, Any]] = []
        self.is_ready: bool = False
        self.active_source_name: str = "Benchmark Dataset (12 SKUs)"

state = AppState()

def compute_portfolio_analysis(
    df: pd.DataFrame,
    horizon_days: int = 14,
    service_level: str = "95%",
    model_type: str = "RandomForest"
) -> List[Dict[str, Any]]:
    meta_list = DataPreprocessor.get_product_metadata(df)
    results = []

    for meta in meta_list:
        pid = meta["Product_ID"]
        p_df = DataPreprocessor.prepare_product_series(df, product_id=pid)
        
        train_df, test_df, split_meta = ChronologicalTimeSplitter.split(p_df, train_ratio=0.8)
        X_train, y_train, _ = FeatureEngineer.prepare_matrices(train_df)
        X_test, y_test, _ = FeatureEngineer.prepare_matrices(test_df)

        base_model = BaselineDemandModel(window_size=7).fit(y_train)
        base_preds = base_model.predict(X_test)

        ml_model = MLDemandModel(model_type=model_type).fit(X_train, y_train)
        ml_preds = ml_model.predict(X_test)

        comp_df, comp_analysis = ModelEvaluator.compare_models(
            y_test.values, base_preds, ml_preds,
            baseline_name="Baseline (7D MA)",
            ml_name=f"ML ({model_type})"
        )

        future_fc = ml_model.recursive_forecast(
            p_df,
            horizon_days=horizon_days,
            unit_price=meta["Unit_Price"]
        )
        total_predicted_demand = float(future_fc["Forecast_Demand"].sum())

        risk_info = InventoryRiskEngine.calculate_risk_score(
            current_inventory=meta["Current_Stock"],
            predicted_demand=total_predicted_demand,
            historical_series=p_df["Sales_Units"],
            lead_time_days=meta["Lead_Time_Days"]
        )

        shock_info = InventoryRiskEngine.detect_demand_shock(p_df["Sales_Units"])

        reorder_plan = SmartReorderAdvisor.calculate_reorder_plan(
            product_name=meta["Product_Name"],
            current_inventory=meta["Current_Stock"],
            predicted_demand=total_predicted_demand,
            historical_daily_demand=p_df["Sales_Units"],
            lead_time_days=meta["Lead_Time_Days"],
            service_level=service_level,
            unit_cost=meta["Unit_Price"]
        )

        # Convert date column in history and forecast for serialization
        hist_records = []
        for _, row in p_df.sort_values("Date").iterrows():
            hist_records.append({
                "Date": pd.to_datetime(row["Date"]).strftime("%Y-%m-%d"),
                "Sales_Units": float(row["Sales_Units"]),
                "Stock_On_Hand": float(row.get("Stock_On_Hand", 0)),
                "Unit_Price": float(row.get("Unit_Price", 19.99)),
                "Promotion_Active": int(row.get("Promotion_Active", 0))
            })

        fc_records = []
        for _, row in future_fc.iterrows():
            fc_records.append({
                "Date": pd.to_datetime(row["Date"]).strftime("%Y-%m-%d"),
                "Forecast_Demand": float(row["Forecast_Demand"]),
                "Horizon_Day": int(row["Horizon_Day"])
            })

        test_records = []
        for i, (_, row) in enumerate(test_df.iterrows()):
            test_records.append({
                "Date": pd.to_datetime(row["Date"]).strftime("%Y-%m-%d"),
                "Actual": float(row["Sales_Units"]),
                "Baseline_Pred": float(base_preds[i]) if i < len(base_preds) else 0.0,
                "ML_Pred": float(ml_preds[i]) if i < len(ml_preds) else 0.0,
                "Residual_ML": float(row["Sales_Units"] - (ml_preds[i] if i < len(ml_preds) else 0.0))
            })

        results.append({
            "Product_ID": pid,
            "Product_Name": meta["Product_Name"],
            "Category": meta["Category"],
            "Current_Stock": meta["Current_Stock"],
            "Avg_Daily_Demand": meta["Avg_Daily_Demand"],
            "Total_Sales": meta["Total_Sales"],
            "Lead_Time_Days": meta["Lead_Time_Days"],
            "Unit_Price": meta["Unit_Price"],
            "Predicted_Demand": round(total_predicted_demand, 1),
            "Demand_Gap": risk_info["demand_gap"],
            "Risk_Score": risk_info["risk_score"],
            "Risk_Level": risk_info["risk_level"],
            "Action_Code": risk_info["action_code"],
            "Badge_Color": risk_info["badge_color"],
            "Coverage_Ratio": risk_info["coverage_ratio"],
            "Trend": risk_info["trend"],
            "Trend_Pct": risk_info["trend_details"]["pct_change"],
            "Trend_Slope": risk_info["trend_details"]["slope"],
            "Shock_Status": shock_info["shock_status"],
            "Shock_Z": shock_info["z_score"],
            "Shock_Dev_Pct": shock_info["pct_deviation"],
            "Shock_Recent_Mean": shock_info["recent_mean"],
            "Shock_Baseline_Mean": shock_info["baseline_mean"],
            "Safety_Buffer": reorder_plan["safety_buffer"],
            "Recommended_Target_Stock": reorder_plan["recommended_target_inventory"],
            "Recommended_Additional_Stock": reorder_plan["recommended_additional_stock"],
            "Estimated_Capital": reorder_plan["estimated_capital_required"],
            "Days_Of_Supply": reorder_plan["days_of_supply"],
            "Reorder_Plan": reorder_plan,
            "Risk_Info": risk_info,
            "ML_MAE": comp_analysis["ml_metrics"]["MAE"],
            "Base_MAE": comp_analysis["base_metrics"]["MAE"],
            "ML_RMSE": comp_analysis["ml_metrics"]["RMSE"],
            "Base_RMSE": comp_analysis["base_metrics"]["RMSE"],
            "ML_R2": comp_analysis["ml_metrics"]["R2"],
            "Base_R2": comp_analysis["base_metrics"]["R2"],
            "ML_MAPE": comp_analysis["ml_metrics"]["Safe_MAPE"],
            "Base_MAPE": comp_analysis["base_metrics"]["Safe_MAPE"],
            "Feature_Importances": ml_model.feature_importances_,
            "Split_Meta": split_meta,
            "History_Records": hist_records,
            "Forecast_Records": fc_records,
            "Test_Evaluation_Records": test_records
        })

    return results

def init_benchmark():
    if not os.path.exists(BENCHMARK_PATH):
        os.makedirs(os.path.dirname(BENCHMARK_PATH), exist_ok=True)
        generate_benchmark_dataset(output_path=BENCHMARK_PATH)
    
    df, diag = DataLoader.load_file(BENCHMARK_PATH)
    state.raw_df = df
    state.diagnostics = diag
    state.product_metadata = DataPreprocessor.get_product_metadata(df)
    state.portfolio_results = compute_portfolio_analysis(
        df,
        horizon_days=state.forecast_horizon_days,
        service_level=state.service_level_target,
        model_type=state.model_type
    )
    state.is_ready = True
    state.active_source_name = "Curated Benchmark (12 SKUs)"

# Initialize at startup
init_benchmark()

# Pydantic Request Models
class TrainRequest(BaseModel):
    forecast_horizon_days: Optional[int] = 14
    service_level: Optional[str] = "95%"
    model_type: Optional[str] = "RandomForest"

class WhatIfRequest(BaseModel):
    product_id: str
    demand_pct_change: float = 0.0
    current_inventory_override: Optional[float] = None
    safety_buffer_multiplier: float = 1.0

class ColumnMappingRequest(BaseModel):
    custom_mapping: Dict[str, str]

# API Endpoints
@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "service": "Stock Guardian AI Backend",
        "is_ready": state.is_ready,
        "product_count": len(state.product_metadata),
        "active_source": state.active_source_name,
        "forecast_horizon_days": state.forecast_horizon_days,
        "service_level": state.service_level_target
    }

@app.get("/api/v1/dashboard/summary")
def get_dashboard_summary():
    if not state.is_ready or not state.portfolio_results:
        raise HTTPException(status_code=400, detail="No active dataset loaded.")
    
    total_products = len(state.portfolio_results)
    critical_count = sum(1 for p in state.portfolio_results if p["Risk_Level"] == "CRITICAL")
    high_risk_count = sum(1 for p in state.portfolio_results if p["Risk_Level"] == "HIGH RISK")
    watch_count = sum(1 for p in state.portfolio_results if p["Risk_Level"] == "WATCH")
    safe_count = sum(1 for p in state.portfolio_results if p["Risk_Level"] == "SAFE")
    
    total_reorder_units = int(sum(p["Recommended_Additional_Stock"] for p in state.portfolio_results))
    total_reorder_capital = float(sum(p["Estimated_Capital"] for p in state.portfolio_results))
    avg_predicted_demand = round(float(np.mean([p["Predicted_Demand"] for p in state.portfolio_results])), 1)

    # Statistical demand shock alerts
    shock_alerts = []
    for p in state.portfolio_results:
        if p["Shock_Status"] != "NORMAL":
            shock_alerts.append({
                "product_id": p["Product_ID"],
                "product_name": p["Product_Name"],
                "category": p["Category"],
                "shock_status": p["Shock_Status"],
                "z_score": p["Shock_Z"],
                "pct_deviation": p["Shock_Dev_Pct"],
                "recent_mean": p["Shock_Recent_Mean"],
                "baseline_mean": p["Shock_Baseline_Mean"],
                "current_stock": p["Current_Stock"],
                "days_of_supply": p["Days_Of_Supply"]
            })

    # Critical stockout alerts
    critical_alerts = []
    for p in state.portfolio_results:
        if p["Risk_Level"] in ["CRITICAL", "HIGH RISK"]:
            critical_alerts.append({
                "product_id": p["Product_ID"],
                "product_name": p["Product_Name"],
                "risk_level": p["Risk_Level"],
                "risk_score": p["Risk_Score"],
                "current_stock": p["Current_Stock"],
                "predicted_demand": p["Predicted_Demand"],
                "demand_gap": p["Demand_Gap"],
                "reorder_units": p["Recommended_Additional_Stock"],
                "days_of_supply": p["Days_Of_Supply"],
                "action_code": p["Action_Code"]
            })

    # Attention table summary
    products_table = []
    for p in state.portfolio_results:
        products_table.append({
            "product_id": p["Product_ID"],
            "product_name": p["Product_Name"],
            "category": p["Category"],
            "current_stock": p["Current_Stock"],
            "predicted_demand": p["Predicted_Demand"],
            "demand_gap": p["Demand_Gap"],
            "risk_score": p["Risk_Score"],
            "risk_level": p["Risk_Level"],
            "badge_color": p["Badge_Color"],
            "trend": p["Trend"],
            "trend_pct": p["Trend_Pct"],
            "shock_status": p["Shock_Status"],
            "recommended_additional_stock": p["Recommended_Additional_Stock"],
            "days_of_supply": p["Days_Of_Supply"],
            "estimated_capital": p["Estimated_Capital"],
            "lead_time_days": p["Lead_Time_Days"],
            "action_code": p["Action_Code"]
        })

    # Sort attention table by risk score descending by default
    products_table.sort(key=lambda x: x["risk_score"], reverse=True)

    # Categories list
    categories = sorted(list({p["Category"] for p in state.portfolio_results}))

    return {
        "kpis": {
            "total_products": total_products,
            "critical_stockouts": critical_count,
            "high_risk": high_risk_count,
            "watch": watch_count,
            "safe": safe_count,
            "total_reorder_units": total_reorder_units,
            "total_reorder_capital": round(total_reorder_capital, 2),
            "avg_predicted_demand": avg_predicted_demand,
            "forecast_horizon_days": state.forecast_horizon_days,
            "service_level": state.service_level_target,
            "active_dataset": state.active_source_name
        },
        "shock_alerts": shock_alerts,
        "critical_alerts": critical_alerts,
        "categories": categories,
        "products_table": products_table,
        "diagnostics": {
            "cleaned_rows": state.diagnostics.get("cleaned_rows", 0),
            "product_count": state.diagnostics.get("product_count", 0),
            "date_range": state.diagnostics.get("date_range", ["N/A", "N/A"])
        }
    }

@app.get("/api/v1/products")
def get_products():
    if not state.is_ready:
        raise HTTPException(status_code=400, detail="No dataset loaded.")
    
    return [
        {
            "product_id": p["Product_ID"],
            "product_name": p["Product_Name"],
            "category": p["Category"],
            "current_stock": p["Current_Stock"],
            "avg_daily_demand": p["Avg_Daily_Demand"],
            "lead_time_days": p["Lead_Time_Days"],
            "unit_price": p["Unit_Price"],
            "risk_level": p["Risk_Level"],
            "risk_score": p["Risk_Score"],
            "predicted_demand": p["Predicted_Demand"],
            "demand_gap": p["Demand_Gap"],
            "badge_color": p["Badge_Color"],
            "trend": p["Trend"],
            "shock_status": p["Shock_Status"],
            "reorder_units": p["Recommended_Additional_Stock"]
        }
        for p in state.portfolio_results
    ]

@app.get("/api/v1/products/{product_id}/forecast")
def get_product_forecast(product_id: str):
    match = next((p for p in state.portfolio_results if p["Product_ID"] == product_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found.")

    return {
        "product_id": match["Product_ID"],
        "product_name": match["Product_Name"],
        "category": match["Category"],
        "current_stock": match["Current_Stock"],
        "lead_time_days": match["Lead_Time_Days"],
        "unit_price": match["Unit_Price"],
        "forecast_horizon_days": state.forecast_horizon_days,
        "total_predicted_demand": match["Predicted_Demand"],
        "avg_daily_forecast": round(match["Predicted_Demand"] / max(1, state.forecast_horizon_days), 1),
        "history": match["History_Records"],
        "forecast_breakdown": match["Forecast_Records"],
        "feature_importances": match["Feature_Importances"]
    }

@app.get("/api/v1/products/{product_id}/risk")
def get_product_risk(product_id: str):
    match = next((p for p in state.portfolio_results if p["Product_ID"] == product_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found.")

    return {
        "product_id": match["Product_ID"],
        "product_name": match["Product_Name"],
        "risk_info": match["Risk_Info"],
        "reorder_plan": match["Reorder_Plan"],
        "shock_status": match["Shock_Status"],
        "shock_z": match["Shock_Z"],
        "shock_dev_pct": match["Shock_Dev_Pct"]
    }

@app.get("/api/v1/products/{product_id}/trend")
def get_product_trend(product_id: str):
    match = next((p for p in state.portfolio_results if p["Product_ID"] == product_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found.")

    return {
        "product_id": match["Product_ID"],
        "product_name": match["Product_Name"],
        "trend": match["Trend"],
        "trend_pct": match["Trend_Pct"],
        "trend_slope": match["Trend_Slope"],
        "shock_status": match["Shock_Status"],
        "shock_z": match["Shock_Z"]
    }

@app.get("/api/v1/inventory/alerts")
def get_inventory_alerts():
    if not state.is_ready:
        return {"alerts": [], "shocks": []}

    criticals = [
        p for p in state.portfolio_results
        if p["Risk_Level"] in ["CRITICAL", "HIGH RISK"]
    ]
    shocks = [
        p for p in state.portfolio_results
        if p["Shock_Status"] != "NORMAL"
    ]

    return {
        "critical_count": len(criticals),
        "shock_count": len(shocks),
        "critical_alerts": [
            {
                "product_id": p["Product_ID"],
                "product_name": p["Product_Name"],
                "risk_level": p["Risk_Level"],
                "risk_score": p["Risk_Score"],
                "current_stock": p["Current_Stock"],
                "predicted_demand": p["Predicted_Demand"],
                "days_of_supply": p["Days_Of_Supply"],
                "action_code": p["Action_Code"],
                "reorder_units": p["Recommended_Additional_Stock"]
            }
            for p in criticals
        ],
        "shock_alerts": [
            {
                "product_id": p["Product_ID"],
                "product_name": p["Product_Name"],
                "shock_status": p["Shock_Status"],
                "z_score": p["Shock_Z"],
                "pct_deviation": p["Shock_Dev_Pct"]
            }
            for p in shocks
        ]
    }

@app.post("/api/v1/simulator/what-if")
def simulate_scenario(req: WhatIfRequest):
    match = next((p for p in state.portfolio_results if p["Product_ID"] == req.product_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Product {req.product_id} not found.")

    history_sales = pd.Series([r["Sales_Units"] for r in match["History_Records"]])
    
    sim_result = WhatIfSimulator.simulate_scenario(
        base_predicted_demand=match["Predicted_Demand"],
        current_inventory=match["Current_Stock"],
        historical_daily_demand=history_sales,
        demand_pct_change=req.demand_pct_change,
        inventory_override=req.current_inventory_override,
        safety_multiplier=req.safety_buffer_multiplier,
        lead_time_days=match["Lead_Time_Days"],
        forecast_horizon_days=state.forecast_horizon_days
    )

    return {
        "product_id": match["Product_ID"],
        "product_name": match["Product_Name"],
        "unit_price": match["Unit_Price"],
        "simulation": sim_result
    }

@app.get("/api/v1/models/performance")
def get_model_performance(product_id: Optional[str] = Query(None)):
    if not state.is_ready or not state.portfolio_results:
        raise HTTPException(status_code=400, detail="No dataset loaded.")

    if product_id:
        target = next((p for p in state.portfolio_results if p["Product_ID"] == product_id), None)
        if not target:
            target = state.portfolio_results[0]
    else:
        target = state.portfolio_results[0]

    # Global portfolio metrics
    avg_ml_mae = round(float(np.mean([p["ML_MAE"] for p in state.portfolio_results])), 2)
    avg_base_mae = round(float(np.mean([p["Base_MAE"] for p in state.portfolio_results])), 2)
    avg_ml_rmse = round(float(np.mean([p["ML_RMSE"] for p in state.portfolio_results])), 2)
    avg_base_rmse = round(float(np.mean([p["Base_RMSE"] for p in state.portfolio_results])), 2)
    avg_ml_r2 = round(float(np.mean([p["ML_R2"] for p in state.portfolio_results])), 3)

    return {
        "selected_product": {
            "product_id": target["Product_ID"],
            "product_name": target["Product_Name"],
            "ml_mae": target["ML_MAE"],
            "base_mae": target["Base_MAE"],
            "ml_rmse": target["ML_RMSE"],
            "base_rmse": target["Base_RMSE"],
            "ml_r2": target["ML_R2"],
            "base_r2": target["Base_R2"],
            "ml_mape": target["ML_MAPE"],
            "base_mape": target["Base_MAPE"],
            "split_meta": target["Split_Meta"],
            "feature_importances": target["Feature_Importances"],
            "test_evaluation_records": target["Test_Evaluation_Records"]
        },
        "portfolio_aggregate": {
            "avg_ml_mae": avg_ml_mae,
            "avg_base_mae": avg_base_mae,
            "avg_ml_rmse": avg_ml_rmse,
            "avg_base_rmse": avg_base_rmse,
            "avg_ml_r2": avg_ml_r2,
            "mae_improvement_pct": round(((avg_base_mae - avg_ml_mae) / (avg_base_mae + 1e-5)) * 100.0, 1),
            "model_type": state.model_type,
            "total_skus_evaluated": len(state.portfolio_results)
        }
    }

@app.post("/api/v1/models/train")
def train_models(req: TrainRequest):
    if state.raw_df is None:
        raise HTTPException(status_code=400, detail="No active dataset available.")

    state.forecast_horizon_days = req.forecast_horizon_days or 14
    state.service_level_target = req.service_level or "95%"
    state.model_type = req.model_type or "RandomForest"

    state.portfolio_results = compute_portfolio_analysis(
        state.raw_df,
        horizon_days=state.forecast_horizon_days,
        service_level=state.service_level_target,
        model_type=state.model_type
    )

    return {
        "status": "success",
        "message": f"Successfully re-trained models with {state.model_type} over {state.forecast_horizon_days}-day horizon.",
        "forecast_horizon_days": state.forecast_horizon_days,
        "service_level": state.service_level_target,
        "model_type": state.model_type,
        "product_count": len(state.portfolio_results)
    }

@app.get("/api/v1/data/summary")
def get_data_summary():
    if state.raw_df is None:
        raise HTTPException(status_code=400, detail="No active dataset.")

    # Convert preview records
    preview_df = state.raw_df.head(100).copy()
    if "Date" in preview_df.columns:
        preview_df["Date"] = pd.to_datetime(preview_df["Date"]).dt.strftime("%Y-%m-%d")

    records = preview_df.replace({np.nan: None}).to_dict(orient="records")

    return {
        "active_source": state.active_source_name,
        "total_rows": state.diagnostics.get("total_rows", len(state.raw_df)),
        "cleaned_rows": state.diagnostics.get("cleaned_rows", len(state.raw_df)),
        "total_cols": state.diagnostics.get("total_cols", len(state.raw_df.columns)),
        "product_count": state.diagnostics.get("product_count", state.raw_df["Product_ID"].nunique() if "Product_ID" in state.raw_df else 0),
        "categories": state.diagnostics.get("categories", sorted(state.raw_df["Category"].unique().tolist()) if "Category" in state.raw_df else []),
        "date_range": state.diagnostics.get("date_range", ["N/A", "N/A"]),
        "detected_mapping": state.diagnostics.get("detected_mapping", {}),
        "missing_required": state.diagnostics.get("missing_required", []),
        "null_counts": state.diagnostics.get("null_counts", {}),
        "columns": list(state.raw_df.columns),
        "preview_records": records
    }

@app.post("/api/v1/data/upload")
async def upload_dataset(file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename.lower() if file.filename else "uploaded.csv"
    
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a CSV or Excel file.")

        clean_df, diag = DataLoader.validate_and_standardize(df)

        if not diag["is_valid"]:
            return {
                "status": "mapping_required",
                "message": f"Uploaded file is missing required fields: {', '.join(diag['missing_required'])}. Please map columns manually.",
                "diagnostics": diag,
                "available_columns": list(df.columns),
                "total_rows": len(df)
            }

        state.raw_df = clean_df
        state.diagnostics = diag
        state.product_metadata = DataPreprocessor.get_product_metadata(clean_df)
        state.active_source_name = f"Uploaded File ({file.filename})"
        state.portfolio_results = compute_portfolio_analysis(
            clean_df,
            horizon_days=state.forecast_horizon_days,
            service_level=state.service_level_target,
            model_type=state.model_type
        )
        state.is_ready = True

        return {
            "status": "success",
            "message": f"Successfully parsed and trained on {file.filename}.",
            "diagnostics": diag,
            "product_count": len(state.product_metadata)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process uploaded file: {str(e)}")

@app.post("/api/v1/data/map-columns")
def map_custom_columns(req: ColumnMappingRequest):
    if state.raw_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded to map.")

    try:
        clean_df, diag = DataLoader.validate_and_standardize(state.raw_df, custom_mapping=req.custom_mapping)
        if not diag["is_valid"]:
            raise HTTPException(status_code=400, detail=f"Mapping still missing required columns: {', '.join(diag['missing_required'])}")

        state.raw_df = clean_df
        state.diagnostics = diag
        state.product_metadata = DataPreprocessor.get_product_metadata(clean_df)
        state.portfolio_results = compute_portfolio_analysis(
            clean_df,
            horizon_days=state.forecast_horizon_days,
            service_level=state.service_level_target,
            model_type=state.model_type
        )
        state.is_ready = True

        return {
            "status": "success",
            "message": "Custom column mappings applied successfully.",
            "diagnostics": diag,
            "product_count": len(state.product_metadata)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error applying column mapping: {str(e)}")

@app.post("/api/v1/data/load-benchmark")
def load_benchmark():
    init_benchmark()
    return {
        "status": "success",
        "message": "Loaded 12-SKU retail benchmark dataset.",
        "diagnostics": state.diagnostics,
        "product_count": len(state.product_metadata)
    }

# Serve React SPA if dist exists
DIST_PATH = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(DIST_PATH):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    assets_path = os.path.join(DIST_PATH, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        file_path = os.path.join(DIST_PATH, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(DIST_PATH, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
