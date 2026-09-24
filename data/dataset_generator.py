import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_benchmark_dataset(
    output_path: str = "data/retail_inventory_history.csv",
    num_days: int = 540,
    seed: int = 42
) -> pd.DataFrame:
    np.random.seed(seed)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    start_date = datetime(2025, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    
    products = [
        {
            "Product_ID": "SKU-ELEC-101",
            "Product_Name": "Wireless Noise-Canceling Headphones",
            "Category": "Electronics",
            "Base_Demand": 45,
            "Volatility": 8,
            "Price": 149.99,
            "Lead_Time_Days": 10,
            "Trend_Slope": 0.04,
            "Weekend_Boost": 1.45,
            "Base_Stock": 110,
            "Stock_Depletion_Rate": 0.95
        },
        {
            "Product_ID": "SKU-ELEC-102",
            "Product_Name": "4K Ultra-HD Smart Monitor 27-inch",
            "Category": "Electronics",
            "Base_Demand": 28,
            "Volatility": 6,
            "Price": 299.99,
            "Lead_Time_Days": 14,
            "Trend_Slope": 0.02,
            "Weekend_Boost": 1.25,
            "Base_Stock": 42,
            "Stock_Depletion_Rate": 1.10
        },
        {
            "Product_ID": "SKU-ELEC-103",
            "Product_Name": "Ergonomic Mechanical Keyboard",
            "Category": "Electronics",
            "Base_Demand": 38,
            "Volatility": 7,
            "Price": 89.99,
            "Lead_Time_Days": 7,
            "Trend_Slope": 0.01,
            "Weekend_Boost": 1.30,
            "Base_Stock": 210,
            "Stock_Depletion_Rate": 0.85
        },
        {
            "Product_ID": "SKU-APPL-201",
            "Product_Name": "All-Weather Technical Parka Jacket",
            "Category": "Apparel",
            "Base_Demand": 22,
            "Volatility": 5,
            "Price": 189.50,
            "Lead_Time_Days": 12,
            "Trend_Slope": -0.015,
            "Weekend_Boost": 1.60,
            "Base_Stock": 65,
            "Stock_Depletion_Rate": 0.90
        },
        {
            "Product_ID": "SKU-APPL-202",
            "Product_Name": "Performance Running Shoes Pro",
            "Category": "Apparel",
            "Base_Demand": 62,
            "Volatility": 12,
            "Price": 129.00,
            "Lead_Time_Days": 8,
            "Trend_Slope": 0.05,
            "Weekend_Boost": 1.50,
            "Base_Stock": 75,
            "Stock_Depletion_Rate": 1.15
        },
        {
            "Product_ID": "SKU-HOME-301",
            "Product_Name": "Stainless Steel Espresso Machine",
            "Category": "Home & Kitchen",
            "Base_Demand": 18,
            "Volatility": 4,
            "Price": 349.00,
            "Lead_Time_Days": 15,
            "Trend_Slope": 0.01,
            "Weekend_Boost": 1.35,
            "Base_Stock": 35,
            "Stock_Depletion_Rate": 0.95
        },
        {
            "Product_ID": "SKU-HOME-302",
            "Product_Name": "Ceramic Non-Stick Cookware Set (10-Pc)",
            "Category": "Home & Kitchen",
            "Base_Demand": 30,
            "Volatility": 6,
            "Price": 119.99,
            "Lead_Time_Days": 10,
            "Trend_Slope": -0.005,
            "Weekend_Boost": 1.40,
            "Base_Stock": 140,
            "Stock_Depletion_Rate": 0.90
        },
        {
            "Product_ID": "SKU-HLTH-401",
            "Product_Name": "Sonic Electric Toothbrush Elite",
            "Category": "Health & Personal Care",
            "Base_Demand": 55,
            "Volatility": 9,
            "Price": 69.95,
            "Lead_Time_Days": 6,
            "Trend_Slope": 0.03,
            "Weekend_Boost": 1.20,
            "Base_Stock": 180,
            "Stock_Depletion_Rate": 0.92
        },
        {
            "Product_ID": "SKU-HLTH-402",
            "Product_Name": "Organic Whey Protein Isolate (2kg)",
            "Category": "Health & Personal Care",
            "Base_Demand": 70,
            "Volatility": 14,
            "Price": 54.99,
            "Lead_Time_Days": 5,
            "Trend_Slope": 0.06,
            "Weekend_Boost": 1.15,
            "Base_Stock": 80,
            "Stock_Depletion_Rate": 1.20
        },
        {
            "Product_ID": "SKU-GROC-501",
            "Product_Name": "Artisanal Single-Origin Coffee Beans (1kg)",
            "Category": "Groceries",
            "Base_Demand": 85,
            "Volatility": 15,
            "Price": 24.50,
            "Lead_Time_Days": 4,
            "Trend_Slope": 0.02,
            "Weekend_Boost": 1.25,
            "Base_Stock": 260,
            "Stock_Depletion_Rate": 0.95
        },
        {
            "Product_ID": "SKU-GROC-502",
            "Product_Name": "Organic Extra Virgin Olive Oil (1L)",
            "Category": "Groceries",
            "Base_Demand": 40,
            "Volatility": 7,
            "Price": 18.75,
            "Lead_Time_Days": 5,
            "Trend_Slope": 0.00,
            "Weekend_Boost": 1.30,
            "Base_Stock": 160,
            "Stock_Depletion_Rate": 0.88
        },
        {
            "Product_ID": "SKU-GROC-503",
            "Product_Name": "Premium Raw Manuka Honey MGO 500+",
            "Category": "Groceries",
            "Base_Demand": 15,
            "Volatility": 3,
            "Price": 48.00,
            "Lead_Time_Days": 9,
            "Trend_Slope": -0.01,
            "Weekend_Boost": 1.20,
            "Base_Stock": 95,
            "Stock_Depletion_Rate": 0.70
        }
    ]
    
    rows = []
    
    for p in products:
        current_inv = p["Base_Stock"]
        
        for t, date in enumerate(dates):
            day_of_week = date.weekday()
            month = date.month
            
            trend_val = p["Trend_Slope"] * t
            is_weekend = 1 if day_of_week in [5, 6] else 0
            dow_multiplier = p["Weekend_Boost"] if is_weekend else 1.0
            seasonality = 1.0 + 0.18 * np.sin(2 * np.pi * (date.timetuple().tm_yday) / 365.25)
            
            promo_cycle = (t % 48)
            is_promo = 1 if (promo_cycle in [14, 15, 16, 17]) else 0
            promo_multiplier = 1.35 if is_promo else 1.0
            
            shock_boost = 1.0
            if p["Product_ID"] == "SKU-APPL-202" and t >= (num_days - 12):
                shock_boost = 1.65
            elif p["Product_ID"] == "SKU-GROC-503" and t >= (num_days - 10):
                shock_boost = 0.60
                
            mean_demand = (p["Base_Demand"] + trend_val) * dow_multiplier * seasonality * promo_multiplier * shock_boost
            noise = np.random.normal(0, p["Volatility"])
            sales_units = max(0, int(round(mean_demand + noise)))
            
            if t % (p["Lead_Time_Days"] + 4) == 0 and t > 0:
                restock_qty = int(p["Base_Demand"] * (p["Lead_Time_Days"] + 4) * 0.95)
                current_inv += restock_qty
            
            current_inv = max(0, current_inv - int(sales_units * 0.85))
            unit_price = round(p["Price"] * (0.88 if is_promo else 1.0), 2)
            
            rows.append({
                "Date": date.strftime("%Y-%m-%d"),
                "Product_ID": p["Product_ID"],
                "Product_Name": p["Product_Name"],
                "Category": p["Category"],
                "Sales_Units": sales_units,
                "Stock_On_Hand": current_inv,
                "Unit_Price": unit_price,
                "Lead_Time_Days": p["Lead_Time_Days"],
                "Promotion_Active": is_promo
            })
            
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    return df

if __name__ == "__main__":
    generate_benchmark_dataset()
