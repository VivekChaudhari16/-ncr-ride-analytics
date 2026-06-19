import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="NCR Rides Analytics", page_icon="🚗", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }
[data-testid="stAppViewContainer"] { background:#0b0c14; }
[data-testid="stSidebar"] { display:none; }
.block-container { padding:0 !important; max-width:100% !important; }
header[data-testid="stHeader"] { display:none; }

/* ── TOP NAV ── */
.top-nav {
    background:#0f1018;
    border-bottom:1px solid #1c1f2e;
    padding:14px 28px;
    display:flex; align-items:center; justify-content:space-between;
}
.nav-brand { font-size:1.35rem; font-weight:800; color:#fff; letter-spacing:-0.02em; }
.nav-brand span { color:#06C167; font-style:italic; }
.nav-meta { font-size:0.78rem; color:#555577; display:flex; align-items:center; gap:16px; }
.nav-badge {
    background:#0d2d1e; border:1px solid #06C167;
    color:#06C167; padding:4px 12px; border-radius:20px;
    font-size:0.72rem; font-weight:600; letter-spacing:0.03em;
    display:flex; align-items:center; gap:5px;
}
.nav-dot { width:7px; height:7px; background:#06C167; border-radius:50%; animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* ── FILTER BAR ── */
.filter-bar {
    background:#0f1018; border-bottom:1px solid #1c1f2e;
    padding:10px 28px; display:flex; align-items:center; gap:20px; flex-wrap:wrap;
}
.filter-group { display:flex; align-items:center; gap:8px; }
.filter-label { font-size:0.65rem; font-weight:600; color:#444466;
    text-transform:uppercase; letter-spacing:0.1em; white-space:nowrap; }
.filter-pills { display:flex; gap:6px; flex-wrap:wrap; }
.pill {
    padding:5px 14px; border-radius:20px; font-size:0.75rem; font-weight:500;
    cursor:pointer; border:1px solid #2a2a4a; background:#13141f; color:#8888bb;
    transition:all 0.15s ease; white-space:nowrap;
}
.pill.active { background:#06C167; color:#000; border-color:#06C167; font-weight:700; }
.pill.active-status { border-color:currentColor; }
.records-bar {
    background:#0f1018; border-bottom:1px solid #1c1f2e;
    padding:7px 28px; text-align:right;
    font-size:0.75rem; color:#444466;
}
.records-bar b { color:#06C167; }

/* ── SECTION LABEL ── */
.section-label {
    font-size:0.65rem; font-weight:700; color:#333355;
    text-transform:uppercase; letter-spacing:0.15em;
    padding:20px 28px 10px 28px; display:flex; align-items:center; gap:12px;
}
.section-label::after { content:''; flex:1; height:1px; background:#1c1f2e; }

/* ── KPI CARDS ── */
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:1px;
    background:#1c1f2e; margin:0 28px 1px 28px; border-radius:16px; overflow:hidden; }
.kpi-card {
    background:#0f1018; padding:22px 24px; position:relative; overflow:hidden;
}
.kpi-card::after {
    content:''; position:absolute; bottom:0; left:0; right:0; height:2px;
}
.kpi-card.c1::after { background:linear-gradient(90deg,#1FBAD6,transparent); }
.kpi-card.c2::after { background:linear-gradient(90deg,#06C167,transparent); }
.kpi-card.c3::after { background:linear-gradient(90deg,#FFD166,transparent); }
.kpi-card.c4::after { background:linear-gradient(90deg,#EF233C,transparent); }
.kpi-card.c5::after { background:linear-gradient(90deg,#A259FF,transparent); }
.kpi-card.c6::after { background:linear-gradient(90deg,#FF6B35,transparent); }
.kpi-card.c7::after { background:linear-gradient(90deg,#F72585,transparent); }
.kpi-card.c8::after { background:linear-gradient(90deg,#4CC9F0,transparent); }
.kpi-icon { font-size:1.4rem; margin-bottom:10px; display:block; }
.kpi-title { font-size:0.63rem; font-weight:600; color:#444466;
    text-transform:uppercase; letter-spacing:0.12em; margin-bottom:6px; }
.kpi-val { font-size:1.9rem; font-weight:800; line-height:1; margin-bottom:4px; }
.kpi-val.c1 { color:#1FBAD6; } .kpi-val.c2 { color:#06C167; }
.kpi-val.c3 { color:#FFD166; } .kpi-val.c4 { color:#EF233C; }
.kpi-val.c5 { color:#A259FF; } .kpi-val.c6 { color:#FF6B35; }
.kpi-val.c7 { color:#F72585; } .kpi-val.c8 { color:#4CC9F0; }
.kpi-sub { font-size:0.68rem; color:#333355; }
.kpi-bar { height:2px; background:#1c1f2e; margin-top:14px; border-radius:2px; overflow:hidden; }
.kpi-bar-fill { height:100%; border-radius:2px; }

/* ── CHART AREA ── */
.chart-grid { display:grid; gap:1px; background:#1c1f2e; margin:0 28px 28px 28px; border-radius:16px; overflow:hidden; }
.chart-grid.cols2 { grid-template-columns:1fr 1fr; }
.chart-grid.cols3 { grid-template-columns:2fr 1fr; }
.chart-box { background:#0f1018; padding:20px; }
.chart-title { font-size:0.88rem; font-weight:700; color:#ccccee; margin-bottom:2px; }
.chart-sub { font-size:0.7rem; color:#333355; margin-bottom:0; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background:#0f1018 !important; gap:2px !important;
    border-bottom:1px solid #1c1f2e !important; padding:0 28px !important;
    border-radius:0 !important;
}
.stTabs [data-baseweb="tab"] {
    background:transparent !important; color:#555577 !important;
    border-radius:0 !important; padding:12px 20px !important;
    font-size:0.82rem !important; font-weight:500 !important;
    border:none !important; border-bottom:2px solid transparent !important;
}
.stTabs [data-baseweb="tab"] p { color:#888899 !important; font-size:0.82rem !important; }
.stTabs [aria-selected="true"] {
    background:transparent !important; color:#ffffff !important;
    border-bottom:2px solid #06C167 !important; font-weight:700 !important;
}
.stTabs [aria-selected="true"] p { color:#ffffff !important; font-weight:700 !important; }
.stTabs [data-baseweb="tab-highlight"] { display:none !important; }
.stTabs [data-baseweb="tab-border"] { display:none !important; }
.stTabs [data-baseweb="tab-panel"] { padding:0 !important; }

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] { border-radius:12px; overflow:hidden; }
iframe { border-radius:12px; }
</style>
""", unsafe_allow_html=True)

# ── COLORS & CHART THEME ────────────────────────────────────
C = ['#06C167','#1FBAD6','#FF6B35','#A259FF','#FFD166','#EF233C','#4CC9F0','#F72585']

def mk(title="", height=340):
    return dict(
        plot_bgcolor='#0f1018', paper_bgcolor='#0f1018',
        font=dict(color='#666688', family='Inter', size=11),
        title=dict(text="", font=dict(color='#ccccee', size=13)),
        xaxis=dict(gridcolor='#1a1a2a', showgrid=True, color='#444466',
                   linecolor='#1c1f2e', tickfont=dict(size=10, color='#555577')),
        yaxis=dict(gridcolor='#1a1a2a', showgrid=True, color='#444466',
                   linecolor='#1c1f2e', tickfont=dict(size=10, color='#555577')),
        legend=dict(bgcolor='rgba(0,0,0,0)', borderwidth=0,
                    font=dict(color='#888899', size=10)),
        margin=dict(t=20, b=36, l=50, r=16),
        hoverlabel=dict(bgcolor='#1a1a2e', bordercolor='#2a2a4a',
                        font=dict(color='white', size=11, family='Inter')),
        height=height
    )

# ── LOAD DATA ───────────────────────────────────────────────
import json

@st.cache_data
def load_locations():
    with open("ncr_locations.json") as f:
        return json.load(f)

@st.cache_data
def load():
    df = pd.read_csv("ncr_ride_bookings.csv")
    df['Date']      = pd.to_datetime(df['Date'])
    df['Hour']      = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour
    df['Month']     = df['Date'].dt.strftime('%B')
    df['Month_Num'] = df['Date'].dt.month
    df['DayOfWeek'] = df['Date'].dt.strftime('%A')
    df['Quarter']   = 'Q' + df['Date'].dt.quarter.astype(str)
    return df

df = load()
MONTHS  = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
MO_FULL = ['January','February','March','April','May','June',
           'July','August','September','October','November','December']
DAYS    = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
VEHICLES = ['All'] + sorted(df['Vehicle Type'].dropna().unique())
STATUSES = {
    'All':'All','Completed':'Completed','Driver Cancel':'Cancelled by Driver',
    'Cust Cancel':'Cancelled by Customer','No Driver':'No Driver Found','Incomplete':'Incomplete'
}

# ── TOP NAV ─────────────────────────────────────────────────
st.markdown("""
<div class="top-nav">
  <div class="nav-brand">NCR Rides <span>Analytics</span></div>
  <div class="nav-meta">
    <span>Jan 2024 – Dec 2024 &nbsp;·&nbsp; 150,000 bookings</span>
    <div class="nav-badge"><div class="nav-dot"></div> Interactive Filters Active</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── FILTER BAR ──────────────────────────────────────────────
col_v, col_s = st.columns([3,2])
with col_v:
    sel_v = st.selectbox("VEHICLE", VEHICLES, index=0, label_visibility="visible", key="veh")
with col_s:
    sel_s = st.selectbox("STATUS", list(STATUSES.keys()), index=0, label_visibility="visible", key="stat")

# ── FILTER DATA ─────────────────────────────────────────────
# Base filter: vehicle only (used for Cancellations/Overview status mix)
fd_vehicle = df.copy()
if sel_v != 'All':
    fd_vehicle = fd_vehicle[fd_vehicle['Vehicle Type'] == sel_v]

# Full filter: vehicle + status (used for most tabs)
fd = fd_vehicle.copy()
if sel_s != 'All':
    fd = fd[fd['Booking Status'] == STATUSES[sel_s]]

fd_c = fd[fd['Booking Status'] == 'Completed']

total       = len(fd)
completed   = len(fd_c)
comp_rate   = completed / total * 100 if total else 0
revenue     = fd_c['Booking Value'].sum() if completed else 0
avg_fare    = fd_c['Booking Value'].mean() if completed else 0
cancelled   = fd['Booking Status'].str.startswith('Cancelled').sum()
cancel_rate = cancelled / total * 100 if total else 0
avg_dr      = fd_c['Driver Ratings'].mean() if completed else 0
avg_cr      = fd_c['Customer Rating'].mean() if completed else 0
avg_dist    = fd_c['Ride Distance'].mean() if completed else 0
avg_vtat    = fd['Avg VTAT'].mean() if total else 0
avg_ctat    = fd_c['Avg CTAT'].mean() if completed else 0

st.markdown(f"**Showing {total:,} records** — Vehicle: `{sel_v}` | Status: `{sel_s}`")
st.markdown("---")

# ── TABS ────────────────────────────────────────────────────
t1,t2,t3,t4,t5,t6 = st.tabs(["📊 Overview","⏰ Time Analysis","🚗 Vehicles & Routes","❌ Cancellations","⭐ Ratings & Wait","🗺️ Map View"])

# ════════════ TAB 1 ══════════════════════════════════════════
with t1:
    # KPI CARDS
    st.markdown('<div class="section-label">KEY PERFORMANCE INDICATORS</div>', unsafe_allow_html=True)

    def rev_fmt(v):
        if v >= 1e6: return f"₹{v/1e5:.1f}L"
        return f"₹{v/1000:.1f}K"

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card c1">
        <span class="kpi-icon">🚗</span>
        <div class="kpi-title">Total Bookings</div>
        <div class="kpi-val c1">{total:,}</div>
        <div class="kpi-sub">bookings in selection</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:100%;background:#1FBAD6"></div></div>
      </div>
      <div class="kpi-card c2">
        <span class="kpi-icon">✅</span>
        <div class="kpi-title">Completed Rides</div>
        <div class="kpi-val c2">{completed:,}</div>
        <div class="kpi-sub">{comp_rate:.1f}% completion rate</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{comp_rate:.0f}%;background:#06C167"></div></div>
      </div>
      <div class="kpi-card c3">
        <span class="kpi-icon">💰</span>
        <div class="kpi-title">Total Revenue</div>
        <div class="kpi-val c3">{rev_fmt(revenue)}</div>
        <div class="kpi-sub">Avg ₹{avg_fare:.0f} per ride</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:80%;background:#FFD166"></div></div>
      </div>
      <div class="kpi-card c4">
        <span class="kpi-icon">❌</span>
        <div class="kpi-title">Cancellations</div>
        <div class="kpi-val c4">{cancelled:,}</div>
        <div class="kpi-sub">{cancel_rate:.1f}% cancellation rate</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{cancel_rate:.0f}%;background:#EF233C"></div></div>
      </div>
    </div>
    <div style="margin-top:1px"></div>
    <div class="kpi-grid">
      <div class="kpi-card c5">
        <span class="kpi-icon">⭐</span>
        <div class="kpi-title">Avg Driver Rating</div>
        <div class="kpi-val c5">{avg_dr:.2f}</div>
        <div class="kpi-sub">out of 5.00</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{avg_dr/5*100:.0f}%;background:#A259FF"></div></div>
      </div>
      <div class="kpi-card c6">
        <span class="kpi-icon">🌟</span>
        <div class="kpi-title">Avg Cust Rating</div>
        <div class="kpi-val c6">{avg_cr:.2f}</div>
        <div class="kpi-sub">out of 5.00</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{avg_cr/5*100:.0f}%;background:#FF6B35"></div></div>
      </div>
      <div class="kpi-card c7">
        <span class="kpi-icon">📍</span>
        <div class="kpi-title">Avg Ride Distance</div>
        <div class="kpi-val c7">{avg_dist:.1f} km</div>
        <div class="kpi-sub">avg per ride</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:65%;background:#F72585"></div></div>
      </div>
      <div class="kpi-card c8">
        <span class="kpi-icon">⏱️</span>
        <div class="kpi-title">Avg VTAT / CTAT</div>
        <div class="kpi-val c8">{avg_vtat:.1f} / {avg_ctat:.1f}</div>
        <div class="kpi-sub">VTAT / CTAT (min)</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:55%;background:#4CC9F0"></div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── NEW VIZ: Booking-to-Completion Funnel ────────────────
    st.markdown('<div class="section-label">BOOKING TO COMPLETION FUNNEL</div>', unsafe_allow_html=True)
    funnel_total      = total
    funnel_no_driver  = (fd['Booking Status'] != 'No Driver Found').sum()
    funnel_not_cancel = (~fd['Booking Status'].str.startswith('Cancelled')).sum()
    funnel_completed  = completed

    funnel_data = pd.DataFrame({
        'Stage': ['Total Bookings','Driver Assigned','Not Cancelled','Completed'],
        'Count': [funnel_total, funnel_no_driver, funnel_not_cancel, funnel_completed]
    })
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_data['Stage'], x=funnel_data['Count'],
        textinfo='value+percent initial',
        marker=dict(color=['#1FBAD6','#A259FF','#FFD166','#06C167']),
        connector=dict(line=dict(color='#2a2a4a', width=1)),
        textfont=dict(color='white', size=12)
    ))
    fig_funnel.update_layout(**mk(height=320))
    st.plotly_chart(fig_funnel, use_container_width=True, config={'displayModeBar': False})

    st.markdown('<div class="section-label">BOOKING OVERVIEW &amp; TRENDS</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown('<div class="chart-title">Monthly Bookings &amp; Revenue Trend</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">Ride count (bars) vs total revenue line — Jan to Dec 2024</div>', unsafe_allow_html=True)
        if completed:
            mo = fd_c.groupby(['Month','Month_Num']).agg(
                Rides=('Booking Value','count'), Revenue=('Booking Value','sum')
            ).reset_index().sort_values('Month_Num')
            mo['Mon'] = mo['Month'].str[:3]
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=mo['Mon'], y=mo['Rides'],
                name='Rides', marker_color='#1a3a2a',
                marker_line_color='#06C167', marker_line_width=1,
                hovertemplate='%{x}<br>Rides: %{y:,}<extra></extra>'), secondary_y=False)
            fig.add_trace(go.Scatter(x=mo['Mon'], y=mo['Revenue'],
                name='Revenue(₹)', mode='lines+markers',
                line=dict(color='#FFD166', width=2.5),
                marker=dict(size=7, color='#FFD166', line=dict(color='#0b0c14', width=2)),
                hovertemplate='%{x}<br>₹%{y:,.0f}<extra></extra>'), secondary_y=True)
            layout = mk(height=300)
            layout['legend'] = dict(orientation='h', y=-0.15, x=0,
                bgcolor='rgba(0,0,0,0)', font=dict(color='#888899', size=10))
            fig.update_layout(**layout)
            fig.update_yaxes(gridcolor='#1a1a2a', color='#444466',
                tickfont=dict(size=10, color='#555577'), secondary_y=False)
            fig.update_yaxes(gridcolor='#1a1a2a', color='#444466',
                tickfont=dict(size=10, color='#555577'),
                tickprefix='₹', secondary_y=True)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No completed rides in current filter")

    with col2:
        st.markdown('<div class="chart-title">Booking Status Distribution</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">Count and share of each booking outcome</div>', unsafe_allow_html=True)
        sc = fd['Booking Status'].value_counts().reset_index()
        fig2 = px.pie(sc, values='count', names='Booking Status',
            color_discrete_sequence=C, hole=0.6)
        fig2.update_traces(textfont_size=10, textinfo='percent',
            marker=dict(line=dict(color='#0b0c14', width=2)),
            hovertemplate='<b>%{label}</b><br>%{value:,} rides<br>%{percent}<extra></extra>')
        _lay2 = mk(height=300)
        _lay2['legend'] = dict(orientation='v', x=1.02, y=0.5,
            font=dict(color='#888899', size=10), bgcolor='rgba(0,0,0,0)')
        fig2.update_layout(**_lay2)
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="chart-title">Revenue by Vehicle Type</div>', unsafe_allow_html=True)
        if completed:
            vr = fd_c.groupby('Vehicle Type')['Booking Value'].sum().sort_values().reset_index()
            fig3 = px.bar(vr, x='Booking Value', y='Vehicle Type', orientation='h',
                color='Vehicle Type', color_discrete_sequence=C)
            fig3.update_traces(marker_line_width=0,
                hovertemplate='<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>')
            fig3.update_layout(**mk(height=280), showlegend=False, xaxis_tickprefix='₹')
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
    with col4:
        st.markdown('<div class="chart-title">Payment Method Share</div>', unsafe_allow_html=True)
        if completed:
            pm = fd_c['Payment Method'].dropna().value_counts().reset_index()
            fig4 = px.bar(pm, x='count', y='Payment Method', orientation='h',
                color='Payment Method', color_discrete_sequence=C)
            fig4.update_traces(marker_line_width=0,
                hovertemplate='<b>%{y}</b><br>%{x:,} rides<extra></extra>')
            fig4.update_layout(**mk(height=280), showlegend=False)
            st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

# ════════════ TAB 2 ══════════════════════════════════════════
with t2:
    st.markdown('<div class="section-label">TIME-BASED PATTERNS</div>', unsafe_allow_html=True)

    hourly = fd.groupby(['Hour','Booking Status']).size().reset_index(name='count')
    fig = px.line(hourly, x='Hour', y='count', color='Booking Status',
        color_discrete_sequence=C, markers=True)
    fig.update_traces(line_width=2.5, marker_size=6)
    lay = mk(height=320)
    lay['xaxis']['tickvals'] = list(range(0, 24, 2))
    lay['xaxis']['title'] = 'Hour of Day'
    fig.update_layout(**lay)
    st.markdown('<div class="chart-title">Hourly Bookings by Status</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-title">Rides Heatmap — Day × Hour</div>', unsafe_allow_html=True)
        if completed:
            heat = fd_c.groupby(['DayOfWeek','Hour']).size().reset_index(name='rides')
            pivot = heat.pivot(index='DayOfWeek', columns='Hour', values='rides').fillna(0)
            pivot = pivot.reindex([d for d in DAYS if d in pivot.index])
            fig2 = px.imshow(pivot,
                color_continuous_scale=[[0,'#0f1018'],[0.3,'#0d3322'],[1,'#06C167']],
                labels=dict(x='Hour', y='', color='Rides'),
                aspect='auto')
            fig2.update_layout(**mk(height=310))
            fig2.update_coloraxes(showscale=False)
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    with col2:
        st.markdown('<div class="chart-title">Revenue by Day of Week</div>', unsafe_allow_html=True)
        if completed:
            dow = fd_c.groupby('DayOfWeek')['Booking Value'].sum().reset_index()
            dow['ord'] = dow['DayOfWeek'].apply(lambda x: DAYS.index(x) if x in DAYS else 7)
            dow = dow.sort_values('ord')
            fig3 = px.bar(dow, x='DayOfWeek', y='Booking Value',
                color='Booking Value', color_continuous_scale=['#1a1a2e','#06C167'])
            fig3.update_traces(marker_line_width=0,
                hovertemplate='<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>')
            _lay = mk(height=310)
            _lay['yaxis']['tickprefix'] = '₹'
            fig3.update_layout(**_lay, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="chart-title">Quarterly Revenue</div>', unsafe_allow_html=True)
        if completed:
            q = fd_c.groupby('Quarter')['Booking Value'].sum().reset_index()
            fig4 = px.bar(q, x='Quarter', y='Booking Value', color='Quarter',
                color_discrete_sequence=C)
            fig4.update_traces(marker_line_width=0,
                hovertemplate='<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>')
            fig4.update_layout(**mk(height=280), showlegend=False, yaxis_tickprefix='₹')
            st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
    with col4:
        st.markdown('<div class="chart-title">Quarterly Ride Count</div>', unsafe_allow_html=True)
        if completed:
            qr = fd_c.groupby('Quarter').size().reset_index(name='Rides')
            fig5 = px.bar(qr, x='Quarter', y='Rides', color='Quarter',
                color_discrete_sequence=C)
            fig5.update_traces(marker_line_width=0,
                hovertemplate='<b>%{x}</b><br>%{y:,} rides<extra></extra>')
            fig5.update_layout(**mk(height=280), showlegend=False)
            st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})

# ════════════ TAB 3 ══════════════════════════════════════════
with t3:
    st.markdown('<div class="section-label">VEHICLE PERFORMANCE</div>', unsafe_allow_html=True)

    if completed:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="chart-title">Rides by Vehicle</div>', unsafe_allow_html=True)
            vt = fd_c['Vehicle Type'].value_counts().reset_index()
            fig = px.bar(vt, x='Vehicle Type', y='count',
                color='Vehicle Type', color_discrete_sequence=C)
            fig.update_traces(marker_line_width=0)
            fig.update_layout(**mk(height=280), showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        with col2:
            st.markdown('<div class="chart-title">Avg Fare by Vehicle</div>', unsafe_allow_html=True)
            vf = fd_c.groupby('Vehicle Type')['Booking Value'].mean().reset_index()
            fig2 = px.bar(vf, x='Vehicle Type', y='Booking Value',
                color='Vehicle Type', color_discrete_sequence=C)
            fig2.update_traces(marker_line_width=0)
            fig2.update_layout(**mk(height=280), showlegend=False, yaxis_tickprefix='₹')
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        with col3:
            st.markdown('<div class="chart-title">Revenue Share</div>', unsafe_allow_html=True)
            vrev = fd_c.groupby('Vehicle Type')['Booking Value'].sum().reset_index()
            fig3 = px.pie(vrev, values='Booking Value', names='Vehicle Type',
                color_discrete_sequence=C, hole=0.55)
            fig3.update_traces(textfont_size=10, textinfo='percent',
                marker=dict(line=dict(color='#0b0c14', width=2)))
            fig3.update_layout(**mk(height=280))
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

        st.markdown('<div class="chart-title">Distance vs Fare by Vehicle Type</div>', unsafe_allow_html=True)
        sample = fd_c[['Ride Distance','Booking Value','Vehicle Type']].dropna().sample(
            min(3000, completed), random_state=42)
        fig4 = px.scatter(sample, x='Ride Distance', y='Booking Value',
            color='Vehicle Type', color_discrete_sequence=C, opacity=0.5,
            labels={'Ride Distance':'Distance (km)', 'Booking Value':'Fare (₹)'})
        fig4.update_traces(marker_size=4, marker_line_width=0)
        fig4.update_layout(**mk(height=360))
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

        st.markdown('<div class="section-label">TOP ROUTES</div>', unsafe_allow_html=True)
        routes = fd_c.groupby(['Pickup Location','Drop Location']).agg(
            Trips=('Booking Value','count'),
            Avg_Fare=('Booking Value','mean'),
            Avg_Dist=('Ride Distance','mean')
        ).reset_index().sort_values('Trips', ascending=False).head(15).round(2)
        routes['Route'] = routes['Pickup Location'] + ' → ' + routes['Drop Location']
        st.dataframe(routes[['Route','Trips','Avg_Fare','Avg_Dist']],
            use_container_width=True, hide_index=True, height=420)

        # ── NEW VIZ: Distance Bucket Analysis ────────────────
        st.markdown('<div class="section-label">RIDE DISTANCE BUCKETS</div>', unsafe_allow_html=True)
        dist_bins = [0, 5, 10, 20, 30, 50, 1000]
        dist_labels = ['0-5 km','5-10 km','10-20 km','20-30 km','30-50 km','50+ km']
        fd_c_dist = fd_c.copy()
        fd_c_dist['Distance_Bucket'] = pd.cut(fd_c_dist['Ride Distance'], bins=dist_bins, labels=dist_labels)
        bucket_stats = fd_c_dist.groupby('Distance_Bucket', observed=True).agg(
            Rides=('Booking Value','count'),
            Revenue=('Booking Value','sum'),
            Avg_Fare=('Booking Value','mean')
        ).reset_index()

        db1, db2 = st.columns(2)
        with db1:
            st.markdown('<div class="chart-title">Rides by Distance Bucket</div>', unsafe_allow_html=True)
            fig_db1 = px.bar(bucket_stats, x='Distance_Bucket', y='Rides',
                color='Distance_Bucket', color_discrete_sequence=C)
            fig_db1.update_traces(marker_line_width=0,
                hovertemplate='<b>%{x}</b><br>%{y:,} rides<extra></extra>')
            _lay = mk(height=300)
            _lay['xaxis']['title'] = 'Distance Range'
            fig_db1.update_layout(**_lay, showlegend=False)
            st.plotly_chart(fig_db1, use_container_width=True, config={'displayModeBar': False})
        with db2:
            st.markdown('<div class="chart-title">Revenue Contribution by Distance</div>', unsafe_allow_html=True)
            fig_db2 = px.pie(bucket_stats, values='Revenue', names='Distance_Bucket',
                color_discrete_sequence=C, hole=0.55)
            fig_db2.update_traces(textfont_size=10, textinfo='percent',
                marker=dict(line=dict(color='#0b0c14', width=2)),
                hovertemplate='<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>')
            fig_db2.update_layout(**mk(height=300))
            st.plotly_chart(fig_db2, use_container_width=True, config={'displayModeBar': False})

        # ── NEW VIZ: Customer Repeat / LTV Segments ──────────
        st.markdown('<div class="section-label">CUSTOMER LOYALTY SEGMENTS</div>', unsafe_allow_html=True)
        cust_stats = fd_c.groupby('Customer ID').agg(
            Rides=('Booking Value','count'),
            LTV=('Booking Value','sum')
        ).reset_index()
        cust_stats['Segment'] = pd.cut(cust_stats['Rides'],
            bins=[0,1,3,7,1000], labels=['1 Ride (One-time)','2-3 Rides (Occasional)','4-7 Rides (Regular)','8+ Rides (Loyal)'])
        seg_summary = cust_stats.groupby('Segment', observed=True).agg(
            Customers=('Customer ID','count'),
            Avg_LTV=('LTV','mean'),
            Total_Revenue=('LTV','sum')
        ).reset_index()

        cs1, cs2 = st.columns(2)
        with cs1:
            st.markdown('<div class="chart-title">Customers by Loyalty Segment</div>', unsafe_allow_html=True)
            fig_cs1 = px.bar(seg_summary, x='Segment', y='Customers',
                color='Segment', color_discrete_sequence=C)
            fig_cs1.update_traces(marker_line_width=0,
                hovertemplate='<b>%{x}</b><br>%{y:,} customers<extra></extra>')
            _lay = mk(height=300)
            _lay['xaxis']['tickfont'] = dict(size=9)
            fig_cs1.update_layout(**_lay, showlegend=False)
            st.plotly_chart(fig_cs1, use_container_width=True, config={'displayModeBar': False})
        with cs2:
            st.markdown('<div class="chart-title">Avg Lifetime Value by Segment</div>', unsafe_allow_html=True)
            fig_cs2 = px.bar(seg_summary, x='Segment', y='Avg_LTV',
                color='Segment', color_discrete_sequence=C)
            fig_cs2.update_traces(marker_line_width=0,
                hovertemplate='<b>%{x}</b><br>₹%{y:,.0f} avg LTV<extra></extra>')
            _lay = mk(height=300)
            _lay['xaxis']['tickfont'] = dict(size=9)
            _lay['yaxis']['tickprefix'] = '₹'
            fig_cs2.update_layout(**_lay, showlegend=False)
            st.plotly_chart(fig_cs2, use_container_width=True, config={'displayModeBar': False})

# ════════════ TAB 4 ══════════════════════════════════════════
with t4:
    st.markdown('<div class="section-label">CANCELLATION ANALYSIS</div>', unsafe_allow_html=True)
    st.caption("This tab always shows all booking statuses for the selected vehicle type, regardless of the Status filter above.")

    # Use fd_vehicle (vehicle filter only) so this tab isn't blanked out by the Status dropdown
    cust_c = fd_vehicle[fd_vehicle['Booking Status'] == 'Cancelled by Customer']
    drv_c  = fd_vehicle[fd_vehicle['Booking Status'] == 'Cancelled by Driver']
    no_drv = fd_vehicle[fd_vehicle['Booking Status'] == 'No Driver Found']
    veh_total = len(fd_vehicle)
    veh_cancel_rate = (len(cust_c) + len(drv_c)) / veh_total * 100 if veh_total else 0

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("By Customer",     f"{len(cust_c):,}", f"{len(cust_c)/veh_total*100:.1f}%" if veh_total else "")
    col2.metric("By Driver",       f"{len(drv_c):,}",  f"{len(drv_c)/veh_total*100:.1f}%" if veh_total else "")
    col3.metric("No Driver Found", f"{len(no_drv):,}", f"{len(no_drv)/veh_total*100:.1f}%" if veh_total else "")
    col4.metric("Total Cancel Rate",f"{veh_cancel_rate:.1f}%")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-title">Customer Cancellations by Vehicle</div>', unsafe_allow_html=True)
        if len(cust_c):
            cc = cust_c['Vehicle Type'].value_counts().reset_index()
            fig = px.bar(cc, x='Vehicle Type', y='count',
                color='count', color_continuous_scale=['#2a0a0a','#EF233C'])
            fig.update_traces(marker_line_width=0)
            fig.update_layout(**mk(height=300), coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    with c2:
        st.markdown('<div class="chart-title">Driver Cancellations by Vehicle</div>', unsafe_allow_html=True)
        if len(drv_c):
            dc = drv_c['Vehicle Type'].value_counts().reset_index()
            fig2 = px.bar(dc, x='Vehicle Type', y='count',
                color='count', color_continuous_scale=['#2a1a0a','#FF6B35'])
            fig2.update_traces(marker_line_width=0)
            fig2.update_layout(**mk(height=300), coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    cancel_all = fd_vehicle[fd_vehicle['Booking Status'].str.startswith('Cancelled')]
    if len(cancel_all):
        st.markdown('<div class="chart-title">Cancellations by Hour of Day</div>', unsafe_allow_html=True)
        hc = cancel_all.groupby('Hour').size().reset_index(name='count')
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=hc['Hour'], y=hc['count'],
            fill='tozeroy', line=dict(color='#EF233C', width=2.5),
            fillcolor='rgba(239,35,60,0.10)', mode='lines+markers',
            marker=dict(size=6, color='#EF233C'),
            hovertemplate='Hour %{x}:00 — %{y} cancellations<extra></extra>'))
        lay = mk(height=280)
        lay['xaxis']['tickvals'] = list(range(0, 24, 2))
        fig3.update_layout(**lay)
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    # ── NEW VIZ: Cancellation Reasons Breakdown ──────────────
    st.markdown('<div class="section-label">WHY RIDES ARE CANCELLED</div>', unsafe_allow_html=True)
    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown('<div class="chart-title">Customer Cancellation Reasons</div>', unsafe_allow_html=True)
        cust_reasons = fd_vehicle['Reason for cancelling by Customer'].dropna().value_counts().reset_index()
        if len(cust_reasons):
            fig_cr = px.bar(cust_reasons, x='count', y='Reason for cancelling by Customer',
                orientation='h', color='count',
                color_continuous_scale=['#2a0a0a','#EF233C'])
            fig_cr.update_traces(marker_line_width=0,
                hovertemplate='<b>%{y}</b><br>%{x:,} rides<extra></extra>')
            _lay = mk(height=300)
            _lay['yaxis']['tickfont'] = dict(size=10)
            fig_cr.update_layout(**_lay, coloraxis_showscale=False)
            st.plotly_chart(fig_cr, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No customer cancellation data in current filter")
    with rc2:
        st.markdown('<div class="chart-title">Driver Cancellation Reasons</div>', unsafe_allow_html=True)
        drv_reasons = fd_vehicle['Driver Cancellation Reason'].dropna().value_counts().reset_index()
        if len(drv_reasons):
            fig_dr = px.bar(drv_reasons, x='count', y='Driver Cancellation Reason',
                orientation='h', color='count',
                color_continuous_scale=['#2a1a0a','#FF6B35'])
            fig_dr.update_traces(marker_line_width=0,
                hovertemplate='<b>%{y}</b><br>%{x:,} rides<extra></extra>')
            _lay = mk(height=300)
            _lay['yaxis']['tickfont'] = dict(size=10)
            fig_dr.update_layout(**_lay, coloraxis_showscale=False)
            st.plotly_chart(fig_dr, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No driver cancellation data in current filter")

    incomplete_reasons = fd_vehicle['Incomplete Rides Reason'].dropna().value_counts().reset_index()
    if len(incomplete_reasons):
        st.markdown('<div class="chart-title">Incomplete Ride Reasons</div>', unsafe_allow_html=True)
        fig_ir = px.bar(incomplete_reasons, x='Incomplete Rides Reason', y='count',
            color='Incomplete Rides Reason', color_discrete_sequence=C)
        fig_ir.update_traces(marker_line_width=0,
            hovertemplate='<b>%{x}</b><br>%{y:,} rides<extra></extra>')
        fig_ir.update_layout(**mk(height=260), showlegend=False)
        st.plotly_chart(fig_ir, use_container_width=True, config={'displayModeBar': False})

# ════════════ TAB 5 — RATINGS ═════════════════════════════════
with t5:
    st.markdown('<div class="section-label">RATINGS &amp; WAIT TIMES</div>', unsafe_allow_html=True)

    five_star = int((fd_c['Driver Ratings'] == 5).sum()) if completed else 0
    low_rated = int((fd_c['Driver Ratings'] < 3).sum()) if completed else 0

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Avg Driver Rating",   f"{avg_dr:.2f} ⭐")
    col2.metric("Avg Customer Rating", f"{avg_cr:.2f} ⭐")
    col3.metric("Avg VTAT",            f"{avg_vtat:.1f} min")
    col4.metric("Avg CTAT",            f"{avg_ctat:.1f} min")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-title">Driver vs Customer Rating Distribution</div>', unsafe_allow_html=True)
        if completed:
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=fd_c['Driver Ratings'].dropna(),
                nbinsx=20, name='Driver Rating', marker_color='#06C167', opacity=0.8))
            fig.add_trace(go.Histogram(x=fd_c['Customer Rating'].dropna(),
                nbinsx=20, name='Cust Rating', marker_color='#A259FF', opacity=0.7))
            fig.update_layout(**mk(height=300), barmode='overlay')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    with c2:
        st.markdown('<div class="chart-title">Avg VTAT by Vehicle Type</div>', unsafe_allow_html=True)
        vtat = fd.groupby('Vehicle Type')['Avg VTAT'].mean().sort_values().reset_index()
        fig2 = px.bar(vtat, x='Avg VTAT', y='Vehicle Type', orientation='h',
            color='Avg VTAT', color_continuous_scale=['#0d1a3a','#1FBAD6'])
        fig2.update_traces(marker_line_width=0)
        fig2.update_layout(**mk(height=300), coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    if completed:
        st.markdown('<div class="chart-title">Monthly Avg Wait Times (VTAT &amp; CTAT)</div>', unsafe_allow_html=True)
        mw = fd.groupby(['Month','Month_Num'])[['Avg VTAT','Avg CTAT']].mean().reset_index().sort_values('Month_Num')
        mw['Mon'] = mw['Month'].str[:3]
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=mw['Mon'], y=mw['Avg VTAT'],
            mode='lines+markers', name='VTAT',
            line=dict(color='#1FBAD6', width=2.5),
            marker=dict(size=8, color='#1FBAD6', line=dict(color='#0b0c14', width=2))))
        fig3.add_trace(go.Scatter(x=mw['Mon'], y=mw['Avg CTAT'],
            mode='lines+markers', name='CTAT',
            line=dict(color='#FF6B35', width=2.5),
            marker=dict(size=8, color='#FF6B35', line=dict(color='#0b0c14', width=2))))
        lay = mk(height=300)
        lay['yaxis']['title'] = dict(text='Minutes', font=dict(color='#555577'))
        fig3.update_layout(**lay)
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

        st.markdown('<div class="section-label">VEHICLE SUMMARY TABLE</div>', unsafe_allow_html=True)
        summary = fd_c.groupby('Vehicle Type').agg(
            Rides=('Booking Value','count'),
            Revenue=('Booking Value','sum'),
            Avg_Fare=('Booking Value','mean'),
            Avg_Distance=('Ride Distance','mean'),
            Driver_Rating=('Driver Ratings','mean'),
            Customer_Rating=('Customer Rating','mean')
        ).reset_index().round(2)
        st.dataframe(summary, use_container_width=True, hide_index=True)

# ════════════ TAB 6 — MAP VIEW ═══════════════════════════════
with t6:
    st.markdown('<div class="section-label">PICKUP LOCATIONS MAP</div>', unsafe_allow_html=True)

    locs = load_locations()

    map_metric = st.radio("View by", ["Pickup Locations", "Drop Locations"],
        horizontal=True, key="map_metric")

    loc_col = 'Pickup Location' if map_metric == "Pickup Locations" else 'Drop Location'

    if completed:
        loc_stats = fd_c.groupby(loc_col).agg(
            Rides=('Booking Value','count'),
            Revenue=('Booking Value','sum'),
            Avg_Fare=('Booking Value','mean')
        ).reset_index()
        loc_stats['lat'] = loc_stats[loc_col].map(lambda x: locs.get(x, (None,None))[0])
        loc_stats['lon'] = loc_stats[loc_col].map(lambda x: locs.get(x, (None,None))[1])
        loc_stats = loc_stats.dropna(subset=['lat','lon'])

        col1, col2, col3 = st.columns(3)
        col1.metric("Locations Mapped", f"{len(loc_stats):,}")
        col2.metric("Top Location", loc_stats.sort_values('Rides',ascending=False).iloc[0][loc_col] if len(loc_stats) else "—")
        col3.metric("Total Mapped Rides", f"{loc_stats['Rides'].sum():,}")

        st.markdown(f'<div class="chart-title">Ride Density — {map_metric}</div>', unsafe_allow_html=True)

        fig_map = px.scatter_mapbox(
            loc_stats, lat='lat', lon='lon',
            size='Rides', color='Rides',
            color_continuous_scale=['#1a1a3a','#1FBAD6','#06C167','#FFD166'],
            size_max=35, zoom=8.5,
            hover_name=loc_col,
            hover_data={'Rides':True,'Revenue':':,.0f','Avg_Fare':':.0f','lat':False,'lon':False},
            center=dict(lat=28.58, lon=77.22),
            mapbox_style="carto-darkmatter"
        )
        fig_map.update_layout(
            height=560,
            paper_bgcolor='#0f1018',
            plot_bgcolor='#0f1018',
            margin=dict(t=10,b=10,l=10,r=10),
            font=dict(color='#888899', family='Inter'),
            coloraxis_colorbar=dict(
                title=dict(text="Rides", font=dict(color='#888899')),
                tickfont=dict(color='#888899'),
                bgcolor='rgba(0,0,0,0)'
            ),
            hoverlabel=dict(bgcolor='#1a1a2e', bordercolor='#2a2a4a',
                font=dict(color='white', size=12, family='Inter'))
        )
        st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})

        st.markdown('<div class="section-label">TOP 20 LOCATIONS BY RIDES</div>', unsafe_allow_html=True)
        top_locs = loc_stats.sort_values('Rides', ascending=False).head(20)[
            [loc_col,'Rides','Revenue','Avg_Fare']].round(2)
        st.dataframe(top_locs, use_container_width=True, hide_index=True, height=420)
    else:
        st.info("No completed rides in current filter to display on map")
