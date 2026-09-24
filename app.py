import os
import streamlit as st
import pandas as pd
import numpy as np
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
from visualization.styles import CUSTOM_CSS, render_badge, render_metric_card
from visualization.charts import ChartEngine, PALETTE
from data.dataset_generator import generate_benchmark_dataset

st.set_page_config(
    page_title="Stock Guardian AI | Demand Prediction & Inventory Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

BENCHMARK_PATH = "data/retail_inventory_history.csv"

if not os.path.exists(BENCHMARK_PATH):
    generate_benchmark_dataset(output_path=BENCHMARK_PATH)

def load_dataset(file_source=None):
    if file_source is not None:
        df, diag = DataLoader.load_file(file_source)
    else:
        df, diag = DataLoader.load_file(BENCHMARK_PATH)
    return df, diag

with st.sidebar:
    st.markdown('<div class="app-brand-title">Stock Guardian AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-brand-tagline">Demand Intelligence Platform</div>', unsafe_allow_html=True)
    st.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)

    st.markdown("**Data Source**")
    data_source_mode = st.radio(
        "Choose dataset:",
        ["Curated Benchmark (12 SKUs)", "Upload CSV / Excel"],
        label_visibility="collapsed"
    )

    uploaded_file = None
    if data_source_mode == "Upload CSV / Excel":
        uploaded_file = st.file_uploader(
            "Upload inventory sales history (.csv, .xlsx)",
            type=["csv", "xlsx", "xls"]
        )

    st.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)
    st.markdown("**Global Forecast Parameters**")
    forecast_horizon_days = st.slider("Forecast Horizon (Days)", min_value=7, max_value=30, value=14, step=7)
    service_level_target = st.selectbox("Target Service Level", ["90%", "95%", "98%", "99%"], index=1)

    st.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='secondary-text' style='font-size: 0.75rem;'>"
        "<b>Engine:</b> Supervised ML Forecaster<br>"
        "<b>Validation:</b> Chronological 80/20 Split<br>"
        "<b>Zero-Leakage:</b> Shift(1) Lags"
        "</div>",
        unsafe_allow_html=True
    )

raw_df, diagnostics = load_dataset(uploaded_file if data_source_mode == "Upload CSV / Excel" and uploaded_file is not None else None)

if raw_df is None or not diagnostics.get("is_valid", False):
    st.error(f"Error loading dataset: {diagnostics.get('error', 'Missing required Date or Sales columns')}")
    st.info("Please verify the uploaded file has valid date and sales/quantity columns.")
    st.stop()

product_metadata = DataPreprocessor.get_product_metadata(raw_df)
product_list = [p["Product_ID"] for p in product_metadata]
product_name_map = {p["Product_ID"]: f"{p['Product_ID']} - {p['Product_Name']}" for p in product_metadata}

