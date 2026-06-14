import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from data import MARKETS, CATEGORIES, generate_stall_map

st.set_page_config(page_title="Competitor Heatmap — Vendora", page_icon="🔥", layout="wide")
st.title("🔥 Competitor Density Heatmap")
st.caption("See how saturated each zone is for your food category — before you book")

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    market      = st.selectbox("Select Market", MARKETS['Market Name'].tolist())
with col2:
    my_category = st.selectbox("Your Food Category", CATEGORIES)

stalls_df = generate_stall_map(market)
booked    = stalls_df[stalls_df['Status'] == 'Booked'].copy()

# Map short labels → full category names
cat_map = {
    'Street Food': 'Street Food & Snacks',
    'Bakery':      'Bakery Items',
    'Beverages':   'Beverages & Desserts',
    'Homemade':    'Homemade Food Products',
    'Festival Food': 'Festival Food',
}
booked['Category Full'] = booked['Vendor Category'].map(cat_map)

zones        = stalls_df['Zone'].unique().tolist()
all_cats     = list(cat_map.values())

# ── Build heatmap data ────────────────────────────────────────────────────────
heat_rows = []
for zone in zones:
    z_short  = zone.split(' - ')[0]
    z_booked = booked[booked['Zone'] == zone]
    for cat in all_cats:
        count = (z_booked['Category Full'] == cat).sum()
        heat_rows.append({'Zone': z_short, 'Category': cat, 'Vendors': int(count)})

heat_df = pd.DataFrame(heat_rows)
pivot   = heat_df.pivot(index='Category', columns='Zone', values='Vendors').fillna(0)

fig = px.imshow(
    pivot,
    labels=dict(x="Zone", y="Food Category", color="Vendors"),
    color_continuous_scale='RdYlGn_r',
    title=f"Vendor Density at {market}  (Darker = More Competition)",
    aspect='auto',
    text_auto=True,
)
fig.update_layout(height=380, margin=dict(t=60, b=10))
st.plotly_chart(fig, use_container_width=True)
st.caption("A = Entrance Zone · B = Main Walkway · C = Inner Area · D = Back Area")

st.divider()

# ── Zone recommendation ───────────────────────────────────────────────────────
st.subheader(f"Best Zones for You — {my_category}")

recs = []
for zone in zones:
    z_short        = zone.split(' - ')[0]
    sub            = stalls_df[stalls_df['Zone'] == zone]
    booked_sub     = booked[booked['Zone'] == zone]
    competitors    = int((booked_sub['Category Full'] == my_category).sum())
    avg_fp         = round(float(sub['Footfall Score'].mean()), 1)
    avail          = int((sub['Status'] == 'Available').sum())
    composite      = avg_fp - (competitors * 9)   # reward footfall, penalise competition
    recs.append({
        'Zone':             z_short,
        'Full Zone':        zone,
        'Avg Footfall':     avg_fp,
        'Competitors':      competitors,
        'Available Stalls': avail,
        'Score':            composite,
    })

recs_df = pd.DataFrame(recs).sort_values('Score', ascending=False)

for _, z in recs_df.iterrows():
    if z['Available Stalls'] == 0:
        st.error(f"**Zone {z['Zone']} — {z['Full Zone'].split(' - ')[1]}** — No available stalls")
        continue

    sc = z['Score']
    msg = (
        f"**Zone {z['Zone']} — {z['Full Zone'].split(' - ')[1]}**  |  "
        f"Footfall Score: {z['Avg Footfall']}/100  |  "
        f"Your competitors here: {z['Competitors']}  |  "
        f"Available stalls: {z['Available Stalls']}"
    )

    if sc > 70:
        st.success(f"✅ Best zone for you  —  {msg}")
    elif sc > 50:
        st.info(f"👍 Good option  —  {msg}")
    elif sc > 30:
        st.warning(f"⚠️ Moderate — some competition  —  {msg}")
    else:
        st.error(f"❌ High competition, low footfall  —  {msg}")

st.divider()

# ── Category distribution bar chart ──────────────────────────────────────────
st.subheader("Category Distribution Across Booked Stalls")
cat_totals = booked['Category Full'].value_counts().reset_index()
cat_totals.columns = ['Category', 'Count']

fig2 = px.bar(
    cat_totals.sort_values('Count'),
    x='Count', y='Category',
    orientation='h',
    color='Count',
    color_continuous_scale='Oranges',
    title='How many vendors of each category are already booked?',
    labels={'Count': 'Booked Vendors', 'Category': ''},
    height=340,
)
fig2.update_layout(showlegend=False, coloraxis_showscale=False)

# Highlight the user's category
colours = [
    '#FF6B35' if cat == my_category else '#cccccc'
    for cat in cat_totals.sort_values('Count')['Category']
]
fig2.update_traces(marker_color=colours)
st.plotly_chart(fig2, use_container_width=True)
st.caption(f"🟠 Orange bar = your category ({my_category})")
