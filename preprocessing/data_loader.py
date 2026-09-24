import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List

COLUMN_ALIASES = {
    "date": ["date", "timestamp", "datetime", "transaction_date", "day", "record_date", "ds"],
    "product_id": ["product_id", "product", "sku", "item_id", "item", "product_code", "id"],
    "product_name": ["product_name", "item_name", "title", "name", "description"],
    "category": ["category", "dept", "department", "group", "product_group", "type"],
    "sales_units": ["sales_units", "sales", "quantity", "units_sold", "demand", "qty", "volume", "sold_units", "y"],
    "stock_on_hand": ["stock_on_hand", "stock", "inventory", "inventory_level", "current_stock", "qty_on_hand", "units_in_stock", "on_hand"],
    "unit_price": ["unit_price", "price", "selling_price", "mrp", "unit_cost", "cost"],
    "lead_time_days": ["lead_time_days", "lead_time", "delivery_days", "lead_days", "supplier_lead_time"],
    "promotion_active": ["promotion_active", "promotion", "promo", "is_promo", "discount_active", "sale_event"]
}

class DataLoader:
    @staticmethod
    def detect_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
        lower_cols = {col.lower().strip().replace(" ", "_"): col for col in df.columns}
        mapping: Dict[str, Optional[str]] = {}

        for canonical_name, aliases in COLUMN_ALIASES.items():
            matched = None
            for alias in aliases:
                clean_alias = alias.lower().replace(" ", "_")
                if clean_alias in lower_cols:
                    matched = lower_cols[clean_alias]
                    break
            mapping[canonical_name] = matched

        return mapping

    @staticmethod
    def validate_and_standardize(
        df: pd.DataFrame,
        custom_mapping: Optional[Dict[str, str]] = None
    ) -> Tuple[pd.DataFrame, Dict[str, any]]:
        detected = DataLoader.detect_columns(df)
        if custom_mapping:
            detected.update(custom_mapping)

        required = ["date", "sales_units"]
        missing_required = [req for req in required if not detected.get(req)]

        diagnostics = {
            "total_rows": len(df),
            "total_cols": len(df.columns),
            "detected_mapping": detected,
            "missing_required": missing_required,
            "is_valid": len(missing_required) == 0,
            "null_counts": df.isnull().sum().to_dict(),
            "date_range": (None, None),
            "product_count": 0,
            "categories": []
        }

        if not diagnostics["is_valid"]:
            return df, diagnostics

        clean_df = df.copy()
        rename_dict = {}
        for canonical, orig in detected.items():
            if orig and orig in clean_df.columns:
                rename_dict[orig] = canonical.title() if "_" not in canonical else "_".join(w.capitalize() for w in canonical.split("_"))
                if canonical == "date":
                    rename_dict[orig] = "Date"
                elif canonical == "product_id":
                    rename_dict[orig] = "Product_ID"
                elif canonical == "product_name":
                    rename_dict[orig] = "Product_Name"
                elif canonical == "category":
                    rename_dict[orig] = "Category"
                elif canonical == "sales_units":
                    rename_dict[orig] = "Sales_Units"
                elif canonical == "stock_on_hand":
                    rename_dict[orig] = "Stock_On_Hand"
                elif canonical == "unit_price":
                    rename_dict[orig] = "Unit_Price"
                elif canonical == "lead_time_days":
                    rename_dict[orig] = "Lead_Time_Days"
                elif canonical == "promotion_active":
                    rename_dict[orig] = "Promotion_Active"

        clean_df = clean_df.rename(columns=rename_dict)
        clean_df["Date"] = pd.to_datetime(clean_df["Date"], errors="coerce")
        clean_df = clean_df.dropna(subset=["Date"])
        clean_df = clean_df.sort_values(by="Date").reset_index(drop=True)

        if "Product_ID" not in clean_df.columns:
            if "Product_Name" in clean_df.columns:
                clean_df["Product_ID"] = clean_df["Product_Name"].astype(str)
            else:
                clean_df["Product_ID"] = "DEFAULT_SKU"

        if "Product_Name" not in clean_df.columns:
            clean_df["Product_Name"] = clean_df["Product_ID"]

        if "Category" not in clean_df.columns:
            clean_df["Category"] = "General Merchandise"

        if "Stock_On_Hand" not in clean_df.columns:
            avg_demand = clean_df["Sales_Units"].mean()
            clean_df["Stock_On_Hand"] = max(10, int(avg_demand * 5))

        if "Unit_Price" not in clean_df.columns:
            clean_df["Unit_Price"] = 19.99

        if "Lead_Time_Days" not in clean_df.columns:
            clean_df["Lead_Time_Days"] = 7

        if "Promotion_Active" not in clean_df.columns:
            clean_df["Promotion_Active"] = 0

        clean_df["Sales_Units"] = pd.to_numeric(clean_df["Sales_Units"], errors="coerce").fillna(0).clip(lower=0)
        clean_df["Stock_On_Hand"] = pd.to_numeric(clean_df["Stock_On_Hand"], errors="coerce").fillna(0).clip(lower=0)
        clean_df["Unit_Price"] = pd.to_numeric(clean_df["Unit_Price"], errors="coerce").fillna(19.99).clip(lower=0.01)
        clean_df["Lead_Time_Days"] = pd.to_numeric(clean_df["Lead_Time_Days"], errors="coerce").fillna(7).astype(int).clip(lower=1)
        clean_df["Promotion_Active"] = pd.to_numeric(clean_df["Promotion_Active"], errors="coerce").fillna(0).astype(int)

        diagnostics["date_range"] = (
            clean_df["Date"].min().strftime("%Y-%m-%d"),
            clean_df["Date"].max().strftime("%Y-%m-%d")
        )
        diagnostics["product_count"] = clean_df["Product_ID"].nunique()
        diagnostics["categories"] = sorted(clean_df["Category"].unique().tolist())
        diagnostics["cleaned_rows"] = len(clean_df)

        return clean_df, diagnostics

    @staticmethod
    def load_file(file_obj_or_path) -> Tuple[Optional[pd.DataFrame], Dict[str, any]]:
        try:
            if hasattr(file_obj_or_path, "name"):
                name = file_obj_or_path.name.lower()
                if name.endswith(".csv"):
                    df = pd.read_csv(file_obj_or_path)
                elif name.endswith((".xlsx", ".xls")):
                    df = pd.read_excel(file_obj_or_path)
                else:
                    return None, {"error": "Unsupported file format. Please upload CSV or Excel (.xlsx)."}
            else:
                path = str(file_obj_or_path)
                if path.endswith(".csv"):
                    df = pd.read_csv(path)
                else:
                    df = pd.read_excel(path)

            return DataLoader.validate_and_standardize(df)
        except Exception as e:
            return None, {"error": f"Failed to parse file: {str(e)}", "is_valid": False}
