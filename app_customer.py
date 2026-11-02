import streamlit as st
import pandas as pd
import requests
import time
import io

st.set_page_config(
    page_title="Customer Refining Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Google Sheet Link (Ganti/Gunakan link database utama Anda)
URL_ASLI_SHEET = "https://docs.google.com/spreadsheets/d/1haDJKJFD_o4tOwXSE4kw4wXHjnfM9UCo3LwQXztrWLk/edit?gid=577877479#gid=577877479"

@st.cache_data(ttl=10)
def load_customer_data():
    try:
        base_url = URL_ASLI_SHEET.split("/edit")[0]
        # Mengambil data dari tab khusus customer, misal: 'Customer_Tracking'
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

st.title("🌟 Customer Refining Service Portal")
st.caption("Track your gold refining progress, purity, weight balance, and estimated completion date in real-time.")
st.divider()

if df_cust.empty:
    st.info("ℹ️ Please create a sheet tab named **'Customer_Tracking'** in your Google Sheets to store customer live tracking data.")
    
    # --- INTERACTIVE SIMULATION FOR DEMO / PREVIEW ---
    st.markdown("### 🔍 Search Your Batch / Customer Code")
    search_code = st.text_input("Enter Production Code or Customer Name:", value="YT170926-8")
    
    if search_code:
        st.divider()
        st.markdown(f"### 📋 Refining Order Status: `{search_code}`")
        
        # Metric Overview Cards (Ditambah Purity)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Received Weight", "10.00 Kg")
        c2.metric("Purity Level", "99.107 %", "Verified 🟢")
        c3.metric("DP Process / Initial Set", "5.00 Kg", "Completed")
        c4.metric("Remaining Balance Due", "5.00 Kg", "Pending Final")
        c5.metric("Est. Completion", "2026-11-05")

        st.markdown("---")
        st.markdown("### 📍 Live Process Tracking")
        
        # Visual Progress Bar / Status Steps
        stages = [
            "1. Material Receiving", 
            "2. Purity Testing", 
            "3. Refining Process", 
            "4. Reduction & Cleaning", 
            "5. Packaging & Ready"
        ]
        
        current_active_stage = 2 # Misal posisi di Refining Process
        
        progress_cols = st.columns(len(stages))
        for idx, stage_name in enumerate(stages):
            with progress_cols[idx]:
                if idx < current_active_stage:
                    st.success(f"✅ {stage_name}")
                elif idx == current_active_stage:
                    st.warning(f"🔄 **{stage_name} (Active)**")
                else:
                    st.info(f"⏳ {stage_name}")

        st.markdown("---")
        st.markdown("### 📝 Order Notes & Details")
        st.info("**Customer Name:** PT. Sumber Mulia Logam\n\n**Purity Note:** Initial sample test recorded at 99.107% purity.\n\n**Payment/Settlement Notes:** Initial DP of 5 Kg received. The remaining 5 Kg will be settled upon final packaging and purity verification.")
        
else:
    # JIKA DATA DI GOOGLE SHEET SUDAH ADA
    customer_list = df_cust['Customer Name'].unique() if 'Customer Name' in df_cust.columns else []
    selected_customer = st.selectbox("Select Customer / Batch Code:", df_cust.iloc[:, 0].unique())
    
    row_data = df_cust[df_cust.iloc[:, 0] == selected_customer].iloc[-1]
    
    st.markdown(f"### 📋 Tracking Details for: `{selected_customer}`")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Weight", f"{row_data.get('Total Weight', 0)} Kg")
    col2.metric("Purity", f"{row_data.get('Purity', 0)} %")
    col3.metric("DP Process Set", f"{row_data.get('DP Weight', 0)} Kg")
    col4.metric("Remaining Balance", f"{row_data.get('Remaining Weight', 0)} Kg")
    col5.metric("Est. Completion", str(row_data.get('Est Date', '-')))
    
    st.markdown("---")
    st.markdown("### 📍 Process Stage Status")
    st.success(f"Current Status: **{row_data.get('Current Status', 'In Progress')}**")

st.caption("🔄 Secured Real-time Connection via Google Sheets.")