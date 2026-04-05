import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="TrustPay · Fraud Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1525 50%, #0a1020 100%); color: #e2e8f0; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f1729 0%, #111c30 100%); border-right: 1px solid rgba(99,179,237,0.15); }
    .stButton > button { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; border: none; border-radius: 10px; padding: 12px 28px; font-weight: 600; font-size: 15px; width: 100%; box-shadow: 0 4px 15px rgba(37,99,235,0.4); }
    .stButton > button:hover { background: linear-gradient(135deg, #3b82f6, #2563eb); transform: translateY(-1px); }
    .risk-card { background: rgba(15,23,42,0.85); border-radius: 16px; padding: 24px; border: 1px solid rgba(99,179,237,0.2); margin: 8px 0; }
    .badge-allow { background:#064e3b; color:#6ee7b7; border:1px solid #059669; padding:6px 16px; border-radius:30px; font-weight:700; }
    .badge-otp { background:#451a03; color:#fcd34d; border:1px solid #d97706; padding:6px 16px; border-radius:30px; font-weight:700; }
    .badge-block { background:#450a0a; color:#fca5a5; border:1px solid #dc2626; padding:6px 16px; border-radius:30px; font-weight:700; }
    .section-header { font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 2px; color: #60a5fa; text-transform: uppercase; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid rgba(96,165,250,0.2); }
    .reason-pill { display:inline-block; background:rgba(37,99,235,0.15); border:1px solid rgba(37,99,235,0.3); color:#93c5fd; border-radius:20px; padding:4px 12px; font-size:13px; margin:3px 2px; }
    .logo-text { font-family: 'IBM Plex Mono', monospace; font-size: 22px; font-weight: 700; color: #60a5fa; }
    .logo-sub { font-size: 11px; color: #64748b; letter-spacing: 2px; text-transform: uppercase; }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

for key, default in {
    "token": None,
    "username": None,
    "last_result": None,
    "page": "login"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

def api_register(username, email, password):
    resp = requests.post(f"{API_URL}/register", json={"username": username, "email": email, "password": password})
    return resp.json(), resp.status_code

def api_login(username, password):
    resp = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
    return resp.json(), resp.status_code

def api_pay(amount, merchant, category, lat, lon, location):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    resp = requests.post(f"{API_URL}/pay", json={"amount": amount, "merchant": merchant, "category": category, "latitude": lat, "longitude": lon, "location_name": location}, headers=headers)
    return resp.json(), resp.status_code

def api_transactions():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    resp = requests.get(f"{API_URL}/transactions", headers=headers)
    return resp.json() if resp.status_code == 200 else []

def render_auth_page():
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("<div style='text-align:center; padding: 40px 0 20px 0;'><div class='logo-text'>🛡️ TrustPay</div><div class='logo-sub'>Fraud Intelligence Engine</div></div>", unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_user", placeholder="your_username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In →", key="btn_login"):
                if username and password:
                    data, code = api_login(username, password)
                    if code == 200:
                        st.session_state.token = data["access_token"]
                        st.session_state.username = data["username"]
                        st.session_state.page = "dashboard"
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error(f"❌ {data.get('detail', 'Login failed')}")
                else:
                    st.warning("Please fill in all fields.")
        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            r_user  = st.text_input("Username", key="reg_user",  placeholder="choose_username")
            r_email = st.text_input("Email",    key="reg_email", placeholder="you@email.com")
            r_pass  = st.text_input("Password", key="reg_pass",  type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account →", key="btn_register"):
                if r_user and r_email and r_pass:
                    data, code = api_register(r_user, r_email, r_pass)
                    if code == 201:
                        st.success("✅ Account created! Please sign in.")
                    else:
                        st.error(f"❌ {data.get('detail', 'Registration failed')}")
                else:
                    st.warning("Please fill in all fields.")

def render_sidebar():
    with st.sidebar:
        st.markdown("<div style='padding: 16px 0;'><div class='logo-text'>🛡️ TrustPay</div><div class='logo-sub'>Fraud Intelligence</div></div><hr style='border-color: rgba(99,179,237,0.15); margin: 0 0 20px 0;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:rgba(37,99,235,0.1); border:1px solid rgba(37,99,235,0.3); border-radius:10px; padding:12px; margin-bottom:20px;'><div style='font-size:12px; color:#64748b;'>Logged in as</div><div style='font-weight:600; color:#60a5fa;'>{st.session_state.username}</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Navigation</div>", unsafe_allow_html=True)
        nav = st.radio("", ["💳 Payment Simulator", "📊 Risk Dashboard", "🗺️ Fraud Heatmap"], label_visibility="collapsed")
        st.markdown("<br><hr style='border-color:rgba(99,179,237,0.1);'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Quick Presets</div>", unsafe_allow_html=True)
        preset = st.selectbox("Load a test scenario", ["— none —", "🟢 Normal Purchase", "🟡 Suspicious Travel", "🔴 High-Risk Crypto"])
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign Out"):
            for key in ["token", "username", "last_result"]:
                st.session_state[key] = None
            st.session_state.page = "login"
            st.rerun()
    return nav, preset

def render_risk_result(result):
    score    = result["risk_score"]
    decision = result["decision"]
    alert    = result["alert_level"]
    reasons  = result["reasons"]
    if decision == "ALLOW":
        color = "#10b981"; badge_class = "badge-allow"; icon = "✅"
    elif decision == "OTP":
        color = "#f59e0b"; badge_class = "badge-otp";   icon = "⚠️"
    else:
        color = "#ef4444"; badge_class = "badge-block"; icon = "🚫"
    st.markdown(f"<div class='risk-card' style='border-color:{color}40;'><div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;'><div><div class='section-header'>Transaction Decision</div><div style='font-size:28px; font-weight:700; color:{color};'>{icon} {alert}</div></div><span class='{badge_class}'>{decision}</span></div></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:13px; color:#94a3b8; margin-bottom:6px;'>Risk Score: <b style='color:{color};'>{score:.1f} / 100</b></div>", unsafe_allow_html=True)
    st.progress(min(score / 100, 1.0))
    col1, col2, col3 = st.columns(3)
    col1.metric("Risk Score",  f"{score:.1f}")
    col2.metric("ML Signal",   f"{result['ml_score']*100:.1f}%")
    col3.metric("Rule Score",  f"{result['rule_score']:.1f}")
    st.markdown("<br><div class='section-header'>Transaction Details</div>", unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    d1.markdown(f"**Merchant:** {result['merchant']}")
    d1.markdown(f"**Amount:** ${result['amount']:,.2f}")
    d2.markdown(f"**Category:** {result['category']}")
    d2.markdown(f"**Location:** {result['location_name']}")
    if reasons:
        st.markdown("<br><div class='section-header'>Why This Decision Was Made</div>", unsafe_allow_html=True)
        pills = "".join([f"<span class='reason-pill'>⚡ {r}</span>" for r in reasons])
        st.markdown(f"<div style='padding:8px 0;'>{pills}</div>", unsafe_allow_html=True)
    msg_map = {
        "Safe":       ("✅ Transaction processed successfully.", "#065f46", "#6ee7b7"),
        "Suspicious": ("⚠️ OTP sent to your mobile. Please verify.", "#451a03", "#fcd34d"),
        "Fraud":      ("🚫 Transaction BLOCKED. High fraud risk detected.", "#450a0a", "#fca5a5"),
    }
    msg, bg, fg = msg_map.get(alert, ("Transaction processed.", "#1e293b", "#e2e8f0"))
    st.markdown(f"<div style='background:{bg}; border-left:4px solid {fg}; padding:14px 18px; border-radius:0 10px 10px 0; margin-top:20px; color:{fg};'>{msg}</div>", unsafe_allow_html=True)

PRESET_DATA = {
    "🟢 Normal Purchase":  {"amount": 45.50,   "merchant": "Whole Foods",     "category": "Grocery",     "lat": 37.77,  "lon": -122.41, "location": "San Francisco, CA"},
    "🟡 Suspicious Travel": {"amount": 890.00,  "merchant": "Dubai Duty Free", "category": "Travel",      "lat": 25.20,  "lon": 55.27,   "location": "Dubai, UAE"},
    "🔴 High-Risk Crypto":  {"amount": 4500.00, "merchant": "Binance",         "category": "Crypto",      "lat": 1.35,   "lon": 103.82,  "location": "Singapore"},
}

def render_payment_page(preset):
    st.markdown("<h2 style='font-family:\"IBM Plex Mono\",monospace; color:#60a5fa;'>💳 Payment Simulator</h2>", unsafe_allow_html=True)
    pre = PRESET_DATA.get(preset, {})
    col_form, col_result = st.columns([1, 1], gap="large")
    with col_form:
        st.markdown("<div class='section-header'>Transaction Details</div>", unsafe_allow_html=True)
        amount   = st.number_input("Amount (USD)", min_value=0.01, max_value=50000.0, value=float(pre.get("amount", 100.0)), step=10.0, format="%.2f")
        merchant = st.text_input("Merchant Name", value=pre.get("merchant", "Amazon"))
        cats     = ["Grocery","Entertainment","Electronics","Travel","Luxury","Crypto","Gaming","Dining","Healthcare","Other"]
        category = st.selectbox("Category", cats, index=cats.index(pre.get("category", "Electronics")) if pre.get("category") in cats else 2)
        st.markdown("<div class='section-header'>Location</div>", unsafe_allow_html=True)
        lc1, lc2 = st.columns(2)
        lat      = lc1.number_input("Latitude",  value=float(pre.get("lat", 37.7749)),   format="%.4f")
        lon      = lc2.number_input("Longitude", value=float(pre.get("lon", -122.4194)), format="%.4f")
        location = st.text_input("Location Name", value=pre.get("location", "San Francisco, CA"))
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Analyze & Process Payment"):
            with st.spinner("Running AI fraud analysis..."):
                data, code = api_pay(amount, merchant, category, lat, lon, location)
            if code == 200:
                st.session_state.last_result = data
                st.rerun()
            else:
                st.error(f"Error: {data.get('detail', 'Unknown error')}")
    with col_result:
        if st.session_state.last_result:
            render_risk_result(st.session_state.last_result)
        else:
            st.markdown("<div style='height:400px; display:flex; align-items:center; justify-content:center; background:rgba(15,23,42,0.5); border-radius:16px; border:1px dashed rgba(99,179,237,0.2);'><div style='text-align:center; color:#475569;'><div style='font-size:48px;'>🛡️</div><div style='font-size:16px;'>Submit a payment to see results</div></div></div>", unsafe_allow_html=True)

def render_dashboard_page():
    st.markdown("<h2 style='font-family:\"IBM Plex Mono\",monospace; color:#60a5fa;'>📊 Risk Dashboard</h2>", unsafe_allow_html=True)
    txns = api_transactions()
    if not txns:
        st.info("No transactions yet. Simulate a payment to get started.")
        return
    df = pd.DataFrame(txns)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Transactions", len(df))
    c2.metric("Avg Risk Score",     f"{df['risk_score'].mean():.1f}")
    c3.metric("Blocked",            len(df[df["decision"] == "BLOCK"]))
    c4.metric("Flagged (OTP)",      len(df[df["decision"] == "OTP"]))
    st.markdown("<br>", unsafe_allow_html=True)
    chart_col, table_col = st.columns([1.2, 1], gap="large")
    with chart_col:
        st.markdown("<div class='section-header'>Risk Score Trend</div>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(8, 3.5))
        fig.patch.set_facecolor("#0a0e1a")
        ax.set_facecolor("#0d1525")
        scores = df["risk_score"].values[::-1]
        x = range(len(scores))
        ax.fill_between(x, scores, alpha=0.15, color="#3b82f6")
        ax.plot(x, scores, color="#60a5fa", linewidth=2, marker="o", markersize=4)
        ax.axhline(y=70, color="#ef4444", linestyle="--", linewidth=1, alpha=0.7, label="Block (70)")
        ax.axhline(y=40, color="#f59e0b", linestyle="--", linewidth=1, alpha=0.7, label="OTP (40)")
        ax.set_ylim(0, 105)
        ax.tick_params(colors="#64748b")
        for spine in ax.spines.values(): spine.set_color("#1e293b")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(framealpha=0.2, facecolor="#0d1525", edgecolor="#1e293b", labelcolor="#94a3b8", fontsize=9)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
    with table_col:
        st.markdown("<div class='section-header'>Recent Transactions</div>", unsafe_allow_html=True)
        for _, row in df.head(15).iterrows():
            if row["decision"] == "ALLOW": border = "#10b981"; icon = "✅"
            elif row["decision"] == "OTP": border = "#f59e0b"; icon = "⚠️"
            else:                          border = "#ef4444"; icon = "🚫"
            ts = pd.to_datetime(row["timestamp"]).strftime("%b %d, %H:%M")
            st.markdown(f"<div style='background:rgba(15,23,42,0.8); border-left:3px solid {border}; border-radius:0 8px 8px 0; padding:10px 14px; margin-bottom:6px;'><div style='display:flex; justify-content:space-between;'><span style='font-weight:600;'>{icon} {row['merchant']}</span><span style='color:{border};'>${row['amount']:,.0f}</span></div><div style='font-size:12px; color:#94a3b8;'>Risk: {row['risk_score']:.1f} · {row['alert_level']} · {ts}</div></div>", unsafe_allow_html=True)

def render_heatmap_page():
    st.markdown("<h2 style='font-family:\"IBM Plex Mono\",monospace; color:#60a5fa;'>🗺️ Fraud Heatmap</h2>", unsafe_allow_html=True)
    txns = api_transactions()
    geo_txns = [t for t in txns if t.get("latitude") and t.get("longitude")]
    if not geo_txns:
        st.info("No geo-tagged transactions yet.")
        return
    df = pd.DataFrame(geo_txns)
    st.map(df[["latitude", "longitude"]].rename(columns={"latitude": "lat", "longitude": "lon"}), zoom=2)
    st.markdown("<div class='section-header'>Location Risk Summary</div>", unsafe_allow_html=True)
    display_df = df[["merchant","amount","risk_score","decision","alert_level","latitude","longitude"]].copy()
    display_df.columns = ["Merchant","Amount ($)","Risk Score","Decision","Alert","Lat","Lon"]
    display_df["Amount ($)"] = display_df["Amount ($)"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def main():
    if not st.session_state.token:
        render_auth_page()
        return
    nav, preset = render_sidebar()
    if "Payment" in nav:
        render_payment_page(preset)
    elif "Dashboard" in nav:
        render_dashboard_page()
    elif "Heatmap" in nav:
        render_heatmap_page()

if __name__ == "__main__":
    main()