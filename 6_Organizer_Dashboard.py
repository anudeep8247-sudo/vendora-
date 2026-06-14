import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from data import MARKETS, VENDORS, generate_stall_map

st.set_page_config(page_title="Organizer Dashboard — Vendora", page_icon="📊", layout="wide")
st.title("📊 Organizer Dashboard")
st.caption("Manage occupancy, track revenue, and monitor vendor allocation for your market")

# ── Market selector ───────────────────────────────────────────────────────────
market     = st.selectbox("Select Your Market", MARKETS['Market Name'].tolist())
market_row = MARKETS[MARKETS['Market Name'] == market].iloc[0]
stalls_df  = generate_stall_map(market, total_stalls=int(market_row['Total Stalls']))

total      = len(stalls_df)
booked     = int((stalls_df['Status'] == 'Booked').sum())
available  = int((stalls_df['Status'] == 'Available').sum())
waitlisted = int((stalls_df['Status'] == 'Waitlisted').sum())
occ_pct    = booked / total * 100
stall_fee  = int(market_row['Stall Price'])

# ── KPI row ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Occupancy Rate",   f"{occ_pct:.0f}%",    f"{booked}/{total} stalls")
c2.metric("Booked",           booked)
c3.metric("Available",        available)
c4.metric("Waitlisted",       waitlisted)
c5.metric("Revenue Collected", f"₹{booked * stall_fee:,}", f"of ₹{total * stall_fee:,} potential")

if occ_pct < 60:
    st.warning(f"⚠️ Occupancy at {occ_pct:.0f}% — consider promoting this event to fill empty stalls.")
elif occ_pct > 90:
    st.success(f"✅ Near full capacity ({occ_pct:.0f}%). Consider opening a waitlist or adding stalls.")
else:
    st.info(f"📊 Occupancy at {occ_pct:.0f}% — on track.")

st.divider()

# ── Charts row ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    # Stall status by zone
    zone_counts = (
        stalls_df.groupby(['Zone', 'Status'])
        .size().reset_index(name='Count')
    )
    zone_counts['Zone Short'] = zone_counts['Zone'].str.split(' - ').str[0]
    fig1 = px.bar(
        zone_counts, x='Zone Short', y='Count', color='Status',
        color_discrete_map={'Booked': '#E53935', 'Available': '#43A047', 'Waitlisted': '#FB8C00'},
        title='Stall Status by Zone',
        barmode='stack',
        height=360,
        labels={'Zone Short': 'Zone', 'Count': 'Stalls'},
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Vendor category pie
    booked_df  = stalls_df[stalls_df['Status'] == 'Booked']
    cat_counts = booked_df['Vendor Category'].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Count']
    fig2 = px.pie(
        cat_counts, names='Category', values='Count',
        title='Booked Vendors by Food Category',
        color_discrete_sequence=px.colors.qualitative.Bold,
        height=360,
    )
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Revenue gauge ─────────────────────────────────────────────────────────────
st.subheader("Revenue Tracker")
current_rev = booked * stall_fee
max_rev     = total  * stall_fee

fig3 = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=current_rev,
    delta={'reference': max_rev, 'relative': True, 'valueformat': '.0%'},
    title={'text': f"Revenue Collected vs Max Potential (₹{max_rev:,})"},
    number={'prefix': '₹', 'valueformat': ','},
    gauge={
        'axis': {'range': [0, max_rev]},
        'bar': {'color': '#FF6B35'},
        'steps': [
            {'range': [0,           max_rev * 0.5], 'color': '#ffcdd2'},
            {'range': [max_rev * 0.5, max_rev * 0.8], 'color': '#fff9c4'},
            {'range': [max_rev * 0.8, max_rev],       'color': '#c8e6c9'},
        ],
    }
))
fig3.update_layout(height=300, margin=dict(t=60, b=10))
st.plotly_chart(fig3, use_container_width=True)

unrealised = max_rev - current_rev
st.caption(
    f"₹{current_rev:,} collected from {booked} booked stalls · "
    f"₹{unrealised:,} unrealised from {available + waitlisted} unfilled stalls"
)

st.divider()

# ── Footfall by zone ──────────────────────────────────────────────────────────
st.subheader("Average Footfall Score by Zone")
zone_fp = (
    stalls_df.groupby('Zone')['Footfall Score']
    .mean().reset_index()
)
zone_fp.columns = ['Zone', 'Avg Footfall Score']
zone_fp['Zone Short'] = zone_fp['Zone'].str.split(' - ').str[0]

fig4 = px.bar(
    zone_fp.sort_values('Avg Footfall Score', ascending=False),
    x='Zone Short', y='Avg Footfall Score',
    color='Avg Footfall Score',
    color_continuous_scale='RdYlGn',
    text='Avg Footfall Score',
    title='Which zones have the best footfall?',
    height=320,
    labels={'Zone Short': 'Zone', 'Avg Footfall Score': 'Avg Score /100'},
)
fig4.update_traces(texttemplate='%{text:.0f}', textposition='outside')
fig4.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Registered vendor list ────────────────────────────────────────────────────
st.subheader("Registered Vendors on Platform")
st.dataframe(VENDORS, use_container_width=True, hide_index=True)

st.divider()

# ── Full stall allocation table ───────────────────────────────────────────────
st.subheader("Full Stall Allocation")
status_filter = st.multiselect(
    "Filter by Status",
    ['Booked', 'Available', 'Waitlisted'],
    default=['Booked', 'Available', 'Waitlisted']
)
display_df = stalls_df[stalls_df['Status'].isin(status_filter)][
    ['Stall ID', 'Zone', 'Footfall Score', 'Status', 'Vendor Category', 'Price (₹)']
]
st.dataframe(display_df, use_container_width=True, hide_index=True)