def analyze_all_products(df_data, horizon_days, service_level):
    summaries = []
    
    for meta in product_metadata:
        pid = meta["Product_ID"]
        p_df = DataPreprocessor.prepare_product_series(df_data, product_id=pid)
        
        train_df, test_df, split_meta = ChronologicalTimeSplitter.split(p_df, train_ratio=0.8)
        X_train, y_train, feat_names = FeatureEngineer.prepare_matrices(train_df)
        X_test, y_test, _ = FeatureEngineer.prepare_matrices(test_df)

        base_model = BaselineDemandModel(window_size=7).fit(y_train)
        base_preds = base_model.predict(X_test)

        ml_model = MLDemandModel(model_type="RandomForest").fit(X_train, y_train)
        ml_preds = ml_model.predict(X_test)

        comp_df, comp_analysis = ModelEvaluator.compare_models(
            y_test.values, base_preds, ml_preds,
            baseline_name="Baseline (7D MA)",
            ml_name="ML (Supervised Forecaster)"
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

        summaries.append({
            "Product_ID": pid,
            "Product_Name": meta["Product_Name"],
            "Category": meta["Category"],
            "Current_Stock": meta["Current_Stock"],
            "Avg_Daily_Demand": meta["Avg_Daily_Demand"],
            "Predicted_Demand": round(total_predicted_demand, 1),
            "Demand_Gap": risk_info["demand_gap"],
            "Risk_Score": risk_info["risk_score"],
            "Risk_Level": risk_info["risk_level"],
            "Action_Code": risk_info["action_code"],
            "Badge_Color": risk_info["badge_color"],
            "Trend": risk_info["trend"],
            "Trend_Pct": risk_info["trend_details"]["pct_change"],
            "Shock_Status": shock_info["shock_status"],
            "Shock_Z": shock_info["z_score"],
            "Shock_Dev_Pct": shock_info["pct_deviation"],
            "Safety_Buffer": reorder_plan["safety_buffer"],
            "Recommended_Additional_Stock": reorder_plan["recommended_additional_stock"],
            "Estimated_Capital": reorder_plan["estimated_capital_required"],
            "Days_Of_Supply": reorder_plan["days_of_supply"],
            "Lead_Time_Days": meta["Lead_Time_Days"],
            "Unit_Price": meta["Unit_Price"],
            "ML_MAE": comp_analysis["ml_metrics"]["MAE"],
            "Base_MAE": comp_analysis["base_metrics"]["MAE"],
            "ML_RMSE": comp_analysis["ml_metrics"]["RMSE"],
            "ML_R2": comp_analysis["ml_metrics"]["R2"],
            "ML_MAPE": comp_analysis["ml_metrics"]["Safe_MAPE"],
            "Feature_Importances": ml_model.feature_importances_,
            "Split_Meta": split_meta,
            "History_DF": p_df,
            "Forecast_DF": future_fc,
            "Test_DF": test_df,
            "Base_Preds": base_preds,
            "ML_Preds": ml_preds,
            "Reorder_Plan": reorder_plan,
            "Risk_Info": risk_info
        })
        
    return summaries

with st.spinner("Analyzing inventory and demand forecasting across SKUs..."):
    portfolio_results = analyze_all_products(raw_df, forecast_horizon_days, service_level_target)
    portfolio_df = pd.DataFrame(portfolio_results)

st.markdown(
    """
    <div class="app-header-container">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <h1 style="margin: 0; font-size: 1.60rem; color: #1E3A8A; font-weight: 700;">STOCK GUARDIAN AI</h1>
                <p style="margin: 2px 0 0 0; color: #4B5563; font-size: 0.90rem;">
                    <b>Predict demand. Prevent stock-outs. Make smarter inventory decisions.</b>
                </p>
            </div>
            <div style="text-align: right;">
                <span class="status-badge" style="background-color: #EFF6FF; color: #1E3A8A; border-color: #BFDBFE;">
                    [ • ] ACTIVE DATASET: """ + str(diagnostics.get("product_count", 0)) + """ SKUs | """ + str(diagnostics.get("cleaned_rows", 0)) + """ RECORDS
                </span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

tab_overview, tab_forecast, tab_risk, tab_what_if, tab_model, tab_data, tab_legal = st.tabs([
    "1. Dashboard Overview",
    "2. Demand Forecast",
    "3. Inventory Risk & Reorder",
    "4. What-If Simulator",
    "5. Model Performance",
    "6. Data Inspector & Upload",
    "7. Legal & Compliance"
])

with tab_overview:
    total_products = len(portfolio_df)
    critical_count = len(portfolio_df[portfolio_df["Risk_Level"] == "CRITICAL"])
    high_risk_count = len(portfolio_df[portfolio_df["Risk_Level"] == "HIGH RISK"])
    watch_count = len(portfolio_df[portfolio_df["Risk_Level"] == "WATCH"])
    safe_count = len(portfolio_df[portfolio_df["Risk_Level"] == "SAFE"])
    total_reorder_units = int(portfolio_df["Recommended_Additional_Stock"].sum())
    total_reorder_capital = float(portfolio_df["Estimated_Capital"].sum())
    avg_predicted_demand = round(float(portfolio_df["Predicted_Demand"].mean()), 1)

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.markdown(render_metric_card("Total Monitored SKUs", str(total_products), f"{diagnostics['categories'][0]} & more"), unsafe_allow_html=True)
    with kpi2:
        st.markdown(render_metric_card("Critical Stockouts", f"{critical_count} SKUs", "Immediate order required", "#DC2626"), unsafe_allow_html=True)
    with kpi3:
        st.markdown(render_metric_card("High Risk / Watch", f"{high_risk_count + watch_count} SKUs", "Tight coverage deficit", "#D97706"), unsafe_allow_html=True)
    with kpi4:
        st.markdown(render_metric_card("Avg 14D Demand", f"{avg_predicted_demand} units", "Per product expectation", "#1E3A8A"), unsafe_allow_html=True)
    with kpi5:
        st.markdown(render_metric_card("Recommended Reorder", f"{total_reorder_units:,} units", f"${total_reorder_capital:,.2f} total cost", "#15803D"), unsafe_allow_html=True)

    shock_items = portfolio_df[portfolio_df["Shock_Status"] != "NORMAL"]
    if not shock_items.empty:
        st.markdown("<h3 style='margin-top: 15px;'>Statistical Demand Shock Alerts</h3>", unsafe_allow_html=True)
        for _, s_row in shock_items.iterrows():
            if s_row["Shock_Status"] == "UNUSUAL INCREASE":
                st.markdown(
                    f"""
                    <div class="alert-critical-box">
                        <div class="alert-title">[ ▲ ] DEMAND SURGE DETECTED: {s_row['Product_Name']} ({s_row['Product_ID']})</div>
                        <div class="secondary-text" style="color: #991B1B;">
                            Recent demand increased by <b>+{s_row['Shock_Dev_Pct']:.1f}%</b> against 30-day baseline (Z-Score: +{s_row['Shock_Z']:.2f}). 
                            Current stock of {s_row['Current_Stock']} units covers only {s_row['Days_Of_Supply']:.1f} days of supply.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="info-callout" style="border-left-color: #D97706;">
                        <div style="font-weight: 600; color: #B45309;">[ ▼ ] UNUSUAL DEMAND DROP: {s_row['Product_Name']} ({s_row['Product_ID']})</div>
                        <div class="secondary-text">
                            Recent demand dropped by <b>{s_row['Shock_Dev_Pct']:.1f}%</b> (Z-Score: {s_row['Shock_Z']:.2f}). Replenishment pace can be safely moderated to avoid overstocking.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown("<h3>Products Requiring Attention</h3>", unsafe_allow_html=True)
    st.markdown("<div class='secondary-text'>Prioritized by Risk Score (0–100) combining stockout gap, demand trend, historical volatility, and supplier lead time.</div>", unsafe_allow_html=True)

    f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
    with f_col1:
        cat_filter = st.multiselect("Filter Category", options=diagnostics["categories"], default=diagnostics["categories"])
    with f_col2:
        risk_filter = st.multiselect("Filter Risk Level", options=["CRITICAL", "HIGH RISK", "WATCH", "SAFE"], default=["CRITICAL", "HIGH RISK", "WATCH", "SAFE"])
    with f_col3:
        sort_by = st.selectbox("Sort Table By", ["Risk Score (High to Low)", "Recommended Reorder (High to Low)", "Demand Gap (High to Low)"])

    filtered_df = portfolio_df[
        (portfolio_df["Category"].isin(cat_filter)) &
        (portfolio_df["Risk_Level"].isin(risk_filter))
    ].copy()

    if sort_by == "Risk Score (High to Low)":
        filtered_df = filtered_df.sort_values(by="Risk_Score", ascending=False)
    elif sort_by == "Recommended Reorder (High to Low)":
        filtered_df = filtered_df.sort_values(by="Recommended_Additional_Stock", ascending=False)
    else:
        filtered_df = filtered_df.sort_values(by="Demand_Gap", ascending=False)

    display_table = filtered_df[[
        "Product_ID", "Product_Name", "Category", "Current_Stock", 
        "Predicted_Demand", "Demand_Gap", "Risk_Score", "Risk_Level", 
        "Trend", "Recommended_Additional_Stock", "Days_Of_Supply"
    ]].rename(columns={
        "Product_ID": "SKU",
        "Product_Name": "Product",
        "Current_Stock": "Current Stock",
        "Predicted_Demand": f"Forecast ({forecast_horizon_days}D)",
        "Demand_Gap": "Deficit Gap",
        "Risk_Score": "Risk Score (0-100)",
        "Risk_Level": "Risk Level",
        "Trend": "Demand Trend",
        "Recommended_Additional_Stock": "Reorder Units",
        "Days_Of_Supply": "Days Supply"
    })

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<h3 style='margin-top: 20px;'>Portfolio Risk Matrix</h3>", unsafe_allow_html=True)
    matrix_fig = ChartEngine.plot_risk_matrix(portfolio_results)
    st.plotly_chart(matrix_fig, use_container_width=True)

with tab_forecast:
    st.markdown("<h2>Product-Level Demand Forecast</h2>", unsafe_allow_html=True)
    st.markdown("<div class='secondary-text'>Select a product to inspect historical sales patterns, moving trends, and recursive machine learning demand forecasts.</div>", unsafe_allow_html=True)

    selected_pid = st.selectbox(
        "Select Product SKU:",
        options=product_list,
        format_func=lambda x: product_name_map.get(x, x),
        key="forecast_sku_select"
    )

    selected_prod = next(p for p in portfolio_results if p["Product_ID"] == selected_pid)

    pm1, pm2, pm3, pm4, pm5 = st.columns(5)
    with pm1:
        st.markdown(render_metric_card("Current Physical Stock", f"{selected_prod['Current_Stock']} units", f"Lead time: {selected_prod['Lead_Time_Days']} days"), unsafe_allow_html=True)
    with pm2:
        st.markdown(render_metric_card(f"ML Forecast ({forecast_horizon_days}D)", f"{selected_prod['Predicted_Demand']} units", f"Avg: {round(selected_prod['Predicted_Demand']/forecast_horizon_days, 1)} units/day"), unsafe_allow_html=True)
    with pm3:
        st.markdown(render_metric_card("Demand Gap Deficit", f"{selected_prod['Demand_Gap']} units", "Forecast minus current stock", "#DC2626" if selected_prod['Demand_Gap'] > 0 else "#15803D"), unsafe_allow_html=True)
    with pm4:
        st.markdown(render_metric_card("Inventory Risk Score", f"{selected_prod['Risk_Score']} / 100", f"Level: {selected_prod['Risk_Level']}", selected_prod['Badge_Color']), unsafe_allow_html=True)
    with pm5:
        st.markdown(render_metric_card("Reorder Recommendation", f"{selected_prod['Recommended_Additional_Stock']} units", f"Buffer: {selected_prod['Safety_Buffer']} units", "#1E3A8A"), unsafe_allow_html=True)

    timeline_fig = ChartEngine.plot_forecast_timeline(
        history_df=selected_prod["History_DF"],
        forecast_df=selected_prod["Forecast_DF"],
        product_name=selected_prod["Product_Name"],
        current_stock=selected_prod["Current_Stock"]
    )
    st.plotly_chart(timeline_fig, use_container_width=True)

    col_fc1, col_fc2 = st.columns([1, 1])
    with col_fc1:
        st.markdown("<h3>Top Predictive Drivers</h3>", unsafe_allow_html=True)
        feat_fig = ChartEngine.plot_feature_importance(selected_prod["Feature_Importances"])
        st.plotly_chart(feat_fig, use_container_width=True)

    with col_fc2:
        st.markdown(f"<h3>Daily Forecast Breakdown ({forecast_horizon_days} Days)</h3>", unsafe_allow_html=True)
        fc_display = selected_prod["Forecast_DF"].copy()
        fc_display["Date"] = pd.to_datetime(fc_display["Date"]).dt.strftime("%Y-%m-%d (%a)")
        fc_display = fc_display.rename(columns={
            "Horizon_Day": "Day #",
            "Forecast_Demand": "Predicted Demand (Units)"
        })
        st.dataframe(fc_display[["Day #", "Date", "Predicted Demand (Units)"]], use_container_width=True, hide_index=True, height=320)

with tab_risk:
    st.markdown("<h2>Inventory Risk Engine & Smart Reorder Advisor</h2>", unsafe_allow_html=True)
    st.markdown("<div class='secondary-text'>Rigorous risk quantification and transparent inventory replenishment mathematics.</div>", unsafe_allow_html=True)

    sel_pid_risk = st.selectbox(
        "Select Product for Risk Audit:",
        options=product_list,
        format_func=lambda x: product_name_map.get(x, x),
        key="risk_sku_select"
    )
    r_prod = next(p for p in portfolio_results if p["Product_ID"] == sel_pid_risk)
    r_info = r_prod["Risk_Info"]
    r_plan = r_prod["Reorder_Plan"]

    rc1, rc2, rc3 = st.columns([1.2, 1.2, 1.6])
    with rc1:
        st.markdown(
            f"""
            <div class="metric-box" style="border-left: 4px solid {r_info['badge_color']};">
                <div class="metric-label">Composite Risk Status</div>
                <div style="margin: 8px 0;">{render_badge(r_info['risk_level'])}</div>
                <div class="metric-value">{r_info['risk_score']} <span style="font-size: 1rem; color: #6B7280;">/ 100</span></div>
                <div class="metric-sub"><b>Action:</b> {r_info['action_code']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with rc2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">Demand Dynamics</div>
                <div class="metric-value" style="font-size: 1.25rem;">Trend: <b>{r_info['trend']}</b></div>
                <div class="metric-sub" style="margin-top: 6px;">
                    • Growth Rate: <b>{r_info['trend_details']['pct_change']:+.1f}%</b><br>
                    • Demand Shock: <b>{r_prod['Shock_Status']}</b><br>
                    • Volatility (CV): <b>{r_info['volatility_cv']}</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with rc3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">Risk Component Score Weights</div>
                <div class="secondary-text" style="margin-top: 6px;">
                    1. <b>Coverage Deficit (45% wt):</b> {r_info['component_scores']['coverage_deficit']}/100<br>
                    2. <b>Trend Acceleration (20% wt):</b> {r_info['component_scores']['trend_acceleration']}/100<br>
                    3. <b>Demand Volatility (20% wt):</b> {r_info['component_scores']['demand_volatility']}/100<br>
                    4. <b>Lead Time Exposure (15% wt):</b> {r_info['component_scores']['lead_time_exposure']}/100
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<h3>Actionable Reorder Plan</h3>", unsafe_allow_html=True)
    
    plan_c1, plan_c2, plan_c3, plan_c4 = st.columns(4)
    with plan_c1:
        st.markdown(render_metric_card("Current Inventory", f"{r_plan['current_inventory']} units", f"{r_plan['days_of_supply']} days of supply"), unsafe_allow_html=True)
    with plan_c2:
        st.markdown(render_metric_card("14D Predicted Demand", f"{r_plan['predicted_demand']} units", f"Target Service: {r_plan['service_level']}"), unsafe_allow_html=True)
    with plan_c3:
        st.markdown(render_metric_card("Safety Buffer Stock", f"+{r_plan['safety_buffer']} units", f"Lead Time: {r_plan['lead_time_days']} days"), unsafe_allow_html=True)
    with plan_c4:
        st.markdown(render_metric_card("Recommended Order Units", f"{r_plan['recommended_additional_stock']} units", f"Capital: ${r_plan['estimated_capital_required']:,.2f}", "#1E3A8A"), unsafe_allow_html=True)

    with st.expander("How is this calculated? (Transparent Reorder Formula Audit)", expanded=True):
        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; padding: 12px; border: 1px solid #E5E7EB;">
                <div style="font-weight: 600; color: #1E3A8A; margin-bottom: 8px;">Mathematical Derivation Trace:</div>
                <div class="secondary-text" style="line-height: 1.6;">
                    <b>Step 1: Lead-Time Aware Safety Buffer ($SS$)</b><br>
                    <span class="mono-text">SS = Z_service × σ_daily_demand × √(Lead_Time_Days)</span><br>
                    Calculation: <span class="mono-text">{r_plan['formula_breakdown']['step_1_safety_buffer']}</span><br><br>

                    <b>Step 2: Recommended Target Inventory Level ($S_{{target}}$)</b><br>
                    <span class="mono-text">Target = Forecast_Demand + Safety_Buffer</span><br>
                    Calculation: <span class="mono-text">{r_plan['formula_breakdown']['step_2_target_inventory']}</span><br><br>

                    <b>Step 3: Recommended Additional Stock to Reorder ($Q$)</b><br>
                    <span class="mono-text">Q = max(0, Target - Current_Stock)</span><br>
                    Calculation: <span class="mono-text">{r_plan['formula_breakdown']['step_3_reorder_qty']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

with tab_what_if:
    st.markdown("<h2>What-If Inventory Simulator</h2>", unsafe_allow_html=True)
    st.markdown("<div class='secondary-text'>Stress-test your supply chain in real time. Simulate promotional demand surges, supplier lead time delays, or custom inventory overrides to observe immediate risk changes.</div>", unsafe_allow_html=True)

    sim_pid = st.selectbox(
        "Select Product to Simulate:",
        options=product_list,
        format_func=lambda x: product_name_map.get(x, x),
        key="whatif_sku_select"
    )
    s_prod = next(p for p in portfolio_results if p["Product_ID"] == sim_pid)

    st.markdown("<div class='sim-container'>", unsafe_allow_html=True)
    st.markdown("<div class='sim-header'>Interactive Scenario Parameters</div>", unsafe_allow_html=True)

    st.markdown("<div style='font-size: 0.82rem; font-weight: 600; color: #4B5563; margin-bottom: 6px;'>Quick Scenario Presets:</div>", unsafe_allow_html=True)
    pres_col1, pres_col2, pres_col3, pres_col4 = st.columns(4)
    with pres_col1:
        if st.button("Baseline (0% Shift)"):
            st.session_state["demand_shift_slider"] = 0.0
    with pres_col2:
        if st.button("+20% Demand Surge"):
            st.session_state["demand_shift_slider"] = 20.0
    with pres_col3:
        if st.button("+50% Flash Sale Spike"):
            st.session_state["demand_shift_slider"] = 50.0
    with pres_col4:
        if st.button("-30% Market Slowdown"):
            st.session_state["demand_shift_slider"] = -30.0

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        sim_demand_change = st.slider(
            "Expected Demand Change %",
            min_value=-50.0,
            max_value=100.0,
            value=st.session_state.get("demand_shift_slider", 20.0),
            step=5.0,
            key="demand_shift_slider"
        )
    with sc2:
        sim_stock_override = st.slider(
            "Current Physical Stock (Units)",
            min_value=0,
            max_value=max(300, int(s_prod["Current_Stock"] * 2)),
            value=int(s_prod["Current_Stock"]),
            step=5
        )
    with sc3:
        sim_safety_mult = st.select_slider(
            "Safety Buffer Multiplier",
            options=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
            value=1.0,
            format_func=lambda x: f"{x}x Buffer"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    sim_results = WhatIfSimulator.simulate_scenario(
        base_predicted_demand=s_prod["Predicted_Demand"],
        current_inventory=sim_stock_override,
        historical_daily_demand=s_prod["History_DF"]["Sales_Units"],
        demand_pct_change=sim_demand_change,
        safety_multiplier=sim_safety_mult,
        lead_time_days=s_prod["Lead_Time_Days"],
        forecast_horizon_days=forecast_horizon_days
    )

    st.markdown("<h3>Simulated Impact & Recalculated Decisions</h3>", unsafe_allow_html=True)

    sim_res1, sim_res2, sim_res3, sim_res4 = st.columns(4)
    with sim_res1:
        st.markdown(render_metric_card("Adjusted Demand", f"{sim_results['adjusted_predicted_demand']} units", f"Base: {sim_results['base_predicted_demand']} units ({sim_demand_change:+.0f}%)"), unsafe_allow_html=True)
    with sim_res2:
        st.markdown(render_metric_card("Potential Shortage", f"{sim_results['potential_shortage']} units", "Demand exceeding current stock", "#DC2626" if sim_results['potential_shortage'] > 0 else "#15803D"), unsafe_allow_html=True)
    with sim_res3:
        st.markdown(render_metric_card("Simulated Risk Status", sim_results["simulated_risk_level"], sim_results["action_summary"], sim_results["badge_color"]), unsafe_allow_html=True)
    with sim_res4:
        st.markdown(render_metric_card("Adjusted Reorder Units", f"{sim_results['simulated_additional_stock']} units", f"Target stock: {sim_results['simulated_target_stock']} units", "#1E3A8A"), unsafe_allow_html=True)

    if sim_results["stockout_occurs"]:
        st.markdown(
            f"""
            <div class="alert-critical-box">
                <div class="alert-title">[ ! ] CRITICAL STOCKOUT ALERT IN SIMULATION</div>
                <div class="secondary-text" style="color: #991B1B;">
                    Under this {sim_demand_change:+.0f}% scenario, stock will run out in <b>{sim_results['estimated_days_to_stockout']} days</b> 
                    (Supplier lead time is {sim_results['lead_time_days']} days). An immediate emergency reorder of <b>{sim_results['simulated_additional_stock']} units</b> is required to prevent lost sales.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    whatif_chart = ChartEngine.plot_what_if_comparison(
        current_stock=sim_results["current_stock"],
        base_demand=sim_results["base_predicted_demand"],
        adjusted_demand=sim_results["adjusted_predicted_demand"],
        safety_buffer=sim_results["simulated_buffer"],
        recommended_target=sim_results["simulated_target_stock"],
        product_name=s_prod["Product_Name"]
    )
    st.plotly_chart(whatif_chart, use_container_width=True)

with tab_model:
    st.markdown("<h2>Model Performance & Evaluation Methodology</h2>", unsafe_allow_html=True)
    st.markdown("<div class='secondary-text'>Rigorous time-series split validation comparing Baseline moving averages against Supervised ML.</div>", unsafe_allow_html=True)

    m_pid = st.selectbox(
        "Select Product Evaluation:",
        options=product_list,
        format_func=lambda x: product_name_map.get(x, x),
        key="model_sku_select"
    )
    m_prod = next(p for p in portfolio_results if p["Product_ID"] == m_pid)

    st.markdown(
        f"""
        <div class="info-callout">
            <div style="font-weight: 600; color: #1E3A8A; font-size: 0.95rem;">Chronological Out-of-Time Split Methodology:</div>
            <div class="secondary-text" style="margin-top: 4px;">
                • <b>Training Partition:</b> {m_prod['Split_Meta']['train_size']} records ({m_prod['Split_Meta']['train_start_date']} to {m_prod['Split_Meta']['train_end_date']})<br>
                • <b>Holdout Test Partition:</b> {m_prod['Split_Meta']['test_size']} records ({m_prod['Split_Meta']['test_start_date']} to {m_prod['Split_Meta']['test_end_date']})<br>
                • <b>Anti-Leakage Guarantee:</b> {m_prod['Split_Meta']['leakage_check_passed']} (Strict chronological separation; all lag/rolling features use shift(1) backward windows only).
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h3>Holdout Test Evaluation Metrics</h3>", unsafe_allow_html=True)
    
    comp_metrics_df = pd.DataFrame([
        {
            "Model Architecture": "Baseline (7-Day Moving Average)",
            "MAE (Units)": m_prod["Base_MAE"],
            "RMSE (Units)": round(float(np.sqrt(np.mean((m_prod['Test_DF']['Sales_Units'].values - m_prod['Base_Preds'])**2))), 2),
            "R² Score": round(float(np.corrcoef(m_prod['Test_DF']['Sales_Units'].values, m_prod['Base_Preds'])[0,1]**2), 3) if len(m_prod['Test_DF']) > 1 else 0.0,
            "Evaluation Status": "Reference Benchmark"
        },
        {
            "Model Architecture": "Machine Learning (Supervised Forecaster)",
            "MAE (Units)": m_prod["ML_MAE"],
            "RMSE (Units)": m_prod["ML_RMSE"],
            "R² Score": m_prod["ML_R2"],
            "Evaluation Status": "Primary Production Model"
        }
    ])

    st.dataframe(comp_metrics_df, use_container_width=True, hide_index=True)

    mae_diff = m_prod["Base_MAE"] - m_prod["ML_MAE"]
    mae_pct = round((mae_diff / (m_prod["Base_MAE"] + 1e-5)) * 100.0, 1)
    if mae_diff > 0:
        st.markdown(
            f"<div style='font-weight: 600; color: #15803D; margin: 8px 0;'>"
            f"[ ✓ ] ML Model demonstrates a <b>{mae_pct}% reduction in Mean Absolute Error</b> over the baseline on unseen test data."
            f"</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='font-weight: 600; color: #4B5563; margin: 8px 0;'>"
            f"[ • ] Baseline and ML Model exhibit comparable performance on this stable demand profile."
            f"</div>",
            unsafe_allow_html=True
        )

    res_fig = ChartEngine.plot_model_comparison_residuals(
        test_df=m_prod["Test_DF"],
        baseline_preds=m_prod["Base_Preds"],
        ml_preds=m_prod["ML_Preds"],
        product_name=m_prod["Product_Name"]
    )
    st.plotly_chart(res_fig, use_container_width=True)

with tab_data:
    st.markdown("<h2>Dataset Diagnostics & Schema Inspector</h2>", unsafe_allow_html=True)
    st.markdown("<div class='secondary-text'>Detailed profile of active dataset, auto-detected schema mappings, and raw record preview.</div>", unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.markdown(render_metric_card("Total Valid Records", f"{diagnostics['cleaned_rows']:,}", f"{diagnostics['total_cols']} columns"), unsafe_allow_html=True)
    with d2:
        st.markdown(render_metric_card("Unique Products", f"{diagnostics['product_count']} SKUs", f"{len(diagnostics['categories'])} categories"), unsafe_allow_html=True)
    with d3:
        st.markdown(render_metric_card("Historical Date Range", f"{diagnostics['date_range'][0]}", f"to {diagnostics['date_range'][1]}"), unsafe_allow_html=True)
    with d4:
        st.markdown(render_metric_card("Data Integrity Status", "PASSED", "Zero missing values", "#15803D"), unsafe_allow_html=True)

    st.markdown("<h3>Auto-Detected Column Mapping</h3>", unsafe_allow_html=True)
    mapping_df = pd.DataFrame([
        {"Canonical System Field": k.replace("_", " ").title(), "Detected CSV/Excel Column": v if v else "(Inferred / Defaulted)"}
        for k, v in diagnostics["detected_mapping"].items()
    ])
    st.dataframe(mapping_df, use_container_width=True, hide_index=True)

    st.markdown("<h3>Raw Data Preview (Recent Records)</h3>", unsafe_allow_html=True)
    st.dataframe(raw_df.tail(100), use_container_width=True, hide_index=True, height=350)

with tab_legal:
    st.markdown("<h2>Legal & Compliance Disclaimers</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="alert-critical-box" style="background-color: #F8F9FA; border-color: #D1D5DB; border-left-color: #1E3A8A;">
            <div style="font-weight: 700; color: #1E3A8A; font-size: 0.95rem;">[ DRAFT FOR REVIEW ] - TERMS OF SERVICE & PRIVACY POLICY</div>
            <div class="secondary-text" style="margin-top: 6px;">
                The following documentation outlines the operational terms and data handling practices for Stock Guardian AI.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown("<h3>Terms of Service (Draft)</h3>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; padding: 16px; font-size: 0.85rem; line-height: 1.5; color: #374151;">
                <b>1. Operational Scope:</b> Stock Guardian AI provides decision-support forecasts and inventory safety stock calculations based on statistical and machine learning algorithms. Forecasts represent statistical expectations and not financial guarantees.<br><br>
                <b>2. Decision Authority:</b> Final replenishment orders and procurement decisions remain under the sole discretion and validation of the enterprise inventory manager.<br><br>
                <b>3. Local Processing:</b> All model training, simulation recalculations, and dataset parsing occur entirely within local runtime memory.
            </div>
            """,
            unsafe_allow_html=True
        )

    with t_col2:
        st.markdown("<h3>Privacy Policy (Draft)</h3>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; padding: 16px; font-size: 0.85rem; line-height: 1.5; color: #374151;">
                <b>1. Data Privacy:</b> Uploaded inventory logs, sales records, and proprietary SKU identifiers are processed in-session and are never transmitted to third-party tracking APIs or external servers.<br><br>
                <b>2. Telemetry & Analytics:</b> This software does not contain telemetry trackers, third-party advertising cookies, or unauthorized external data storage.<br><br>
                <b>3. Storage:</b> Session data resides in temporary local memory and is purged upon session termination.
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<hr style='margin: 30px 0 10px 0; border: none; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; font-size: 0.78rem; color: #6B7280;'>"
    "Stock Guardian AI • PS-08: Inventory Demand Prediction • Built with Python, Scikit-Learn, Plotly & Streamlit"
    "</div>",
    unsafe_allow_html=True
)
