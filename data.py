import pandas as pd
import numpy as np
import hashlib
import streamlit as st

# ── Shared CSS applied across all pages ───────────────────────────────────────
def apply_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');

    html, body, [class*="css"], .stMarkdown {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }
    .stDeployButton { display: none !important; }

    /* ── Sidebar dark ── */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: #0F172A !important;
    }
    [data-testid="stSidebarNav"] a {
        color: #94A3B8 !important;
        border-radius: 8px;
        padding: 6px 10px !important;
        font-size: 0.88rem;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(255,107,53,0.15) !important;
        color: #FF6B35 !important;
    }
    [data-testid="stSidebarNav"] a[aria-selected="true"] {
        background: rgba(255,107,53,0.2) !important;
        color: #FF6B35 !important;
        font-weight: 700;
        border-left: 3px solid #FF6B35;
    }

    /* ── Main layout ── */
    .block-container {
        padding-top: 0.5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 1350px !important;
    }

    /* ── Stat cards ── */
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 22px 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 20px rgba(0,0,0,0.07);
        border-top: 4px solid #FF6B35;
    }
    .stat-num   { font-size: 2.4rem; font-weight: 900; color: #FF6B35; letter-spacing: -1px; line-height: 1.1; }
    .stat-sub   { font-size: 0.72rem; color: #43A047; font-weight: 600; margin-top: 4px; }
    .stat-label { font-size: 0.73rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px; }

    /* ── Problem / Solution cards ── */
    .problem-card {
        background: #FFF5F0;
        border: 1.5px solid #FF6B35;
        border-radius: 16px;
        padding: 28px 26px;
        height: 100%;
    }
    .solution-card {
        background: #F0FFF4;
        border: 1.5px solid #43A047;
        border-radius: 16px;
        padding: 28px 26px;
        height: 100%;
    }

    /* ── Step cards ── */
    .step-card {
        background: white;
        border-radius: 14px;
        padding: 22px 18px;
        text-align: center;
        box-shadow: 0 2px 16px rgba(0,0,0,0.06);
        border-bottom: 3px solid #FF6B35;
        height: 100%;
    }
    .step-icon {
        width: 46px; height: 46px;
        background: linear-gradient(135deg, #FF6B35, #FF8C61);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 12px;
        font-size: 1.3rem;
        color: white;
        font-weight: 800;
        box-shadow: 0 4px 12px rgba(255,107,53,0.35);
    }

    /* ── Recommendation cards ── */
    .rec-gold  { background: linear-gradient(135deg,#FFFDE7,#FFF9C4); border: 2px solid #F9A825; border-radius: 16px; padding: 24px; margin-bottom: 14px; }
    .rec-green { background: linear-gradient(135deg,#E8F5E9,#F1F8E9); border: 2px solid #43A047; border-radius: 16px; padding: 24px; margin-bottom: 14px; }
    .rec-blue  { background: linear-gradient(135deg,#E3F2FD,#EDE7F6); border: 2px solid #1E88E5; border-radius: 16px; padding: 24px; margin-bottom: 14px; }

    /* ── Tags ── */
    .tag {
        display: inline-block;
        padding: 3px 11px;
        border-radius: 20px;
        font-size: 0.73rem;
        font-weight: 600;
        margin-right: 5px;
        margin-bottom: 4px;
    }
    .tag-orange { background:#FFF3E0; color:#E65100; }
    .tag-green  { background:#E8F5E9; color:#2E7D32; }
    .tag-blue   { background:#E3F2FD; color:#1565C0; }
    .tag-gray   { background:#F1F5F9; color:#475569; }

    /* ── Nav cards on Home ── */
    .nav-card {
        background: white;
        border-radius: 12px;
        padding: 18px 16px;
        border-left: 4px solid #FF6B35;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────
MARKETS = pd.DataFrame({
    'Market Name': [
        'Malakpet Sunday Market', 'Kukatpally Weekly Bazaar', 'HITEC City Food Fest',
        'Jubilee Hills Exhibition', 'Madhapur Night Market', 'Secunderabad Grand Fair',
        'Banjara Hills Farmers Market', 'LB Nagar Weekend Market',
        'Ameerpet Food Street', 'Gachibowli Tech Park Fair'
    ],
    'Area': [
        'Malakpet', 'Kukatpally', 'HITEC City', 'Jubilee Hills', 'Madhapur',
        'Secunderabad', 'Banjara Hills', 'LB Nagar', 'Ameerpet', 'Gachibowli'
    ],
    'Day': [
        'Sunday', 'Saturday', 'Friday', 'Sat-Sun', 'Thu-Fri',
        'Sunday', 'Saturday', 'Sat-Sun', 'Wednesday', 'Saturday'
    ],
    'Expected Footfall': [4200, 3800, 5500, 6200, 4800, 3500, 2900, 3200, 2600, 4100],
    'Stall Price': [800, 750, 1200, 1500, 1000, 700, 900, 800, 650, 1100],
    'Total Stalls': [44, 36, 60, 72, 52, 36, 28, 40, 32, 48],
    'Available Stalls': [12, 8, 24, 18, 10, 15, 9, 20, 7, 22],
    'Type': [
        'Weekly Market', 'Weekly Market', 'Food Festival', 'Exhibition', 'Night Market',
        'Fair', 'Farmers Market', 'Weekly Market', 'Food Street', 'Tech Park Fair'
    ],
    'Lat': [17.3616, 17.4849, 17.4435, 17.4239, 17.4478, 17.4415, 17.4145, 17.3483, 17.4375, 17.4401],
    'Lon': [78.4747, 78.4007, 78.3772, 78.4072, 78.3762, 78.4978, 78.4378, 78.5390, 78.4485, 78.3489],
    'Rating': [4.2, 3.9, 4.6, 4.5, 4.3, 3.7, 4.1, 3.8, 3.5, 4.4],
})

CATEGORIES = [
    'Street Food & Snacks', 'Bakery Items',
    'Homemade Food Products', 'Beverages & Desserts', 'Festival Food'
]

REVENUE_DATA = {
    'Street Food & Snacks': {
        'Weekly Market':  {'low': 900,  'avg': 1800, 'high': 3200},
        'Food Festival':  {'low': 1500, 'avg': 3200, 'high': 5500},
        'Exhibition':     {'low': 1200, 'avg': 2800, 'high': 4800},
        'Night Market':   {'low': 1100, 'avg': 2400, 'high': 4200},
        'Fair':           {'low': 800,  'avg': 1600, 'high': 2800},
        'Farmers Market': {'low': 700,  'avg': 1400, 'high': 2400},
        'Food Street':    {'low': 600,  'avg': 1200, 'high': 2000},
        'Tech Park Fair': {'low': 1300, 'avg': 2600, 'high': 4500},
    },
    'Bakery Items': {
        'Weekly Market':  {'low': 800,  'avg': 1600, 'high': 2800},
        'Food Festival':  {'low': 1400, 'avg': 2900, 'high': 5000},
        'Exhibition':     {'low': 1100, 'avg': 2500, 'high': 4200},
        'Night Market':   {'low': 900,  'avg': 2000, 'high': 3500},
        'Fair':           {'low': 700,  'avg': 1500, 'high': 2500},
        'Farmers Market': {'low': 900,  'avg': 1800, 'high': 3200},
        'Food Street':    {'low': 500,  'avg': 1100, 'high': 1900},
        'Tech Park Fair': {'low': 1200, 'avg': 2400, 'high': 4000},
    },
    'Homemade Food Products': {
        'Weekly Market':  {'low': 600,  'avg': 1300, 'high': 2400},
        'Food Festival':  {'low': 1000, 'avg': 2400, 'high': 4200},
        'Exhibition':     {'low': 900,  'avg': 2100, 'high': 3800},
        'Night Market':   {'low': 700,  'avg': 1700, 'high': 3000},
        'Fair':           {'low': 600,  'avg': 1300, 'high': 2200},
        'Farmers Market': {'low': 1100, 'avg': 2200, 'high': 4000},
        'Food Street':    {'low': 400,  'avg': 900,  'high': 1600},
        'Tech Park Fair': {'low': 1000, 'avg': 2000, 'high': 3500},
    },
    'Beverages & Desserts': {
        'Weekly Market':  {'low': 1000, 'avg': 2000, 'high': 3600},
        'Food Festival':  {'low': 1800, 'avg': 3600, 'high': 6000},
        'Exhibition':     {'low': 1400, 'avg': 3000, 'high': 5200},
        'Night Market':   {'low': 1300, 'avg': 2800, 'high': 4800},
        'Fair':           {'low': 900,  'avg': 1800, 'high': 3200},
        'Farmers Market': {'low': 800,  'avg': 1600, 'high': 2800},
        'Food Street':    {'low': 700,  'avg': 1400, 'high': 2400},
        'Tech Park Fair': {'low': 1500, 'avg': 3000, 'high': 5000},
    },
    'Festival Food': {
        'Weekly Market':  {'low': 700,  'avg': 1500, 'high': 2600},
        'Food Festival':  {'low': 2000, 'avg': 4000, 'high': 7000},
        'Exhibition':     {'low': 1500, 'avg': 3200, 'high': 5500},
        'Night Market':   {'low': 1200, 'avg': 2500, 'high': 4500},
        'Fair':           {'low': 1000, 'avg': 2000, 'high': 3500},
        'Farmers Market': {'low': 600,  'avg': 1300, 'high': 2200},
        'Food Street':    {'low': 500,  'avg': 1000, 'high': 1800},
        'Tech Park Fair': {'low': 1100, 'avg': 2200, 'high': 3800},
    },
}

VENDORS = pd.DataFrame({
    'Vendor Name': [
        'Priya Snacks', 'Raju Bakery', 'Meena Home Foods', 'Chai Corner',
        'Festival Eats', 'Biryani Point', 'Sweet Tooth', 'Spice Hub'
    ],
    'Category': [
        'Street Food & Snacks', 'Bakery Items', 'Homemade Food Products',
        'Beverages & Desserts', 'Festival Food', 'Street Food & Snacks',
        'Beverages & Desserts', 'Street Food & Snacks'
    ],
    'Reliability Score': [92, 88, 95, 79, 85, 91, 76, 83],
    'Total Bookings': [47, 38, 62, 29, 41, 55, 22, 36],
    'Cancellations': [2, 3, 0, 4, 3, 2, 5, 3],
    'Avg Daily Revenue (₹)': [2400, 1900, 2100, 2800, 3200, 2600, 2200, 2050],
    'Markets Visited': [8, 6, 9, 5, 7, 8, 4, 6],
})


def generate_stall_map(market_name, total_stalls=40):
    seed = int(hashlib.md5(market_name.encode()).hexdigest(), 16) % (2 ** 31)
    rng  = np.random.RandomState(seed)

    zones_config = [
        ('A - Entrance Zone', 80, 95),
        ('B - Main Walkway',  60, 79),
        ('C - Inner Area',    40, 59),
        ('D - Back Area',     20, 39),
    ]

    stalls   = []
    per_zone = max(1, total_stalls // 4)
    cols     = 7

    for zone_idx, (zone_name, fp_min, fp_max) in enumerate(zones_config):
        rows_in_zone = max(1, (per_zone - 1) // cols + 1)
        y_base       = zone_idx * (rows_in_zone + 2)

        for i in range(per_zone):
            r = rng.random()
            if r < 0.58:
                status   = 'Booked'
                category = rng.choice(['Street Food', 'Bakery', 'Beverages', 'Homemade', 'Festival Food'])
            elif r < 0.85:
                status   = 'Available'
                category = '—'
            else:
                status   = 'Waitlisted'
                category = '—'

            zone_prefix = zone_name[0]
            stalls.append({
                'Stall ID':       f'{zone_prefix}{i + 1:02d}',
                'Zone':           zone_name,
                'Footfall Score': int(rng.randint(fp_min, fp_max + 1)),
                'Status':         status,
                'Vendor Category': category,
                'Price (₹)':      900 if zone_prefix in ['A', 'B'] else 650,
                'X':              i % cols,
                'Y':              y_base + i // cols,
            })

    return pd.DataFrame(stalls)
