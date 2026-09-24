export interface KPIStats {
  total_products: number;
  critical_stockouts: number;
  high_risk: number;
  watch: number;
  safe: number;
  total_reorder_units: number;
  total_reorder_capital: number;
  avg_predicted_demand: number;
  forecast_horizon_days: number;
  service_level: string;
  active_dataset: string;
}

export interface ShockAlert {
  product_id: string;
  product_name: string;
  category: string;
  shock_status: string;
  z_score: number;
  pct_deviation: number;
  recent_mean: number;
  baseline_mean: number;
  current_stock: number;
  days_of_supply: number;
}

export interface CriticalAlert {
  product_id: string;
  product_name: string;
  risk_level: string;
  risk_score: number;
  current_stock: number;
  predicted_demand: number;
  demand_gap: number;
  reorder_units: number;
  days_of_supply: number;
  action_code: string;
}

export interface ProductSummary {
  product_id: string;
  product_name: string;
  category: string;
  current_stock: number;
  predicted_demand: number;
  demand_gap: number;
  risk_score: number;
  risk_level: string;
  badge_color: string;
  trend: string;
  trend_pct: number;
  shock_status: string;
  recommended_additional_stock: number;
  days_of_supply: number;
  estimated_capital: number;
  lead_time_days: number;
  action_code: string;
}

export interface DashboardSummaryResponse {
  kpis: KPIStats;
  shock_alerts: ShockAlert[];
  critical_alerts: CriticalAlert[];
  categories: string[];
  products_table: ProductSummary[];
  diagnostics: {
    cleaned_rows: number;
    product_count: number;
    date_range: [string, string];
  };
}

export interface HistoryRecord {
  Date: string;
  Sales_Units: number;
  Stock_On_Hand: number;
  Unit_Price: number;
  Promotion_Active: number;
}

export interface ForecastRecord {
  Date: string;
  Forecast_Demand: number;
  Horizon_Day: number;
}

export interface TestEvaluationRecord {
  Date: string;
  Actual: number;
  Baseline_Pred: number;
  ML_Pred: number;
  Residual_ML: number;
}

export interface ProductForecastResponse {
  product_id: string;
  product_name: string;
  category: string;
  current_stock: number;
  lead_time_days: number;
  unit_price: number;
  forecast_horizon_days: number;
  total_predicted_demand: number;
  avg_daily_forecast: number;
  history: HistoryRecord[];
  forecast_breakdown: ForecastRecord[];
  feature_importances: Record<string, number>;
}

export interface RiskInfo {
  risk_score: number;
  risk_level: string;
  action_code: string;
  badge_color: string;
  current_inventory: number;
  predicted_demand: number;
  demand_gap: number;
  coverage_ratio: number;
  trend: string;
  trend_details: {
    trend: string;
    slope: number;
    normalized_slope: number;
    pct_change: number;
  };
  volatility_cv: number;
  lead_time_days: number;
  component_scores: {
    coverage_deficit: number;
    trend_acceleration: number;
    demand_volatility: number;
    lead_time_exposure: number;
  };
}

export interface ReorderPlan {
  product_name: string;
  current_inventory: number;
  predicted_demand: number;
  safety_buffer: number;
  recommended_target_inventory: number;
  recommended_additional_stock: number;
  estimated_capital_required: number;
  days_of_supply: number;
  service_level: string;
  z_factor: number;
  daily_demand_std: number;
  lead_time_days: number;
  unit_cost: number;
  formula_breakdown: {
    step_1_safety_buffer: string;
    step_2_target_inventory: string;
    step_3_reorder_qty: string;
  };
}

export interface ProductRiskResponse {
  product_id: string;
  product_name: string;
  risk_info: RiskInfo;
  reorder_plan: ReorderPlan;
  shock_status: string;
  shock_z: number;
  shock_dev_pct: number;
}

export interface SimulationResult {
  demand_pct_change: number;
  base_predicted_demand: number;
  adjusted_predicted_demand: number;
  current_stock: number;
  potential_shortage: number;
  net_stock_after_period: number;
  simulated_buffer: number;
  simulated_target_stock: number;
  simulated_additional_stock: number;
  estimated_days_to_stockout: number;
  stockout_occurs: boolean;
  simulated_risk_level: string;
  badge_color: string;
  action_summary: string;
  coverage_ratio: number;
  lead_time_days: number;
  forecast_horizon_days: number;
}

export interface WhatIfResponse {
  product_id: string;
  product_name: string;
  unit_price: number;
  simulation: SimulationResult;
}

export interface ModelPerformanceResponse {
  selected_product: {
    product_id: string;
    product_name: string;
    ml_mae: number;
    base_mae: number;
    ml_rmse: number;
    base_rmse: number;
    ml_r2: number;
    base_r2: number;
    ml_mape: number;
    base_mape: number;
    split_meta: {
      train_size: number;
      test_size: number;
      split_date?: string;
      train_start_date?: string;
      train_end_date?: string;
      test_start_date?: string;
      test_end_date?: string;
      train_date_range?: [string, string];
      test_date_range?: [string, string];
      leakage_check_passed?: boolean;
    };
    feature_importances: Record<string, number>;
    test_evaluation_records: TestEvaluationRecord[];
  };
  portfolio_aggregate: {
    avg_ml_mae: number;
    avg_base_mae: number;
    avg_ml_rmse: number;
    avg_base_rmse: number;
    avg_ml_r2: number;
    mae_improvement_pct: number;
    model_type: string;
    total_skus_evaluated: number;
  };
}

export interface DataSummaryResponse {
  active_source: string;
  total_rows: number;
  cleaned_rows: number;
  total_cols: number;
  product_count: number;
  categories: string[];
  date_range: [string, string];
  detected_mapping: Record<string, string | null>;
  missing_required: string[];
  null_counts: Record<string, number>;
  columns: string[];
  preview_records: Record<string, any>[];
}

export interface HealthResponse {
  status: string;
  service: string;
  is_ready: boolean;
  product_count: number;
  active_source: string;
  forecast_horizon_days: number;
  service_level: string;
}
