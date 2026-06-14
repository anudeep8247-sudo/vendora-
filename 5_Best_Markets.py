import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from data import MARKETS, CATEGORIES, REVENUE_DATA

st.set_page_config(page_title="Best Markets — Vendora", page_icon="⭐", layout="wide")
st.title("⭐ Best Market Recommender")
st.caption("Get ranked market recommendations based on your food category and profit potential")

# ── Category selector ─────────────────────────────────────────────────────────
category = st.selectbox("Select Your Food Category", CATEGORIES)

# ── Build ranked table ────────────────────────────────────────────────────────
rows = []
for _, row in MARKETS.iterrows():
    mt = row['Type']
    if mt not in REVENUE_DATA[category]:
        continue
    rev        = REVENUE_DATA[category][mt]
    profit_avg = rev['avg'] - row['Stall Price']
    profit_low = rev['low'] - row['Stall Price']
    roi        = round((profit_avg / row['Stall Price']) * 100, 1)
    rows.append({
        'Market':              row['Market Name'],
        'Area':                row['Area'],
        'Type':                mt,
        'Day':                 row['Day'],
        'Stall Fee (₹)':       int(row['Stall Price']),
        'Avg Revenue (₹)':     rev['avg'],
        'Worst-Case (₹)':      rev['low'],
        'Best-Case (₹)':       rev['high'],
        'Avg Profit (₹)':      profit_avg,
        'Worst Profit (₹)':    profit_low,
        'ROI (%)':             roi,
        'Footfall':            int(row['Expected Footfall']),
        'Available Stalls':    int(row['Available Stalls']),
        'Rating':              row['Rating'],
    })

rec_df = pd.DataFrame(rows).sort_values('Avg Profit (₹)', ascending=False).reset_index(drop=True)
rec_df.insert(0, 'Rank', range(1, len(rec_df) + 1))

# ── Top pick highlight ────────────────────────────────────────────────────────
top = rec_df.iloc[0]
st.success(f"""
🏆 **Top Pick for {category}:  {top['Market']}**  
📍 {top['Area']} · {top['Day']} · {top['Type']}  
💰 Avg Revenue ₹{top['Avg Revenue (₹)']:,} · Avg Profit ₹{top['Avg Profit (₹)']:,} · ROI {top['ROI (%)']}%  
📊 Expected Footfall {top['Footfall']:,} · Available Stalls {top['Available Stalls']} · ⭐ {top['Rating']}
""")

st.divider()

# ── Bar chart ─────────────────────────────────────────────────────────────────
fig = px.bar(
    rec_df,
    x='Market',
    y='Avg Profit (₹)',
    color='ROI (%)',
    color_continuous_scale='RdYlGn',
    text='Avg Profit (₹)',
    title=f'Estimated Daily Profit by Market — {category}  (after stall fee)',
    height=420,
    labels={'Avg Profit (₹)': 'Avg Profit (₹)', 'Market': ''},
)
fig.update_traces(texttemplate='₹%{text:,}', textposition='outside')
fig.update_layout(xaxis_tickangle=-30, uniformtext_minsize=8, uniformtext_mode='hide')
st.plotly_chart(fig, use_container_width=True)

# ── Scatter: Footfall vs Profit ───────────────────────────────────────────────
fig2 = px.scatter(
    rec_df,
    x='Footfall',
    y='Avg Profit (₹)',
    size='Available Stalls',
    color='ROI (%)',
    color_continuous_scale='RdYlGn',
    hover_name='Market',
    hover_data={'Stall Fee (₹)': True, 'ROI (%)': True, 'Rating': True},
    title='Footfall vs Profit — Bubble size = Available Stalls',
    labels={'Footfall': 'Expected Footfall', 'Avg Profit (₹)': 'Avg Profit (₹)'},
    height=400,
)
fig2.add_hline(y=0, line_dash='dash', line_color='red', annotation_text='Break-even line')
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Full ranked table ─────────────────────────────────────────────────────────
st.subheader("Full Rankings")
display_cols = [
    'Rank', 'Market', 'Area', 'Type', 'Day',
    'Stall Fee (₹)', 'Avg Revenue (₹)', 'Avg Profit (₹)',
    'Worst Profit (₹)', 'ROI (%)', 'Footfall', 'Available Stalls', 'Rating'
]
st.dataframe(rec_df[display_cols], use_container_width=True, hide_index=True)

st.divider()

# ── Revenue range comparison ──────────────────────────────────────────────────
st.subheader("Revenue Range — All Markets")
fig3 = go.Figure()
for _, row in rec_df.iterrows():
    fig3.add_trace(go.Bar(
        name=row['Market'],
        x=['Worst Case', 'Average', 'Best Case'],
        y=[row['Worst-Case (₹)'], row['Avg Revenue (₹)'], row['Best-Case (₹)']],
        visible='legendonly' if row['Rank'] > 3 else True,
    ))
fig3.update_layout(
    barmode='group',
    title='Revenue Scenarios Across Markets (top 3 shown — toggle others in legend)',
    height=420,
    yaxis_title='Revenue (₹)',
    legend=dict(orientation='h', yanchor='bottom', y=1.02)
)
st.plotly_chart(fig3, use_container_width=True)
