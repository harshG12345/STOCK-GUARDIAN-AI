import numpy as np
import pandas as pd
from typing import Optional

class BaselineDemandModel:
    def __init__(self, window_size: int = 7):
        self.window_size = window_size
        self.model_name = f"Baseline ({window_size}-Day Moving Average)"
        self.historical_mean: float = 0.0
        self.last_window_values: list = []

    def fit(self, y_train: pd.Series) -> "BaselineDemandModel":
        clean_y = pd.Series(y_train).fillna(0)
        self.historical_mean = float(clean_y.mean()) if len(clean_y) > 0 else 0.0
        if len(clean_y) >= self.window_size:
            self.last_window_values = clean_y.iloc[-self.window_size:].tolist()
        else:
            self.last_window_values = clean_y.tolist()
        return self

    def predict(self, X_test: pd.DataFrame, past_y: Optional[pd.Series] = None) -> np.ndarray:
        if "Rolling_Mean_7" in X_test.columns:
            preds = X_test["Rolling_Mean_7"].to_numpy()
        elif "Lag_1" in X_test.columns:
            preds = X_test["Lag_1"].to_numpy()
        else:
            baseline_val = np.mean(self.last_window_values) if self.last_window_values else self.historical_mean
            preds = np.full(len(X_test), baseline_val)

        return np.maximum(0, preds)
