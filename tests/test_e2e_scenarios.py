"""
End-to-End Scenario Testing for Stock Guardian AI.
Validates the 5 required hackathon scenarios:
1. Safe Inventory Case
2. Low Inventory / Stockout Case
3. Demand Shock Detection Case
4. Demand Increase Simulation (+20%)
5. Missing / Invalid Data Handling Case
"""

import os
import sys

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import numpy as np
import pandas as pd
from datetime import datetime

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

def test_scenario_1_safe_inventory():
    """Scenario 1: Product with abundant inventory (Stock > Demand * 1.5)."""
    dates = pd.date_range("2025-01-01", periods=180, freq="D")
    df = pd.DataFrame({
        "Date": dates,
        "Product_ID": ["SKU-SAFE-01"] * 180,
        "Product_Name": ["Heavy Duty Screwdriver Set"] * 180,
        "Category": ["Tools"] * 180,
        "Sales_Units": [15 + int(x % 5) for x in range(180)],
        "Stock_On_Hand": [250] * 180,
        "Unit_Price": [14.99] * 180,
        "Lead_Time_Days": [5] * 180,
        "Promotion_Active": [0] * 180
    })

    p_df = DataPreprocessor.prepare_product_series(df, "SKU-SAFE-01")
    train_df, test_df, _ = ChronologicalTimeSplitter.split(p_df, 0.8)
    X_train, y_train, _ = FeatureEngineer.prepare_matrices(train_df)
    ml = MLDemandModel().fit(X_train, y_train)
    fc = ml.recursive_forecast(p_df, horizon_days=14)
    pred_demand = fc["Forecast_Demand"].sum()

    risk = InventoryRiskEngine.calculate_risk_score(
        current_inventory=500,
        predicted_demand=pred_demand,
        historical_series=p_df["Sales_Units"],
        lead_time_days=5
    )

    reorder = SmartReorderAdvisor.calculate_reorder_plan(
        product_name="Heavy Duty Screwdriver Set",
        current_inventory=500,
        predicted_demand=pred_demand,
        historical_daily_demand=p_df["Sales_Units"],
        lead_time_days=5
    )

    assert risk["risk_level"] == "SAFE"
    assert risk["risk_score"] < 35
    assert reorder["recommended_additional_stock"] == 0
    print("Scenario 1 (Safe Inventory): PASSED - Risk Level:", risk["risk_level"], "Reorder Units:", reorder["recommended_additional_stock"])

def test_scenario_2_low_inventory_stockout():
    """Scenario 2: Product with critically depleted inventory."""
    dates = pd.date_range("2025-01-01", periods=180, freq="D")
    df = pd.DataFrame({
        "Date": dates,
        "Product_ID": ["SKU-CRIT-02"] * 180,
        "Product_Name": ["Gaming Graphics Card RTX"] * 180,
        "Category": ["Electronics"] * 180,
        "Sales_Units": [40 + int(x % 10) for x in range(180)],
        "Stock_On_Hand": [12] * 180,  # Critical stock (only ~12 units for 40/day demand)
        "Unit_Price": [599.00] * 180,
        "Lead_Time_Days": [14] * 180,
        "Promotion_Active": [0] * 180
    })

    p_df = DataPreprocessor.prepare_product_series(df, "SKU-CRIT-02")
    train_df, test_df, _ = ChronologicalTimeSplitter.split(p_df, 0.8)
    X_train, y_train, _ = FeatureEngineer.prepare_matrices(train_df)
    ml = MLDemandModel().fit(X_train, y_train)
    fc = ml.recursive_forecast(p_df, horizon_days=14)
    pred_demand = fc["Forecast_Demand"].sum()

    risk = InventoryRiskEngine.calculate_risk_score(
        current_inventory=12,
        predicted_demand=pred_demand,
        historical_series=p_df["Sales_Units"],
        lead_time_days=14
    )

    reorder = SmartReorderAdvisor.calculate_reorder_plan(
        product_name="Gaming Graphics Card RTX",
        current_inventory=12,
        predicted_demand=pred_demand,
        historical_daily_demand=p_df["Sales_Units"],
        lead_time_days=14
    )

    assert risk["risk_level"] in ["CRITICAL", "HIGH RISK"]
    assert risk["risk_score"] >= 60
    assert reorder["recommended_additional_stock"] > 400
    print("Scenario 2 (Low Inventory Stockout): PASSED - Risk Level:", risk["risk_level"], "Score:", risk["risk_score"], "Reorder Units:", reorder["recommended_additional_stock"])

