import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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

def run_sample_dataset_test():
    print("=" * 80)
    print("STOCK GUARDIAN AI — COMPLETE SAMPLE DATASET VERIFICATION TEST")
    print("=" * 80)

    dataset_path = "data/retail_inventory_history.csv"
    if not os.path.exists(dataset_path):
        from data.dataset_generator import generate_benchmark_dataset
        generate_benchmark_dataset(output_path=dataset_path)

    print("\n[STEP 1] Ingesting & Validating Sample Dataset...")
    df, diagnostics = DataLoader.load_file(dataset_path)
    
    print(f" • Total Rows Loaded: {diagnostics['cleaned_rows']:,}")
    print(f" • Total Columns: {diagnostics['total_cols']}")
    print(f" • Unique Products (SKUs): {diagnostics['product_count']}")
    print(f" • Categories: {', '.join(diagnostics['categories'])}")
    print(f" • Historical Date Range: {diagnostics['date_range'][0]} to {diagnostics['date_range'][1]}")
    print(f" • Schema Integrity Validation: {'PASSED' if diagnostics['is_valid'] else 'FAILED'}")
    
    assert diagnostics["is_valid"] is True
    assert diagnostics["product_count"] == 12

    print("\n[STEP 2] Extracting Product Metadata & Portfolios...")
    products = DataPreprocessor.get_product_metadata(df)
    
    prod_table = []
    for p in products:
        prod_table.append({
            "SKU": p["Product_ID"],
            "Product Name": p["Product_Name"][:28],
            "Category": p["Category"],
            "Current Stock": p["Current_Stock"],
            "Avg Daily Demand": p["Avg_Daily_Demand"],
            "Lead Time": f"{p['Lead_Time_Days']}d",
            "Price": f"${p['Unit_Price']:.2f}"
        })
    print(pd.DataFrame(prod_table).to_string(index=False))

    print("\n[STEP 3] Running Chronological Split, Anti-Leakage Feature Engineering & Model Evaluation...")
    horizon_days = 14
    evaluation_results = []
    
    for p in products:
        pid = p["Product_ID"]
        p_df = DataPreprocessor.prepare_product_series(df, product_id=pid)
        
        train_df, test_df, split_meta = ChronologicalTimeSplitter.split(p_df, train_ratio=0.8)
        assert split_meta["leakage_check_passed"] is True, f"Leakage check failed for {pid}"
        
        X_train, y_train, feat_names = FeatureEngineer.prepare_matrices(train_df)
        X_test, y_test, _ = FeatureEngineer.prepare_matrices(test_df)
        
        base_model = BaselineDemandModel(window_size=7).fit(y_train)
        base_preds = base_model.predict(X_test)
        
        ml_model = MLDemandModel(model_type="RandomForest").fit(X_train, y_train)
        ml_preds = ml_model.predict(X_test)
        
        comp_df, analysis = ModelEvaluator.compare_models(y_test.values, base_preds, ml_preds)
        
        future_fc = ml_model.recursive_forecast(p_df, horizon_days=horizon_days, unit_price=p["Unit_Price"])
        pred_demand_14d = float(future_fc["Forecast_Demand"].sum())
        
        risk_info = InventoryRiskEngine.calculate_risk_score(
            current_inventory=p["Current_Stock"],
            predicted_demand=pred_demand_14d,
            historical_series=p_df["Sales_Units"],
            lead_time_days=p["Lead_Time_Days"]
        )
        
        shock_info = InventoryRiskEngine.detect_demand_shock(p_df["Sales_Units"])
        
        reorder = SmartReorderAdvisor.calculate_reorder_plan(
            product_name=p["Product_Name"],
            current_inventory=p["Current_Stock"],
            predicted_demand=pred_demand_14d,
            historical_daily_demand=p_df["Sales_Units"],
            lead_time_days=p["Lead_Time_Days"],
            service_level="95%",
            unit_cost=p["Unit_Price"]
        )
        
        evaluation_results.append({
            "SKU": pid,
            "Product": p["Product_Name"][:22],
            "Current Stock": p["Current_Stock"],
            "14D Forecast": round(pred_demand_14d, 1),
            "Gap": round(risk_info["demand_gap"], 1),
            "Risk Score": f"{risk_info['risk_score']}/100",
            "Risk Level": risk_info["risk_level"],
            "Shock Status": shock_info["shock_status"],
            "Trend": risk_info["trend"],
            "Reorder Units": reorder["recommended_additional_stock"],
            "Base MAE": analysis["base_metrics"]["MAE"],
            "ML MAE": analysis["ml_metrics"]["MAE"],
            "ML R²": analysis["ml_metrics"]["R2"]
        })
        
    eval_df = pd.DataFrame(evaluation_results)
    print("\n" + eval_df.to_string(index=False))

    print("\n[STEP 4] Deep-Dive on Specific Sample Products:")
    
    shock_sku = next(p for p in evaluation_results if p["Shock Status"] == "UNUSUAL INCREASE")
    print(f"\n • Product with Statistical Demand Shock: {shock_sku['SKU']} ({shock_sku['Product']})")
    print(f"   - Shock Status: {shock_sku['Shock Status']}")
    print(f"   - Current Physical Stock: {shock_sku['Current Stock']} units")
    print(f"   - 14-Day Expected Demand: {shock_sku['14D Forecast']} units")
    print(f"   - Risk Score: {shock_sku['Risk Score']} ({shock_sku['Risk Level']})")
    print(f"   - Actionable Reorder Required: {shock_sku['Reorder Units']} units immediately")

    safe_sku = next(p for p in evaluation_results if p["Risk Level"] == "SAFE")
    print(f"\n • Well-Stocked / Safe Product: {safe_sku['SKU']} ({safe_sku['Product']})")
    print(f"   - Current Physical Stock: {safe_sku['Current Stock']} units")
    print(f"   - 14-Day Expected Demand: {safe_sku['14D Forecast']} units")
    print(f"   - Risk Score: {safe_sku['Risk Score']} ({safe_sku['Risk Level']})")
    print(f"   - Reorder Required: {safe_sku['Reorder Units']} units (Stock is sufficient)")

    print("\n[STEP 5] Testing What-If Simulator on Sample SKU:")
    test_sku_id = "SKU-ELEC-101"
    p_df = DataPreprocessor.prepare_product_series(df, product_id=test_sku_id)
    ml_model = MLDemandModel(model_type="RandomForest").fit(
        FeatureEngineer.prepare_matrices(p_df)[0],
        FeatureEngineer.prepare_matrices(p_df)[1]
    )
    base_14d_demand = float(ml_model.recursive_forecast(p_df, 14)["Forecast_Demand"].sum())
    current_stock = 110.0

    print(f" • Baseline SKU: {test_sku_id}")
    print(f"   Current Stock: {int(current_stock)} units | Base 14D Demand: {round(base_14d_demand, 1)} units")

    sim_20 = WhatIfSimulator.simulate_scenario(
        base_predicted_demand=base_14d_demand,
        current_inventory=current_stock,
        historical_daily_demand=p_df["Sales_Units"],
        demand_pct_change=20.0,
        safety_multiplier=1.0,
        lead_time_days=10
    )
    print(f"\n   [Scenario: +20% Demand Surge]")
    print(f"   - Adjusted Demand: {sim_20['adjusted_predicted_demand']} units")
    print(f"   - Potential Shortage: {sim_20['potential_shortage']} units")
    print(f"   - Recalculated Risk: {sim_20['simulated_risk_level']}")
    print(f"   - Days to Stockout: {sim_20['estimated_days_to_stockout']} days")
    print(f"   - Adjusted Reorder Units: {sim_20['simulated_additional_stock']} units")

    sim_50_low = WhatIfSimulator.simulate_scenario(
        base_predicted_demand=base_14d_demand,
        current_inventory=30.0,
        historical_daily_demand=p_df["Sales_Units"],
        demand_pct_change=50.0,
        safety_multiplier=1.25,
        lead_time_days=10
    )
    print(f"\n   [Scenario: +50% Flash Sale with Depleted Stock (30 units)]")
    print(f"   - Adjusted Demand: {sim_50_low['adjusted_predicted_demand']} units")
    print(f"   - Potential Shortage: {sim_50_low['potential_shortage']} units")
    print(f"   - Recalculated Risk: {sim_50_low['simulated_risk_level']}")
    print(f"   - Stockout Imminent: {sim_50_low['stockout_occurs']} (in {sim_50_low['estimated_days_to_stockout']} days)")
    print(f"   - Emergency Reorder Needed: {sim_50_low['simulated_additional_stock']} units")

    print("\n" + "=" * 80)
    print("SAMPLE DATASET TESTING COMPLETED WITH 100% SUCCESS!")
    print("=" * 80)

if __name__ == "__main__":
    run_sample_dataset_test()
