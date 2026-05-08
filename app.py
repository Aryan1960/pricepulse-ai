"""
app.py
PricePulse AI — Streamlit Dashboard
Run: streamlit run app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scripts.optimization import get_recommendations
from utils.helpers import load_model, predict_demand, load_data

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PricePulse AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .metric-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
    }
    .metric-card h3 { color: #94a3b8; font-size: 0.8rem; margin: 0 0 4px; text-transform: uppercase; letter-spacing: 1px; }
    .metric-card .value { color: #f1f5f9; font-size: 1.8rem; font-weight: 700; }
    .metric-card .sub { color: #64748b; font-size: 0.8rem; margin-top: 2px; }
    .rec-box {
        background: #0f172a;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
    }
    .rec-box.green { border-left-color: #22c55e; }
    .rec-box.red   { border-left-color: #ef4444; }
    .rec-box.yellow{ border-left-color: #f59e0b; }
    .rec-box h4 { color: #e2e8f0; margin: 0 0 6px; font-size: 1rem; }
    .rec-box p  { color: #94a3b8; margin: 0; font-size: 0.88rem; }
    .sdg-badge {
        display: inline-block;
        background: #1e3a5f;
        color: #93c5fd;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 0.78rem;
        margin: 2px;
    }
    div[data-testid="stSidebar"] { background: #0f172a; }
    h1, h2, h3 { color: #f1f5f9 !important; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; }
    .stTabs [aria-selected="true"] { color: #3b82f6; border-bottom-color: #3b82f6; }
</style>
""", unsafe_allow_html=True)

# ── Load model (once) ──────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    try:
        return load_model()
    except FileNotFoundError:
        return None, None

@st.cache_data
def get_dataset():
    return load_data()

model, feature_list = get_model()
df = get_dataset()

# ── Sidebar — Inputs ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Business Inputs")
    st.markdown("---")

    price = st.slider("Your Selling Price (₹)", 60, 200, 92)
    inventory = st.slider("Current Inventory (units)", 50, 1000, 450)
    raw_material_cost = st.slider("Raw Material Cost (₹)", 30, 120, 55)
    competitor_price = st.slider("Competitor Price (₹)", 60, 200, 105)
    production_capacity = st.slider("Daily Production Capacity (units)", 100, 700, 350)

    st.markdown("---")
    st.markdown("##### 🌍 SDG Alignment")
    for sdg in ["SDG 8 — Economic Growth", "SDG 9 — Industry & Innovation",
                 "SDG 12 — Responsible Production", "SDG 13 — Climate Action"]:
        st.markdown(f'<span class="sdg-badge">{sdg}</span>', unsafe_allow_html=True)

# ── Run AI ─────────────────────────────────────────────────────────────────────
if model is None:
    st.error("⚠️ Model not found. Run `python scripts/train_model.py` first, then refresh.")
    st.stop()

predicted_demand = predict_demand(
    model, feature_list, inventory, raw_material_cost, competitor_price, price
)
rec = get_recommendations(
    predicted_demand, inventory, price, raw_material_cost,
    competitor_price, production_capacity
)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# 📊 PricePulse AI")
st.markdown("*Operational intelligence for small-scale industries & MSMEs*")
st.markdown("---")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🔮 AI Analysis", "📈 Charts", "📋 Recommendations", "ℹ️ About"])