def test_scenario_3_demand_shock_detection():
    """Scenario 3: Product experiencing sudden demand spike +65% in recent 7-day window."""
    normal_demand = [50 + int(i % 5) for i in range(150)]
    shock_demand = [95, 100, 105, 98, 102, 108, 112] # +65% surge
    full_demand = normal_demand + shock_demand
    
    dates = pd.date_range("2025-01-01", periods=len(full_demand), freq="D")
    df = pd.DataFrame({
        "Date": dates,
        "Product_ID": ["SKU-SHOCK-03"] * len(full_demand),
        "Sales_Units": full_demand,
        "Stock_On_Hand": [80] * len(full_demand),
        "Lead_Time_Days": [7] * len(full_demand)
    })

    shock_info = InventoryRiskEngine.detect_demand_shock(df["Sales_Units"], recent_window=7, baseline_window=30)
    assert shock_info["shock_status"] == "UNUSUAL INCREASE"
    assert shock_info["z_score"] >= 2.0
    assert shock_info["pct_deviation"] > 40.0
    print("Scenario 3 (Demand Shock Detection): PASSED - Status:", shock_info["shock_status"], "Z-Score:", shock_info["z_score"])

def test_scenario_4_what_if_demand_surge_20():
    """Scenario 4: User stress-tests +20% demand increase in What-If Simulator."""
    hist = pd.Series([30, 32, 28, 35, 31, 29, 33, 30, 34, 32])
    base_demand = 125.0
    current_stock = 80.0

    sim = WhatIfSimulator.simulate_scenario(
        base_predicted_demand=base_demand,
        current_inventory=current_stock,
        historical_daily_demand=hist,
        demand_pct_change=20.0,
        safety_multiplier=1.0,
        lead_time_days=7,
        forecast_horizon_days=14
    )

    assert sim["adjusted_predicted_demand"] == 150.0  # 125 * 1.20
    assert sim["current_stock"] == 80
    assert sim["potential_shortage"] == 70.0  # 150 - 80
    assert sim["simulated_additional_stock"] > 70.0  # Accounts for safety buffer
    assert sim["simulated_risk_level"] in ["CRITICAL", "HIGH RISK"]
    print("Scenario 4 (What-If 20% Surge): PASSED - Adjusted Demand:", sim["adjusted_predicted_demand"], "Shortage:", sim["potential_shortage"], "Risk:", sim["simulated_risk_level"])

def test_scenario_5_invalid_data_graceful_handling():
    """Scenario 5: Uploading malformed or missing-column dataset is caught gracefully."""
    invalid_df = pd.DataFrame({
        "Random_Col_A": [1, 2, 3],
        "Random_Col_B": ["A", "B", "C"]
    })
    clean_df, diag = DataLoader.validate_and_standardize(invalid_df)
    assert diag["is_valid"] is False
    assert "sales_units" in diag["missing_required"] or "date" in diag["missing_required"]
    print("Scenario 5 (Graceful Error Diagnostics): PASSED - Validated:", diag["is_valid"], "Missing Required:", diag["missing_required"])

if __name__ == "__main__":
    test_scenario_1_safe_inventory()
    test_scenario_2_low_inventory_stockout()
    test_scenario_3_demand_shock_detection()
    test_scenario_4_what_if_demand_surge_20()
    test_scenario_5_invalid_data_graceful_handling()
    print("\nALL 5 SCENARIOS PASSED SYSTEM VALIDATION.")
