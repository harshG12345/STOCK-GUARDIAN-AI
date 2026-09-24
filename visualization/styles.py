CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

:root {
    --bg-main: #F8F9FA;
    --bg-card: #FFFFFF;
    --bg-subtle: #F3F4F6;
    --text-primary: #111827;
    --text-secondary: #4B5563;
    --text-muted: #6B7280;
    --border-color: #E5E7EB;
    --border-dark: #D1D5DB;
    --accent-navy: #1E3A8A;
    --accent-blue: #2563EB;
    --accent-light: #EFF6FF;
    --status-safe: #15803D;
    --status-safe-bg: #DCFCE7;
    --status-watch: #D97706;
    --status-watch-bg: #FEF3C7;
    --status-high: #EA580C;
    --status-high-bg: #FFEDD5;
    --status-danger: #DC2626;
    --status-danger-bg: #FEE2E2;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #F8F9FA !important;
    color: #111827 !important;
    font-family: 'IBM Plex Sans', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

[data-testid="stHeader"] {
    background-color: #F8F9FA !important;
    border-bottom: 1px solid #E5E7EB !important;
}

[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E5E7EB !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] > div:not([data-baseweb="select"]) label {
    color: #111827 !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #111827 !important;
    font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
}

h1 {
    font-size: 1.85rem !important;
    margin-bottom: 0.25rem !important;
}

h2 {
    font-size: 1.35rem !important;
    margin-top: 1.25rem !important;
    margin-bottom: 0.5rem !important;
}

h3 {
    font-size: 1.10rem !important;
    margin-top: 1.0rem !important;
    margin-bottom: 0.35rem !important;
}

p, label {
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
    color: #111827;
}

.secondary-text {
    color: #4B5563 !important;
    font-size: 0.90rem;
    line-height: 1.45;
}

.mono-text {
    font-family: 'IBM Plex Mono', monospace !important;
}

.app-header-container {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    padding: 18px 24px;
    margin-bottom: 20px;
    border-radius: 4px;
}

.app-brand-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #1E3A8A;
    letter-spacing: -0.01em;
    display: inline-block;
}

.app-brand-tagline {
    font-size: 0.85rem;
    color: #4B5563;
    margin-top: 2px;
}

.metric-box {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    padding: 16px 20px;
    margin-bottom: 14px;
    border-radius: 4px;
}

.metric-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #6B7280;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: #111827;
    line-height: 1.2;
    letter-spacing: -0.02em;
}

.metric-sub {
    font-size: 0.80rem;
    color: #4B5563;
    margin-top: 4px;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    border: 1px solid transparent;
    border-radius: 4px;
}

.badge-critical {
    background-color: #FEE2E2;
    color: #DC2626;
    border-color: #FCA5A5;
}

.badge-high {
    background-color: #FFEDD5;
    color: #EA580C;
    border-color: #FDBA74;
}

.badge-watch {
    background-color: #FEF3C7;
    color: #D97706;
    border-color: #FCD34D;
}

.badge-safe {
    background-color: #DCFCE7;
    color: #15803D;
    border-color: #86EFAC;
}

.info-callout {
    background-color: #FFFFFF;
    border-left: 3px solid #1E3A8A;
    border-top: 1px solid #E5E7EB;
    border-right: 1px solid #E5E7EB;
    border-bottom: 1px solid #E5E7EB;
    padding: 14px 18px;
    margin: 14px 0;
    border-radius: 4px;
}

.alert-critical-box {
    background-color: #FEF2F2;
    border-left: 4px solid #DC2626;
    border-top: 1px solid #FECACA;
    border-right: 1px solid #FECACA;
    border-bottom: 1px solid #FECACA;
    padding: 14px 18px;
    margin: 14px 0;
    border-radius: 4px;
}

.alert-title {
    font-weight: 600;
    font-size: 0.90rem;
    color: #DC2626;
    margin-bottom: 4px;
}

.sim-container {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    padding: 20px;
    margin-top: 10px;
    margin-bottom: 20px;
    border-radius: 4px;
}