# ═══════════════════════════════════════════════════════════
# TAB 1 — AI ANALYSIS
# ═══════════════════════════════════════════════════════════
with tab1:
    st.markdown("### AI Predictions & Key Metrics")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("🎯 Predicted Demand", f"{int(rec['predicted_demand'])} units",
                  delta=f"{int(rec['predicted_demand']) - 300:+d} vs avg")
    with c2:
        risk_color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
        st.metric("📦 Inventory Risk",
                  f"{risk_color[rec['inventory_risk']]} {rec['inventory_risk']}",
                  delta=f"{rec['inventory_days']} days cover")
    with c3:
        st.metric("💰 Margin", f"{rec['margin_pct']}%",
                  delta="healthy" if rec['margin_pct'] > 25 else "tight")
    with c4:
        profit_delta = rec['profit_change_pct']
        st.metric("📈 Profit Change", f"{profit_delta:+.1f}%",
                  delta_color="normal" if profit_delta >= 0 else "inverse")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Production Signal")
        action = rec["production_action"]
        color_map = {"INCREASE": "green", "DECREASE": "red", "MAINTAIN": "blue"}
        arrow_map = {"INCREASE": "⬆️", "DECREASE": "⬇️", "MAINTAIN": "➡️"}
        pct = rec["production_change_pct"]
        st.markdown(f"""
        <div class="rec-box {'green' if action=='INCREASE' else 'red' if action=='DECREASE' else ''}">
            <h4>{arrow_map[action]} {action} Production</h4>
            <p>Adjust by <strong>{pct:+d}%</strong> from current capacity ({production_capacity} units/day)</p>
            <p style="margin-top:6px;">Suggested output: <strong>{int(production_capacity * (1 + pct/100))} units/day</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("#### Pricing Signal")
        p_action = rec["pricing_action"]
        suggested = rec["suggested_price"]
        st.markdown(f"""
        <div class="rec-box {'green' if p_action=='MAINTAIN' else 'yellow'}">
            <h4>{"⬆️" if p_action=="INCREASE" else "⬇️" if p_action=="DECREASE" else "✅"} {p_action} Price</h4>
            <p>Current: <strong>₹{price}</strong> → Suggested: <strong>₹{suggested}</strong></p>
            <p style="margin-top:6px;">Competitor benchmark: <strong>₹{competitor_price}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 💡 AI Insight Reasons")
    for r in rec["reasons"]:
        st.markdown(f"- {r}")

# ═══════════════════════════════════════════════════════════
# TAB 2 — CHARTS
# ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Historical Trends")

    # Demand trend
    fig_demand = go.Figure()
    fig_demand.add_trace(go.Scatter(
        x=df["date"], y=df["demand"],
        mode="lines", name="Demand",
        line=dict(color="#3b82f6", width=1.5),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.08)"
    ))
    fig_demand.add_hline(y=predicted_demand, line_dash="dash",
                         line_color="#f59e0b",
                         annotation_text=f"Your predicted demand: {int(predicted_demand)}",
                         annotation_position="bottom right")
    fig_demand.update_layout(
        title="Demand Over Time",
        paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        font_color="#94a3b8", height=300,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig_demand, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Pricing trends
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=df["date"], y=df["price"],
                                       name="Our Price", line=dict(color="#22c55e", width=1.5)))
        fig_price.add_trace(go.Scatter(x=df["date"], y=df["competitor_price"],
                                       name="Competitor", line=dict(color="#ef4444", width=1.5, dash="dot")))
        fig_price.update_layout(
            title="Price vs Competitor",
            paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            font_color="#94a3b8", height=280,
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_price, use_container_width=True)

    with col2:
        # Inventory
        fig_inv = go.Figure()
        fig_inv.add_trace(go.Bar(x=df["date"], y=df["inventory"],
                                 name="Inventory",
                                 marker_color="rgba(139,92,246,0.6)"))
        fig_inv.add_hline(y=inventory, line_dash="dash", line_color="#f59e0b",
                          annotation_text=f"Your inventory: {inventory}")
        fig_inv.update_layout(
            title="Inventory Levels",
            paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            font_color="#94a3b8", height=280,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig_inv, use_container_width=True)

    # Raw material cost
    fig_rmc = go.Figure()
    fig_rmc.add_trace(go.Scatter(x=df["date"], y=df["raw_material_cost"],
                                 name="Raw Material Cost",
                                 line=dict(color="#f97316", width=1.5),
                                 fill="tozeroy", fillcolor="rgba(249,115,22,0.06)"))
    fig_rmc.add_hline(y=raw_material_cost, line_dash="dash", line_color="#3b82f6",
                      annotation_text=f"Your cost: ₹{raw_material_cost}")
    fig_rmc.update_layout(
        title="Raw Material Cost Trend",
        paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        font_color="#94a3b8", height=250,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig_rmc, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# TAB 3 — RECOMMENDATION SUMMARY
# ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📋 Full Recommendation Summary")
    st.markdown("---")

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        prod_pct = rec["production_change_pct"]
        price_delta = rec["suggested_price"] - price

        st.markdown(f"""
        <div class="rec-box {'green' if prod_pct > 0 else 'red' if prod_pct < 0 else ''}">
            <h4>🏭 Production</h4>
            <p>Recommended change: <strong>{prod_pct:+d}%</strong></p>
            <p>New suggested output: <strong>{int(production_capacity * (1 + prod_pct/100))} units/day</strong></p>
        </div>
        <div class="rec-box {'green' if price_delta >= 0 else 'red'}">
            <h4>💲 Pricing</h4>
            <p>Current price: <strong>₹{price}</strong></p>
            <p>Suggested price: <strong>₹{rec['suggested_price']}</strong>  ({price_delta:+.1f} change)</p>
        </div>
        <div class="rec-box">
            <h4>📦 Inventory</h4>
            <p>Current stock covers <strong>{rec['inventory_days']} days</strong> of predicted demand.</p>
            <p>Risk level: <strong>{rec['inventory_risk']}</strong></p>
        </div>
        <div class="rec-box {'green' if rec['profit_change_pct'] >= 0 else 'red'}">
            <h4>📈 Profit Outlook</h4>
            <p>Current estimated profit: <strong>₹{rec['current_profit_estimate']:,.0f}</strong></p>
            <p>After optimization: <strong>₹{rec['future_profit_estimate']:,.0f}</strong>
               (<strong>{rec['profit_change_pct']:+.1f}%</strong>)</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Why these recommendations?")
        for i, r in enumerate(rec["reasons"], 1):
            st.markdown(f"**{i}.** {r}")

    with col_right:
        # Gauge — predicted demand vs capacity
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=predicted_demand,
            delta={"reference": production_capacity},
            title={"text": "Demand vs Capacity", "font": {"color": "#94a3b8", "size": 14}},
            gauge={
                "axis": {"range": [0, production_capacity * 1.5], "tickcolor": "#64748b"},
                "bar": {"color": "#3b82f6"},
                "bgcolor": "#1e293b",
                "steps": [
                    {"range": [0, production_capacity * 0.6], "color": "#0f172a"},
                    {"range": [production_capacity * 0.6, production_capacity], "color": "#1e293b"},
                    {"range": [production_capacity, production_capacity * 1.5], "color": "#2d1515"},
                ],
                "threshold": {
                    "line": {"color": "#ef4444", "width": 3},
                    "thickness": 0.8,
                    "value": production_capacity,
                },
            },
            number={"font": {"color": "#f1f5f9"}},
        ))
        fig_gauge.update_layout(
            paper_bgcolor="#0f172a", font_color="#94a3b8",
            height=300, margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Profit bar chart
        fig_profit = go.Figure(go.Bar(
            x=["Current Profit", "Optimized Profit"],
            y=[rec["current_profit_estimate"], rec["future_profit_estimate"]],
            marker_color=["#475569", "#22c55e" if rec["profit_change_pct"] >= 0 else "#ef4444"],
            text=[f"₹{rec['current_profit_estimate']:,.0f}", f"₹{rec['future_profit_estimate']:,.0f}"],
            textposition="outside",
            textfont=dict(color="#f1f5f9"),
        ))
        fig_profit.update_layout(
            title="Profit Comparison",
            paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            font_color="#94a3b8", height=280,
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(showgrid=False, visible=False),
        )
        st.plotly_chart(fig_profit, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# TAB 4 — ABOUT
# ═══════════════════════════════════════════════════════════
with tab4:
    st.markdown("### About PricePulse AI")
    st.markdown("""
    **PricePulse AI** is an operational intelligence system designed for Micro, Small, and Medium Enterprises (MSMEs).

    It combines machine learning demand forecasting with rule-based optimization to help small businesses make smarter decisions — without needing a data science team.

    ---
    #### How it works
    1. **Data** — Synthetic industrial data (400 rows) simulates realistic MSME patterns including seasonality, price elasticity, and raw material cost trends.
    2. **AI Model** — A `RandomForestRegressor` trained on historical data predicts demand based on your current inputs.
    3. **Optimizer** — Rule-based logic translates the prediction into actionable production and pricing recommendations.
    4. **Dashboard** — Streamlit visualizes everything in real time as you adjust inputs.

    ---
    #### SDG Alignment
    | SDG | How PricePulse AI contributes |
    |-----|-------------------------------|
    | **SDG 8** — Decent Work & Economic Growth | Helps MSMEs optimize profits and sustain jobs |
    | **SDG 9** — Industry & Innovation | Democratizes AI for small-scale industries |
    | **SDG 12** — Responsible Production | Reduces overproduction and inventory waste |
    | **SDG 13** — Climate Action | Efficient production = lower resource consumption |

    ---
    #### Tech Stack
    `Python` · `Scikit-learn` · `Pandas` · `NumPy` · `Streamlit` · `Plotly`
    """)

    st.markdown("---")
    st.caption("PricePulse AI — Built for MSMEs | Hackathon Prototype")
