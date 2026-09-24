import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional, List, Dict

PALETTE = {
    "navy": "#1E3A8A",
    "blue": "#2563EB",
    "light_blue": "#93C5FD",
    "charcoal": "#111827",
    "slate": "#475569",
    "gray": "#6B7280",
    "light_gray": "#E5E7EB",
    "bg_white": "#FFFFFF",
    "bg_light": "#F8F9FA",
    "green": "#15803D",
    "amber": "#D97706",
    "orange": "#EA580C",
    "red": "#DC2626"
}

FONT_FAMILY = "IBM Plex Sans, system-ui, -apple-system, Segoe UI, sans-serif"

def get_base_layout(title: str = "", height: int = 400) -> dict:
    return dict(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family=FONT_FAMILY, size=15, color=PALETTE["charcoal"]),
            x=0.01,
            y=0.96
        ),
        height=height,
        margin=dict(l=50, r=30, t=50, b=40),
        paper_bgcolor=PALETTE["bg_white"],
        plot_bgcolor=PALETTE["bg_white"],
        font=dict(family=FONT_FAMILY, size=12, color=PALETTE["charcoal"]),
        xaxis=dict(
            showgrid=True,
            gridcolor=PALETTE["light_gray"],
            gridwidth=1,
            zeroline=False,
            linecolor=PALETTE["light_gray"],
            tickfont=dict(family=FONT_FAMILY, size=11, color=PALETTE["slate"])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=PALETTE["light_gray"],
            gridwidth=1,
            zeroline=False,
            linecolor=PALETTE["light_gray"],
            tickfont=dict(family=FONT_FAMILY, size=11, color=PALETTE["slate"])
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
            font=dict(family=FONT_FAMILY, size=11, color=PALETTE["slate"]),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=PALETTE["light_gray"],
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor=PALETTE["charcoal"],
            font_size=12,
            font_family=FONT_FAMILY,
            font_color="#FFFFFF"
        )
    )

