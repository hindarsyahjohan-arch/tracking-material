import streamlit as st
import pandas as pd
import requests
import time
import io

st.set_page_config(
    page_title="Reactor & Melting Parameters Work Sheet",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Google Sheet Link
URL_ASLI_SHEET = "https://docs.google.com/spreadsheets/d/1haDJKJFD_o4tOwXSE4kw4wXHjnfM9UCo3LwQXztrWLk/edit?gid=577877479#gid=577877479"

@st.cache_data(ttl=10)
def load_parameter_data():
    try:
        base_url = URL_ASLI_SHEET.split("/edit")[0]
        url_csv = f"{base_url}/gviz/tq?tqx=out:csv&sheet=Parameter&t={int(time.time())}"
        response = requests.get(url_csv, timeout=10)
        
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            df.columns = [str(col).strip() for col in df.columns]
            return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

df_param = load_parameter_data()

st.title("🧪 Production Work Sheet & Parameters")
st.caption("Real-time monitoring for Floor Operator Tablets")
st.divider()

if df_param.empty:
    st.warning("⚠️ No data found in the 'Parameter' tab or connection blocked.")
    st.info("Please make sure the Google Sheet 'Parameter' tab is populated.")
else:
    last_row = df_param.iloc[-1]
    
    def get_val(df_row, possible_keys, default="-"):
        for key in possible_keys:
            if key in df_row and pd.notna(df_row[key]):
                return df_row[key]
        return default

    def clean_float(val):
        try:
            if pd.isna(val):
                return 0.0
            cleaned = str(val).replace('%', '').replace(',', '').strip()
            return float(cleaned)
        except:
            return 0.0

    # --------------------------------------------------------------------------
    # 0. PILIHAN PROSES UTAMA (OPERATOR SELECTOR)
    # --------------------------------------------------------------------------
    selected_process_type = st.selectbox(
        "📌 Select Work Sheet Process Type:",
        [
            "1. Gold Lead Making (Banting / Melting)",
            "2. Refining Process (Reactor 1)"
        ]
    )

    st.divider()

    # --------------------------------------------------------------------------
    # KONDISI 1: TAMPILAN PROSES GOLD LEAD MAKING (BANTING / MELTING)
    # --------------------------------------------------------------------------
    if "Gold Lead Making" in selected_process_type:
        st.markdown("### 🔥 Gold Lead Making Work Sheet (Banting / Melting)")
        
        # Header Info Batch
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        col_h1.metric("Production Code", str(get_val(last_row, ["Kode Produksi", "Kode_Produksi"])))
        col_h2.metric("Process Date", str(get_val(last_row, ["Tanggal"])))
        col_h3.metric("Lead Operator", str(get_val(last_row, ["Operator"])))
        col_h4.metric("Status", "Active Melting 🟢")

        st.divider()

        col_b1, col_b2 = st.columns(2)

        with col_b1:
            st.markdown("#### ⚖️ Material Balance & Banting Data")
            w_in = clean_float(get_val(last_row, ["Weight in", "Weight In Gram", "Weight_In"], 0))
            raw_purity = clean_float(get_val(last_row, ["Purity"], 0))
            purity_decimal = raw_purity / 100.0 if raw_purity > 1 else raw_purity
            est_24k = w_in * purity_decimal
            
            w_out = clean_float(get_val(last_row, ["Out", "Weight Out"], 0))
            loss = clean_float(get_val(last_row, ["Loss"], 0))
            sample = clean_float(get_val(last_row, ["Sample"], 0))

            st.write(f"• **Weight In:** {w_in:,.2f} Gram")
            st.write(f"• **Purity:** {raw_purity:.3f}%" if raw_purity > 1 else f"• **Purity:** {raw_purity * 100:.3f}%")
            st.write(f"• **Est. 99.99 (24K):** {est_24k:,.2f} Gram")
            st.markdown("---")
            st.write(f"• **Banting In:** {w_in:,.2f} Gram")
            st.write(f"• **Banting Out:** {w_out:,.2f} Gram")
            st.write(f"• **Sample:** {sample:,.2f} Gram")
            st.write(f"• **Loss:** {loss:,.2f} Gram")
            st.write(f"• **Banting Operator:** {get_val(last_row, ['Banting Operator', 'Operator'], '-')}")

        with col_b2:
            st.markdown("#### ⚙️ Vacuum, Nitrogen & Furnace Parameters")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.metric("Vacum 1 (s)", get_val(last_row, ["Vacum 1 (s)", "Vacum 1"], "30"))
                st.metric("Nitrogen 1 (s)", get_val(last_row, ["Nitrogen 1 (s)", "Nitrogen 1"], "30"))
                st.metric("Vacum 2 (s)", get_val(last_row, ["Vacum 2 (s)", "Vacum 2"], "30"))
                st.metric("Nitrogen Status", get_val(last_row, ["Nitrogen"], "on"))
                st.metric("Chiller (°C)", get_val(last_row, ["Chiller ( C)", "Chiller"], "25"))
            with col_v2:
                st.metric("First Heat (°C)", get_val(last_row, ["First Heat ( C)", "First Heat"], "1050"))
                st.metric("Nitrogen (bar)", get_val(last_row, ["Nitrogen (bar )", "Nitrogen bar"], "6"))
                st.metric("Speed (%)", get_val(last_row, ["Speed", "Speed (%)"], "55%"))
                st.metric("Delay Heat (°C)", get_val(last_row, ["Delay Heat ( C)", "Delay Heat"], "970"))
                st.metric("Cooling Nitrogen (bar)", get_val(last_row, ["Cooling Nitrogen (bar )", "Cooling N2"], "10"))

    # --------------------------------------------------------------------------
    # KONDISI 2: TAMPILAN PROSES REFINING (REACTOR 1)
    # --------------------------------------------------------------------------
    else:
        st.markdown("### ⚗️ Refining Process Work Sheet (Reactor 1)")
        
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        col_h1.metric("Production Code", str(get_val(last_row, ["Kode Produksi", "Kode_Produksi"])))
        col_h2.metric("Process Date", str(get_val(last_row, ["Tanggal"])))
        col_h3.metric("Lead Operator", str(get_val(last_row, ["Operator"])))
        col_h4.metric("Reactor Status", "Active Refining 🟢")

        st.divider()

        tab_reaktor1, tab_neraca, tab_timing, tab_history = st.tabs([
            "⚗️ Reactor 1 Parameters", 
            "⚖️ Mass & Refining Balance", 
            "⏱️ Operator Time Log",
            "📋 Batch Parameter History"
        ])

        with tab_reaktor1:
            st.markdown("#### ⚗️ Chemical Solutions, Oxygen & Heating Parameters")
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("HNO3 from Tank (Ltr)", get_val(last_row, ["HNO3 dari Tank (Ltr)", "HNO3 Tank"], "0.00"))
                st.metric("HNO3 from Shower (Ltr)", get_val(last_row, ["HNO3 dari Shower (Ltr)", "HNO3 Shower"], "0.00"))
                st.metric("Initial HNO3 (%)", get_val(last_row, ["HNO3 Awal (%)", "HNO3 Awal"], "0%"))
                st.metric("Dosing from Tank (Ltr)", get_val(last_row, ["Dosing dari tank (Ltr)", "Dosing Tank"], "0.00"))
                st.metric("Dosing from Shower (Ltr)", get_val(last_row, ["Dosing dari shower (Ltr)", "Dosing Shower"], "0.00"))
                st.metric("Dosing Pause (Minutes)", get_val(last_row, ["Jeda dosing (Menit)", "Dosing Pause"], "0"))
            with col_r2:
                st.metric("HCL (Ltr) [4x Alloy]", get_val(last_row, ["HCL (Ltr) 4 x berat alloy", "HCL"], "0.00"))
                st.metric("Delay Air (Angin)", get_val(last_row, ["Delay Angin"], "0"))
                st.metric("Open Air Duration", get_val(last_row, ["Lama Angin Buka"], "0"))
                st.metric("Oxygen Parameter", get_val(last_row, ["Oxygen"], "-"))
                st.metric("Cycle Time (')", get_val(last_row, ["Cycle Time (')"], "0"))
            with col_r3:
                st.metric("SMB (Ltr)", get_val(last_row, ["SMB (Ltr)", "SMB"], "0.00"))
                st.metric("Heating Temp (°C)", get_val(last_row, ["Heating Temp", "Heating_Temp"], "0"))
                st.metric("Heating Time (h)", get_val(last_row, ["Heating Time", "Heating_Time"], "0"))
                st.metric("Total Aquaregia (Ltr)", get_val(last_row, ["Total Aquaregia"], "0.00"))

        with tab_neraca:
            st.markdown("#### 📊 Material Balance & Refining Stages")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                w_in = clean_float(get_val(last_row, ["Weight in", "Weight In Gram"], 0))
                st.write(f"• **Weight In:** {w_in:,.2f} Gram")
                st.write(f"• **Purity:** {get_val(last_row, ['Purity'], '0')}%")
            with col_m2:
                st.write(f"• **Gold Powder Result:** {get_val(last_row, ['Powder'], '-')}")
                st.write(f"• **Operators:** {get_val(last_row, ['Operator Refining', 'Operator'], '-')}")

        with tab_timing:
            st.markdown("#### ⏱️ Operator Operational Time Log")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.write(f"• **Check Weight:** {get_val(last_row, ['Check Weight'], '-')}")
                st.write(f"• **Melting Au:** {get_val(last_row, ['Melting Au'], '-')}")
                st.write(f"• **Put in RC & Dissolve Au:** {get_val(last_row, ['Put in RC & dissolve Au'], '-')}")
            with col_t2:
                st.write(f"• **Granulating:** {get_val(last_row, ['Granulating'], '-')}")
                st.write(f"• **Drying:** {get_val(last_row, ['Drying'], '-')}")

        with tab_history:
            st.markdown("#### 📜 Complete Parameter Records Table")
            st.dataframe(df_param, use_container_width=True, hide_index=True)

st.caption("🔄 Data automatically synchronized with Google Sheets 'Parameter' tab.")