import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="NCR Ride Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .stSidebar { background-color: #161b22; }
    .stSidebar .stMarkdown { color: white; }
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
    }
    div[data-testid="metric-container"] label { color: #8b949e !important; }
    div[data-testid="metric-container"] div { color: #06C167 !important; font-size: 1.6rem !important; }
    h1, h2, h3 { color: #06C167 !important; }
    .stTabs [data-baseweb="tab"] { background-color: #161b22; color: white; }
    .stTabs [aria-selected="true"] { background-color: #06C167 !important; color: black !important; }
    .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

COLORS = ['#06C167','#1FBAD6','#FF6B35','#A259FF','#FFD166','#EF233C','#4CC9F0']
TEMPLATE = dict(
    plot_bgcolor='#161b22', paper_bgcolor='#0d1117',
    font_color='white', title_font_color='#06C167',
    xaxis=dict(gridcolor='#2a2a4a', showgrid=True),
    yaxis=dict(gridcolor='#2a2a4a', showgrid=True)
)

# ── Load Data ────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("ncr_ride_bookings.csv")
    df['Date']      = pd.to_datetime(df['Date'])
    df['Hour']      = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour
    df['Month']     = df['Date'].dt.strftime('%B')
    df['Month_Num'] = df['Date'].dt.month
    df['DayOfWeek'] = df['Date'].dt.strftime('%A')
    df['Quarter']   = 'Q' + df['Date'].dt.quarter.astype(str)
    df['Week']      = df['Date'].dt.isocalendar().week.astype(int)
    return df

df = load_data()
df_c = df[df['Booking Status'] == 'Completed'].copy()

MONTH_ORDER = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']
DAY_ORDER   = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.markdown("## 🚗 NCR Ride Analytics")
st.sidebar.markdown("---")

vehicle_opts = sorted(df['Vehicle Type'].dropna().unique())
pay_opts     = sorted(df['Payment Method'].dropna().unique())
month_opts   = [m for m in MONTH_ORDER if m in df['Month'].unique()]

sel_vehicles = st.sidebar.multiselect("🚙 Vehicle Type", vehicle_opts, default=vehicle_opts)
sel_months   = st.sidebar.multiselect("📅 Month", month_opts, default=month_opts)
sel_status   = st.sidebar.multiselect("📋 Booking Status",
    df['Booking Status'].unique().tolist(), default=df['Booking Status'].unique().tolist())

filtered_all = df[
    df['Vehicle Type'].isin(sel_vehicles) &
    df['Month'].isin(sel_months) &
    df['Booking Status'].isin(sel_status)
]
filtered_c = filtered_all[filtered_all['Booking Status'] == 'Completed']

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing:** `{len(filtered_all):,}` bookings")
st.sidebar.markdown(f"**Completed:** `{len(filtered_c):,}` rides")
st.sidebar.markdown("---")
st.sidebar.markdown("Built with ❤️ using Streamlit + Plotly")

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "⏰ Time Analysis", "🚗 Vehicle & Routes",
    "❌ Cancellations", "⭐ Ratings & Wait"
])

# ════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ════════════════════════════════════════════════════════════
with tab1:
    st.title("📊 NCR Ride Bookings — Executive Dashboard")

    total        = len(filtered_all)
    completed    = len(filtered_c)
    comp_rate    = completed / total * 100 if total else 0
    revenue      = filtered_c['Booking Value'].sum()
    avg_fare     = filtered_c['Booking Value'].mean()
    avg_dist     = filtered_c['Ride Distance'].mean()
    avg_rating   = filtered_c['Driver Ratings'].mean()
    cancelled    = filtered_all['Booking Status'].str.startswith('Cancelled').sum()
    cancel_rate  = cancelled / total * 100 if total else 0

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Total Bookings",  f"{total:,}")
    c2.metric("Completed",       f"{completed:,}")
    c3.metric("Completion Rate", f"{comp_rate:.1f}%")
    c4.metric("Total Revenue",   f"₹{revenue/1e6:.2f}M")
    c5.metric("Avg Fare",        f"₹{avg_fare:.0f}")
    c6.metric("Cancel Rate",     f"{cancel_rate:.1f}%")

    st.markdown("---")

    # Monthly Revenue
    monthly = filtered_c.groupby(['Month','Month_Num'])['Booking Value'].sum().reset_index()
    monthly = monthly.sort_values('Month_Num')
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(x=monthly['Month'], y=monthly['Booking Value'],
        marker_color=COLORS[0], name='Revenue', opacity=0.85))
    fig_monthly.add_trace(go.Scatter(x=monthly['Month'], y=monthly['Booking Value'],
        mode='lines+markers', line=dict(color='#FFD166', width=2.5),
        marker=dict(size=7), name='Trend'))
    fig_monthly.update_layout(**TEMPLATE, title='Monthly Revenue — 2024', height=360,
        yaxis_tickprefix='₹', showlegend=True)
    st.plotly_chart(fig_monthly, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        status_counts = filtered_all['Booking Status'].value_counts().reset_index()
        fig_status = px.pie(status_counts, values='count', names='Booking Status',
            color_discrete_sequence=COLORS, hole=0.42, title='Booking Status Breakdown')
        fig_status.update_layout(**TEMPLATE, height=320)
        fig_status.update_traces(textfont_size=11)
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        vt_rev = filtered_c.groupby('Vehicle Type')['Booking Value'].sum().sort_values().reset_index()
        fig_vt = px.bar(vt_rev, x='Booking Value', y='Vehicle Type', orientation='h',
            color='Vehicle Type', color_discrete_sequence=COLORS,
            title='Revenue by Vehicle Type')
        fig_vt.update_layout(**TEMPLATE, height=320, showlegend=False,
            xaxis_tickprefix='₹')
        st.plotly_chart(fig_vt, use_container_width=True)

    with col3:
        pm = filtered_c['Payment Method'].value_counts().reset_index()
        fig_pm = px.bar(pm, x='count', y='Payment Method', orientation='h',
            color='Payment Method', color_discrete_sequence=COLORS,
            title='Payment Methods')
        fig_pm.update_layout(**TEMPLATE, height=320, showlegend=False)
        st.plotly_chart(fig_pm, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — TIME ANALYSIS
# ════════════════════════════════════════════════════════════
with tab2:
    st.title("⏰ Time-Based Analysis")

    # Hourly trend by status
    hourly = filtered_all.groupby(['Hour','Booking Status']).size().reset_index(name='count')
    fig_hourly = px.line(hourly, x='Hour', y='count', color='Booking Status',
        color_discrete_sequence=COLORS, markers=True,
        title='Hourly Bookings by Status', labels={'count':'Rides'})
    fig_hourly.update_layout(**TEMPLATE, height=370)
    fig_hourly.update_xaxes(tickvals=list(range(0,24,2)))
    st.plotly_chart(fig_hourly, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Heatmap
        heat = filtered_c.groupby(['DayOfWeek','Hour']).size().reset_index(name='rides')
        heat_pivot = heat.pivot(index='DayOfWeek', columns='Hour', values='rides').fillna(0)
        heat_pivot = heat_pivot.reindex([d for d in DAY_ORDER if d in heat_pivot.index])
        fig_heat = px.imshow(heat_pivot, color_continuous_scale='YlOrRd',
            title='Rides Heatmap — Day × Hour',
            labels=dict(x='Hour', y='', color='Rides'))
        fig_heat.update_layout(**TEMPLATE, height=360)
        st.plotly_chart(fig_heat, use_container_width=True)

    with col2:
        # Day of week revenue
        dow = filtered_c.groupby('DayOfWeek')['Booking Value'].sum().reset_index()
        dow['order'] = dow['DayOfWeek'].apply(lambda x: DAY_ORDER.index(x) if x in DAY_ORDER else 7)
        dow = dow.sort_values('order')
        fig_dow = px.bar(dow, x='DayOfWeek', y='Booking Value',
            color='DayOfWeek', color_discrete_sequence=COLORS,
            title='Revenue by Day of Week')
        fig_dow.update_layout(**TEMPLATE, height=360, showlegend=False,
            yaxis_tickprefix='₹')
        st.plotly_chart(fig_dow, use_container_width=True)

    # Quarterly
    q_data = filtered_c.groupby('Quarter').agg(
        Revenue=('Booking Value','sum'),
        Rides=('Booking Value','count'),
        Avg_Fare=('Booking Value','mean')
    ).reset_index()
    col1, col2 = st.columns(2)
    with col1:
        fig_q = px.bar(q_data, x='Quarter', y='Revenue', color='Quarter',
            color_discrete_sequence=COLORS, title='Quarterly Revenue')
        fig_q.update_layout(**TEMPLATE, height=320, showlegend=False, yaxis_tickprefix='₹')
        st.plotly_chart(fig_q, use_container_width=True)
    with col2:
        fig_qr = px.bar(q_data, x='Quarter', y='Rides', color='Quarter',
            color_discrete_sequence=COLORS, title='Quarterly Ride Count')
        fig_qr.update_layout(**TEMPLATE, height=320, showlegend=False)
        st.plotly_chart(fig_qr, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 3 — VEHICLE & ROUTES
# ════════════════════════════════════════════════════════════
with tab3:
    st.title("🚗 Vehicle Type & Route Analysis")

    vt_stats = filtered_c.groupby('Vehicle Type').agg(
        Rides=('Booking Value','count'),
        Revenue=('Booking Value','sum'),
        Avg_Fare=('Booking Value','mean'),
        Avg_Distance=('Ride Distance','mean'),
        Avg_Rating=('Driver Ratings','mean')
    ).reset_index().sort_values('Revenue', ascending=False)
    vt_stats = vt_stats.round(2)

    col1, col2 = st.columns(2)
    with col1:
        fig_vt2 = px.bar(vt_stats, x='Vehicle Type', y='Rides',
            color='Vehicle Type', color_discrete_sequence=COLORS,
            title='Total Rides by Vehicle Type')
        fig_vt2.update_layout(**TEMPLATE, height=340, showlegend=False)
        st.plotly_chart(fig_vt2, use_container_width=True)
    with col2:
        fig_vt3 = px.bar(vt_stats, x='Vehicle Type', y='Avg_Fare',
            color='Vehicle Type', color_discrete_sequence=COLORS,
            title='Avg Fare by Vehicle Type')
        fig_vt3.update_layout(**TEMPLATE, height=340, showlegend=False,
            yaxis_tickprefix='₹')
        st.plotly_chart(fig_vt3, use_container_width=True)

    # Scatter: Distance vs Fare
    sample = filtered_c[['Ride Distance','Booking Value','Vehicle Type']].dropna().sample(
        min(3000, len(filtered_c)), random_state=42)
    fig_scatter = px.scatter(sample, x='Ride Distance', y='Booking Value',
        color='Vehicle Type', color_discrete_sequence=COLORS,
        opacity=0.45, trendline='ols',
        title='Distance vs Fare by Vehicle Type (sample 3,000 rides)',
        labels={'Ride Distance':'Distance (km)','Booking Value':'Fare (₹)'})
    fig_scatter.update_layout(**TEMPLATE, height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Top Routes
    st.subheader("🗺️ Top 15 Popular Routes")
    routes = filtered_c.groupby(['Pickup Location','Drop Location']).agg(
        Trips=('Booking Value','count'),
        Avg_Fare=('Booking Value','mean'),
        Avg_Distance=('Ride Distance','mean')
    ).reset_index().sort_values('Trips', ascending=False).head(15)
    routes['Route'] = routes['Pickup Location'] + ' → ' + routes['Drop Location']
    routes = routes[['Route','Trips','Avg_Fare','Avg_Distance']].round(2)
    st.dataframe(routes, use_container_width=True, height=420)

    st.subheader("📊 Vehicle Type Summary Table")
    st.dataframe(vt_stats, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 4 — CANCELLATIONS
# ════════════════════════════════════════════════════════════
with tab4:
    st.title("❌ Cancellation Analysis")

    cancelled_df = filtered_all[filtered_all['Booking Status'].str.startswith('Cancelled')]
    cust_cancel  = filtered_all[filtered_all['Booking Status'] == 'Cancelled by Customer']
    drv_cancel   = filtered_all[filtered_all['Booking Status'] == 'Cancelled by Driver']

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Cancellations",   f"{len(cancelled_df):,}")
    c2.metric("By Customer",           f"{len(cust_cancel):,}")
    c3.metric("By Driver",             f"{len(drv_cancel):,}")
    c4.metric("No Driver Found",       f"{(filtered_all['Booking Status']=='No Driver Found').sum():,}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        cc_vt = cust_cancel['Vehicle Type'].value_counts().reset_index()
        fig_cc = px.bar(cc_vt, x='Vehicle Type', y='count',
            color='Vehicle Type', color_discrete_sequence=['#EF233C']*10,
            title='Customer Cancellations by Vehicle')
        fig_cc.update_layout(**TEMPLATE, height=340, showlegend=False)
        st.plotly_chart(fig_cc, use_container_width=True)

    with col2:
        dc_vt = drv_cancel['Vehicle Type'].value_counts().reset_index()
        fig_dc = px.bar(dc_vt, x='Vehicle Type', y='count',
            color='Vehicle Type', color_discrete_sequence=['#FF6B35']*10,
            title='Driver Cancellations by Vehicle')
        fig_dc.update_layout(**TEMPLATE, height=340, showlegend=False)
        st.plotly_chart(fig_dc, use_container_width=True)

    # Hourly cancellation
    hourly_c = cancelled_df.groupby('Hour').size().reset_index(name='cancellations')
    fig_hc = go.Figure()
    fig_hc.add_trace(go.Scatter(x=hourly_c['Hour'], y=hourly_c['cancellations'],
        fill='tozeroy', line=dict(color='#EF233C', width=2.5),
        fillcolor='rgba(239,35,60,0.2)', name='Cancellations'))
    fig_hc.update_layout(**TEMPLATE, title='Cancellations by Hour of Day', height=340)
    fig_hc.update_xaxes(tickvals=list(range(0,24,2)))
    st.plotly_chart(fig_hc, use_container_width=True)

    # Cancellation rate by vehicle
    cancel_rate_vt = filtered_all.groupby('Vehicle Type').apply(
        lambda x: pd.Series({
            'Total': len(x),
            'Cancelled': x['Booking Status'].str.startswith('Cancelled').sum(),
            'Cancel_Rate': x['Booking Status'].str.startswith('Cancelled').mean()*100
        })
    ).reset_index().round(2)
    st.subheader("📋 Cancellation Rate by Vehicle Type")
    st.dataframe(cancel_rate_vt, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 5 — RATINGS & WAIT TIMES
# ════════════════════════════════════════════════════════════
with tab5:
    st.title("⭐ Ratings & Wait Time Analysis")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Avg Driver Rating",   f"{filtered_c['Driver Ratings'].mean():.2f} ⭐")
    c2.metric("Avg Customer Rating", f"{filtered_c['Customer Rating'].mean():.2f} ⭐")
    c3.metric("Avg VTAT",            f"{filtered_all['Avg VTAT'].mean():.1f} min")
    c4.metric("Avg CTAT",            f"{filtered_c['Avg CTAT'].mean():.1f} min")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        fig_rat = go.Figure()
        fig_rat.add_trace(go.Histogram(x=filtered_c['Driver Ratings'].dropna(),
            nbinsx=20, name='Driver', marker_color='#A259FF', opacity=0.75))
        fig_rat.add_trace(go.Histogram(x=filtered_c['Customer Rating'].dropna(),
            nbinsx=20, name='Customer', marker_color='#FFD166', opacity=0.75))
        fig_rat.update_layout(**TEMPLATE, title='Driver vs Customer Rating Distribution',
            barmode='overlay', height=350)
        st.plotly_chart(fig_rat, use_container_width=True)

    with col2:
        vtat_vt = filtered_all.groupby('Vehicle Type')['Avg VTAT'].mean().sort_values().reset_index()
        fig_vtat = px.bar(vtat_vt, x='Avg VTAT', y='Vehicle Type', orientation='h',
            color='Vehicle Type', color_discrete_sequence=COLORS,
            title='Avg VTAT by Vehicle Type (min)',
            labels={'Avg VTAT':'Avg Wait Time (min)'})
        fig_vtat.update_layout(**TEMPLATE, height=350, showlegend=False)
        st.plotly_chart(fig_vtat, use_container_width=True)

    # Monthly wait time trend
    monthly_wait = filtered_all.groupby(['Month','Month_Num'])[['Avg VTAT','Avg CTAT']].mean().reset_index()
    monthly_wait = monthly_wait.sort_values('Month_Num')
    fig_wait = go.Figure()
    fig_wait.add_trace(go.Scatter(x=monthly_wait['Month'], y=monthly_wait['Avg VTAT'],
        mode='lines+markers', name='VTAT (Vehicle Arrival)',
        line=dict(color='#1FBAD6', width=2.5), marker=dict(size=7)))
    fig_wait.add_trace(go.Scatter(x=monthly_wait['Month'], y=monthly_wait['Avg CTAT'],
        mode='lines+markers', name='CTAT (Cab Arrival)',
        line=dict(color='#FF6B35', width=2.5), marker=dict(size=7)))
    fig_wait.update_layout(**TEMPLATE, title='Monthly Avg Wait Times (VTAT & CTAT)',
        height=350, yaxis_title='Minutes')
    st.plotly_chart(fig_wait, use_container_width=True)

    # Rating by vehicle
    rat_vt = filtered_c.groupby('Vehicle Type').agg(
        Avg_Driver_Rating=('Driver Ratings','mean'),
        Avg_Customer_Rating=('Customer Rating','mean'),
        Rides=('Booking Value','count')
    ).reset_index().round(2)
    st.subheader("📊 Rating Summary by Vehicle Type")
    st.dataframe(rat_vt, use_container_width=True)
