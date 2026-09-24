import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

class InventoryRiskEngine:
    @staticmethod
    def detect_demand_trend(historical_series: pd.Series, window: int = 14) -> Dict[str, Any]:
        clean_s = historical_series.dropna()
        if len(clean_s) < 5:
            return {"trend": "STABLE", "slope": 0.0, "pct_change": 0.0}

        recent = clean_s.iloc[-window:] if len(clean_s) >= window else clean_s
        x = np.arange(len(recent))
        y = recent.values

        slope, _ = np.polyfit(x, y, 1)
        mean_val = np.mean(y) if np.mean(y) > 0 else 1.0
        norm_slope = slope / mean_val

        half = len(recent) // 2
        first_half = np.mean(recent.iloc[:half]) if half > 0 else 1.0
        second_half = np.mean(recent.iloc[half:])
        pct_change = ((second_half - first_half) / (first_half + 1e-5)) * 100.0

        if norm_slope > 0.02 or pct_change > 15.0:
            trend = "INCREASING"
        elif norm_slope < -0.02 or pct_change < -15.0:
            trend = "DECREASING"
        else:
            trend = "STABLE"

        return {
            "trend": trend,
            "slope": round(float(slope), 3),
            "normalized_slope": round(float(norm_slope), 4),
            "pct_change": round(float(pct_change), 1)
        }

    @staticmethod
    def detect_demand_shock(
        historical_series: pd.Series,
        recent_window: int = 7,
        baseline_window: int = 30
    ) -> Dict[str, Any]:
        clean_s = historical_series.dropna()
        if len(clean_s) < 14:
            return {
                "shock_status": "NORMAL",
                "z_score": 0.0,
                "pct_deviation": 0.0,
                "recent_mean": float(clean_s.mean()) if len(clean_s) > 0 else 0.0,
                "baseline_mean": float(clean_s.mean()) if len(clean_s) > 0 else 0.0
            }

        recent = clean_s.iloc[-recent_window:]
        baseline = clean_s.iloc[-baseline_window:-recent_window] if len(clean_s) >= baseline_window else clean_s.iloc[:-recent_window]

        if len(baseline) == 0:
            baseline = clean_s

        b_mean = float(baseline.mean())
        b_std = float(baseline.std()) if float(baseline.std()) > 1e-3 else (b_mean * 0.1 + 1.0)
        r_mean = float(recent.mean())

        z_score = (r_mean - b_mean) / b_std
        pct_dev = ((r_mean - b_mean) / (b_mean + 1e-5)) * 100.0

        if z_score >= 2.0 or pct_dev >= 35.0:
            status = "UNUSUAL INCREASE"
        elif z_score <= -2.0 or pct_dev <= -30.0:
            status = "UNUSUAL DECREASE"
        else:
            status = "NORMAL"

        return {
            "shock_status": status,
            "z_score": round(float(z_score), 2),
            "pct_deviation": round(float(pct_dev), 1),
            "recent_mean": round(r_mean, 1),
            "baseline_mean": round(b_mean, 1)
        }

    @staticmethod
    def calculate_risk_score(
        current_inventory: float,
        predicted_demand: float,
        historical_series: pd.Series,
        lead_time_days: int = 7
    ) -> Dict[str, Any]:
        demand_gap = max(0.0, predicted_demand - current_inventory)
        coverage_ratio = current_inventory / (predicted_demand + 1e-5)

        if coverage_ratio >= 1.5:
            s_coverage = 0.0
        elif coverage_ratio >= 1.0:
            s_coverage = (1.5 - coverage_ratio) * 40.0
        elif coverage_ratio >= 0.5:
            s_coverage = 20.0 + (1.0 - coverage_ratio) * 80.0
        else:
            s_coverage = 60.0 + (0.5 - coverage_ratio) * 80.0
        s_coverage = float(np.clip(s_coverage, 0.0, 100.0))

        trend_info = InventoryRiskEngine.detect_demand_trend(historical_series)
        if trend_info["trend"] == "INCREASING":
            s_trend = 80.0 if trend_info["pct_change"] > 30 else 60.0
        elif trend_info["trend"] == "STABLE":
            s_trend = 30.0
        else:
            s_trend = 10.0

        if coverage_ratio >= 1.5:
            s_trend *= 0.3
            s_volatility_damp = 0.3
        else:
            s_volatility_damp = 1.0

        std_val = float(historical_series.std()) if len(historical_series) > 1 else 0.0
        mean_val = float(historical_series.mean()) if float(historical_series.mean()) > 1e-3 else 1.0
        cv = std_val / mean_val
        s_volatility = float(np.clip(cv * 100.0, 0.0, 100.0)) * s_volatility_damp
        s_lead_time = float(np.clip((lead_time_days / 20.0) * 100.0, 0.0, 100.0))

        composite_score = (
            0.45 * s_coverage +
            0.20 * s_trend +
            0.20 * s_volatility +
            0.15 * s_lead_time
        )
        final_score = int(np.clip(round(composite_score), 0, 100))

        if final_score >= 70 or coverage_ratio < 0.40:
            risk_level = "CRITICAL"
            action_code = "IMMEDIATE EXPEDITED REORDER"
            badge_color = "#DC2626"
        elif final_score >= 45 or coverage_ratio < 0.80:
            risk_level = "HIGH RISK"
            action_code = "URGENT REORDER REQUIRED"
            badge_color = "#EA580C"
        elif (final_score >= 25 or coverage_ratio < 1.20) and coverage_ratio < 1.5:
            risk_level = "WATCH"
            action_code = "MONITOR & SCHEDULE REPLENISHMENT"
            badge_color = "#D97706"
        else:
            risk_level = "SAFE"
            action_code = "INVENTORY SUFFICIENT"
            badge_color = "#15803D"

        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "action_code": action_code,
            "badge_color": badge_color,
            "current_inventory": int(current_inventory),
            "predicted_demand": round(float(predicted_demand), 1),
            "demand_gap": round(float(demand_gap), 1),
            "coverage_ratio": round(float(coverage_ratio), 2),
            "trend": trend_info["trend"],
            "trend_details": trend_info,
            "volatility_cv": round(cv, 2),
            "lead_time_days": lead_time_days,
            "component_scores": {
                "coverage_deficit": round(s_coverage, 1),
                "trend_acceleration": round(s_trend, 1),
                "demand_volatility": round(s_volatility, 1),
                "lead_time_exposure": round(s_lead_time, 1)
            }
        }
