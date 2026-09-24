import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class DataPreprocessor:
    @staticmethod
    def prepare_product_series(df: pd.DataFrame, product_id: Optional[str] = None) -> pd.DataFrame:
        if product_id is not None:
            sub_df = df[df["Product_ID"] == product_id].copy()
        else:
            sub_df = df.groupby("Date", as_index=False).agg({
                "Sales_Units": "sum",
                "Stock_On_Hand": "sum",
                "Unit_Price": "mean",
                "Lead_Time_Days": "mean",
                "Promotion_Active": "max"
            })
            sub_df["Product_ID"] = "ALL_AGGREGATED"
            sub_df["Product_Name"] = "All Products (Portfolio)"
            sub_df["Category"] = "Portfolio"

        sub_df["Date"] = pd.to_datetime(sub_df["Date"])
        sub_df = sub_df.sort_values("Date").drop_duplicates(subset=["Date"])

        if len(sub_df) > 1:
            full_idx = pd.date_range(start=sub_df["Date"].min(), end=sub_df["Date"].max(), freq="D")
            sub_df = sub_df.set_index("Date").reindex(full_idx)
            sub_df.index.name = "Date"
            sub_df = sub_df.reset_index()

            if product_id is not None:
                orig_prod = df[df["Product_ID"] == product_id].iloc[0]
                sub_df["Product_ID"] = product_id
                sub_df["Product_Name"] = orig_prod.get("Product_Name", product_id)
                sub_df["Category"] = orig_prod.get("Category", "General")
                sub_df["Lead_Time_Days"] = orig_prod.get("Lead_Time_Days", 7)
            else:
                sub_df["Product_ID"] = "ALL_AGGREGATED"
                sub_df["Product_Name"] = "All Products (Portfolio)"
                sub_df["Category"] = "Portfolio"
                sub_df["Lead_Time_Days"] = 7

            sub_df["Sales_Units"] = sub_df["Sales_Units"].fillna(0)
            sub_df["Stock_On_Hand"] = sub_df["Stock_On_Hand"].ffill().bfill().fillna(0)
            sub_df["Unit_Price"] = sub_df["Unit_Price"].ffill().bfill().fillna(19.99)
            sub_df["Promotion_Active"] = sub_df["Promotion_Active"].fillna(0).astype(int)

        return sub_df

    @staticmethod
    def get_product_metadata(df: pd.DataFrame) -> List[Dict[str, any]]:
        products = []
        for pid, group in df.groupby("Product_ID"):
            latest = group.sort_values("Date").iloc[-1]
            pname = latest.get("Product_Name", pid)
            cat = latest.get("Category", "General")
            curr_stock = int(latest.get("Stock_On_Hand", 0))
            avg_daily_demand = round(float(group["Sales_Units"].mean()), 1)
            total_sales = int(group["Sales_Units"].sum())
            lead_time = int(latest.get("Lead_Time_Days", 7))
            unit_price = float(latest.get("Unit_Price", 19.99))
            
            products.append({
                "Product_ID": pid,
                "Product_Name": pname,
                "Category": cat,
                "Current_Stock": curr_stock,
                "Avg_Daily_Demand": avg_daily_demand,
                "Total_Sales": total_sales,
                "Lead_Time_Days": lead_time,
                "Unit_Price": unit_price,
                "Records_Count": len(group)
            })
            
        return sorted(products, key=lambda x: x["Total_Sales"], reverse=True)
