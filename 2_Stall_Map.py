import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from data import MARKETS, CATEGORIES, generate_stall_map

st.set_page_config(page_title="Stall Map — Vendora", page_icon="📍", layout="wide")
st.title("📍 Stall Map & Booking")
st.caption("See the full stall layout and book your spot based on footfall scores")

# ── Market selector ───────────────────────────────────────────────────────────
market_name = st.selectbox("Select Market", MARKETS['Market Name'].tolist())
market_row  = MARKETS[MARKETS['Market Name'] == market_name].iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Expected Footfall", f"{market_row['Expected Footfall']:,}")
c2.metric("Market Type", market_row['Type'])
c3.metric("Day", market_row['Day'])
c4.metric("Rating", f"⭐ {market_row['Rating']}")

stalls_df = generate_stall_map(market_name, total_stalls=int(market_row['Total Stalls']))

st.divider()

# ── Zone Summary ──────────────────────────────────────────────────────────────
st.subheader("Zone Overview")
zone_cols = st.columns(4)
zone_labels = {
    'A - Entrance Zone': ('🔴 High Traffic', 'success'),
    'B - Main Walkway':  ('🟠 Medium-High',  'info'),
    'C - Inner Area':    ('🟡 Medium',        'warning'),
    'D - Back Area':     ('🟢 Low Traffic',   'error'),
}
for col, (zone, (label, _)) in zip(zone_cols, zone_labels.items()):
    sub = stalls_df[stalls_df['Zone'] == zone]
    avail = (sub['Status'] == 'Available').sum()
    booked = (sub['Status'] == 'Booked').sum()
    avg_fp = sub['Footfall Score'].mean()
    col.metric(zone.split(' - ')[1], f"Avg Score: {avg_fp:.0f}/100",
               f"{avail} available · {booked} booked")

st.divider()

# ── Visual Stall Grid ─────────────────────────────────────────────────────────
st.subheader("Stall Map")
color_map = {'Booked': '#E53935', 'Available': '#43A047', 'Waitlisted': '#FB8C00'}

fig = px.scatter(
    stalls_df,
    x='X', y='Y',
    color='Status',
    color_discrete_map=color_map,
    hover_data={
        'Stall ID': True, 'Zone': True,
        'Footfall Score': True, 'Price (₹)': True,
        'Vendor Category': True, 'X': False, 'Y': False
    },
    title="Click on a stall to see details  |  🟢 Available   🔴 Booked   🟠 Waitlisted",
    height=460,
)
fig.update_traces(marker=dict(size=22, symbol='square', line=dict(width=1, color='white')))
fig.update_layout(
    yaxis_autorange='reversed',
    xaxis_title='', yaxis_title='',
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    plot_bgcolor='#f8f9fa',
    legend_title_text='Status',
)
st.plotly_chart(fig, use_container_width=True)

# Zone labels on the side
for zone, (label, _) in zone_labels.items():
    st.caption(f"**{zone}** — {label}")

st.divider()

# ── Booking Panel ─────────────────────────────────────────────────────────────
st.subheader("Book a Stall")
available_stalls = stalls_df[stalls_df['Status'] == 'Available']

if len(available_stalls) == 0:
    st.error("No stalls available right now. You can join the waitlist via the organizer.")
else:
    col1, col2 = st.columns([1, 1])

    with col1:
        selected_id = st.selectbox(
            "Choose an Available Stall",
            available_stalls['Stall ID'].tolist(),
            format_func=lambda sid: (
                f"Stall {sid}  —  Score "
                f"{available_stalls.loc[available_stalls['Stall ID'] == sid, 'Footfall Score'].values[0]}/100"
                f"  —  ₹{available_stalls.loc[available_stalls['Stall ID'] == sid, 'Price (₹)'].values[0]}"
            )
        )
        info = available_stalls[available_stalls['Stall ID'] == selected_id].iloc[0]

        sc = info['Footfall Score']
        if sc >= 80:
            st.success(f"🔥 **Prime spot** — footfall score {sc}/100. High traffic, high potential.")
        elif sc >= 60:
            st.info(f"👍 **Good spot** — footfall score {sc}/100. Decent traffic expected.")
        elif sc >= 40:
            st.warning(f"⚠️ **Average spot** — footfall score {sc}/100. Moderate traffic.")
        else:
            st.error(f"📉 **Low traffic zone** — footfall score {sc}/100. Consider a different stall.")

    with col2:
        vendor_name = st.text_input("Your Name / Business Name")
        category    = st.selectbox("Food Category", CATEGORIES)
        phone       = st.text_input("Phone Number")

        st.caption(f"Zone: {info['Zone']}  |  Price: ₹{info['Price (₹)']}  |  Score: {sc}/100")

        if st.button("✅ Confirm Booking", type="primary", use_container_width=True):
            if vendor_name and phone:
                st.success(
                    f"**Booking Confirmed!**\n\n"
                    f"Stall **{selected_id}** at **{market_name}** is reserved for **{vendor_name}**."
                )
                st.info(
                    "📋 Cancellations allowed up to 24 hours before market day. "
                    "Late cancellations reduce your Reliability Score."
                )
                st.balloons()
            else:
                st.error("Please fill in your name and phone number to confirm.")
