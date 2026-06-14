import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from data import MARKETS, CATEGORIES, REVENUE_DATA, apply_css

st.set_page_config(page_title="Revenue Predictor — Vendora", page_icon="💰", layout="wide")
apply_css()

st.markdown("""
<div style="margin-bottom:4px;">
  <span style="font-size:2rem; font-weight:900; color:#0F172A;">💰 Revenue Predictor</span>
</div>
<div style="color:#64748B; font-size:0.92rem; margin-bottom:1.5rem;">
  Estimate earnings, simulate customer scenarios, and calculate your break-even — before you book.
</div>
""", unsafe_allow_html=True)

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    category = st.selectbox("Your Food Category", CATEGORIES)
with col2:
    market = st.selectbox("Select Market", MARKETS['Market Name'].tolist())

market_type = MARKETS.loc[MARKETS['Market Name'] == market, 'Type'].values[0]
stall_price = int(MARKETS.loc[MARKETS['Market Name'] == market, 'Stall Price'].values[0])
footfall    = int(MARKETS.loc[MARKETS['Market Name'] == market, 'Expected Footfall'].values[0])
rev         = REVENUE_DATA[category][market_type]

st.divider()

# ── Revenue estimate cards ────────────────────────────────────────────────────
profit_low  = rev['low']  - stall_price
profit_avg  = rev['avg']  - stall_price
profit_high = rev['high'] - stall_price

st.markdown(f"""
<div style="display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:1.2rem;">
  <div style="background:#FFF3F0; border:1.5px solid #FFCCBC; border-radius:14px; padding:18px; text-align:center;">
    <div style="font-size:0.7rem; color:#BF360C; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">Worst Case</div>
    <div style="font-size:1.9rem; font-weight:900; color:#E64A19; margin:6px 0;">₹{rev['low']:,}</div>
    <div style="font-size:0.75rem; color:#78909C;">Profit: ₹{profit_low:,}</div>
  </div>
  <div style="background:#FFF8E1; border:1.5px solid #FFE082; border-radius:14px; padding:18px; text-align:center;">
    <div style="font-size:0.7rem; color:#F57F17; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">Average Day</div>
    <div style="font-size:1.9rem; font-weight:900; color:#F9A825; margin:6px 0;">₹{rev['avg']:,}</div>
    <div style="font-size:0.75rem; color:#78909C;">Profit: ₹{profit_avg:,}</div>
  </div>
  <div style="background:#F1F8E9; border:1.5px solid #C5E1A5; border-radius:14px; padding:18px; text-align:center;">
    <div style="font-size:0.7rem; color:#33691E; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">Best Case</div>
    <div style="font-size:1.9rem; font-weight:900; color:#558B2F; margin:6px 0;">₹{rev['high']:,}</div>
    <div style="font-size:0.75rem; color:#78909C;">Profit: ₹{profit_high:,}</div>
  </div>
  <div style="background:#EDE7F6; border:1.5px solid #CE93D8; border-radius:14px; padding:18px; text-align:center;">
    <div style="font-size:0.7rem; color:#4A148C; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">Stall Fee</div>
    <div style="font-size:1.9rem; font-weight:900; color:#6A1B9A; margin:6px 0;">₹{stall_price:,}</div>
    <div style="font-size:0.75rem; color:#78909C;">{market_type}</div>
  </div>
</div>
""", unsafe_allow_html=True)

if profit_low < 0:
    st.error(f"⚠️ On a bad day you may not cover the stall fee. Average profit: **₹{profit_avg:,}**")
elif profit_avg > 1500:
    st.success(f"✅ Strong opportunity — avg profit after stall fee: **₹{profit_avg:,}**")
else:
    st.info(f"Moderate opportunity — avg profit after stall fee: **₹{profit_avg:,}**")

# ── Gauge ─────────────────────────────────────────────────────────────────────
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=rev['avg'],
    title={'text': f"Expected Avg Daily Revenue · {market_type}", 'font': {'size': 14}},
    number={'prefix': '₹', 'valueformat': ','},
    gauge={
        'axis': {'range': [0, 7500]},
        'bar': {'color': '#FF6B35'},
        'steps': [
            {'range': [0,    1050], 'color': '#FFCDD2'},
            {'range': [1050, 2800], 'color': '#FFF9C4'},
            {'range': [2800, 7500], 'color': '#C8E6C9'},
        ],
        'threshold': {'line': {'color': 'red', 'width': 4}, 'thickness': 0.75, 'value': 1050}
    }
))
fig_gauge.update_layout(height=290, margin=dict(t=50, b=10))
st.plotly_chart(fig_gauge, use_container_width=True)
st.caption("Red line = ₹1,050 break-even threshold")

