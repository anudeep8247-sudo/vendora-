import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from data import MARKETS

st.set_page_config(page_title="Market Discovery — Vendora", page_icon="🛒", layout="wide")
st.title("🛒 Market Discovery")
st.caption("Find upcoming markets, exhibitions, and food events across Hyderabad")

# ── Filters ──────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    types = st.multiselect(
        "Market Type", MARKETS['Type'].unique().tolist(),
        default=MARKETS['Type'].unique().tolist()
    )
with col2:
    days = st.multiselect(
        "Day", MARKETS['Day'].unique().tolist(),
        default=MARKETS['Day'].unique().tolist()
    )
with col3:
    min_stalls = st.slider("Min. Available Stalls", 0, 25, 0)

df = MARKETS[
    MARKETS['Type'].isin(types) &
    MARKETS['Day'].isin(days) &
    (MARKETS['Available Stalls'] >= min_stalls)
].copy()

st.markdown(f"**{len(df)} market(s) found**")

# ── Map ───────────────────────────────────────────────────────────────────────
if len(df) == 0:
    st.warning("No markets match your filters. Try adjusting the selections.")
else:
    fig = px.scatter_mapbox(
        df, lat='Lat', lon='Lon',
        hover_name='Market Name',
        hover_data={
            'Type': True, 'Expected Footfall': True,
            'Available Stalls': True, 'Stall Price': True,
            'Lat': False, 'Lon': False
        },
        color='Expected Footfall',
        size='Expected Footfall',
        size_max=28,
        color_continuous_scale='YlOrRd',
        zoom=11, height=440,
        mapbox_style='carto-positron',
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), coloraxis_colorbar_title="Footfall")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Market Cards ─────────────────────────────────────────────────────────
    st.subheader("All Markets")
    for _, row in df.iterrows():
        booked_pct = (row['Total Stalls'] - row['Available Stalls']) / row['Total Stalls']
        with st.expander(
            f"**{row['Market Name']}** — {row['Area']}  |  {row['Day']}  |  ⭐ {row['Rating']}"
        ):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Expected Footfall", f"{row['Expected Footfall']:,}")
            c2.metric("Stall Price", f"₹{row['Stall Price']}")
            c3.metric("Available Stalls", f"{row['Available Stalls']} / {row['Total Stalls']}")
            c4.metric("Market Type", row['Type'])

            st.progress(booked_pct, text=f"{booked_pct * 100:.0f}% booked")

            if row['Available Stalls'] <= 8:
                st.warning("⚡ Almost full — book fast!")
            elif row['Available Stalls'] >= 20:
                st.success("✅ Good availability — plenty of spots left")

            st.info("👈 Go to **Stall Map & Booking** in the sidebar to reserve a stall here.")
