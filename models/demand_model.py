import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor

class MLDemandModel:
    def __init__(self, model_type: str = "RandomForest", random_state: int = 42):
        self.model_type = model_type
        self.random_state = random_state
        self.model_name = f"ML Model ({model_type})"
        self.feature_names: List[str] = []
        self.feature_importances_: Dict[str, float] = {}

        if model_type == "HistGradientBoosting":
            self.model = HistGradientBoostingRegressor(
                max_iter=100,
                max_depth=5,
                min_samples_leaf=4,
                learning_rate=0.08,
                random_state=random_state
            )
        else:
            self.model = RandomForestRegressor(
                n_estimators=60,
                max_depth=8,
                min_samples_split=3,
                random_state=random_state,
                n_jobs=-1
            )

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> "MLDemandModel":
        self.feature_names = list(X_train.columns)
        clean_X = X_train.fillna(0)
        clean_y = y_train.fillna(0)
        
        self.model.fit(clean_X, clean_y)
        
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            total = float(np.sum(importances))
            norm = (importances / total) if total > 0 else np.ones(len(importances)) / len(importances)
            self.feature_importances_ = {name: float(imp) for name, imp in zip(self.feature_names, norm)}
        else:
            variances = np.var(clean_X.values, axis=0)
            corrs = np.array([np.abs(np.corrcoef(clean_X.iloc[:, i], clean_y)[0, 1]) if np.std(clean_X.iloc[:, i]) > 1e-5 else 0 for i in range(clean_X.shape[1])])
            corrs = np.nan_to_num(corrs, nan=0.0)
            total = np.sum(corrs)
            norm = (corrs / total) if total > 0 else np.ones(len(corrs)) / len(corrs)
            self.feature_importances_ = {name: float(imp) for name, imp in zip(self.feature_names, norm)}
                
        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        clean_X = X_test[self.feature_names].fillna(0)
        raw_preds = self.model.predict(clean_X)
        return np.maximum(0, raw_preds)

    def recursive_forecast(
        self,
        recent_df: pd.DataFrame,
        horizon_days: int = 14,
        unit_price: float = 19.99,
        promotion_active: int = 0
    ) -> pd.DataFrame:
        last_date = pd.to_datetime(recent_df["Date"].max())
        history_sales = list(recent_df["Sales_Units"].values)
        forecast_rows = []

        for h in range(1, horizon_days + 1):
            future_date = last_date + pd.Timedelta(days=h)
            dow = future_date.dayofweek
            month = future_date.month
            quarter = (month - 1) // 3 + 1
            day_of_month = future_date.day
            is_weekend = 1 if dow in [5, 6] else 0

            lag_1 = history_sales[-1] if len(history_sales) >= 1 else 0
            lag_7 = history_sales[-7] if len(history_sales) >= 7 else lag_1
            lag_14 = history_sales[-14] if len(history_sales) >= 14 else lag_7

            roll_7 = np.mean(history_sales[-7:]) if len(history_sales) >= 7 else lag_1
            roll_14 = np.mean(history_sales[-14:]) if len(history_sales) >= 14 else roll_7
            roll_std_7 = np.std(history_sales[-7:]) if len(history_sales) >= 7 else 0

            row_dict = {
                "DayOfWeek": dow,
                "Month": month,
                "Quarter": quarter,
                "DayOfMonth": day_of_month,
                "IsWeekend": is_weekend,
                "Lag_1": lag_1,
                "Lag_7": lag_7,
                "Lag_14": lag_14,
                "Rolling_Mean_7": roll_7,
                "Rolling_Mean_14": roll_14,
                "Rolling_Std_7": roll_std_7,
                "Promotion_Active": promotion_active,
                "Unit_Price": unit_price
            }

            row_df = pd.DataFrame([row_dict])
            pred_demand = float(self.predict(row_df)[0])
            pred_demand = max(0.0, pred_demand)

            history_sales.append(pred_demand)

            forecast_rows.append({
                "Date": future_date,
                "Forecast_Demand": round(pred_demand, 1),
                "Horizon_Day": h
            })

        return pd.DataFrame(forecast_rows)
