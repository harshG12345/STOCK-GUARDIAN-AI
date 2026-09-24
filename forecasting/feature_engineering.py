import pandas as pd
import numpy as np
from typing import List, Tuple

class FeatureEngineer:
    FEATURE_COLS = [
        "DayOfWeek",
        "Month",
        "Quarter",
        "DayOfMonth",
        "IsWeekend",
        "Lag_1",
        "Lag_7",
        "Lag_14",
        "Rolling_Mean_7",
        "Rolling_Mean_14",
        "Rolling_Std_7",
        "Promotion_Active",
        "Unit_Price"
    ]

    @staticmethod
    def extract_features(df: pd.DataFrame, target_col: str = "Sales_Units") -> pd.DataFrame:
        feat_df = df.copy()
        feat_df["Date"] = pd.to_datetime(feat_df["Date"])
        feat_df = feat_df.sort_values("Date").reset_index(drop=True)

        feat_df["DayOfWeek"] = feat_df["Date"].dt.dayofweek
        feat_df["Month"] = feat_df["Date"].dt.month
        feat_df["Quarter"] = feat_df["Date"].dt.quarter
        feat_df["DayOfMonth"] = feat_df["Date"].dt.day
        feat_df["IsWeekend"] = feat_df["DayOfWeek"].isin([5, 6]).astype(int)

        y = feat_df[target_col]
        feat_df["Lag_1"] = y.shift(1)
        feat_df["Lag_7"] = y.shift(7)
        feat_df["Lag_14"] = y.shift(14)

        shifted_y = y.shift(1)
        feat_df["Rolling_Mean_7"] = shifted_y.rolling(window=7, min_periods=1).mean()
        feat_df["Rolling_Mean_14"] = shifted_y.rolling(window=14, min_periods=1).mean()
        feat_df["Rolling_Std_7"] = shifted_y.rolling(window=7, min_periods=1).std().fillna(0)

        if "Promotion_Active" not in feat_df.columns:
            feat_df["Promotion_Active"] = 0
        if "Unit_Price" not in feat_df.columns:
            feat_df["Unit_Price"] = 19.99

        feat_df["Lag_1"] = feat_df["Lag_1"].bfill().fillna(y.mean() if len(y) > 0 else 0)
        feat_df["Lag_7"] = feat_df["Lag_7"].bfill().fillna(feat_df["Lag_1"])
        feat_df["Lag_14"] = feat_df["Lag_14"].bfill().fillna(feat_df["Lag_7"])
        feat_df["Rolling_Mean_7"] = feat_df["Rolling_Mean_7"].bfill().fillna(y.mean() if len(y) > 0 else 0)
        feat_df["Rolling_Mean_14"] = feat_df["Rolling_Mean_14"].bfill().fillna(feat_df["Rolling_Mean_7"])
        feat_df["Rolling_Std_7"] = feat_df["Rolling_Std_7"].fillna(0)

        return feat_df

    @staticmethod
    def prepare_matrices(
        df: pd.DataFrame,
        target_col: str = "Sales_Units"
    ) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        feat_df = FeatureEngineer.extract_features(df, target_col=target_col)
        available_features = [col for col in FeatureEngineer.FEATURE_COLS if col in feat_df.columns]
        X = feat_df[available_features]
        y = feat_df[target_col]
        return X, y, available_features
