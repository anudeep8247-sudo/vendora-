import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from data import MARKETS, CATEGORIES, REVENUE_DATA

st.set_page_config(page_title="Revenue Predictor — Vendora", page_icon="💰", layout="wide")
st.title("💰 Revenue Predictor")
st.caption("Estimate your earning potential before committing to any market")

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    category = st.selectbox("Your Food Category", CATEGORIES)
with col2:
    market = st.selectbox("Select Market", MARKETS['Market Name'].tolist())

market_type  = MARKETS.loc[MARKETS['Market Name'] == market, 'Type'].values[0]
stall_price  = int(MARKETS.loc[MARKETS['Market Name'] == market, 'Stall Price'].values[0])
footfall     = int(MARKETS.loc[MARKETS['Market Name'] == market, 'Expected Footfall'].values[0])
rev          = REVENUE_DATA[category][market_type]

st.divider()

# ── Revenue cards ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Low Estimate",      f"₹{rev['low']:,}",  help="10th percentile — bad day")
c2.metric("Average Estimate",  f"₹{rev['avg']:,}",  help="Typical day at this type of market")
c3.metric("High Estimate",     f"₹{rev['high']:,}", help="90th percentile — great day")
c4.metric("Stall Fee",         f"₹{stall_price:,}")

profit_low  = rev['low']  - stall_price
profit_avg  = rev['avg']  - stall_price
profit_high = rev['high'] - stall_price

if profit_low < 0:
    st.error(
        f"⚠️ On a bad day you may not cover the stall fee. "
        f"Average profit after fee: **₹{profit_avg:,}**"
    )
elif profit_avg > 1500:
    st.success(
        f"✅ Strong opportunity. Average profit after stall fee: **₹{profit_avg:,}**. "
        f"Range: ₹{profit_low:,} – ₹{profit_high:,}"
    )
else:
    st.info(
        f"Moderate opportunity. Average profit after stall fee: **₹{profit_avg:,}**. "
        f"Range: ₹{profit_low:,} – ₹{profit_high:,}"
    )

# ── Gauge chart ───────────────────────────────────────────────────────────────
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=rev['avg'],
    title={'text': f"Expected Avg Daily Revenue (₹) — {market_type}"},
    number={'prefix': '₹', 'valueformat': ','},
    gauge={
        'axis': {'range': [0, 7500]},
        'bar': {'color': '#FF6B35'},
        'steps': [
            {'range': [0,    1050], 'color': '#ffcdd2'},
            {'range': [1050, 2500], 'color': '#fff9c4'},
            {'range': [2500, 7500], 'color': '#c8e6c9'},
        ],
        'threshold': {
            'line': {'color': 'red', 'width': 4},
            'thickness': 0.75,
            'value': 1050
        }
    }
))
fig_gauge.update_layout(height=310, margin=dict(t=50, b=10))
st.plotly_chart(fig_gauge, use_container_width=True)
st.caption("🔴 Red line = ₹1,050 estimated daily break-even threshold")

st.divider()

# ── Cross-market comparison ───────────────────────────────────────────────────
st.subheader(f"How does {category} perform across all market types?")

rows = []
for mt, vals in REVENUE_DATA[category].items():
    rows.append({'Market Type': mt, 'Low ₹': vals['low'], 'Average ₹': vals['avg'], 'High ₹': vals['high']})
comp_df = pd.DataFrame(rows).sort_values('Average ₹', ascending=True)

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(name='Low',     x=comp_df['Market Type'], y=comp_df['Low ₹'],     marker_color='#ffcdd2'))
fig_bar.add_trace(go.Bar(name='Average', x=comp_df['Market Type'], y=comp_df['Average ₹'], marker_color='#FF6B35'))
fig_bar.add_trace(go.Bar(name='High',    x=comp_df['Market Type'], y=comp_df['High ₹'],    marker_color='#c8e6c9'))
fig_bar.update_layout(
    barmode='group',
    title=f'Revenue Range for {category} by Market Type',
    height=400,
    yaxis_title='Revenue (₹)',
    legend_title_text='Scenario',
)
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Break-even Calculator ─────────────────────────────────────────────────────
st.subheader("🧮 Break-Even Calculator")
st.caption("Fill in your costs to see exactly how many sales you need to cover expenses")

col1, col2, col3 = st.columns(3)
with col1:
    ingredient_cost  = st.number_input("Daily Ingredient Cost (₹)", min_value=0, value=400, step=50)
with col2:
    avg_item_price   = st.number_input("Avg Selling Price per Item (₹)", min_value=1, value=60, step=5)
with col3:
    transport_cost   = st.number_input("Transport / Misc Cost (₹)", min_value=0, value=100, step=50)

total_cost    = stall_price + ingredient_cost + transport_cost
units_needed  = -(-total_cost // avg_item_price)   # ceiling division
projected_rev = units_needed * avg_item_price

st.markdown(f"""
| Item | Amount |
|---|---|
| Stall Fee | ₹{stall_price:,} |
| Ingredient Cost | ₹{ingredient_cost:,} |
| Transport / Misc | ₹{transport_cost:,} |
| **Total Daily Cost** | **₹{total_cost:,}** |
| Selling Price per Item | ₹{avg_item_price} |
| **Items Needed to Break Even** | **{units_needed} items** |
""")

surplus = rev['avg'] - total_cost
if surplus > 0:
    st.success(
        f"✅ At average revenue (₹{rev['avg']:,}), you'd cover all costs "
        f"with a **₹{surplus:,} surplus**."
    )
else:
    st.error(
        f"⚠️ Average revenue (₹{rev['avg']:,}) may not fully cover your costs "
        f"(₹{total_cost:,}). Consider a higher-footfall market."
    )
