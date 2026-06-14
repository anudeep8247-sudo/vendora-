import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import apply_css

st.set_page_config(
    page_title="Vendora — Smart Stall Booking",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_css()

# ── Hero Banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #FF6B35 0%, #E8400C 60%, #C62828 100%);
    border-radius: 22px;
    padding: 52px 40px 48px;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(255,107,53,0.3);
">
  <div style="font-size:3.8rem; font-weight:900; color:white; letter-spacing:-3px; margin-bottom:10px;">
    🏪 VENDORA
  </div>
  <div style="font-size:1.1rem; color:rgba(255,255,255,0.88); max-width:580px; margin:0 auto; line-height:1.6;">
    Smart Stall Booking &amp; Market Intelligence for Hyderabad's Food Vendors
  </div>
  <div style="margin-top:20px; display:flex; justify-content:center; gap:10px; flex-wrap:wrap;">
    <span style="background:rgba(255,255,255,0.18); color:white; padding:5px 16px; border-radius:20px; font-size:0.82rem; font-weight:600;">📍 Hyderabad</span>
    <span style="background:rgba(255,255,255,0.18); color:white; padding:5px 16px; border-radius:20px; font-size:0.82rem; font-weight:600;">🏪 25,000+ Micro-Vendors</span>
    <span style="background:rgba(255,255,255,0.18); color:white; padding:5px 16px; border-radius:20px; font-size:0.82rem; font-weight:600;">💰 Up to 4x Revenue Uplift</span>
    <span style="background:rgba(255,255,255,0.18); color:white; padding:5px 16px; border-radius:20px; font-size:0.82rem; font-weight:600;">📊 Data-Driven Placement</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stat Cards ────────────────────────────────────────────────────────────────
stats = [
    ("10",    "+2 new this month",  "Active Markets"),
    ("847",   "+23 this week",      "Registered Vendors"),
    ("2,340", "this season",        "Stalls Booked"),
    ("68%",   "vs unplanned vendors", "Avg Revenue Uplift"),
]
cols = st.columns(4)
for col, (num, sub, label) in zip(cols, stats):
    col.markdown(f"""
    <div class="stat-card">
      <div class="stat-num">{num}</div>
      <div class="stat-sub">↑ {sub}</div>
      <div class="stat-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Dark Stats Section ────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: #0F172A;
    border-radius: 18px;
    padding: 36px 32px;
    margin: 0.5rem 0 1.5rem 0;
">
  <div style="text-align:center; color:#64748B; font-size:0.72rem; text-transform:uppercase;
              letter-spacing:0.15em; margin-bottom:24px; font-weight:600;">
    THE NUMBERS BEHIND THE PROBLEM
  </div>
  <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:16px; text-align:center;">
    <div>
      <div style="font-size:2.8rem; font-weight:900; color:#FF6B35; letter-spacing:-2px;">82%</div>
      <div style="color:#94A3B8; font-size:0.82rem; margin-top:6px; line-height:1.4;">of vendors arrive<br>4–5 AM for a spot</div>
    </div>
    <div>
      <div style="font-size:2.8rem; font-weight:900; color:#FF6B35; letter-spacing:-2px;">40%</div>
      <div style="color:#94A3B8; font-size:0.82rem; margin-top:6px; line-height:1.4;">still land in<br>low-traffic zones</div>
    </div>
    <div>
      <div style="font-size:2.8rem; font-weight:900; color:#FF6B35; letter-spacing:-2px;">4x</div>
      <div style="color:#94A3B8; font-size:0.82rem; margin-top:6px; line-height:1.4;">revenue gap between<br>best &amp; worst spots</div>
    </div>
    <div>
      <div style="font-size:2.8rem; font-weight:900; color:#FF6B35; letter-spacing:-2px;">60%</div>
      <div style="color:#94A3B8; font-size:0.82rem; margin-top:6px; line-height:1.4;">first-timers quit<br>after 2 appearances</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Problem vs Solution ───────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="problem-card">
      <div style="font-size:1rem; font-weight:700; color:#C62828; margin-bottom:14px;">
        😓 Before Vendora
      </div>
      <div style="line-height:2.1; color:#374151; font-size:0.92rem;">
        🕓 Wake up at 4 AM just to get a <b>decent spot</b><br>
        📍 35–40% still end up in <b>low-traffic zones</b><br>
        📉 Poor placement = <b>40–60% lower sales</b><br>
        🎲 No footfall data — placement is <b>pure luck</b><br>
        💸 ₹600–900/day below <b>break-even</b> in bad spots
      </div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="solution-card">
      <div style="font-size:1rem; font-weight:700; color:#2E7D32; margin-bottom:14px;">
        ✅ With Vendora
      </div>
      <div style="line-height:2.1; color:#374151; font-size:0.92rem;">
        📅 Book stalls <b>days in advance</b> — no early rush<br>
        🎯 See <b>footfall scores</b> for every stall before booking<br>
        🔥 Know <b>competitor density</b> by zone &amp; category<br>
        💰 <b>Predict your revenue</b> before showing up<br>
        ⭐ Build a <b>reliability score</b> for premium early access
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── How it Works ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; font-size:1.4rem; font-weight:800; color:#0F172A; margin-bottom:20px;">
  How It Works
</div>
""", unsafe_allow_html=True)

steps = [
    ("🔍", "1", "Discover",  "Browse markets, food fests, and events happening across Hyderabad"),
    ("📊", "2", "Analyse",   "Compare footfall, competitor density, and revenue potential by stall"),
    ("📍", "3", "Book",      "Reserve your exact stall from an interactive map — paid & confirmed"),
    ("💰", "4", "Earn More", "Show up to the right spot, track performance, grow your score"),
]
cols = st.columns(4)
for col, (icon, num, title, desc) in zip(cols, steps):
    col.markdown(f"""
    <div class="step-card">
      <div class="step-icon">{num}</div>
      <div style="font-size:1.5rem; margin-bottom:6px;">{icon}</div>
      <div style="font-weight:700; font-size:0.95rem; color:#1E293B; margin-bottom:8px;">{title}</div>
      <div style="font-size:0.82rem; color:#64748B; line-height:1.5;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Navigation Guide ──────────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:1.1rem; font-weight:700; color:#0F172A; margin-bottom:14px;">
  👈 Navigate from the sidebar
</div>
""", unsafe_allow_html=True)

nav = [
    ("🛒", "Market Discovery",      "Browse and filter all markets on a live Hyderabad map"),
    ("📍", "Stall Map & Booking",   "Visual stall grid — pick your spot by footfall score"),
    ("💰", "Revenue Predictor",     "Estimate earnings + live simulation slider + break-even calc"),
    ("🔥", "Competitor Heatmap",    "See zone saturation for your food category before booking"),
    ("⭐", "Best Markets",          "Ranked recommendations with ROI, profit, and radar chart"),
    ("🎯", "Smart Suggest",         "AI-style recommendation — fill your profile, get your best match"),
    ("📊", "Organizer Dashboard",   "Occupancy tracking, revenue gauges, full stall allocation view"),
]
col1, col2 = st.columns(2)
for i, (icon, title, desc) in enumerate(nav):
    target = col1 if i % 2 == 0 else col2
    target.markdown(f"""
    <div class="nav-card">
      <span style="font-size:1rem;">{icon}</span>
      <strong style="color:#0F172A;"> {title}</strong>
      <span style="color:#64748B; font-size:0.85rem;"> — {desc}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Vendora · BBA Innovation Project 2025 · Mahindra University, Hyderabad")
