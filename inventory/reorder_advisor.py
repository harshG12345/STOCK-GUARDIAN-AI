import numpy as np
import pandas as pd
from typing import Dict, Any

class SmartReorderAdvisor:
    SERVICE_LEVEL_Z = {
        "90%": 1.282,
        "95%": 1.645,
        "98%": 2.054,
        "99%": 2.326
    }

    @staticmethod
    def calculate_reorder_plan(
        product_name: str,
        current_inventory: float,
        predicted_demand: float,
        historical_daily_demand: pd.Series,
        lead_time_days: int = 7,
        service_level: str = "95%",
        unit_cost: float = 19.99
    ) -> Dict[str, Any]:
        z_factor = SmartReorderAdvisor.SERVICE_LEVEL_Z.get(service_level, 1.645)
        demand_std = float(historical_daily_demand.std()) if len(historical_daily_demand) > 1 else (predicted_demand * 0.15)
        demand_std = max(0.5, demand_std)

        lead_time_factor = float(np.sqrt(max(1, lead_time_days)))
        safety_buffer = int(np.ceil(z_factor * demand_std * lead_time_factor))
        recommended_target_inventory = int(np.ceil(predicted_demand + safety_buffer))
        recommended_additional_stock = max(0, int(np.ceil(recommended_target_inventory - current_inventory)))
        estimated_capital = round(recommended_additional_stock * unit_cost, 2)

        daily_burn_rate = (predicted_demand / 14.0) if predicted_demand > 0 else 1.0
        days_of_supply = round(current_inventory / (daily_burn_rate + 1e-5), 1)

        return {
            "product_name": product_name,
            "current_inventory": int(current_inventory),
            "predicted_demand": round(float(predicted_demand), 1),
            "safety_buffer": safety_buffer,
            "recommended_target_inventory": recommended_target_inventory,
            "recommended_additional_stock": recommended_additional_stock,
            "estimated_capital_required": estimated_capital,
            "days_of_supply": days_of_supply,
            "service_level": service_level,
            "z_factor": z_factor,
            "daily_demand_std": round(demand_std, 2),
            "lead_time_days": lead_time_days,
            "unit_cost": unit_cost,
            "formula_breakdown": {
                "step_1_safety_buffer": f"{z_factor} (Z-Score for {service_level}) × {round(demand_std, 2)} (Daily Demand Std Dev) × √{lead_time_days} (Lead Time Days) = {safety_buffer} units",
                "step_2_target_inventory": f"{round(float(predicted_demand), 1)} (Forecast Demand) + {safety_buffer} (Safety Buffer) = {recommended_target_inventory} units",
                "step_3_reorder_qty": f"max(0, {recommended_target_inventory} Target - {int(current_inventory)} Current Stock) = {recommended_additional_stock} units to order immediately"
            }
        }
