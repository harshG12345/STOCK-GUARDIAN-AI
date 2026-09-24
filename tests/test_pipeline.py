"""
Automated Unit Tests for Stock Guardian AI.
Validates data pipelines, anti-leakage time splitting, ML training,
risk scores, reorder recommendations, and What-If simulations.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

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

@pytest.fixture
def sample_dataset():
    """Generates small in-memory sample DataFrame."""
    dates = pd.date_range("2025-01-01", periods=100, freq="D")
    df = pd.DataFrame({
        "Date": dates,
        "Product_ID": ["SKU-001"] * 100,
        "Product_Name": ["Test Widget"] * 100,
        "Category": ["Hardware"] * 100,
        "Sales_Units": np.random.randint(10, 50, size=100),
        "Stock_On_Hand": [80] * 100,
        "Unit_Price": [25.0] * 100,
        "Lead_Time_Days": [7] * 100,
        "Promotion_Active": [0] * 90 + [1] * 10
    })
    return df

def test_data_loader_and_validation(sample_dataset):
    df_clean, diag = DataLoader.validate_and_standardize(sample_dataset)
    assert diag["is_valid"] is True
    assert diag["product_count"] == 1
    assert "Sales_Units" in df_clean.columns
    assert "Date" in df_clean.columns

def test_chronological_time_splitter(sample_dataset):
    train_df, test_df, meta = ChronologicalTimeSplitter.split(sample_dataset, train_ratio=0.8)
    assert len(train_df) == 80
    assert len(test_df) == 20
    assert meta["leakage_check_passed"] is True
    assert train_df["Date"].max() <= test_df["Date"].min()

def test_feature_engineering_anti_leakage(sample_dataset):
    feat_df = FeatureEngineer.extract_features(sample_dataset)
    assert "Lag_1" in feat_df.columns
    assert "Rolling_Mean_7" in feat_df.columns
    # Check that Lag_1 at index 1 matches Sales_Units at index 0
    assert feat_df.loc[1, "Lag_1"] == sample_dataset.loc[0, "Sales_Units"]

def test_baseline_model(sample_dataset):
    train_df, test_df, _ = ChronologicalTimeSplitter.split(sample_dataset, train_ratio=0.8)
    X_train, y_train, _ = FeatureEngineer.prepare_matrices(train_df)
    X_test, y_test, _ = FeatureEngineer.prepare_matrices(test_df)

    model = BaselineDemandModel(window_size=7).fit(y_train)
    preds = model.predict(X_test)
    assert len(preds) == len(test_df)
    assert np.all(preds >= 0)

def test_ml_demand_model_and_forecast(sample_dataset):
    train_df, test_df, _ = ChronologicalTimeSplitter.split(sample_dataset, train_ratio=0.8)
    X_train, y_train, _ = FeatureEngineer.prepare_matrices(train_df)
    X_test, y_test, _ = FeatureEngineer.prepare_matrices(test_df)

    ml_model = MLDemandModel(model_type="HistGradientBoosting").fit(X_train, y_train)
    preds = ml_model.predict(X_test)
    assert len(preds) == len(test_df)
    assert np.all(preds >= 0)

    # Recursive future forecast
    future_fc = ml_model.recursive_forecast(sample_dataset, horizon_days=14)
    assert len(future_fc) == 14
    assert "Forecast_Demand" in future_fc.columns

def test_evaluation_metrics():
    y_true = np.array([20, 25, 30, 35, 40])
    y_pred = np.array([22, 24, 29, 36, 41])
    metrics = ModelEvaluator.calculate_metrics(y_true, y_pred)
    assert metrics["MAE"] > 0
    assert metrics["RMSE"] > 0
    assert metrics["R2"] <= 1.0

def test_inventory_risk_score_and_categorization():
    # Case 1: Low inventory, high demand -> CRITICAL or HIGH RISK
    hist_series = pd.Series([20, 22, 25, 28, 30, 35, 40, 45, 50, 55])
    risk_low_stock = InventoryRiskEngine.calculate_risk_score(
        current_inventory=15,
        predicted_demand=60,
        historical_series=hist_series,
        lead_time_days=10
    )
    assert 0 <= risk_low_stock["risk_score"] <= 100
    assert risk_low_stock["risk_level"] in ["CRITICAL", "HIGH RISK"]
    assert risk_low_stock["demand_gap"] == 45.0

    # Case 2: Safe inventory
    risk_safe = InventoryRiskEngine.calculate_risk_score(
        current_inventory=200,
        predicted_demand=50,
        historical_series=hist_series,
        lead_time_days=5
    )
    assert 0 <= risk_safe["risk_score"] <= 100
    assert risk_safe["risk_level"] == "SAFE"

def test_demand_shock_detection():
    # History with normal baseline then surge
    normal_part = [30] * 25
    shock_part = [75, 80, 85, 90, 88, 92, 95]
    series_with_shock = pd.Series(normal_part + shock_part)
    shock_result = InventoryRiskEngine.detect_demand_shock(series_with_shock)
    assert shock_result["shock_status"] == "UNUSUAL INCREASE"
    assert shock_result["z_score"] > 2.0

def test_smart_reorder_advisor():
    hist_series = pd.Series([30, 32, 28, 31, 35, 29, 33])
    plan = SmartReorderAdvisor.calculate_reorder_plan(
        product_name="Test Widget",
        current_inventory=40,
        predicted_demand=80,
        historical_daily_demand=hist_series,
        lead_time_days=7,
        service_level="95%"
    )
    assert plan["safety_buffer"] > 0
    assert plan["recommended_target_inventory"] > plan["predicted_demand"]
    assert plan["recommended_additional_stock"] > 0
    assert "formula_breakdown" in plan

def test_what_if_simulator():
    hist_series = pd.Series([25, 28, 26, 30, 27, 29, 31])
    sim = WhatIfSimulator.simulate_scenario(
        base_predicted_demand=100.0,
        current_inventory=60.0,
        historical_daily_demand=hist_series,
        demand_pct_change=20.0,  # +20% demand surge
        safety_multiplier=1.0,
        lead_time_days=7,
        forecast_horizon_days=14
    )
    assert sim["adjusted_predicted_demand"] == 120.0
    assert sim["potential_shortage"] == 60.0  # 120 - 60
    assert sim["simulated_additional_stock"] > 60.0  # Accounts for buffer
    assert sim["simulated_risk_level"] in ["CRITICAL", "HIGH RISK"]

def test_benchmark_dataset_integrity():
    df = generate_benchmark_dataset(output_path="data/test_retail.csv", num_days=100)
    assert len(df) > 0
    assert df["Product_ID"].nunique() == 12
    assert "Sales_Units" in df.columns
    assert "Stock_On_Hand" in df.columns
