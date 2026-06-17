# 🚗 NCR Ride Bookings Analytics Dashboard

A full interactive analytics dashboard built with **Streamlit + Plotly** on 1,50,000 real NCR ride bookings.

## 📊 Features
- **Overview** — KPIs, monthly revenue, status breakdown, payment methods
- **Time Analysis** — Hourly trends, day×hour heatmap, quarterly revenue
- **Vehicle & Routes** — Vehicle performance, distance vs fare, top routes
- **Cancellations** — By customer/driver, by vehicle, hourly patterns
- **Ratings & Wait Times** — VTAT, CTAT, driver vs customer ratings

## 🚀 Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 Deploy on Render
See deployment guide below.

## 📁 Dataset
`ncr_ride_bookings.csv` — 1,50,000 rows, 21 columns, Year 2024

## 🛠️ Tech Stack
- Python 3.11
- Streamlit 1.35
- Plotly 5.22
- Pandas 2.2
