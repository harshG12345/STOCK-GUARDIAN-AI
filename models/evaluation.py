import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class ModelEvaluator:
    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        y_t = np.array(y_true, dtype=float)
        y_p = np.array(y_pred, dtype=float)

        if len(y_t) == 0 or len(y_p) == 0:
            return {"MAE": 0.0, "RMSE": 0.0, "R2": 0.0, "Safe_MAPE": 0.0}

        mae = float(mean_absolute_error(y_t, y_p))
        rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))
        
        if np.var(y_t) < 1e-6:
            r2 = 1.0 if mae < 1e-6 else 0.0
        else:
            r2 = float(r2_score(y_t, y_p))

        non_zero_mask = y_t > 0
        if np.sum(non_zero_mask) > 0:
            safe_mape = float(np.mean(np.abs((y_t[non_zero_mask] - y_p[non_zero_mask]) / y_t[non_zero_mask])) * 100.0)
        else:
            safe_mape = float(np.mean(np.abs(y_t - y_p) / (y_t + 1.0)) * 100.0)

        return {
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "R2": round(r2, 3),
            "Safe_MAPE": round(safe_mape, 1)
        }

    @staticmethod
    def compare_models(
        y_true: np.ndarray,
        baseline_preds: np.ndarray,
        ml_preds: np.ndarray,
        baseline_name: str = "Baseline (Moving Avg)",
        ml_name: str = "ML Model (Supervised)"
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        base_metrics = ModelEvaluator.calculate_metrics(y_true, baseline_preds)
        ml_metrics = ModelEvaluator.calculate_metrics(y_true, ml_preds)

        comparison_df = pd.DataFrame([
            {
                "Model": baseline_name,
                "MAE (Units)": base_metrics["MAE"],
                "RMSE (Units)": base_metrics["RMSE"],
                "R² Score": base_metrics["R2"],
                "MAPE (%)": f"{base_metrics['Safe_MAPE']}%"
            },
            {
                "Model": ml_name,
                "MAE (Units)": ml_metrics["MAE"],
                "RMSE (Units)": ml_metrics["RMSE"],
                "R² Score": ml_metrics["R2"],
                "MAPE (%)": f"{ml_metrics['Safe_MAPE']}%"
            }
        ])

        mae_delta = base_metrics["MAE"] - ml_metrics["MAE"]
        mae_pct_reduction = round((mae_delta / (base_metrics["MAE"] + 1e-5) * 100.0), 1) if base_metrics["MAE"] > 0 else 0.0

        rmse_delta = base_metrics["RMSE"] - ml_metrics["RMSE"]
        rmse_pct_reduction = round((rmse_delta / (base_metrics["RMSE"] + 1e-5) * 100.0), 1) if base_metrics["RMSE"] > 0 else 0.0

        analysis = {
            "winner": ml_name if ml_metrics["MAE"] <= base_metrics["MAE"] else baseline_name,
            "mae_reduction_pct": mae_pct_reduction,
            "rmse_reduction_pct": rmse_pct_reduction,
            "is_ml_better": ml_metrics["MAE"] < base_metrics["MAE"],
            "base_metrics": base_metrics,
            "ml_metrics": ml_metrics
        }

        return comparison_df, analysis
