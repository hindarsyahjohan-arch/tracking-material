import streamlit as st
import pandas as pd
import requests
import time
import io
import plotly.express as px

# 1. SETTING LAYOUT WIDE & COMPACT STYLE
st.set_page_config(
    page_title="Industrial Kiosk Mode - All in One",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to remove padding so it fits in a single screen without scrolling
st.markdown("""
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        iframe {height: 800px !important;}
    </style>
""", unsafe_allow_html=True)

# Main Google Sheet Link
URL_ASLI_SHEET = "https://docs.google.com/spreadsheets/d/1haDJKJFD_o4tOwXSE4kw4wXHjnfM9UCo3LwQXztrWLk/edit?gid=577877479#gid=577877479"

# 2. KIOSK CONTROL HEADER & AUTO-ROTATION
st.markdown("### 🏭 Production Floor - Kiosk Multi-Display Mode")

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 6])

with col_ctrl1:
    mode_tampilan = st.selectbox(
        "Select Display Mode:",
        ["🔄 Auto Rotate", "📊 1. Executive Dashboard", "🧪 2. Reactor Parameters", "🛠️ 3. Operator Checklist"]
    )

with col_ctrl2:
    waktu_rotasi = st.slider("Rotation Interval (Seconds):", min_value=5, max_value=30, value=15)

# Session state logic for auto-rotation
if "last_switch" not in st.session_state:
    st.session_state.last_switch = time.time()
if "page_index" not in st.session_state:
    st.session_state.page_index = 0

pages_list = [
    "📊 1. Executive Dashboard", 
    "🧪 2. Reactor Parameters", 
    "🛠️ 3. Operator Checklist"
]

if mode_tampilan == "🔄 Auto Rotate":
    current_time = time.time()
    if current_time - st.session_state.last_switch > waktu_rotasi:
        st.session_state.page_index = (st.session_state.page_index + 1) % len(pages_list)
        st.session_state.last_switch = current_time
        st.rerun()
    
    selected_page = pages_list[st.session_state.page_index]
    col_ctrl3.markdown(f"👉 **Currently Auto-Displaying:** `{selected_page}` (Switches every {waktu_rotasi}s)")
else:
    selected_page = mode_tampilan

st.divider()

# ==============================================================================
# PAGE 1: EXECUTIVE DASHBOARD
# ==============================================================================
if "Dashboard" in selected_page:
    st.markdown("#### 📊 Production Executive Summary (Live - Last 5 Batches)")
    
    @st.cache_data(ttl=10)
    def load_dash_data():
        try:
            base_url = URL_ASLI_SHEET.split("/edit")[0]
            url_csv = f"{base_url}/export?format=csv&t={int(time.time())}"
            res = requests.get(url_csv, timeout=5)
            return pd.read_csv(io.StringIO(res.text))
        except:
            return pd.DataFrame()

    df_dash = load_dash_data()
    if not df_dash.empty:
        df_dash.columns = [str(c).strip() for c in df_dash.columns]
        
        numeric_df = df_dash.select_dtypes(include='number')
        total_berat = numeric_df.sum().iloc[0] if not numeric_df.empty and len(numeric_df.columns) > 0 else 0.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Items", len(df_dash))
        c2.metric("Total Weight (Kg)", f"{total_berat:,.2f}")
        c3.metric("Kiosk Status", "Online 🟢")
        c4.metric("Refresh Rate", "10s")
        
        # Display the last 5 batches
        st.dataframe(df_dash.tail(5), use_container_width=True, hide_index=True)
    else:
        st.warning("Loading dashboard data...")

# ==============================================================================
# PAGE 2: REACTOR PARAMETERS
# ==============================================================================
elif "Parameters" in selected_page:
    st.markdown("#### 🧪 Reactor Parameters & Work Sheet Display")
    
    @st.cache_data(ttl=10)
    def load_param_data():
        try:
            base_url = URL_ASLI_SHEET.split("/edit")[0]
            url_csv = f"{base_url}/gviz/tq?tqx=out:csv&sheet=Parameter&t={int(time.time())}"
            res = requests.get(url_csv, timeout=5)
            df = pd.read_csv(io.StringIO(res.text))
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except:
            return pd.DataFrame()

    df_param = load_param_data()
    if not df_param.empty:
        last_row = df_param.iloc[-1]
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Production Code", str(last_row.get("Kode Produksi", "-")))
        p2.metric("Weight In (g)", str(last_row.get("Weight In Gram", "-")))
        p3.metric("Purity", str(last_row.get("Purity", "-")))
        p4.metric("Heating Temp", f"{last_row.get('Heating Temp', '-')} °C")
        
        st.info(f"**Latest Floor Remarks:** {last_row.get('Notes', 'No special notes.')}")
    else:
        st.warning("Loading reactor parameter data...")

# ==============================================================================
# PAGE 3: OPERATOR CHECKLIST FORM (COMPACT)
# ==============================================================================
elif "Checklist" in selected_page:
    st.markdown("#### 🛠️ Operator Checklist Form (Compact Mode)")
    
    pilihan_proses = st.selectbox(
        "Select Process Stage:",
        ["1. Melting (Banting)", "2. Aquaregia Process", "3. Filter & Reduction"]
    )
    
    col_f1, col_f2, col_f3 = st.columns(3)
    op_name = col_f1.text_input("Operator Name:", placeholder="Name...")
    batch_num = col_f2.text_input("Batch Number:", placeholder="Batch...")
    shift = col_f3.selectbox("Shift:", ["Shift 1", "Shift 2", "Shift 3"])
    
    st.success("Form ready for floor tablet operation in compact view.")

# Auto-refresh cycle every 5 seconds for smooth rotation
time.sleep(5)
st.rerun()