class ChartEngine:
    @staticmethod
    def plot_forecast_timeline(
        history_df: pd.DataFrame,
        forecast_df: pd.DataFrame,
        product_name: str,
        current_stock: Optional[int] = None
    ) -> go.Figure:
        fig = go.Figure()
        recent_hist = history_df.sort_values("Date").tail(90).copy()

        fig.add_trace(go.Scatter(
            x=recent_hist["Date"],
            y=recent_hist["Sales_Units"],
            mode="lines",
            name="Historical Sales (Actual)",
            line=dict(color=PALETTE["slate"], width=1.8),
            hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Actual Sales:</b> %{y} units<extra></extra>"
        ))

        recent_hist["Rolling_7"] = recent_hist["Sales_Units"].rolling(7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=recent_hist["Date"],
            y=recent_hist["Rolling_7"],
            mode="lines",
            name="7-Day Moving Avg",
            line=dict(color=PALETTE["gray"], width=1.2, dash="dot"),
            hovertemplate="<b>7D Trend:</b> %{y:.1f} units<extra></extra>"
        ))

        if not forecast_df.empty:
            last_hist_date = recent_hist["Date"].iloc[-1]
            last_hist_val = recent_hist["Sales_Units"].iloc[-1]
            
            f_dates = [last_hist_date] + list(forecast_df["Date"])
            f_vals = [last_hist_val] + list(forecast_df["Forecast_Demand"])

            fig.add_trace(go.Scatter(
                x=f_dates,
                y=f_vals,
                mode="lines+markers",
                name="ML Demand Forecast",
                line=dict(color=PALETTE["blue"], width=2.5),
                marker=dict(size=5, color=PALETTE["blue"]),
                hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>ML Forecast:</b> %{y:.1f} units<extra></extra>"
            ))

        if current_stock is not None:
            all_dates = list(recent_hist["Date"]) + (list(forecast_df["Date"]) if not forecast_df.empty else [])
            fig.add_trace(go.Scatter(
                x=[all_dates[0], all_dates[-1]],
                y=[current_stock, current_stock],
                mode="lines",
                name=f"Current Stock ({current_stock} units)",
                line=dict(color=PALETTE["red"] if current_stock < recent_hist["Sales_Units"].mean() * 10 else PALETTE["green"], width=1.5, dash="dash"),
                hovertemplate=f"<b>Current Stock Level:</b> {current_stock} units<extra></extra>"
            ))

        layout = get_base_layout(f"Demand History & Out-of-Sample Forecast: {product_name}", height=420)
        layout["xaxis"]["title"] = "Date"
        layout["yaxis"]["title"] = "Units / Period"
        fig.update_layout(layout)
        return fig

    @staticmethod
    def plot_model_comparison_residuals(
        test_df: pd.DataFrame,
        baseline_preds: np.ndarray,
        ml_preds: np.ndarray,
        product_name: str
    ) -> go.Figure:
        fig = go.Figure()
        dates = test_df["Date"]
        actuals = test_df["Sales_Units"].values

        fig.add_trace(go.Scatter(
            x=dates,
            y=actuals,
            mode="lines",
            name="Test Actuals",
            line=dict(color=PALETTE["charcoal"], width=2.0),
            hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Actual:</b> %{y} units<extra></extra>"
        ))

        fig.add_trace(go.Scatter(
            x=dates,
            y=baseline_preds,
            mode="lines",
            name="Baseline (7D Moving Avg)",
            line=dict(color=PALETTE["slate"], width=1.5, dash="dash"),
            hovertemplate="<b>Baseline Pred:</b> %{y:.1f} units<extra></extra>"
        ))

        fig.add_trace(go.Scatter(
            x=dates,
            y=ml_preds,
            mode="lines",
            name="ML Model (Supervised)",
            line=dict(color=PALETTE["blue"], width=2.2),
            hovertemplate="<b>ML Pred:</b> %{y:.1f} units<extra></extra>"
        ))

        layout = get_base_layout(f"Holdout Test Performance: Actual vs Predictions ({product_name})", height=380)
        layout["xaxis"]["title"] = "Test Period Date"
        layout["yaxis"]["title"] = "Demand (Units)"
        fig.update_layout(layout)
        return fig

    @staticmethod
    def plot_what_if_comparison(
        current_stock: float,
        base_demand: float,
        adjusted_demand: float,
        safety_buffer: float,
        recommended_target: float,
        product_name: str
    ) -> go.Figure:
        categories = ["Current Stock", "Base Forecast", "Simulated Demand", "Recommended Target (Demand + Buffer)"]
        values = [current_stock, base_demand, adjusted_demand, recommended_target]
        colors = [
            PALETTE["slate"],
            PALETTE["blue"],
            PALETTE["orange"] if adjusted_demand > base_demand else PALETTE["blue"],
            PALETTE["red"] if recommended_target > current_stock else PALETTE["green"]
        ]

        fig = go.Figure(go.Bar(
            x=values,
            y=categories,
            orientation="h",
            marker=dict(color=colors, line=dict(color=PALETTE["charcoal"], width=0.5)),
            text=[f"{int(v)} units" for v in values],
            textposition="auto",
            hovertemplate="<b>%{y}:</b> %{x:.1f} units<extra></extra>"
        ))

        layout = get_base_layout(f"What-If Balance: {product_name}", height=280)
        layout["xaxis"]["title"] = "Inventory / Demand Units"
        layout["yaxis"]["autorange"] = "reversed"
        layout["showlegend"] = False
        fig.update_layout(layout)
        return fig

    @staticmethod
    def plot_risk_matrix(product_summary: List[Dict[str, any]]) -> go.Figure:
        df = pd.DataFrame(product_summary)
        if df.empty:
            return go.Figure()

        color_map = {
            "CRITICAL": PALETTE["red"],
            "HIGH RISK": PALETTE["orange"],
            "WATCH": PALETTE["amber"],
            "SAFE": PALETTE["green"]
        }

        fig = go.Figure()

        for risk_level, color in color_map.items():
            sub = df[df["Risk_Level"] == risk_level]
            if not sub.empty:
                fig.add_trace(go.Scatter(
                    x=sub["Predicted_Demand"],
                    y=sub["Current_Stock"],
                    mode="markers+text",
                    name=risk_level,
                    text=sub["Product_Name"].apply(lambda s: s[:18] + "..."),
                    textposition="top center",
                    marker=dict(size=12, color=color, line=dict(color=PALETTE["charcoal"], width=0.5)),
                    hovertemplate=(
                        "<b>%{text}</b><br>" +
                        "<b>Predicted Demand:</b> %{x:.1f}<br>" +
                        "<b>Current Stock:</b> %{y}<br>" +
                        "<b>Risk Score:</b> " + sub["Risk_Score"].astype(str) + "/100<br>" +
                        "<b>Reorder Needed:</b> " + sub["Recommended_Additional_Stock"].astype(str) + " units<extra></extra>"
                    )
                ))

        max_val = max(df["Predicted_Demand"].max(), df["Current_Stock"].max()) * 1.15
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode="lines",
            name="Parity (Stock = Demand)",
            line=dict(color=PALETTE["gray"], width=1, dash="dash"),
            hoverinfo="skip"
        ))

        layout = get_base_layout("Portfolio Risk Matrix: Stock on Hand vs Predicted Demand", height=440)
        layout["xaxis"]["title"] = "Expected Demand (14-Day Forecast Units)"
        layout["yaxis"]["title"] = "Current Physical Stock on Hand"
        fig.update_layout(layout)
        return fig

    @staticmethod
    def plot_feature_importance(importances: Dict[str, float]) -> go.Figure:
        sorted_imp = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10]
        feats = [x[0] for x in sorted_imp]
        vals = [x[1] for x in sorted_imp]

        fig = go.Figure(go.Bar(
            x=vals,
            y=feats,
            orientation="h",
            marker=dict(color=PALETTE["navy"], line=dict(color=PALETTE["charcoal"], width=0.5)),
            text=[f"{v:.1%}" if v <= 1.0 else f"{v:.2f}" for v in vals],
            textposition="auto",
            hovertemplate="<b>Feature:</b> %{y}<br><b>Importance:</b> %{x:.3f}<extra></extra>"
        ))

        layout = get_base_layout("Top Demand Predictors (Feature Importance)", height=320)
        layout["xaxis"]["title"] = "Normalized Relative Importance"
        layout["yaxis"]["autorange"] = "reversed"
        layout["showlegend"] = False
        fig.update_layout(layout)
        return fig
