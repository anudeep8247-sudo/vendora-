import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from data import MARKETS, CATEGORIES, REVENUE_DATA, apply_css

st.set_page_config(page_title="Smart Suggest — Vendora", page_icon="🎯", layout="wide")
apply_css()

st.markdown("""
<div style="margin-bottom:4px;">
  <span style="font-size:2rem; font-weight:900; color:#0F172A;">🎯 Smart Suggest</span>
</div>
<div style="color:#64748B; font-size:0.92rem; margin-bottom:1.5rem;">
  Tell us about yourself — we'll find your best market and stall match.
</div>
""", unsafe_allow_html=True)


# ── Scoring algorithm ─────────────────────────────────────────────────────────
def score_markets(category, max_budget, preferred_day, area_pref):
    results = []
    for _, row in MARKETS.iterrows():
        mt = row['Type']
        if mt not in REVENUE_DATA[category]:
            continue
        if row['Stall Price'] > max_budget:
            continue
        if preferred_day != 'Any Day' and preferred_day not in row['Day']:
            continue
        if area_pref != 'Any Area' and row['Area'] != area_pref:
            continue
        if row['Available Stalls'] == 0:
            continue

        rev        = REVENUE_DATA[category][mt]
        profit     = rev['avg'] - row['Stall Price']
        roi        = profit / row['Stall Price']

        # 5 dimensions, each 0–100
        rev_score   = min(100, (rev['avg']               / 7000) * 100)
        roi_score   = min(100, max(0, roi)                * 60)
        fp_score    = min(100, (row['Expected Footfall']  / 6200) * 100)
        avail_score = (row['Available Stalls'] / row['Total Stalls']) * 100
        rate_score  = (row['Rating'] / 5.0)                 * 100

        composite = (
            rev_score   * 0.35 +
            roi_score   * 0.25 +
            fp_score    * 0.20 +
            avail_score * 0.10 +
            rate_score  * 0.10
        )

        results.append({
            'market':       row['Market Name'],
            'area':         row['Area'],
            'type':         mt,
            'day':          row['Day'],
            'fee':          int(row['Stall Price']),
            'avg_rev':      rev['avg'],
            'low_rev':      rev['low'],
            'high_rev':     rev['high'],
            'profit':       profit,
            'roi':          round(roi * 100, 1),
            'footfall':     int(row['Expected Footfall']),
            'available':    int(row['Available Stalls']),
            'rating':       row['Rating'],
            'match':        round(composite),
            # dimension scores for radar
            'd_rev':    round(rev_score),
            'd_roi':    round(roi_score),
            'd_fp':     round(fp_score),
            'd_avail':  round(avail_score),
            'd_rate':   round(rate_score),
        })

    return sorted(results, key=lambda x: x['match'], reverse=True)[:3]


# ── Input Form ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:16px; padding:28px; margin-bottom:1.5rem;">
  <div style="font-weight:700; color:#1E293B; margin-bottom:16px; font-size:1rem;">Step 1 — Tell us about you</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    category = st.selectbox("🍽️ Food Category", CATEGORIES)
with col2:
    max_budget = st.selectbox("💸 Max Stall Budget (₹)", [750, 900, 1000, 1200, 1500, 2000], index=2)
with col3:
    preferred_day = st.selectbox("📅 Preferred Day",
        ['Any Day', 'Sunday', 'Saturday', 'Friday', 'Wednesday', 'Sat-Sun', 'Thu-Fri'])
with col4:
    area_pref = st.selectbox("📍 Preferred Area",
        ['Any Area'] + sorted(MARKETS['Area'].tolist()))

st.markdown("</div>", unsafe_allow_html=True)

find = st.button("🎯 Find My Best Match", type="primary", use_container_width=True)

