import streamlit as st
import pandas as pd
import requests
import time
import io

st.set_page_config(
    page_title="Customer Refining Portal - Secure Login",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Google Sheet Link Utama Anda
URL_ASLI_SHEET = "https://docs.google.com/spreadsheets/d/1haDJKJFD_o4tOwXSE4kw4wXHjnfM9UCo3LwQXztrWLk/edit?gid=577877479#gid=577877479"

@st.cache_data(ttl=10)
def load_customer_data():
    try:
        base_url = URL_ASLI_SHEET.split("/edit")[0]
        # Mengambil data dari tab 'Customer_Tracking'
        url_csv = f"{base_url}/gviz/tq?tqx=out:csv&sheet=Customer_Tracking&t={int(time.time())}"
        response = requests.get(url_csv, timeout=10)
        
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            df.columns = [str(col).strip() for col in df.columns]
            return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

df_cust = load_customer_data()

# Inisialisasi Session State untuk Login
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "batch_code" not in st.session_state:
    st.session_state.batch_code = ""

st.title("🌟 Customer Refining Service Portal")
st.caption("Secure tracking portal for your gold refining progress, purity, and weight balance.")
st.divider()

# ==============================================================================
# HALAMAN LOGIN (JIKA BELUM LOGIN)
# ==============================================================================
if not st.session_state.authenticated:
    st.markdown("### 🔐 Customer Authentication Required")
    st.info("Please enter your assigned **Batch Code** and **PIN / Password** to view your refining progress securely.")

    with st.form("login_form"):
        input_batch = st.text_input("Production / Batch Code:", placeholder="e.g., YT170926-8")
        input_pin = st.text_input("PIN / Security Password:", type="password", placeholder="Enter your PIN...")
        login_btn = st.form_submit_button("🔓 Access Portal", use_container_width=True)

        if login_btn:
            if df_cust.empty:
                # Mode Simulasi / Fallback jika Google Sheet belum diisi
                if input_batch == "YT170926-8" and input_pin == "1234":
                    st.session_state.authenticated = True
                    st.session_state.batch_code = input_batch
                    st.rerun()
                else:
                    st.error("❌ Invalid Batch Code or PIN. (Demo mode: use Batch: YT170926-8, PIN: 1234)")
            else:
                # Pencocokan data dengan Google Sheets tab 'Customer_Tracking'
                # Kolom di Sheet diasumsikan: 'Batch Code' dan 'PIN'
                matched = df_cust[
                    (df_cust['Batch Code'].astype(str).str.strip() == input_batch.strip()) & 
                    (df_cust['PIN'].astype(str).str.strip() == input_pin.strip())
                ]
                
                if not matched.empty:
                    st.session_state.authenticated = True
                    st.session_state.batch_code = input_batch
                    st.rerun()
                else:
                    st.error("❌ Invalid Batch Code or PIN. Please check your credentials.")

# ==============================================================================
# HALAMAN UTAMA DASHBOARD CUSTOMER (SETELAH LOGIN BERHASIL)
# ==============================================================================
else:
    active_batch = st.session_state.batch_code
    
    # Ambil data spesifik milik customer yang login
    if not df_cust.empty:
        row_data = df_cust[df_cust['Batch Code'].astype(str).str.strip() == active_batch.strip()].iloc[-1]
    else:
        # Data Mockup / Simulasi Default
        row_data = {
            "Customer Name": "PT. Sumber Mulia Logam",
            "Total Weight": 10.00,
            "Purity": 99.107,
            "DP Weight": 5.00,
            "Remaining Weight": 5.00,
            "Est Date": "2026-11-05",
            "Current Status": "Refining Process",
            "Notes": "Initial DP of 5 Kg received. The remaining 5 Kg will be settled upon final packaging and purity verification."
        }

    # Header sambutan & tombol Logout
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.markdown(f"### Welcome, **{row_data.get('Customer Name', 'Valued Customer')}**")
        st.markdown(f"Active Batch Code: `🔒 {active_batch}`")
    with col_h2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.batch_code = ""
            st.rerun()

    st.divider()

    # 1. Metric Cards (Berat, Purity, DP, Sisa, Estimasi)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Received Weight", f"{float(row_data.get('Total Weight', 0)):,.2f} Kg")
    c2.metric("Purity Level", f"{float(row_data.get('Purity', 0)):,.3f} %", "Verified 🟢")
    c3.metric("DP Process Set", f"{float(row_data.get('DP Weight', 0)):,.2f} Kg", "Completed")
    c4.metric("Remaining Balance Due", f"{float(row_data.get('Remaining Weight', 0)):,.2f} Kg", "Pending Final")
    c5.metric("Est. Completion", str(row_data.get('Est Date', '-')))

    st.markdown("---")
    st.markdown("### 📍 Live Process Stage Tracker")

    # Visual Progress Stages
    stages = [
        "1. Material Receiving", 
        "2. Purity Testing", 
        "3. Refining Process", 
        "4. Reduction & Cleaning", 
        "5. Packaging & Ready"
    ]
    
    status_str = str(row_data.get('Current Status', 'Refining Process')).lower()
    
    # Menentukan posisi tahap aktif berdasarkan status di database
    active_idx = 2 # Default di Refining
    if "receiv" in status_str: active_idx = 0
    elif "purity" in status_str or "test" in status_str: active_idx = 1
    elif "refin" in status_str: active_idx = 2
    elif "reduc" in status_str or "clean" in status_str: active_idx = 3
    elif "pack" in status_str or "complet" in status_str or "ready" in status_str: active_idx = 4

    progress_cols = st.columns(len(stages))
    for idx, stage_name in enumerate(stages):
        with progress_cols[idx]:
            if idx < active_idx:
                st.success(f"✅ {stage_name}")
            elif idx == active_idx:
                st.warning(f"🔄 **{stage_name} (Active)**")
            else:
                st.info(f"⏳ {stage_name}")

    st.markdown("---")
    st.markdown("### 📝 Order Notes & Settlement Details")
    st.info(f"**Notes:**\n\n{row_data.get('Notes', 'No special notes.')}")

st.caption("🔄 Secured Real-time Connection via Google Sheets.")