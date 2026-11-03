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

# Custom CSS untuk menghilangkan ruang kosong (padding) atas/bawah agar pas di satu layar
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

# Google Sheet Link Utama
URL_ASLI_SHEET = "https://docs.google.com/spreadsheets/d/1haDJKJFD_o4tOwXSE4kw4wXHjnfM9UCo3LwQXztrWLk/edit?gid=577877479#gid=577877479"

# 2. HEADER KONTROL KIOSK & ROTASI OTOMATIS
st.markdown("### 🏭 Lantai Produksi - Kiosk Multi-Display Mode")

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 6])

with col_ctrl1:
    mode_tampilan = st.selectbox(
        "Pilih Mode Tampilan:",
        ["🔄 Auto Rotate (Bergantian Otomatis)", "📊 1. Executive Dashboard", "🧪 2. Reactor Parameters", "🛠️ 3. Operator Checklist"]
    )

with col_ctrl2:
    # Waktu jeda rotasi otomatis (dalam detik)
    waktu_rotasi = st.slider("Durasi Ganti Halaman (Detik):", min_value=5, max_value=30, value=15)

# Logika Auto Rotate menggunakan Session State & Auto-run
if "last_switch" not in st.session_state:
    st.session_state.last_switch = time.time()
if "page_index" not in st.session_state:
    st.session_state.page_index = 0

pages_list = [
    "📊 1. Executive Dashboard", 
    "🧪 2. Reactor Parameters", 
    "🛠️ 3. Operator Checklist"
]

if mode_tampilan == "🔄 Auto Rotate (Bergantian Otomatis)":
    current_time = time.time()
    if current_time - st.session_state.last_switch > waktu_rotasi:
        st.session_state.page_index = (st.session_state.page_index + 1) % len(pages_list)
        st.session_state.last_switch = current_time
        st.rerun()
    
    selected_page = pages_list[st.session_state.page_index]
    col_ctrl3.markdown(f"👉 **Sedang Menampilkan Otomatis:** `{selected_page}` (Berganti tiap {waktu_rotasi} detik)")
else:
    selected_page = mode_tampilan

st.divider()

# ==============================================================================
# HALAMAN 1: EXECUTIVE DASHBOARD
# ==============================================================================
if "Dashboard" in selected_page:
    st.markdown("#### 📊 Production Executive Summary (Live)")
    
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
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Items", len(df_dash))
        c2.metric("Total Berat (Kg)", f"{df_dash.select_dtypes(include='number').sum().iloc[0]:,.2f}")
        c3.metric("Status Kiosk", "Online 🟢")
        c4.metric("Refresh Rate", "10 Detik")
        
        # Tampilkan ringkasan tabel yang pas di layar tanpa scroll panjang
        st.dataframe(df_dash.head(5), use_container_width=True, hide_index=True)
    else:
        st.warning("Memuat data dashboard...")

# ==============================================================================
# HALAMAN 2: REACTOR PARAMETERS
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
        p1.metric("Kode Produksi", str(last_row.get("Kode Produksi", "-")))
        p2.metric("Weight In (g)", str(last_row.get("Weight In Gram", "-")))
        p3.metric("Purity", str(last_row.get("Purity", "-")))
        p4.metric("Heating Temp", f"{last_row.get('Heating Temp', '-')} °C")
        
        st.info(f"**Catatan Lapangan Terkini:** {last_row.get('Notes', 'Tidak ada catatan.')}")
    else:
        st.warning("Memuat data parameter reaktor...")

# ==============================================================================
# HALAMAN 3: OPERATOR CHECKLIST FORM (COMPACT)
# ==============================================================================
elif "Checklist" in selected_page:
    st.markdown("#### 🛠️ Form Checklist Operator Ringkas")
    
    pilihan_proses = st.selectbox(
        "Pilih Tahapan Proses:",
        ["1. Proses Banting (Melting)", "2. Proses Aquaregia", "3. Filter Emas & Reduksi"]
    )
    
    col_f1, col_f2, col_f3 = st.columns(3)
    op_name = col_f1.text_input("Nama Operator:", placeholder="Nama...")
    batch_num = col_f2.text_input("Nomor Batch:", placeholder="Batch...")
    shift = col_f3.selectbox("Shift:", ["Shift 1", "Shift 2", "Shift 3"])
    
    st.success("Form siap digunakan di tablet operator dalam mode ringkas satu layar.")

# Auto-refresh halaman setiap 5 detik agar siklus rotasi berjalan mulus
time.sleep(5)
st.rerun()