if find:
    with st.spinner("Analysing 10 markets across 5 dimensions..."):
        recs = score_markets(category, max_budget, preferred_day, area_pref)

    if not recs:
        st.error("No markets match your filters. Try increasing your budget or selecting 'Any Day'.")
        st.stop()

    # ── Step 2 header ────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-weight:700; color:#1E293B; font-size:1rem; margin:1.5rem 0 1rem 0;">
      Step 2 — Your Personalised Matches
    </div>
    """, unsafe_allow_html=True)

    card_styles = [
        ('rec-gold',  '#F9A825', '🥇 Best Match',         'Most profitable option for you'),
        ('rec-green', '#43A047', '🥈 Strong Alternative', 'Great footfall, solid returns'),
        ('rec-blue',  '#1E88E5', '🥉 Worth Considering',  'Good availability, lower competition'),
    ]

    col_left, col_right = st.columns([3, 2])

    with col_left:
        for i, rec in enumerate(recs):
            if i >= len(card_styles):
                break
            css_cls, border_color, badge, tagline = card_styles[i]

            # Why explanation
            strengths = []
            if rec['d_rev']  > 70: strengths.append("high revenue potential")
            if rec['d_roi']  > 70: strengths.append("strong ROI")
            if rec['d_fp']   > 70: strengths.append("high footfall")
            if rec['d_avail']> 60: strengths.append("good stall availability")
            why = (", ".join(strengths[:3]).capitalize() + ".") if strengths else "Balanced across all dimensions."

            st.markdown(f"""
            <div class="{css_cls}">
              <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:14px;">
                <div>
                  <div style="font-size:0.72rem; font-weight:700; color:{border_color};
                              text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">
                    {badge}
                  </div>
                  <div style="font-size:1.45rem; font-weight:900; color:#0F172A; letter-spacing:-0.5px;">
                    {rec['market']}
                  </div>
                  <div style="color:#64748B; font-size:0.85rem; margin-top:3px;">
                    📍 {rec['area']} &nbsp;·&nbsp; 📅 {rec['day']} &nbsp;·&nbsp; 🏪 {rec['type']}
                  </div>
                </div>
                <div style="text-align:right; flex-shrink:0; margin-left:16px;">
                  <div style="font-size:2.8rem; font-weight:900; color:{border_color}; line-height:1;">
                    {rec['match']}%
                  </div>
                  <div style="font-size:0.7rem; color:#94A3B8; font-weight:600;">match score</div>
                </div>
              </div>

              <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:12px;
                          margin-bottom:14px;">
                <div style="background:rgba(255,255,255,0.7); border-radius:10px; padding:10px; text-align:center;">
                  <div style="font-size:1.2rem; font-weight:800; color:#0F172A;">₹{rec['avg_rev']:,}</div>
                  <div style="font-size:0.7rem; color:#64748B; margin-top:2px;">Avg Revenue</div>
                </div>
                <div style="background:rgba(255,255,255,0.7); border-radius:10px; padding:10px; text-align:center;">
                  <div style="font-size:1.2rem; font-weight:800; color:#0F172A;">₹{rec['profit']:,}</div>
                  <div style="font-size:0.7rem; color:#64748B; margin-top:2px;">Est. Profit</div>
                </div>
                <div style="background:rgba(255,255,255,0.7); border-radius:10px; padding:10px; text-align:center;">
                  <div style="font-size:1.2rem; font-weight:800; color:#0F172A;">{rec['roi']}%</div>
                  <div style="font-size:0.7rem; color:#64748B; margin-top:2px;">ROI</div>
                </div>
                <div style="background:rgba(255,255,255,0.7); border-radius:10px; padding:10px; text-align:center;">
                  <div style="font-size:1.2rem; font-weight:800; color:#0F172A;">{rec['available']}</div>
                  <div style="font-size:0.7rem; color:#64748B; margin-top:2px;">Stalls Free</div>
                </div>
              </div>

              <div style="background:rgba(255,255,255,0.5); border-radius:8px; padding:10px 14px;
                          font-size:0.82rem; color:#475569;">
                <strong>Why this?</strong> {why}
                Revenue range: ₹{rec['low_rev']:,} – ₹{rec['high_rev']:,} &nbsp;·&nbsp; ⭐ {rec['rating']}
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Radar chart for top pick ──────────────────────────────────────────────
    with col_right:
        st.markdown(f"""
        <div style="font-weight:700; color:#1E293B; margin-bottom:12px; font-size:0.9rem;">
          📡 Top Pick — Dimension Breakdown
        </div>
        """, unsafe_allow_html=True)

        top = recs[0]
        dims   = ['Revenue\nPotential', 'ROI', 'Footfall', 'Availability', 'Rating']
        scores = [top['d_rev'], top['d_roi'], top['d_fp'], top['d_avail'], top['d_rate']]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=dims + [dims[0]],
            fill='toself',
            fillcolor='rgba(255,107,53,0.18)',
            line=dict(color='#FF6B35', width=2.5),
            marker=dict(size=7, color='#FF6B35'),
            name=top['market'],
        ))
        if len(recs) > 1:
            s2 = recs[1]
            sc2 = [s2['d_rev'], s2['d_roi'], s2['d_fp'], s2['d_avail'], s2['d_rate']]
            fig.add_trace(go.Scatterpolar(
                r=sc2 + [sc2[0]],
                theta=dims + [dims[0]],
                fill='toself',
                fillcolor='rgba(67,160,71,0.12)',
                line=dict(color='#43A047', width=1.5, dash='dot'),
                marker=dict(size=5, color='#43A047'),
                name=recs[1]['market'],
            ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9)),
                angularaxis=dict(tickfont=dict(size=10)),
            ),
            showlegend=True,
            height=360,
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(font=dict(size=9)),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Comparison bar
        if len(recs) >= 2:
            st.markdown("<div style='font-weight:700; color:#1E293B; margin:12px 0 8px; font-size:0.9rem;'>Match Score Comparison</div>", unsafe_allow_html=True)
            comp_df = pd.DataFrame({
                'Market': [r['market'].split()[0] + '...' if len(r['market']) > 18 else r['market'] for r in recs],
                'Score':  [r['match'] for r in recs],
            })
            fig2 = go.Figure(go.Bar(
                x=comp_df['Score'],
                y=comp_df['Market'],
                orientation='h',
                marker_color=['#FF6B35', '#43A047', '#1E88E5'][:len(recs)],
                text=[f"{s}%" for s in comp_df['Score']],
                textposition='auto',
            ))
            fig2.update_layout(
                height=180, margin=dict(t=0, b=0, l=0, r=20),
                xaxis=dict(range=[0, 100], title='Match Score'),
                yaxis=dict(title=''),
                showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.info("👈 Go to **Stall Map & Booking** in the sidebar to reserve a stall at your top pick.")
