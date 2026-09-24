import pandas as pd
from typing import Tuple

class ChronologicalTimeSplitter:
    @staticmethod
    def split(
        df: pd.DataFrame,
        train_ratio: float = 0.80,
        date_col: str = "Date"
    ) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
        sorted_df = df.sort_values(by=date_col).reset_index(drop=True)
        total_rows = len(sorted_df)
        
        if total_rows < 10:
            split_idx = max(1, total_rows - 2)
        else:
            split_idx = int(total_rows * train_ratio)

        train_df = sorted_df.iloc[:split_idx].copy()
        test_df = sorted_df.iloc[split_idx:].copy()

        train_start = train_df[date_col].min()
        train_end = train_df[date_col].max()
        test_start = test_df[date_col].min()
        test_end = test_df[date_col].max()

        metadata = {
            "methodology": "Chronological Out-of-Time Validation (Zero Future-Data Leakage)",
            "train_ratio": train_ratio,
            "train_size": len(train_df),
            "test_size": len(test_df),
            "train_start_date": str(train_start)[:10] if pd.notnull(train_start) else "N/A",
            "train_end_date": str(train_end)[:10] if pd.notnull(train_end) else "N/A",
            "test_start_date": str(test_start)[:10] if pd.notnull(test_start) else "N/A",
            "test_end_date": str(test_end)[:10] if pd.notnull(test_end) else "N/A",
            "split_date": str(test_start)[:10] if pd.notnull(test_start) else "N/A",
            "train_date_range": [str(train_start)[:10] if pd.notnull(train_start) else "N/A", str(train_end)[:10] if pd.notnull(train_end) else "N/A"],
            "test_date_range": [str(test_start)[:10] if pd.notnull(test_start) else "N/A", str(test_end)[:10] if pd.notnull(test_end) else "N/A"],
            "leakage_check_passed": bool(train_end <= test_start) if (pd.notnull(train_end) and pd.notnull(test_start)) else True
        }

        return train_df, test_df, metadata
