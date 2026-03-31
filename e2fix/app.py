"""
E2FIX — Environment Evaluation & Fixing System
Main Streamlit Application
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import time
import folium
from streamlit_folium import st_folium
import json
import os

# Local modules
import database as db
import engine
import reports
from config import CARBON_FACTORS, SCORE_BANDS

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E2FIX | Environment Evaluation & Fixing System",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — dark eco-tech aesthetic
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #080f0a !important;
    color: #d4e8d0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0c1a10 !important;
    border-right: 1px solid #1e3a24 !important;
}
section[data-testid="stSidebar"] * { color: #a8d4a0 !important; }

/* ── Headers ── */
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.02em; }

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0f2014 0%, #0c1a10 100%);
    border: 1px solid #1e3a24;
    border-radius: 12px;
    padding: 1rem 1.2rem;
}
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.8rem !important;
    color: #4ade80 !important;
}
[data-testid="stMetricLabel"] { color: #6b9e72 !important; font-size: 0.8rem !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #166534, #15803d) !important;
    color: #dcfce7 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #15803d, #16a34a) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(74, 222, 128, 0.25) !important;
}

/* ── Select / Input ── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #0f2014 !important;
    border: 1px solid #1e3a24 !important;
    color: #d4e8d0 !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: #0c1a10 !important; border-radius: 10px; gap: 4px; }
.stTabs [data-baseweb="tab"] { color: #6b9e72 !important; font-family: 'Space Grotesk', sans-serif !important; }
.stTabs [aria-selected="true"] { background: #166534 !important; color: #dcfce7 !important; border-radius: 8px; }

/* ── Cards ── */
.e2fix-card {
    background: linear-gradient(135deg, #0f2014 0%, #0c1a10 100%);
    border: 1px solid #1e3a24;
    border-radius: 16px;
    padding: 1.4rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.e2fix-card:hover { border-color: #2d6a3f; }

/* ── Score Big ── */
.score-ring {
    text-align: center;
    padding: 2rem;
    background: radial-gradient(ellipse at center, #0f2a14 0%, #080f0a 70%);
    border: 1px solid #1e3a24;
    border-radius: 20px;
}
.score-number {
    font-size: 5rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    line-height: 1;
    text-shadow: 0 0 40px currentColor;
}
.score-label { font-size: 1.1rem; margin-top: 0.4rem; font-weight: 500; }

/* ── Action card ── */
.action-card {
    background: #0f2014;
    border-left: 4px solid #166534;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
}
.action-card.urgent { border-left-color: #ef4444; }
.action-card.high   { border-left-color: #f97316; }
.action-card.medium { border-left-color: #eab308; }
.action-card.low    { border-left-color: #22c55e; }

/* ── Badge ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.badge-urgent { background: #450a0a; color: #fca5a5; }
.badge-high   { background: #431407; color: #fdba74; }
.badge-medium { background: #422006; color: #fde68a; }
.badge-low    { background: #052e16; color: #86efac; }

/* ── Demo banner ── */
.demo-banner {
    background: linear-gradient(90deg, #1a1a00, #2a2200);
    border: 1px solid #3d3500;
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    color: #fde68a;
    font-size: 0.88rem;
    margin-bottom: 1rem;
}

/* ── Certificate ── */
.cert-card {
    background: linear-gradient(135deg, #052e16, #0f2014);
    border: 2px solid #15803d;
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #080f0a; }
::-webkit-scrollbar-thumb { background: #1e3a24; border-radius: 3px; }

/* ── Divider ── */
hr { border-color: #1e3a24 !important; }

/* ── Plotly backgrounds ── */
.js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# INIT
# ──────────────────────────────────────────────────────────────────────────────
db.init_db()

# Removed static CITIES list


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def priority_class(p):
    return p.lower() if p.lower() in ("urgent", "high", "medium", "low") else "low"


def score_color(score):
    for lo, hi, _, color in SCORE_BANDS:
        if lo <= score <= hi:
            return color
    return "#94a3b8"


def gauge_fig(score, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"color": color, "size": 52, "family": "JetBrains Mono"}, "suffix": ""},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#1e3a24",
                     "tickfont": {"color": "#4a7c59"}},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "#0c1a10",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 39],  "color": "#1a0505"},
                {"range": [40, 59], "color": "#1a0d00"},
                {"range": [60, 79], "color": "#1a1a00"},
                {"range": [80, 100],"color": "#041a0a"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20, l=30, r=30),
        height=260,
        font={"color": "#d4e8d0"},
    )
    return fig


def radar_fig(sub_scores):
    cats  = ["AQI Score", "Heat", "Green Cover", "Noise\nControl", "Water", "Waste\nMgmt"]
    vals  = [
        sub_scores["aqi"],
        sub_scores["heat"],
        sub_scores["green"],
        sub_scores["noise"],
        sub_scores["water"],
        sub_scores["waste"],
    ]
    vals_closed = vals + [vals[0]]
    cats_closed = cats + [cats[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_closed,
        theta=cats_closed,
        fill="toself",
        fillcolor="rgba(22,101,52,0.25)",
        line=dict(color="#4ade80", width=2),
        name="Score",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100],
                            tickfont={"color": "#6b9e72", "size": 9},
                            gridcolor="#1e3a24", linecolor="#1e3a24"),
            angularaxis=dict(tickfont={"color": "#a8d4a0", "size": 11},
                             gridcolor="#1e3a24", linecolor="#1e3a24"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=30, l=40, r=40),
        height=300,
        showlegend=False,
    )
    return fig


def bar_pollutants(data):
    labels = []
    values = []
    colors = []
    thresholds = {"PM2.5": 60, "PM10": 100, "CO (×10)": 10, "NO₂": 40}

    for label, key, mult in [("PM2.5","pm25",1),("PM10","pm10",1),("CO (×10)","co",10),("NO₂","no2",1)]:
        v = data.get(key)
        if v is not None:
            val = v * mult
            labels.append(label)
            values.append(val)
            thresh = thresholds.get(label, 100)
            colors.append("#ef4444" if val > thresh else "#4ade80")

    if not labels:
        return None

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors,
        text=[f"{v:.1f}" for v in values],
        textposition="outside",
        textfont={"color": "#d4e8d0", "size": 12},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10),
        height=240,
        yaxis=dict(gridcolor="#1e3a24", tickfont={"color": "#6b9e72"}, showgrid=True),
        xaxis=dict(tickfont={"color": "#a8d4a0"}, showgrid=False),
        font={"color": "#d4e8d0"},
    )
    return fig


def history_line(records):
    if len(records) < 2:
        return None
    df = pd.DataFrame(records)
    df["ts"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("ts")
    fig = px.line(
        df, x="ts", y="health_score",
        markers=True,
        color_discrete_sequence=["#4ade80"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#1e3a24", tickfont={"color": "#6b9e72"}),
        yaxis=dict(gridcolor="#1e3a24", tickfont={"color": "#6b9e72"}, range=[0, 100]),
        margin=dict(t=10, b=10, l=10, r=10),
        height=220,
        font={"color": "#d4e8d0"},
    )
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION
# ──────────────────────────────────────────────────────────────────────────────
if "user_role" not in st.session_state:
    st.markdown("<div style='text-align: center; margin-top: 5rem;'><span style='font-size: 4rem;'>🌿</span><br><h2 style='color: #4ade80;'>Login to E2FIX</h2></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin, industry, govt, or public")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                print(f"DEBUG: Login Attempt -> USER: '{username}', PASS: '{password}'")
                role = db.authenticate_user(username, password)
                print(f"DEBUG: Role returned -> {role}")
                if role:
                    st.session_state["user_role"] = role
                    st.session_state["username"] = username
                    st.rerun()
                else:
                    st.error(f"Invalid credentials! (Tried username '{username}')")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 0.5rem 0 1.5rem 0;'>
      <div style='font-size:2rem;'>🌿</div>
      <div style='font-size:1.4rem; font-weight:700; color:#4ade80; letter-spacing:-0.03em;'>E2FIX</div>
      <div style='font-size:0.75rem; color:#4a7c59; margin-top:2px;'>Environment Evaluation & Fixing System</div>
    </div>
    """, unsafe_allow_html=True)

    role = st.session_state["user_role"]
    nav_options = ["🏠 Dashboard"]
    if role in ["Admin", "Industry"]:
        nav_options.append("🏭 Industry Module")
        nav_options.append("📜 Green Certificates")
    if role in ["Admin", "Government"]:
        nav_options.append("📊 History & Analytics")
    if role == "Admin":
        nav_options.append("🛡️ Admin Panel")

    page = st.selectbox(
        "Navigation",
        nav_options,
        label_visibility="collapsed",
    )

    st.markdown("---")
    if "env_lat" not in st.session_state:
        st.session_state["env_lat"] = 28.6139
        st.session_state["env_lon"] = 77.2090
        st.session_state["env_city"] = "Delhi, India"

    st.markdown("---")
    st.markdown("<div style='font-size:0.75rem; color:#4a7c59; margin-bottom:0.5rem;'>SEARCH LOCATION (or click Map)</div>", unsafe_allow_html=True)
    search_query = st.text_input("Enter city, street, or place...", key="search_query_input", label_visibility="collapsed")
    if st.button("Search", use_container_width=True):
        if search_query.strip():
            with st.spinner("Finding location..."):
                lat, lon, disp = engine.geocode(search_query)
                if lat is not None:
                    st.session_state["env_lat"] = lat
                    st.session_state["env_lon"] = lon
                    st.session_state["env_city"] = disp
                    st.session_state.pop("env_data", None)
                else:
                    st.error("Location not found!")

    city = st.session_state["env_city"]

    st.markdown("---")
    st.markdown(f"<div style='font-size:0.85rem; color:#a8d4a0;'>Logged in as: <b>{st.session_state['username']}</b> ({role})</div>", unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#4a7c59; line-height:1.6;'>
      <b style='color:#6b9e72;'>IILM University</b><br>
      B.Tech First Year — EVS Project<br>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────
if page == "🏠 Dashboard":
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:1rem; margin-bottom:0.5rem;'>
      <div style='font-size:2rem; font-weight:700; color:#dcfce7; letter-spacing:-0.04em;'>
        Environmental Dashboard
      </div>
      <div style='font-size:0.8rem; color:#4a7c59; padding: 3px 10px; background:#0f2014; border:1px solid #1e3a24; border-radius:99px;'>
        {city}
      </div>
    </div>
    """, unsafe_allow_html=True)

    demo_mode = engine._is_demo_mode()
    if demo_mode:
        st.markdown("""
        <div class='demo-banner'>
          ⚠️ <b>Demo Mode Active</b> — Running with simulated data.
          Add your real API keys in <code>config.py</code> to get live data.
        </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 Fetch Latest Data", use_container_width=False):
        with st.spinner(f"Fetching live environmental data for {city}..."):
            try:
                data = engine.get_all_env_data(st.session_state["env_lat"], st.session_state["env_lon"], city)
                db.save_snapshot(city, data)
                st.session_state["env_data"] = data
                st.session_state["env_city"] = city
                st.success("Data refreshed successfully!")
                time.sleep(0.5)
                st.rerun()
            except Exception as e:
                st.error(f"Error fetching data: {e}")

    # Auto-load if not in session or city changed
    if "env_data" not in st.session_state or st.session_state.get("env_city") != city:
        with st.spinner("Loading data..."):
            try:
                data = engine.get_all_env_data(st.session_state["env_lat"], st.session_state["env_lon"], city)
                db.save_snapshot(city, data)
                st.session_state["env_data"] = data
                st.session_state["env_city"] = city
            except Exception as e:
                st.error(f"Could not load data: {e}")
                st.stop()

    data = st.session_state["env_data"]
    score = data["health_score"]
    color = score_color(score)

    st.markdown("<div style='font-size:0.85rem; color:#6b9e72; font-weight:600; margin-bottom:0.6rem;'>INTERACTIVE MAP — DISCOVER LOCATIONS</div>", unsafe_allow_html=True)
    coords = (st.session_state["env_lat"], st.session_state["env_lon"])
    
    m = folium.Map(location=coords, zoom_start=11, tiles="CartoDB dark_matter")
    # Draw a colored dot using folium.CircleMarker representing health score
    folium.CircleMarker(
        location=coords,
        radius=14,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
        tooltip=f"{city} <br> AQI: {data['aqi']:.0f} | Score: {score}"
    ).add_to(m)

    map_data = st_folium(m, height=400, use_container_width=True)
    if map_data and map_data.get("last_clicked"):
        click_lat = map_data["last_clicked"]["lat"]
        click_lon = map_data["last_clicked"]["lng"]
        if "last_clicked_coords" not in st.session_state or st.session_state["last_clicked_coords"] != (click_lat, click_lon):
            st.session_state["last_clicked_coords"] = (click_lat, click_lon)
            with st.spinner("Selecting map location..."):
                disp = engine.reverse_geocode(click_lat, click_lon)
                st.session_state["env_lat"] = click_lat
                st.session_state["env_lon"] = click_lon
                st.session_state["env_city"] = disp
                st.session_state.pop("env_data", None)
                st.rerun()

    if data["aqi"] > 200:
        st.markdown("""
        <div style='background: #450a0a; border-left: 5px solid #ef4444; padding: 15px; margin-bottom: 20px; border-radius: 5px;'>
        <strong style='color: #ef4444;'>⚠ Environmental Alert</strong><br/>
        <span style='color: #fca5a5;'>Air quality is hazardous today. Avoid outdoor activities.</span>
        </div>
        """, unsafe_allow_html=True)

    # ── TOP ROW: Gauge + Radar ──
    col_g, col_r, col_f = st.columns([1, 1, 1])
    with col_g:
        st.plotly_chart(gauge_fig(score, color), use_container_width=True, config={"displayModeBar": False})
        st.markdown(f"""
        <div style='text-align:center; margin-top:-1rem;'>
          <span style='font-size:1.4rem; font-weight:700; color:{color};'>{data["score_label"]}</span><br>
          <span style='font-size:0.78rem; color:#4a7c59;'>Environmental Health Score • {city}</span>
        </div>
        """, unsafe_allow_html=True)

    with col_r:
        st.plotly_chart(radar_fig(data["sub_scores"]), use_container_width=True, config={"displayModeBar": False})

    with col_f:
        history = db.get_history(city=city, limit=15)
        forecast = engine.predict_next_aqi(history)
        fc_val = f"{forecast:.0f}" if forecast else "N/A"
        st.markdown(f"""
        <div class='e2fix-card' style='text-align:center; margin-top:2rem;'>
          <div style='font-size:2.5rem;'>🤖</div>
          <div style='font-size:0.9rem; color:#4a7c59; margin-bottom:0.5rem; text-transform:uppercase;'><b>Environmental Forecast</b></div>
          <div style='font-size:2.5rem; font-weight:700; color:#4ade80;'>{fc_val}</div>
          <div style='font-size:0.8rem; color:#a8d4a0;'>Predicted Next AQI</div>
          <div style='font-size:0.65rem; color:#4a7c59; margin-top:0.4rem;'>(Simple 7-Day Moving Average)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin:1rem 0;'></div>", unsafe_allow_html=True)

    # ── METRICS ──
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1: st.metric("🌫️ AQI", f"{data['aqi']:.0f}")
    with m2: st.metric("🌡️ Temp", f"{data['temperature']}°C")
    with m3: st.metric("💧 Humidity", f"{data['humidity']}%")
    with m4: st.metric("🔥 Heat Index", f"{data['heat_index']}°C")
    with m5: st.metric("💨 Wind", f"{data['wind_speed']} m/s")
    with m6: st.metric("☁️ Weather", data["description"])

    st.markdown("<div style='margin:0.5rem 0;'></div>", unsafe_allow_html=True)

    # ── DETAIL ROW ──
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div style='font-size:0.85rem; color:#6b9e72; font-weight:600; margin-bottom:0.6rem;'>POLLUTANT LEVELS</div>", unsafe_allow_html=True)
        fig_bar = bar_pollutants(data)
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Pollutant breakdown not available in demo mode.")

        st.markdown("<div style='margin:0.4rem 0;'></div>", unsafe_allow_html=True)
        e1, e2, e3, e4 = st.columns(4)
        with e1: st.metric("🌱 Green", f"{data['green_impact']:.0f}/100")
        with e2: st.metric("🔊 Noise", f"{data['noise_impact']:.0f}/100")
        with e3: st.metric("🚰 Water Stress", f"{data['water_stress']:.0f}/100")
        with e4: st.metric("🗑️ Waste Press.", f"{data['waste_pressure']:.0f}/100")

    with col_b:
        st.markdown("<div style='font-size:0.85rem; color:#6b9e72; font-weight:600; margin-bottom:0.6rem;'>ACTION PLAN</div>", unsafe_allow_html=True)
        for act in data["action_plan"]:
            pc = priority_class(act["priority"])
            st.markdown(f"""
            <div class='action-card {pc}'>
              <div style='display:flex; align-items:center; gap:0.6rem; margin-bottom:0.3rem;'>
                <span style='font-size:1.2rem;'>{act['icon']}</span>
                <span style='font-weight:600; color:#d4e8d0; font-size:0.9rem;'>{act['area']}</span>
                <span class='badge badge-{pc}'>{act['priority']}</span>
              </div>
              <div style='font-size:0.83rem; color:#a8d4a0; line-height:1.5;'>{act['action']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── HISTORY TREND ──
    if len(history) > 1:
        st.markdown("---")
        st.markdown(f"<div style='font-size:0.85rem; color:#6b9e72; font-weight:600; margin-bottom:0.6rem;'>HEALTH SCORE TREND — {city.upper()}</div>", unsafe_allow_html=True)
        fig_hist = history_line(history)
        if fig_hist:
            st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: INDUSTRY MODULE
# ──────────────────────────────────────────────────────────────────────────────
elif page == "🏭 Industry Module":
    st.markdown("<div style='font-size:2rem; font-weight:700; color:#dcfce7; margin-bottom:1rem;'>Industry Carbon Credit Module & Marketplace</div>", unsafe_allow_html=True)

    st.markdown("<div class='e2fix-card'>", unsafe_allow_html=True)
    my_industry = st.text_input("🏢 Active Company Context (Enter your Industry Name)", value=st.session_state.get("active_industry", ""), placeholder="e.g. GreenTech Industries", key="industry_ident")
    if my_industry != st.session_state.get("active_industry", ""):
        st.session_state["active_industry"] = my_industry
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if not my_industry.strip():
        st.warning("Please enter your Company Name above to access the module.")
    else:
        tab1, tab2 = st.tabs(["🏭 Waste Management (Earn Credits)", "💱 Credit Marketplace (Buy/Sell)"])
        
        with tab1:
            col_left, col_right = st.columns([1, 1.2])
            with col_left:
                st.markdown("<div class='e2fix-card'>", unsafe_allow_html=True)
                st.markdown("##### 🏭 Log Waste & Earn Credits")

                waste_type = st.selectbox("Waste Type", list(CARBON_FACTORS.keys()))
                quantity = st.number_input("Quantity Recycled / Managed (kg)", min_value=0.1, value=100.0, step=10.0)

                if st.button("⚡ Calculate & Log Carbon Credits", use_container_width=True):
                    result = engine.calc_carbon_savings(waste_type, quantity)
                    db.log_waste(
                        industry=my_industry,
                        waste_type=waste_type,
                        qty_kg=quantity,
                        carbon_saved=result["carbon_saved_kg"],
                        credits=result["carbon_credits"],
                        revenue=result["revenue_inr"],
                        bonus=result["bonus_score"],
                    )
                    st.session_state["last_carbon"] = result
                    st.success("✅ Logged successfully!")

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='margin:0.5rem 0;'></div>", unsafe_allow_html=True)

                # Carbon factor table
                st.markdown("<div class='e2fix-card'>", unsafe_allow_html=True)
                st.markdown("##### 📊 Carbon Factors Reference")
                factor_df = pd.DataFrame([
                    {"Waste Type": k, "CO₂ Factor (kg/kg)": v, "Credits per 1000kg": v/1000}
                    for k, v in CARBON_FACTORS.items()
                ])
                st.dataframe(factor_df, use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_right:
                # Show result card
                if "last_carbon" in st.session_state:
                    r = st.session_state["last_carbon"]
                    color = "#4ade80"
                    st.markdown(f"""
                    <div class='e2fix-card' style='border-color:#15803d;'>
                      <div style='font-size:0.75rem; color:#4a7c59; font-weight:600; margin-bottom:1rem;'>CALCULATION RESULT — {my_industry.upper()}</div>

                      <div style='display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem;'>
                        <div style='background:#052e16; border-radius:10px; padding:1rem; text-align:center;'>
                          <div style='font-size:0.7rem; color:#4a7c59;'>WASTE MANAGED</div>
                          <div style='font-family:JetBrains Mono,monospace; font-size:1.5rem; color:#4ade80; font-weight:700;'>{r["quantity_kg"]} kg</div>
                          <div style='font-size:0.72rem; color:#4a7c59;'>{r["waste_type"]}</div>
                        </div>
                        <div style='background:#052e16; border-radius:10px; padding:1rem; text-align:center;'>
                          <div style='font-size:0.7rem; color:#4a7c59;'>CO₂ SAVED</div>
                          <div style='font-family:JetBrains Mono,monospace; font-size:1.5rem; color:#4ade80; font-weight:700;'>{r["carbon_saved_kg"]} kg</div>
                          <div style='font-size:0.72rem; color:#4a7c59;'>carbon dioxide equivalent</div>
                        </div>
                      </div>

                      <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.8rem; margin-bottom:1rem;'>
                        <div style='background:#0f2014; border-radius:10px; padding:0.8rem; text-align:center; border:1px solid #1e3a24;'>
                          <div style='font-size:0.7rem; color:#4a7c59;'>CREDITS EARNED</div>
                          <div style='font-family:JetBrains Mono,monospace; font-size:1.2rem; color:#86efac; font-weight:700;'>{r["carbon_credits"]:.4f}</div>
                        </div>
                        <div style='background:#0f2014; border-radius:10px; padding:0.8rem; text-align:center; border:1px solid #1e3a24;'>
                          <div style='font-size:0.7rem; color:#4a7c59;'>EST. REVENUE</div>
                          <div style='font-family:JetBrains Mono,monospace; font-size:1.2rem; color:#86efac; font-weight:700;'>₹{r["revenue_inr"]:.2f}</div>
                        </div>
                        <div style='background:#0f2014; border-radius:10px; padding:0.8rem; text-align:center; border:1px solid #1e3a24;'>
                          <div style='font-size:0.7rem; color:#4a7c59;'>SCORE BONUS</div>
                          <div style='font-family:JetBrains Mono,monospace; font-size:1.2rem; color:#86efac; font-weight:700;'>+{r["bonus_score"]:.2f} pts</div>
                        </div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Industry logs table
                logs = db.get_waste_logs(limit=30)
                if logs:
                    st.markdown("##### 📋 Recent Waste Logs")
                    df = pd.DataFrame(logs)[["timestamp","industry_name","waste_type","quantity_kg","carbon_saved_kg","carbon_credits","revenue_inr","bonus_score"]]
                    df.columns = ["Timestamp","Industry","Type","Qty (kg)","CO₂ Saved (kg)","Credits","Revenue (₹)","Bonus"]
                    df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.strftime("%d %b %H:%M")
                    st.dataframe(df, use_container_width=True, hide_index=True)

        with tab2:
            st.markdown(f"#### 💳 {my_industry} Wallet")
            wallet = db.get_company_wallet(my_industry)
            
            w1, w2, w3, w4 = st.columns(4)
            with w1: st.metric("Available Credits", f"{wallet['balance_credits']:.4f}")
            with w2: st.metric("Locked in Orders", f"{wallet['locked_credits']:.4f}")
            with w3: st.metric("Wallet Balance (INR)", f"₹{wallet['balance_inr']:,.2f}")
            with w4: st.metric("Total Earned (All Time)", f"{wallet['earned']:.4f}")

            st.markdown("---")
            col_list, col_market = st.columns([1, 1.5])
            
            with col_list:
                st.markdown("<div class='e2fix-card'>", unsafe_allow_html=True)
                st.markdown("##### 📈 List Credits for Sale")
                list_amount = st.number_input("Credits to Sell", min_value=0.0001, value=0.0001, step=0.1)
                list_price = st.number_input("Price per Credit (INR)", min_value=1.0, value=1500.0, step=100.0)
                if st.button("List on Market", use_container_width=True):
                    if list_amount <= wallet['balance_credits']:
                        db.create_sell_order(my_industry, list_amount, list_price)
                        st.success("Listed successfully!")
                        st.rerun()
                    else:
                        st.error("Insufficient available credit balance.")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Show own active orders
                st.markdown("##### 🏷️ Your Active Listings")
                orders = db.get_active_orders()
                my_orders = [o for o in orders if o['seller_industry'] == my_industry]
                if my_orders:
                    for mo in my_orders:
                        st.markdown(f"**{mo['credits_amount']:.4f} cr** @ ₹{mo['price_per_credit']:,.2f}/ea")
                        if st.button("Cancel", key=f"cancel_{mo['id']}", help="Cancel this listing"):
                            db.cancel_sell_order(mo['id'], my_industry)
                            st.rerun()
                else:
                    st.info("No active listings.")
            
            with col_market:
                st.markdown("##### 🛒 Open Market")
                other_orders = [o for o in orders if o['seller_industry'] != my_industry]
                if not other_orders:
                    st.info("No active listings from other companies.")
                else:
                    for o in other_orders:
                        st.markdown(f"""
                        <div style='background:#0f2014; border:1px solid #1e3a24; border-radius:8px; padding:1rem; margin-bottom:0.5rem;'>
                          <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div>
                              <div style='font-size:0.8rem; color:#6b9e72;'>SELLER: <b>{o['seller_industry']}</b></div>
                              <div style='font-size:1.2rem; font-weight:700; color:#4ade80;'>{o['credits_amount']:.4f} Credits</div>
                            </div>
                            <div style='text-align:right;'>
                              <div style='font-size:0.8rem; color:#6b9e72;'>PRICE PER CREDIT</div>
                              <div style='font-size:1.1rem; color:#dcfce7;'>₹{o['price_per_credit']:,.2f}</div>
                              <div style='font-size:0.7rem; color:#a8d4a0;'>Total: ₹{o['credits_amount']*o['price_per_credit']:,.2f}</div>
                            </div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"Buy Order #{o['id']}", key=f"buy_{o['id']}", use_container_width=True):
                            total_cost = o['credits_amount']*o['price_per_credit']
                            if wallet["balance_inr"] >= total_cost:
                                ok, msg = db.buy_order(o['id'], my_industry)
                                if ok:
                                    st.success(msg)
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(msg)
                            else:
                                st.error("Insufficient INR balance.")
                
                txns = db.get_transactions(limit=10)
                if txns:
                    st.markdown("##### 🕰️ Global Transaction History")
                    tdf = pd.DataFrame(txns)[["timestamp", "buyer_industry", "seller_industry", "credits_amount", "total_price"]]
                    tdf.columns = ["Time", "Buyer", "Seller", "Credits", "Total (₹)"]
                    tdf["Time"] = pd.to_datetime(tdf["Time"]).dt.strftime("%d %b %H:%M")
                    st.dataframe(tdf, use_container_width=True, hide_index=True)



# ──────────────────────────────────────────────────────────────────────────────
# PAGE: GREEN CERTIFICATES
# ──────────────────────────────────────────────────────────────────────────────
elif page == "📜 Green Certificates":
    st.markdown("<div style='font-size:2rem; font-weight:700; color:#dcfce7; margin-bottom:1rem;'>Green Certification System</div>", unsafe_allow_html=True)

    col_form, col_certs = st.columns([1, 1.4])

    with col_form:
        st.markdown("<div class='e2fix-card'>", unsafe_allow_html=True)
        st.markdown("##### 🏅 Issue Green Certificate")
        st.markdown("<div style='font-size:0.8rem; color:#6b9e72; margin-bottom:1rem;'>Industries with consistent waste management and a good environmental score qualify for certification.</div>", unsafe_allow_html=True)

        cert_industry = st.text_input("Industry Name", key="cert_ind", placeholder="e.g. EcoSteel Ltd.")
        cert_score = st.slider("Current Environmental Health Score", 0, 100, 72)
        cert_credits = st.number_input("Total Carbon Credits Accumulated", min_value=0.0, value=0.5, step=0.01)

        eligible = cert_score >= 65 and cert_credits >= 0.1

        if eligible:
            st.success("✅ This industry meets the certification criteria!")
        else:
            st.warning(f"⚠️ Minimum: Score ≥ 65 (current: {cert_score}) & Credits ≥ 0.1 (current: {cert_credits:.3f})")

        if st.button("🏅 Issue Certificate", disabled=not eligible, use_container_width=True):
            if not cert_industry.strip():
                st.warning("Please enter an industry name.")
            else:
                db.issue_certificate(cert_industry, cert_score, cert_credits)
                st.session_state["show_cert"] = {
                    "industry": cert_industry,
                    "score": cert_score,
                    "credits": cert_credits,
                    "date": datetime.now().strftime("%d %B %Y"),
                }
                st.success("Certificate issued!")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with col_certs:
        if "show_cert" in st.session_state:
            c = st.session_state["show_cert"]
            st.markdown(f"""
            <div class='cert-card'>
              <div style='font-size:3rem;'>🏅</div>
              <div style='font-size:0.7rem; letter-spacing:0.2em; color:#4a7c59; margin:0.5rem 0;'>CERTIFICATE OF ENVIRONMENTAL EXCELLENCE</div>
              <div style='font-size:1.8rem; font-weight:700; color:#4ade80; margin:0.5rem 0;'>{c["industry"]}</div>
              <div style='font-size:0.85rem; color:#a8d4a0; margin-bottom:1.2rem;'>
                has demonstrated outstanding commitment to environmental responsibility
                through consistent waste management and sustainable practices.
              </div>
              <div style='display:flex; justify-content:center; gap:2rem; margin:1rem 0;'>
                <div>
                  <div style='font-size:0.7rem; color:#4a7c59;'>HEALTH SCORE</div>
                  <div style='font-size:1.5rem; font-weight:700; color:#4ade80; font-family:JetBrains Mono,monospace;'>{c["score"]}</div>
                </div>
                <div>
                  <div style='font-size:0.7rem; color:#4a7c59;'>CARBON CREDITS</div>
                  <div style='font-size:1.5rem; font-weight:700; color:#4ade80; font-family:JetBrains Mono,monospace;'>{c["credits"]:.4f}</div>
                </div>
              </div>
              <div style='border-top:1px solid #1e3a24; padding-top:0.8rem; font-size:0.75rem; color:#4a7c59;'>
                Issued on {c["date"]} • E2FIX Green Certification Authority • IILM University
              </div>
            </div>
            """, unsafe_allow_html=True)

        certs = db.get_certificates()
        if certs:
            st.markdown("##### 📋 Issued & Pending Certificates")
            for c in certs:
                status_color = "green" if c.get('status') == 'Approved' else "orange"
                with st.expander(f"{c['industry_name']} - {c['issued_at'][:10]} [{c.get('status', 'Pending')}]"):
                    st.write(f"**Score:** {c['health_score']} | **Credits:** {c['total_credits']:.4f}")
                    if c.get('status') == 'Approved':
                        pdf_path = reports.generate_certificate_pdf(c['industry_name'], c['health_score'], c['total_credits'], c['id'])
                        if os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as f:
                                st.download_button("📥 Download PDF", data=f, file_name=f"Certificate_{c['id']}.pdf", mime="application/pdf", key=f"dl_{c['id']}")
                    elif st.session_state["user_role"] == "Admin" and c.get('status', 'Pending') != 'Approved':
                        if st.button("✅ Approve", key=f"ap_{c['id']}"):
                            db.approve_certificate(c['id'])
                            st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: HISTORY & ANALYTICS
# ──────────────────────────────────────────────────────────────────────────────
elif page == "📊 History & Analytics":
    col_t, col_b = st.columns([3, 1])
    with col_t:
        st.markdown("<div style='font-size:2rem; font-weight:700; color:#dcfce7; margin-bottom:1rem;'>History & Analytics</div>", unsafe_allow_html=True)
    with col_b:
        report_data = {"Target City": city, "Generated For": "Monthly Summary", "Records": len(db.get_history(city=city, limit=100))}
        pdf_path = reports.generate_city_report_pdf(city, datetime.now().strftime("%B %Y"), report_data)
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Export Month Report (PDF)", data=f, file_name=f"{city}_Report.pdf", mime="application/pdf", use_container_width=True)

    tab1, tab2 = st.tabs(["🌍 Environmental History", "🏭 Waste & Carbon Analytics"])

    with tab1:
        all_history = db.get_history(limit=50)
        if not all_history:
            st.info("No history yet. Go to the Dashboard and fetch data for some cities.")
        else:
            df = pd.DataFrame(all_history)
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # City filter
            cities_in_db = sorted(df["city"].unique().tolist())
            sel_city = st.selectbox("Filter by city", ["All"] + cities_in_db)
            if sel_city != "All":
                df = df[df["city"] == sel_city]

            # Score trend
            st.markdown("##### Health Score Over Time")
            fig = px.line(
                df.sort_values("timestamp"),
                x="timestamp", y="health_score",
                color="city",
                markers=True,
                color_discrete_sequence=px.colors.qualitative.G10,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="#1e3a24", tickfont={"color": "#6b9e72"}),
                yaxis=dict(gridcolor="#1e3a24", tickfont={"color": "#6b9e72"}, range=[0, 100]),
                legend=dict(bgcolor="rgba(0,0,0,0)", font={"color": "#a8d4a0"}),
                height=280, margin=dict(t=10,b=10,l=10,r=10),
                font={"color": "#d4e8d0"},
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            # Summary table
            st.markdown("##### All Records")
            show_cols = ["timestamp","city","health_score","score_label","aqi","temperature","humidity"]
            disp = df[show_cols].copy()
            disp["timestamp"] = disp["timestamp"].dt.strftime("%d %b %H:%M")
            disp.columns = ["Time","City","Score","Status","AQI","Temp °C","Humidity %"]
            st.dataframe(disp.sort_values("Time", ascending=False), use_container_width=True, hide_index=True)

    with tab2:
        logs = db.get_waste_logs(limit=100)
        if not logs:
            st.info("No waste logs yet. Go to the Industry Module to log waste data.")
        else:
            df_w = pd.DataFrame(logs)

            # Totals
            t1, t2, t3, t4 = st.columns(4)
            with t1: st.metric("Total CO₂ Saved", f"{df_w['carbon_saved_kg'].sum():.2f} kg")
            with t2: st.metric("Total Credits", f"{df_w['carbon_credits'].sum():.4f}")
            with t3: st.metric("Total Revenue", f"₹{df_w['revenue_inr'].sum():.2f}")
            with t4: st.metric("Log Entries", len(df_w))

            # Waste type breakdown
            st.markdown("##### Carbon Savings by Waste Type")
            type_grp = df_w.groupby("waste_type")["carbon_saved_kg"].sum().reset_index()
            fig_pie = px.pie(
                type_grp, values="carbon_saved_kg", names="waste_type",
                color_discrete_sequence=["#4ade80","#22c55e","#16a34a","#15803d","#166534"],
                hole=0.4,
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font={"color": "#d4e8d0"},
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                height=300,
                margin=dict(t=10,b=10,l=10,r=10),
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

            # Per-industry leaderboard
            st.markdown("##### Industry Leaderboard")
            lb = df_w.groupby("industry_name").agg(
                CO2_Saved=("carbon_saved_kg","sum"),
                Credits=("carbon_credits","sum"),
                Revenue=("revenue_inr","sum"),
                Entries=("id","count"),
            ).reset_index().sort_values("CO2_Saved", ascending=False)
            lb.columns = ["Industry","CO₂ Saved (kg)","Credits","Revenue (₹)","Entries"]
            st.dataframe(lb, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────────────────────────
# PAGE: ADMIN PANEL
# ──────────────────────────────────────────────────────────────────────────────
elif page == "🛡️ Admin Panel":
    st.markdown("<div style='font-size:2rem; font-weight:700; color:#dcfce7; margin-bottom:1rem;'>System Control Panel</div>", unsafe_allow_html=True)
    
    t_settings, t_manage = st.tabs(["⚙️ Settings", "🛡️ Control"])
    
    with t_settings:
        st.markdown("##### Global Settings")
        st.markdown("Configure system parameters. Changes affect new calculations.")
        
        curr_price = float(db.get_setting("carbon_credit_price", 1500))
        new_price = st.number_input("Carbon Credit Market Price (INR)", value=curr_price, step=50.0)
        
        if st.button("Save Configurations"):
            db.update_setting("carbon_credit_price", new_price)
            st.success("✅ Configuration updated successfully!")
            
    with t_manage:
        st.markdown("##### System Status")
        st.metric("Total DB Users", db.get_conn().cursor().execute("SELECT COUNT(*) FROM users").fetchone()[0])
        st.metric("Total Logs", len(db.get_history(limit=5000)))
        
        if st.button("Clear Old Logs (Demo)"):
            st.warning("Feature disabled in frontend for demo.")
