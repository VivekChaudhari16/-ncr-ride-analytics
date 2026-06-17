import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="NCR Ride Analytics", page_icon="🚗", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f0f0f; }
[data-testid="stSidebar"] { background: #1a1a1a; border-right: 1px solid #2d2d2d; }
[data-testid="stSidebar"] * { color: #ffffff !important; }
.block-container { padding: 1.5rem 2rem; }
h1 { color: #06C167 !important; font-size: 2rem !important; margin-bottom: 0.2rem !important; }
h2 { color: #06C167 !important; font-size: 1.3rem !important; }
h3 { color: #cccccc !important; font-size: 1rem !important; }
[data-testid="metric-container"] {
    background: #1e1e1e;
    border: 1px solid #2d2d2d;
    border-radius: 12px;
    padding: 1rem 1.2rem;
}
[data-testid="metric-container"] label { color: #888888 !important; font-size: 0.78rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #06C167 !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #888 !important; }
.stTabs [data-baseweb="tab-list"] { background: #1a1a1a; border-radius: 10px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #888; border-radius: 8px; padding: 8px 20px; font-size: 0.85rem; }
.stTabs [aria-selected="true"] { background: #06C167 !important; color: #000 !important; font-weight: 600 !important; }
.stMultiSelect [data-baseweb="tag"] { background: #06C167 !important; color: #000 !important; border-radius: 6px; }
.stMultiSelect [data-baseweb="select"] > div { background: #2a2a2a !important; border: 1px solid #3d3d3d !important; color: white !important; border-radius: 8px; }
div[data-testid="stSelectbox"] > div { background: #2a2a2a !important; border: 1px solid #3d3d3d !important; color: white !important; border-radius: 8px; }
.stDataFrame { border-radius: 10px; overflow: hidden; }
hr { border-color: #2d2d2d; }
p, span, div { color: #cccccc; }
.sidebar-title { font-size: 1.1rem; font-weight: 700; color: #06C167 !important; margin-bottom: 0.5rem; }
.kpi-subtext { font-size: 0.72rem; color: #555; margin-top: -10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

COLORS = ['#06C167','#1FBAD6','#FF6B35','#A259FF','#FFD166','#EF233C','#4CC9F0']
DARK = dict(plot_bgcolor='#1a1a1a', paper_bgcolor='#0f0f0f', font_color='#cccccc',
            title_font_color='#06C167', title_font_size=14,
            xaxis=dict(gridcolor='#2d2d2d', showgrid=True, color='#888'),
            yaxis=dict(gridcolor='#2d2d2d', showgrid=True, color='#888'),
            legend=dict(bgcolor='#1a1a1a', bordercolor='#2d2d2d', borderwidth=1))

@st.cache_data
def load_data():
    df = pd.read_csv("ncr_ride_bookings.csv")
    df['Date']       = pd.to_datetime(df['Date'])
    df['Hour']       = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour
    df['Month']      = df['Date'].dt.strftime('%B')
    df['Month_Num']  = df['Date'].dt.month
    df['DayOfWeek']  = df['Date'].dt.strftime('%A')
    df['Quarter']    = 'Q' + df['Date'].dt.quarter.astype(str)
    return df

df = load_data()

MONTH_ORDER = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']
DAY_ORDER   = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-title">🚗 NCR Ride Analytics</p>', unsafe_allow_html=True)
    st.markdown("**Filters**")
    st.markdown("---")

    all_vehicles = sorted(df['Vehicle Type'].dropna().unique())
    sel_vehicles = st.multiselect("Vehicle Type", all_vehicles, default=all_vehicles, key="veh")

    all_months = [m for m in MONTH_ORDER if m in df['Month'].unique()]
    sel_months = st.multiselect("Month", all_months, default=all_months, key="mon")

    all_status = sorted(df['Booking Status'].dropna().unique())
    sel_status = st.multiselect("Booking Status", all_status, default=all_status, key="stat")

    st.markdown("---")

# ── FILTER DATA ───────────────────────────────────────────────
mask = (
    df['Vehicle Type'].isin(sel_vehicles) &
    df['Month'].isin(sel_months) &
    df['Booking Status'].isin(sel_status)
)
fd       = df[mask].copy()
fd_c     = fd[fd['Booking Status'] == 'Completed'].copy()

with st.sidebar:
    st.markdown(f"**Filtered:** `{len(fd):,}` bookings")
    st.markdown(f"**Completed:** `{len(fd_c):,}` rides")
    total_rev = fd_c['Booking Value'].sum()
    st.markdown(f"**Revenue:** `₹{total_rev/1e6:.2f}M`")

# ── TABS ─────────────────────────────────────────────────────
t1, t2, t3, t4, t5 = st.tabs(["📊 Overview","⏰ Time","🚗 Vehicles","❌ Cancellations","⭐ Ratings"])

# ════════ TAB 1 — OVERVIEW ═══════════════════════════════════
with t1:
    st.title("📊 NCR Ride Bookings Dashboard")
    st.markdown(f"Showing **{len(fd):,}** bookings · **{len(fd_c):,}** completed · Year 2024")
    st.markdown("---")

    total       = len(fd)
    comp_rate   = len(fd_c)/total*100 if total else 0
    avg_fare    = fd_c['Booking Value'].mean() if len(fd_c) else 0
    avg_dist    = fd_c['Ride Distance'].mean() if len(fd_c) else 0
    cancelled   = fd['Booking Status'].str.startswith('Cancelled').sum()
    cancel_rate = cancelled/total*100 if total else 0
    avg_rating  = fd_c['Driver Ratings'].mean() if len(fd_c) else 0

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Total Bookings",  f"{total:,}")
    c2.metric("Completed",       f"{len(fd_c):,}")
    c3.metric("Completion Rate", f"{comp_rate:.1f}%")
    c4.metric("Total Revenue",   f"₹{total_rev/1e6:.2f}M")
    c5.metric("Avg Fare",        f"₹{avg_fare:.0f}")
    c6.metric("Cancel Rate",     f"{cancel_rate:.1f}%")

    st.markdown("---")

    # Monthly Revenue
    if len(fd_c):
        monthly = fd_c.groupby(['Month','Month_Num'])['Booking Value'].sum().reset_index().sort_values('Month_Num')
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly['Month'], y=monthly['Booking Value'],
            marker_color='#06C167', opacity=0.85, name='Revenue'))
        fig.add_trace(go.Scatter(x=monthly['Month'], y=monthly['Booking Value'],
            mode='lines+markers', line=dict(color='#FFD166',width=2.5),
            marker=dict(size=8,color='#FFD166'), name='Trend'))
        fig.update_layout(**DARK, title='Monthly Revenue Trend', height=350,
            yaxis_tickprefix='₹', margin=dict(t=40,b=40,l=40,r=20))
        st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        status_c = fd['Booking Status'].value_counts().reset_index()
        fig2 = px.pie(status_c, values='count', names='Booking Status',
            color_discrete_sequence=COLORS, hole=0.5, title='Booking Status')
        fig2.update_layout(**DARK, height=300, margin=dict(t=40,b=20,l=20,r=20))
        fig2.update_traces(textfont_size=11, textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        if len(fd_c):
            vt = fd_c.groupby('Vehicle Type')['Booking Value'].sum().sort_values().reset_index()
            fig3 = px.bar(vt, x='Booking Value', y='Vehicle Type', orientation='h',
                color_discrete_sequence=['#1FBAD6'], title='Revenue by Vehicle')
            fig3.update_layout(**DARK, height=300, showlegend=False,
                xaxis_tickprefix='₹', margin=dict(t=40,b=20,l=20,r=20))
            st.plotly_chart(fig3, use_container_width=True)

    with col3:
        if len(fd_c):
            pm = fd_c['Payment Method'].value_counts().reset_index()
            fig4 = px.bar(pm, x='count', y='Payment Method', orientation='h',
                color_discrete_sequence=['#A259FF'], title='Payment Methods')
            fig4.update_layout(**DARK, height=300, showlegend=False,
                margin=dict(t=40,b=20,l=20,r=20))
            st.plotly_chart(fig4, use_container_width=True)

# ════════ TAB 2 — TIME ═══════════════════════════════════════
with t2:
    st.title("⏰ Time Analysis")
    st.markdown("---")

    hourly = fd.groupby(['Hour','Booking Status']).size().reset_index(name='count')
    fig = px.line(hourly, x='Hour', y='count', color='Booking Status',
        color_discrete_sequence=COLORS, markers=True, title='Hourly Bookings by Status')
    fig.update_layout(**DARK, height=370, margin=dict(t=40,b=40))
    fig.update_xaxes(tickvals=list(range(0,24,2)))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if len(fd_c):
            heat = fd_c.groupby(['DayOfWeek','Hour']).size().reset_index(name='rides')
            pivot = heat.pivot(index='DayOfWeek', columns='Hour', values='rides').fillna(0)
            pivot = pivot.reindex([d for d in DAY_ORDER if d in pivot.index])
            fig2 = px.imshow(pivot, color_continuous_scale='YlOrRd',
                title='Rides Heatmap — Day × Hour',
                labels=dict(x='Hour', y='', color='Rides'))
            fig2.update_layout(**DARK, height=360, margin=dict(t=40,b=40))
            st.plotly_chart(fig2, use_container_width=True)

    with col2:
        if len(fd_c):
            dow = fd_c.groupby('DayOfWeek')['Booking Value'].sum().reset_index()
            dow['ord'] = dow['DayOfWeek'].apply(lambda x: DAY_ORDER.index(x) if x in DAY_ORDER else 7)
            dow = dow.sort_values('ord')
            fig3 = px.bar(dow, x='DayOfWeek', y='Booking Value',
                color='DayOfWeek', color_discrete_sequence=COLORS, title='Revenue by Day')
            fig3.update_layout(**DARK, height=360, showlegend=False,
                yaxis_tickprefix='₹', margin=dict(t=40,b=40))
            st.plotly_chart(fig3, use_container_width=True)

    if len(fd_c):
        col1, col2 = st.columns(2)
        with col1:
            q = fd_c.groupby('Quarter')['Booking Value'].sum().reset_index()
            fig4 = px.bar(q, x='Quarter', y='Booking Value', color='Quarter',
                color_discrete_sequence=COLORS, title='Quarterly Revenue')
            fig4.update_layout(**DARK, height=300, showlegend=False,
                yaxis_tickprefix='₹', margin=dict(t=40,b=40))
            st.plotly_chart(fig4, use_container_width=True)
        with col2:
            qr = fd_c.groupby('Quarter').size().reset_index(name='Rides')
            fig5 = px.bar(qr, x='Quarter', y='Rides', color='Quarter',
                color_discrete_sequence=COLORS, title='Quarterly Ride Count')
            fig5.update_layout(**DARK, height=300, showlegend=False, margin=dict(t=40,b=40))
            st.plotly_chart(fig5, use_container_width=True)

# ════════ TAB 3 — VEHICLES ═══════════════════════════════════
with t3:
    st.title("🚗 Vehicle & Route Analysis")
    st.markdown("---")

    if len(fd_c):
        col1, col2 = st.columns(2)
        with col1:
            vt2 = fd_c['Vehicle Type'].value_counts().reset_index()
            fig = px.bar(vt2, x='Vehicle Type', y='count',
                color='Vehicle Type', color_discrete_sequence=COLORS, title='Rides by Vehicle Type')
            fig.update_layout(**DARK, height=340, showlegend=False, margin=dict(t=40,b=60))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            vt3 = fd_c.groupby('Vehicle Type')['Booking Value'].mean().reset_index()
            fig2 = px.bar(vt3, x='Vehicle Type', y='Booking Value',
                color='Vehicle Type', color_discrete_sequence=COLORS, title='Avg Fare by Vehicle')
            fig2.update_layout(**DARK, height=340, showlegend=False,
                yaxis_tickprefix='₹', margin=dict(t=40,b=60))
            st.plotly_chart(fig2, use_container_width=True)

        sample = fd_c[['Ride Distance','Booking Value','Vehicle Type']].dropna().sample(
            min(2000,len(fd_c)), random_state=42)
        fig3 = px.scatter(sample, x='Ride Distance', y='Booking Value',
            color='Vehicle Type', color_discrete_sequence=COLORS,
            opacity=0.5, title='Distance vs Fare by Vehicle Type',
            labels={'Ride Distance':'Distance (km)','Booking Value':'Fare (₹)'})
        fig3.update_layout(**DARK, height=400, margin=dict(t=40,b=40))
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("#### Top 15 Popular Routes")
        routes = fd_c.groupby(['Pickup Location','Drop Location']).agg(
            Trips=('Booking Value','count'),
            Avg_Fare=('Booking Value','mean'),
            Avg_Distance=('Ride Distance','mean')
        ).reset_index().sort_values('Trips',ascending=False).head(15).round(2)
        routes['Route'] = routes['Pickup Location'] + ' → ' + routes['Drop Location']
        st.dataframe(routes[['Route','Trips','Avg_Fare','Avg_Distance']],
            use_container_width=True, hide_index=True)

# ════════ TAB 4 — CANCELLATIONS ══════════════════════════════
with t4:
    st.title("❌ Cancellation Analysis")
    st.markdown("---")

    cust_c = fd[fd['Booking Status']=='Cancelled by Customer']
    drv_c  = fd[fd['Booking Status']=='Cancelled by Driver']
    no_drv = fd[fd['Booking Status']=='No Driver Found']
    total  = len(fd)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("By Customer",     f"{len(cust_c):,}")
    c2.metric("By Driver",       f"{len(drv_c):,}")
    c3.metric("No Driver Found", f"{len(no_drv):,}")
    c4.metric("Cancel Rate",     f"{(len(cust_c)+len(drv_c))/total*100:.1f}%" if total else "0%")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if len(cust_c):
            cc = cust_c['Vehicle Type'].value_counts().reset_index()
            fig = px.bar(cc, x='Vehicle Type', y='count',
                color_discrete_sequence=['#EF233C'], title='Customer Cancellations by Vehicle')
            fig.update_layout(**DARK, height=320, showlegend=False, margin=dict(t=40,b=60))
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if len(drv_c):
            dc = drv_c['Vehicle Type'].value_counts().reset_index()
            fig2 = px.bar(dc, x='Vehicle Type', y='count',
                color_discrete_sequence=['#FF6B35'], title='Driver Cancellations by Vehicle')
            fig2.update_layout(**DARK, height=320, showlegend=False, margin=dict(t=40,b=60))
            st.plotly_chart(fig2, use_container_width=True)

    cancel_all = fd[fd['Booking Status'].str.startswith('Cancelled')]
    if len(cancel_all):
        hc = cancel_all.groupby('Hour').size().reset_index(name='cancellations')
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=hc['Hour'], y=hc['cancellations'],
            fill='tozeroy', line=dict(color='#EF233C',width=2.5),
            fillcolor='rgba(239,35,60,0.15)'))
        fig3.update_layout(**DARK, title='Cancellations by Hour', height=320,
            xaxis=dict(tickvals=list(range(0,24,2)), gridcolor='#2d2d2d'),
            margin=dict(t=40,b=40))
        st.plotly_chart(fig3, use_container_width=True)

# ════════ TAB 5 — RATINGS ════════════════════════════════════
with t5:
    st.title("⭐ Ratings & Wait Times")
    st.markdown("---")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Avg Driver Rating",   f"{fd_c['Driver Ratings'].mean():.2f} ⭐" if len(fd_c) else "—")
    c2.metric("Avg Customer Rating", f"{fd_c['Customer Rating'].mean():.2f} ⭐" if len(fd_c) else "—")
    c3.metric("Avg VTAT",            f"{fd['Avg VTAT'].mean():.1f} min")
    c4.metric("Avg CTAT",            f"{fd_c['Avg CTAT'].mean():.1f} min" if len(fd_c) else "—")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if len(fd_c):
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=fd_c['Driver Ratings'].dropna(),
                nbinsx=20, name='Driver Rating', marker_color='#A259FF', opacity=0.8))
            fig.add_trace(go.Histogram(x=fd_c['Customer Rating'].dropna(),
                nbinsx=20, name='Customer Rating', marker_color='#FFD166', opacity=0.7))
            fig.update_layout(**DARK, title='Rating Distribution', barmode='overlay',
                height=340, margin=dict(t=40,b=40))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        vtat = fd.groupby('Vehicle Type')['Avg VTAT'].mean().sort_values().reset_index()
        fig2 = px.bar(vtat, x='Avg VTAT', y='Vehicle Type', orientation='h',
            color_discrete_sequence=['#1FBAD6'], title='Avg VTAT by Vehicle (min)')
        fig2.update_layout(**DARK, height=340, showlegend=False, margin=dict(t=40,b=40))
        st.plotly_chart(fig2, use_container_width=True)

    if len(fd_c):
        monthly_wait = fd.groupby(['Month','Month_Num'])[['Avg VTAT','Avg CTAT']].mean().reset_index()
        monthly_wait = monthly_wait.sort_values('Month_Num')
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=monthly_wait['Month'], y=monthly_wait['Avg VTAT'],
            mode='lines+markers', name='VTAT', line=dict(color='#1FBAD6',width=2.5),
            marker=dict(size=7)))
        fig3.add_trace(go.Scatter(x=monthly_wait['Month'], y=monthly_wait['Avg CTAT'],
            mode='lines+markers', name='CTAT', line=dict(color='#FF6B35',width=2.5),
            marker=dict(size=7)))
        fig3.update_layout(**DARK, title='Monthly Avg Wait Times', height=340,
            yaxis_title='Minutes', margin=dict(t=40,b=40))
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("#### Vehicle Type Summary")
        summary = fd_c.groupby('Vehicle Type').agg(
            Rides=('Booking Value','count'),
            Revenue=('Booking Value','sum'),
            Avg_Fare=('Booking Value','mean'),
            Avg_Distance=('Ride Distance','mean'),
            Avg_Driver_Rating=('Driver Ratings','mean'),
            Avg_Customer_Rating=('Customer Rating','mean')
        ).reset_index().round(2)
        st.dataframe(summary, use_container_width=True, hide_index=True)