st.divider()

# ── Cross-market comparison ───────────────────────────────────────────────────
st.subheader(f"How {category} performs across all market types")
comp_rows = [{'Market Type': mt, 'Low': v['low'], 'Average': v['avg'], 'High': v['high']}
             for mt, v in REVENUE_DATA[category].items()]
comp_df = pd.DataFrame(comp_rows).sort_values('Average', ascending=True)

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(name='Low',     x=comp_df['Market Type'], y=comp_df['Low'],     marker_color='#FFCDD2'))
fig_bar.add_trace(go.Bar(name='Average', x=comp_df['Market Type'], y=comp_df['Average'], marker_color='#FF6B35'))
fig_bar.add_trace(go.Bar(name='High',    x=comp_df['Market Type'], y=comp_df['High'],    marker_color='#C8E6C9'))
fig_bar.update_layout(barmode='group', height=380, yaxis_title='Revenue (₹)', legend_title='Scenario')
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Break-even Calculator ─────────────────────────────────────────────────────
st.subheader("🧮 Break-Even Calculator")
col1, col2, col3 = st.columns(3)
with col1:
    ingredient_cost = st.number_input("Daily Ingredient Cost (₹)", min_value=0, value=400, step=50)
with col2:
    avg_item_price  = st.number_input("Avg Selling Price per Item (₹)", min_value=1, value=60, step=5)
with col3:
    transport_cost  = st.number_input("Transport / Misc Cost (₹)", min_value=0, value=100, step=50)

total_cost   = stall_price + ingredient_cost + transport_cost
units_needed = -(-total_cost // avg_item_price)

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
    st.success(f"✅ At average revenue (₹{rev['avg']:,}) you'd clear costs with a **₹{surplus:,} surplus**.")
else:
    st.error(f"⚠️ Average revenue (₹{rev['avg']:,}) may not cover total costs (₹{total_cost:,}). Consider a higher-footfall market.")

st.divider()

# ── LIVE REVENUE SIMULATOR ────────────────────────────────────────────────────
st.markdown("""
<div style="background:#0F172A; border-radius:16px; padding:28px 28px 20px; margin-bottom:1rem;">
  <div style="font-size:1.15rem; font-weight:800; color:white; margin-bottom:4px;">⚡ Live Revenue Simulator</div>
  <div style="color:#94A3B8; font-size:0.85rem;">Drag the sliders — revenue updates in real time</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    est_customers    = st.slider("Expected Customers", 20, 450, 120, step=10)
with col2:
    items_per_cust   = st.slider("Avg Items per Customer", 1, 5, 2)
with col3:
    sim_item_price   = st.number_input("Item Price (₹)", min_value=10, max_value=500, value=avg_item_price, step=5)

sim_revenue = est_customers * items_per_cust * sim_item_price
sim_profit  = sim_revenue - total_cost
be_customers = -(-total_cost // (items_per_cust * sim_item_price))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Simulated Revenue",    f"₹{sim_revenue:,}")
c2.metric("Simulated Profit",     f"₹{sim_profit:,}",  "✅ Profitable" if sim_profit > 0 else "⚠️ Loss")
c3.metric("Break-even Customers", f"{be_customers}")
c4.metric("Break-even Items",     f"{units_needed}")

# Simulation chart — revenue & profit vs customer count
cust_range  = list(range(10, 460, 10))
rev_line    = [c * items_per_cust * sim_item_price for c in cust_range]
profit_line = [r - total_cost for r in rev_line]

fig_sim = go.Figure()
fig_sim.add_trace(go.Scatter(
    x=cust_range, y=rev_line,
    name='Revenue', line=dict(color='#FF6B35', width=2.5),
    fill='tonexty', fillcolor='rgba(255,107,53,0.05)'
))
fig_sim.add_trace(go.Scatter(
    x=cust_range, y=profit_line,
    name='Profit', line=dict(color='#43A047', width=2.5),
))
fig_sim.add_hline(y=0,           line_dash='dash', line_color='red',    line_width=1.5,
                  annotation_text='Break-even', annotation_position='bottom right')
fig_sim.add_vline(x=est_customers, line_dash='dot', line_color='#FF6B35', line_width=2,
                  annotation_text=f'You: {est_customers}', annotation_position='top')
fig_sim.update_layout(
    title='Revenue & Profit vs Customer Count',
    xaxis_title='Customers', yaxis_title='Amount (₹)',
    height=360, hovermode='x unified',
    legend=dict(orientation='h', yanchor='bottom', y=1.02),
)
st.plotly_chart(fig_sim, use_container_width=True)
st.caption("Move the sliders above to see your numbers update live.")