.sim-header {
    font-weight: 600;
    font-size: 1.05rem;
    color: #1E3A8A;
    border-bottom: 1px solid #E5E7EB;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

.stButton > button {
    background-color: #1E3A8A !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border: 1px solid #1E3A8A !important;
    border-radius: 4px !important;
    padding: 8px 18px !important;
}

.stButton > button:hover {
    background-color: #1E40AF !important;
    border-color: #1E40AF !important;
    color: #FFFFFF !important;
}

button[data-baseweb="tab"] {
    font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
    font-size: 0.90rem !important;
    font-weight: 600 !important;
    color: #4B5563 !important;
    border-radius: 0px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #1E3A8A !important;
    border-bottom-color: #1E3A8A !important;
    border-bottom-width: 2px !important;
}

/* ==========================================================================
   DROPDOWN, SELECTBOX, MULTISELECT & POPOVER STYLES (CRISP WHITE TEXT)
   ========================================================================== */

/* Dropdown popover containers */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
ul[data-baseweb="menu"],
ul[role="listbox"],
div[role="listbox"] {
    background-color: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3) !important;
    padding: 4px !important;
    z-index: 999999 !important;
}

/* Dropdown list items and text */
div[data-baseweb="popover"] *,
div[data-baseweb="menu"] *,
ul[role="listbox"] *,
div[role="listbox"] *,
li[role="option"],
li[role="option"] *,
div[role="option"],
div[role="option"] *,
[data-baseweb="select"] ul li,
[data-baseweb="select"] ul li * {
    color: #FFFFFF !important;
    font-weight: 500 !important;
    font-size: 0.90rem !important;
}

/* Option item padding and hover */
li[role="option"],
div[role="option"] {
    background-color: transparent !important;
    padding: 9px 14px !important;
    border-radius: 6px !important;
    margin: 2px 0 !important;
    cursor: pointer !important;
    transition: background-color 0.15s ease, color 0.15s ease !important;
}

li[role="option"]:hover,
div[role="option"]:hover,
li[role="option"]:focus,
div[role="option"]:focus {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
}

li[role="option"][aria-selected="true"],
div[role="option"][aria-selected="true"] {
    background-color: #1D4ED8 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

li[role="option"]:hover *,
div[role="option"]:hover *,
li[role="option"][aria-selected="true"] *,
div[role="option"][aria-selected="true"] * {
    color: #FFFFFF !important;
}

/* Selectbox input triggers */
div[data-baseweb="select"],
div[data-baseweb="select"] > div {
    background-color: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
}

div[data-baseweb="select"] *,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
div[data-baseweb="select"] input,
[data-testid="stSidebar"] div[data-baseweb="select"] *,
[data-testid="stSidebar"] div[data-baseweb="select"] span,
[data-testid="stSidebar"] div[data-baseweb="select"] div,
[data-testid="stSidebar"] div[data-baseweb="select"] input {
    color: #FFFFFF !important;
}

div[data-baseweb="select"] svg,
[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: #94A3B8 !important;
}

/* Multi-select filter tags */
div[data-baseweb="tag"] {
    background-color: #2563EB !important;
    border: 1px solid #3B82F6 !important;
    border-radius: 4px !important;
    color: #FFFFFF !important;
    padding: 2px 8px !important;
}

div[data-baseweb="tag"] *,
div[data-baseweb="tag"] span {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

div[data-baseweb="tag"] svg {
    fill: #FFFFFF !important;
}

/* ==========================================================================
   DOWN-PAGE & TABLE STYLING FOR MAXIMUM VISIBILITY
   ========================================================================== */

/* DataFrame and Data Tables */
div[data-testid="stDataFrame"] {
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
    background-color: #FFFFFF !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
}

div[data-testid="stDataFrame"] * {
    font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
}

/* Slider Controls */
div[data-testid="stSlider"] label,
div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p {
    color: #111827 !important;
    font-weight: 600 !important;
}

div[data-testid="stSlider"] span {
    color: #1E3A8A !important;
    font-weight: 600 !important;
}

/* Radio buttons */
div[data-testid="stRadio"] label span {
    color: #111827 !important;
    font-weight: 500 !important;
}
</style>
"""

def render_badge(risk_level: str) -> str:
    risk = risk_level.upper().strip()
    if "CRITICAL" in risk:
        return '<span class="status-badge badge-critical">[ ! ] CRITICAL</span>'
    elif "HIGH" in risk:
        return '<span class="status-badge badge-high">[ ▲ ] HIGH RISK</span>'
    elif "WATCH" in risk:
        return '<span class="status-badge badge-watch">[ • ] WATCH</span>'
    else:
        return '<span class="status-badge badge-safe">[ ✓ ] SAFE</span>'

def render_metric_card(label: str, value: str, sub: str = "", border_left_color: str = None) -> str:
    border_style = f"border-left: 3px solid {border_left_color};" if border_left_color else ""
    return f"""
    <div class="metric-box" style="{border_style}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-sub">{sub}</div>' if sub else ''}
    </div>
    """
