import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="NCR Ride Analytics", page_icon="🚗", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: #0a0a0f; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #111122 100%);
    border-right: 1px solid #1e1e3a;
}
[data-testid="stSidebar"] * { color: #e0e0ff !important; }
.block-container { padding: 1rem 2rem 2rem 2rem; }

/* KPI Cards */
.kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin: 1.2rem 0; }
.kpi-card {
    background: #0d0d1a;
    border: 1px solid #1e1e3a;
    border-radius: 14px;
    padding: 1rem 1.1rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 14px 14px 0 0;
}
.kpi-card.green::before  { background: #06C167; }
.kpi-card.blue::before   { background: #1FBAD6; }
.kpi-card.purple::before { background: #A259FF; }
.kpi-card.orange::before { background: #FF6B35; }
.kpi-card.yellow::before { background: #FFD166; }
.kpi-card.red::before    { background: #EF233C; }
.kpi-label { font-size: 0.72rem; color: #6666aa; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
.kpi-value { font-size: 1.55rem; font-weight: 700; color: #ffffff; line-height: 1.1; }
.kpi-value.green  { color: #06C167; }
.kpi-value.blue   { color: #1FBAD6; }
.kpi-value.purple { color: #A259FF; }
.kpi-value.orange { color: #FF6B35; }
.kpi-value.yellow { color: #FFD166; }
.kpi-value.red    { color: #EF233C; }
.kpi-sub { font-size: 0.7rem; color: #444466; margin-top: 4px; }

/* Page Title */
.page-title {
    font-size: 1.7rem; font-weight: 700; color: #ffffff;
    display: flex; align-items: center; gap: 10px; margin-bottom: 2px;
}
.page-subtitle { font-size: 0.85rem; color: #555577; margin-bottom: 0.5rem; }

/* Section Headers */
.section-header {
    font-size: 0.8rem; font-weight: 600; color: #4444aa;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin: 1.5rem 0 0.8rem 0; padding-bottom: 6px;
    border-bottom: 1px solid #1e1e3a;
}

/* Sidebar Labels */
.sidebar-brand {
    font-size: 1.1rem; font-weight: 700; color: #06C167 !important;
    margin-bottom: 4px; display: block;
}
.sidebar-sub { font-size: 0.75rem; color: #444466 !important; margin-bottom: 1rem; }
.filter-label { font-size: 0.72rem; color: #6666aa !important; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
.stat-pill {
    display: inline-block; background: #1a1a2e; border: 1px solid #2a2a4a;
    border-radius: 20px; padding: 4px 12px; font-size: 0.75rem; color: #8888cc;
    margin: 3px 0;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0d0d1a; border-radius: 12px; padding: 5px 6px;
    gap: 4px; border: 1px solid #1e1e3a;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; color: #555577; border-radius: 8px;
    padding: 8px 18px; font-size: 0.82rem; font-weight: 500;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #06C167 !important; color: #000000 !important;
    font-weight: 700 !important; box-shadow: 0 2px 12px rgba(6,193,103,0.3);
}

/* Multiselect */
.stMultiSelect [data-baseweb="tag"] {
    background: #1a1a3a !important; color: #8888ff !important;
    border: 1px solid #3333aa !important; border-radius: 6px !important;
}
.stMultiSelect [data-baseweb="select"] > div {
    background: #0d0d1a !important; border: 1px solid #2a2a4a !important;
    border-radius: 10px !important; color: white !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid #1e1e3a; }

/* Divider */
hr { border-color: #1e1e3a !important; margin: 1rem 0 !important; }

/* Hide default metrics */
[data-testid="metric-container"] { display: none; }
</style>
""", unsafe_allow_html=True)

COLORS  = ['#06C167','#1FBAD6','#FF6B35','#A259FF','#FFD166','#EF233C','#4CC9F0']
DARK = dict(
    plot_bgcolor='#0d0d1a', paper_bgcolor='#0a0a0f',
    font=dict(color='#8888aa', family='Inter'),
    title_font=dict(color='#ccccee', size=13, family='Inter'),
    xaxis=dict(gridcolor='#1a1a2e', showgrid=True, color='#555577',
               linecolor='#1e1e3a', tickfont=dict(size=11)),
    yaxis=dict(gridcolor='#1a1a2e', showgrid=True, color='#555577',
               linecolor='#1e1e3a', tickfont=dict(size=11)),
    legend=dict(bgcolor='#0d0d1a', bordercolor='#1e1e3a', borderwidth=1,
                font=dict(color='#8888cc')),
    margin=dict(t=45, b=40, l=45, r=20),
    hoverlabel=dict(bgcolor='#1a1a2e', bordercolor='#3333aa',
                    font=dict(color='white', size=12))
)

@st.cache_data
def load_data():
    df = pd.read_csv("ncr_ride_bookings.csv")
    df['Date']      = pd.to_datetime(df['Date'])
    df['Hour']      = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour
    df['Month']     = df['Date'].dt.strftime('%B')
    df['Month_Num'] = df['Date'].dt.month
    df['DayOfWeek'] = df['Date'].dt.strftime('%A')
    df['Quarter']   = 'Q' + df['Date'].dt.quarter.astype(str)
    return df

df = load_data()
MONTH_ORDER = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']
DAY_ORDER   = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="sidebar-brand">🚗 NCR Ride Analytics</span>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-sub">National Capital Region • 2024</span>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<p class="filter-label">Vehicle Type</p>', unsafe_allow_html=True)
    all_v = sorted(df['Vehicle Type'].dropna().unique())
    sel_v = st.multiselect("", all_v, default=all_v, key="veh", label_visibility="collapsed")
    st.markdown('<p class="filter-label">Month</p>', unsafe_allow_html=True)
    all_m = [m for m in MONTH_ORDER if m in df['Month'].unique()]
    sel_m = st.multiselect("", all_m, default=all_m, key="mon", label_visibility="collapsed")
    st.markdown('<p class="filter-label">Booking Status</p>', unsafe_allow_html=True)
    all_s = sorted(df['Booking Status'].dropna().unique())
    sel_s = st.multiselect("", all_s, default=all_s, key="stat", label_visibility="collapsed")
    st.markdown("---")

# ── FILTER ────────────────────────────────────────────────────
fd  = df[df['Vehicle Type'].isin(sel_v) & df['Month'].isin(sel_m) & df['Booking Status'].isin(sel_s)].copy()
fd_c = fd[fd['Booking Status'] == 'Completed'].copy()

total      = len(fd)
completed  = len(fd_c)
comp_rate  = completed/total*100 if total else 0
revenue    = fd_c['Booking Value'].sum()
avg_fare   = fd_c['Booking Value'].mean() if completed else 0
cancelled  = fd['Booking Status'].str.startswith('Cancelled').sum()
cancel_rate= cancelled/total*100 if total else 0
avg_rating = fd_c['Driver Ratings'].mean() if completed else 0
avg_dist   = fd_c['Ride Distance'].mean() if completed else 0

with st.sidebar:
    st.markdown(f'<div class="stat-pill">📋 {total:,} bookings</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-pill">✅ {completed:,} completed</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-pill">💰 ₹{revenue/1e6:.2f}M revenue</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-pill">⭐ {avg_rating:.2f} avg rating</div>', unsafe_allow_html=True)

# ── KPI ROW (custom HTML) ─────────────────────────────────────
def kpi(label, value, color, sub=""):
    return f"""
    <div class="kpi-card {color}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value {color}">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>"""

# ── TABS ──────────────────────────────────────────────────────
t1,t2,t3,t4,t5 = st.tabs(["📊 Overview","⏰ Time","🚗 Vehicles","❌ Cancellations","⭐ Ratings"])

# ════════ TAB 1 ═══════════════════════════════════════════════
with t1:
    st.markdown('<div class="page-title">📊 NCR Ride Bookings Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Showing <b style="color:#06C167">{total:,}</b> bookings · <b style="color:#1FBAD6">{completed:,}</b> completed · Year 2024</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid">
      {kpi("Total Bookings",  f"{total:,}",          "green",  "All statuses")}
      {kpi("Completed",       f"{completed:,}",       "blue",   f"{comp_rate:.1f}% rate")}
      {kpi("Total Revenue",   f"₹{revenue/1e6:.2f}M","purple", "Completed rides")}
      {kpi("Avg Fare",        f"₹{avg_fare:.0f}",    "orange", f"Avg {avg_dist:.1f} km")}
      {kpi("Cancel Rate",     f"{cancel_rate:.1f}%", "red",    f"{cancelled:,} rides")}
      {kpi("Avg Rating",      f"{avg_rating:.2f}⭐", "yellow", "Driver rating")}
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Monthly Revenue
    if completed:
        monthly = fd_c.groupby(['Month','Month_Num'])['Booking Value'].sum().reset_index().sort_values('Month_Num')
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly['Month'], y=monthly['Booking Value'],
            marker=dict(color='#06C167', opacity=0.7, line=dict(color='#09e87a', width=0.5)),
            name='Revenue', hovertemplate='<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>'))
        fig.add_trace(go.Scatter(x=monthly['Month'], y=monthly['Booking Value'],
            mode='lines+markers', line=dict(color='#FFD166', width=2.5),
            marker=dict(size=8, color='#FFD166', symbol='circle',
                        line=dict(color='#0a0a0f', width=2)), name='Trend',
            hovertemplate='<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>'))
        fig.update_layout(**DARK, title='Monthly Revenue — 2024', height=340,
            yaxis_tickprefix='₹', yaxis_tickformat=',.0f',
            xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        status_c = fd['Booking Status'].value_counts().reset_index()
        fig2 = px.pie(status_c, values='count', names='Booking Status',
            color_discrete_sequence=COLORS, hole=0.55, title='Booking Status')
        fig2.update_layout(**DARK, height=300)
        fig2.update_traces(textfont_size=10, textinfo='percent',
            marker=dict(line=dict(color='#0a0a0f', width=2)))
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        if completed:
            vt = fd_c.groupby('Vehicle Type')['Booking Value'].sum().sort_values().reset_index()
            fig3 = px.bar(vt, x='Booking Value', y='Vehicle Type', orientation='h',
                color='Vehicle Type', color_discrete_sequence=COLORS, title='Revenue by Vehicle')
            fig3.update_layout(**DARK, height=300, showlegend=False,
                xaxis_tickprefix='₹', xaxis_tickformat=',.0f')
            fig3.update_traces(marker_line_width=0)
            st.plotly_chart(fig3, use_container_width=True)

    with col3:
        if completed:
            pm = fd_c['Payment Method'].dropna().value_counts().reset_index()
            fig4 = px.bar(pm, x='count', y='Payment Method', orientation='h',
                color='Payment Method', color_discrete_sequence=COLORS, title='Payment Methods')
            fig4.update_layout(**DARK, height=300, showlegend=False)
            fig4.update_traces(marker_line_width=0)
            st.plotly_chart(fig4, use_container_width=True)

# ════════ TAB 2 ═══════════════════════════════════════════════
with t2:
    st.markdown('<div class="page-title">⏰ Time Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Peak hours, daily and quarterly patterns</div>', unsafe_allow_html=True)
    st.markdown("---")

    hourly = fd.groupby(['Hour','Booking Status']).size().reset_index(name='count')
    fig = px.line(hourly, x='Hour', y='count', color='Booking Status',
        color_discrete_sequence=COLORS, markers=True, title='Hourly Bookings by Status')
    fig.update_traces(line_width=2.5, marker_size=7)
    fig.update_layout(**DARK, height=360)
    fig.update_xaxes(tickvals=list(range(0,24,2)))
    st.plotly_chart(fig, use_container_width=True)

    col1,col2 = st.columns(2)
    with col1:
        if completed:
            heat = fd_c.groupby(['DayOfWeek','Hour']).size().reset_index(name='rides')
            pivot = heat.pivot(index='DayOfWeek',columns='Hour',values='rides').fillna(0)
            pivot = pivot.reindex([d for d in DAY_ORDER if d in pivot.index])
            fig2 = px.imshow(pivot, color_continuous_scale=[
                [0,'#0d0d1a'],[0.3,'#1a3a1a'],[0.6,'#0d6632'],[1,'#06C167']],
                title='Rides Heatmap — Day × Hour',
                labels=dict(x='Hour', y='', color='Rides'))
            fig2.update_layout(**DARK, height=340)
            st.plotly_chart(fig2, use_container_width=True)

    with col2:
        if completed:
            dow = fd_c.groupby('DayOfWeek')['Booking Value'].sum().reset_index()
            dow['ord'] = dow['DayOfWeek'].apply(lambda x: DAY_ORDER.index(x) if x in DAY_ORDER else 7)
            dow = dow.sort_values('ord')
            fig3 = px.bar(dow, x='DayOfWeek', y='Booking Value',
                color='Booking Value', color_continuous_scale=['#1a1a3a','#06C167'],
                title='Revenue by Day of Week')
            fig3.update_layout(**DARK, height=340, showlegend=False,
                yaxis_tickprefix='₹', coloraxis_showscale=False)
            fig3.update_traces(marker_line_width=0)
            st.plotly_chart(fig3, use_container_width=True)

    if completed:
        col1,col2 = st.columns(2)
        with col1:
            q = fd_c.groupby('Quarter')['Booking Value'].sum().reset_index()
            fig4 = px.bar(q, x='Quarter', y='Booking Value', color='Quarter',
                color_discrete_sequence=COLORS, title='Quarterly Revenue')
            fig4.update_layout(**DARK, height=300, showlegend=False, yaxis_tickprefix='₹')
            fig4.update_traces(marker_line_width=0)
            st.plotly_chart(fig4, use_container_width=True)
        with col2:
            qr = fd_c.groupby('Quarter').size().reset_index(name='Rides')
            fig5 = px.bar(qr, x='Quarter', y='Rides', color='Quarter',
                color_discrete_sequence=COLORS, title='Quarterly Ride Count')
            fig5.update_layout(**DARK, height=300, showlegend=False)
            fig5.update_traces(marker_line_width=0)
            st.plotly_chart(fig5, use_container_width=True)

# ════════ TAB 3 ═══════════════════════════════════════════════
with t3:
    st.markdown('<div class="page-title">🚗 Vehicle & Route Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Performance breakdown by vehicle type and popular routes</div>', unsafe_allow_html=True)
    st.markdown("---")

    if completed:
        col1,col2 = st.columns(2)
        with col1:
            vt2 = fd_c['Vehicle Type'].value_counts().reset_index()
            fig = px.bar(vt2, x='Vehicle Type', y='count', color='Vehicle Type',
                color_discrete_sequence=COLORS, title='Total Rides by Vehicle Type')
            fig.update_layout(**DARK, height=320, showlegend=False)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            vt3 = fd_c.groupby('Vehicle Type')['Booking Value'].mean().reset_index()
            fig2 = px.bar(vt3, x='Vehicle Type', y='Booking Value', color='Vehicle Type',
                color_discrete_sequence=COLORS, title='Avg Fare by Vehicle Type')
            fig2.update_layout(**DARK, height=320, showlegend=False, yaxis_tickprefix='₹')
            fig2.update_traces(marker_line_width=0)
            st.plotly_chart(fig2, use_container_width=True)

        sample = fd_c[['Ride Distance','Booking Value','Vehicle Type']].dropna().sample(
            min(2000,completed), random_state=42)
        fig3 = px.scatter(sample, x='Ride Distance', y='Booking Value',
            color='Vehicle Type', color_discrete_sequence=COLORS, opacity=0.55,
            title='Distance vs Fare by Vehicle Type',
            labels={'Ride Distance':'Distance (km)','Booking Value':'Fare (₹)'})
        fig3.update_traces(marker_size=5, marker_line_width=0)
        fig3.update_layout(**DARK, height=380)
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown('<div class="section-header">Top 15 Popular Routes</div>', unsafe_allow_html=True)
        routes = fd_c.groupby(['Pickup Location','Drop Location']).agg(
            Trips=('Booking Value','count'),
            Avg_Fare=('Booking Value','mean'),
            Avg_Distance=('Ride Distance','mean')
        ).reset_index().sort_values('Trips',ascending=False).head(15).round(2)
        routes['Route'] = routes['Pickup Location'] + ' → ' + routes['Drop Location']
        st.dataframe(routes[['Route','Trips','Avg_Fare','Avg_Distance']],
            use_container_width=True, hide_index=True, height=400)

# ════════ TAB 4 ═══════════════════════════════════════════════
with t4:
    st.markdown('<div class="page-title">❌ Cancellation Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Why rides are cancelled and when it happens most</div>', unsafe_allow_html=True)
    st.markdown("---")

    cust_c = fd[fd['Booking Status']=='Cancelled by Customer']
    drv_c  = fd[fd['Booking Status']=='Cancelled by Driver']
    no_drv = fd[fd['Booking Status']=='No Driver Found']

    st.markdown(f"""
    <div class="kpi-grid">
      {kpi("By Customer",      f"{len(cust_c):,}",  "red",    f"{len(cust_c)/total*100:.1f}% of all")}
      {kpi("By Driver",        f"{len(drv_c):,}",   "orange", f"{len(drv_c)/total*100:.1f}% of all")}
      {kpi("No Driver Found",  f"{len(no_drv):,}",  "yellow", f"{len(no_drv)/total*100:.1f}% of all")}
      {kpi("Total Cancelled",  f"{len(cust_c)+len(drv_c):,}", "purple", "Combined")}
      {kpi("Cancel Rate",      f"{cancel_rate:.1f}%","blue",  "Cust + Driver")}
      {kpi("Completion Rate",  f"{comp_rate:.1f}%", "green",  f"{completed:,} rides")}
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        if len(cust_c):
            cc = cust_c['Vehicle Type'].value_counts().reset_index()
            fig = px.bar(cc, x='Vehicle Type', y='count',
                color='count', color_continuous_scale=['#3a0a0a','#EF233C'],
                title='Customer Cancellations by Vehicle')
            fig.update_layout(**DARK, height=320, showlegend=False, coloraxis_showscale=False)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if len(drv_c):
            dc = drv_c['Vehicle Type'].value_counts().reset_index()
            fig2 = px.bar(dc, x='Vehicle Type', y='count',
                color='count', color_continuous_scale=['#3a1a0a','#FF6B35'],
                title='Driver Cancellations by Vehicle')
            fig2.update_layout(**DARK, height=320, showlegend=False, coloraxis_showscale=False)
            fig2.update_traces(marker_line_width=0)
            st.plotly_chart(fig2, use_container_width=True)

    cancel_all = fd[fd['Booking Status'].str.startswith('Cancelled')]
    if len(cancel_all):
        hc = cancel_all.groupby('Hour').size().reset_index(name='cancellations')
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=hc['Hour'], y=hc['cancellations'],
            fill='tozeroy', line=dict(color='#EF233C', width=2.5),
            fillcolor='rgba(239,35,60,0.12)', mode='lines+markers',
            marker=dict(size=6, color='#EF233C'),
            hovertemplate='Hour %{x}:00<br>%{y} cancellations<extra></extra>'))
        fig3.update_layout(**DARK, title='Cancellations by Hour of Day', height=300,
            xaxis=dict(tickvals=list(range(0,24,2)), gridcolor='#1a1a2e', color='#555577'))
        st.plotly_chart(fig3, use_container_width=True)

# ════════ TAB 5 ═══════════════════════════════════════════════
with t5:
    st.markdown('<div class="page-title">⭐ Ratings & Wait Times</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Driver & customer satisfaction and service speed</div>', unsafe_allow_html=True)
    st.markdown("---")

    avg_vtat = fd['Avg VTAT'].mean()
    avg_ctat = fd_c['Avg CTAT'].mean() if completed else 0
    avg_cust_rat = fd_c['Customer Rating'].mean() if completed else 0

    st.markdown(f"""
    <div class="kpi-grid">
      {kpi("Driver Rating",    f"{avg_rating:.2f}⭐",  "green",  "Avg by customers")}
      {kpi("Customer Rating",  f"{avg_cust_rat:.2f}⭐","blue",   "Avg by drivers")}
      {kpi("Avg VTAT",         f"{avg_vtat:.1f} min",  "purple", "Vehicle arrival")}
      {kpi("Avg CTAT",         f"{avg_ctat:.1f} min",  "orange", "Trip duration")}
      {kpi("5-Star Rides",     f"{(fd_c['Driver Ratings']==5).sum():,}", "yellow", "Perfect rating")}
      {kpi("Low Rated",        f"{(fd_c['Driver Ratings']<3).sum():,}", "red",    "Below 3 stars")}
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        if completed:
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=fd_c['Driver Ratings'].dropna(),
                nbinsx=20, name='Driver', marker_color='#06C167', opacity=0.8))
            fig.add_trace(go.Histogram(x=fd_c['Customer Rating'].dropna(),
                nbinsx=20, name='Customer', marker_color='#A259FF', opacity=0.7))
            fig.update_layout(**DARK, title='Rating Distribution Comparison',
                barmode='overlay', height=320)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        vtat = fd.groupby('Vehicle Type')['Avg VTAT'].mean().sort_values().reset_index()
        fig2 = px.bar(vtat, x='Avg VTAT', y='Vehicle Type', orientation='h',
            color='Avg VTAT', color_continuous_scale=['#0d1a3a','#1FBAD6'],
            title='Avg Wait Time (VTAT) by Vehicle')
        fig2.update_layout(**DARK, height=320, coloraxis_showscale=False)
        fig2.update_traces(marker_line_width=0)
        st.plotly_chart(fig2, use_container_width=True)

    if completed:
        monthly_wait = fd.groupby(['Month','Month_Num'])[['Avg VTAT','Avg CTAT']].mean().reset_index().sort_values('Month_Num')
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=monthly_wait['Month'], y=monthly_wait['Avg VTAT'],
            mode='lines+markers', name='VTAT (Vehicle Arrival)',
            line=dict(color='#1FBAD6', width=2.5),
            marker=dict(size=8, color='#1FBAD6', line=dict(color='#0a0a0f', width=2))))
        fig3.add_trace(go.Scatter(x=monthly_wait['Month'], y=monthly_wait['Avg CTAT'],
            mode='lines+markers', name='CTAT (Trip Time)',
            line=dict(color='#FF6B35', width=2.5),
            marker=dict(size=8, color='#FF6B35', line=dict(color='#0a0a0f', width=2))))
        fig3.update_layout(**DARK, title='Monthly Avg Wait Times (VTAT & CTAT)',
            height=320, yaxis_title='Minutes')
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown('<div class="section-header">Vehicle Type Full Summary</div>', unsafe_allow_html=True)
        summary = fd_c.groupby('Vehicle Type').agg(
            Rides=('Booking Value','count'),
            Revenue=('Booking Value','sum'),
            Avg_Fare=('Booking Value','mean'),
            Avg_Distance=('Ride Distance','mean'),
            Driver_Rating=('Driver Ratings','mean'),
            Customer_Rating=('Customer Rating','mean'),
            Avg_VTAT=('Avg VTAT','mean') if 'Avg VTAT' in fd_c.columns else ('Booking Value','count')
        ).reset_index().round(2)
        st.dataframe(summary, use_container_width=True, hide_index=True)