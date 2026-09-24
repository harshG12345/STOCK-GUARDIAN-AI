import numpy as np
import pandas as pd
from typing import Dict, Any

class WhatIfSimulator:
    @staticmethod
    def simulate_scenario(
        base_predicted_demand: float,
        current_inventory: float,
        historical_daily_demand: pd.Series,
        demand_pct_change: float = 0.0,
        inventory_override: float = None,
        safety_multiplier: float = 1.0,
        lead_time_days: int = 7,
        forecast_horizon_days: int = 14
    ) -> Dict[str, Any]:
        stock = current_inventory if inventory_override is None else inventory_override
        demand_multiplier = 1.0 + (demand_pct_change / 100.0)
        adjusted_predicted_demand = max(0.0, base_predicted_demand * demand_multiplier)

        demand_std = float(historical_daily_demand.std()) if len(historical_daily_demand) > 1 else (base_predicted_demand * 0.15)
        demand_std = max(0.5, demand_std)
        z_factor = 1.645
        base_buffer = z_factor * demand_std * np.sqrt(max(1, lead_time_days))
        simulated_buffer = int(np.ceil(base_buffer * safety_multiplier))

        simulated_target_stock = int(np.ceil(adjusted_predicted_demand + simulated_buffer))
        simulated_additional_stock = max(0, int(np.ceil(simulated_target_stock - stock)))

        potential_shortage = max(0.0, adjusted_predicted_demand - stock)
        net_stock_after_period = stock - adjusted_predicted_demand

        daily_burn = adjusted_predicted_demand / max(1, forecast_horizon_days)
        estimated_days_to_stockout = (stock / daily_burn) if daily_burn > 0 else 999.0
        stockout_occurs = estimated_days_to_stockout < forecast_horizon_days

        coverage_ratio = stock / (adjusted_predicted_demand + 1e-5)
        if coverage_ratio < 0.40 or estimated_days_to_stockout < lead_time_days:
            simulated_risk_level = "CRITICAL"
            badge_color = "#DC2626"
            action_summary = "STOCKOUT IMMINENT BEFORE SUPPLIER ARRIVAL"
        elif coverage_ratio < 0.80 or estimated_days_to_stockout < (lead_time_days * 1.5):
            simulated_risk_level = "HIGH RISK"
            badge_color = "#EA580C"
            action_summary = "HIGH STOCKOUT RISK - EXPEDITE ORDER"
        elif coverage_ratio < 1.15:
            simulated_risk_level = "WATCH"
            badge_color = "#D97706"
            action_summary = "TIGHT INVENTORY - SCHEDULE REPLENISHMENT"
        else:
            simulated_risk_level = "SAFE"
            badge_color = "#15803D"
            action_summary = "INVENTORY SUFFICIENT TO MEET SURGE"

        return {
            "demand_pct_change": demand_pct_change,
            "base_predicted_demand": round(float(base_predicted_demand), 1),
            "adjusted_predicted_demand": round(float(adjusted_predicted_demand), 1),
            "current_stock": int(stock),
            "potential_shortage": round(float(potential_shortage), 1),
            "net_stock_after_period": round(float(net_stock_after_period), 1),
            "simulated_buffer": simulated_buffer,
            "simulated_target_stock": simulated_target_stock,
            "simulated_additional_stock": simulated_additional_stock,
            "estimated_days_to_stockout": round(float(estimated_days_to_stockout), 1),
            "stockout_occurs": stockout_occurs,
            "simulated_risk_level": simulated_risk_level,
            "badge_color": badge_color,
            "action_summary": action_summary,
            "coverage_ratio": round(float(coverage_ratio), 2),
            "lead_time_days": lead_time_days,
            "forecast_horizon_days": forecast_horizon_days
        }
