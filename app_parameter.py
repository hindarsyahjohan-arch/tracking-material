import streamlit as st
import pandas as pd
import requests
import time
import io

st.set_page_config(
    page_title="Reactor Parameters & Work Sheet",
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

st.title("🧪 Reactor Parameters & Work Sheet Display")
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
    # 1. HEADER DATA BATCH & OPERATOR
    # --------------------------------------------------------------------------
    st.markdown("### 📌 Latest Batch Production Header")
    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    
    col_h1.metric("Production Code", str(get_val(last_row, ["Kode Produksi", "Kode_Produksi"])))
    col_h2.metric("Process Date", str(get_val(last_row, ["Tanggal"])))
    col_h3.metric("Lead Operator", str(get_val(last_row, ["Operator"])))
    col_h4.metric("Reactor Status", str(get_val(last_row, ["Status Reaktor", "Status_Reaktor"], "Active 🟢")))

    st.divider()

    # --------------------------------------------------------------------------
    # 2. TABS DETAIL PARAMETER
    # --------------------------------------------------------------------------
    tab_neraca, tab_reaktor, tab_log = st.tabs([
        "⚖️ Mass & Material Balance", 
        "⚙️ Chemistry & Reactor 1 Parameters", 
        "📋 Batch Parameter History"
    ])

    # --- TAB 1: MASS BALANCE ---
    with tab_neraca:
        st.markdown("#### 📊 Material Balance (Melting & Refining)")
        
        w_in = clean_float(get_val(last_row, ["Weight In Gram", "Weight_In", "Weight In"], 0))
        raw_purity = clean_float(get_val(last_row, ["Purity"], 0))
        
        purity_decimal = raw_purity / 100.0 if raw_purity > 1 else raw_purity
        est_24k = w_in * purity_decimal
        
        w_out = clean_float(get_val(last_row, ["Weight Out", "Weight_Out"], 0))
        loss = clean_float(get_val(last_row, ["Loss"], 0))
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Weight In (Gram)", f"{w_in:,.2f} g")
        col_m2.metric("Alloy Purity", f"{raw_purity:.3f}%" if raw_purity > 1 else f"{raw_purity * 100:.3f}%")
        col_m3.metric("Est. Au (99.99)", f"{est_24k:,.2f} g")
        col_m4.metric("Losses", f"{loss:,.2f} g", delta_color="inverse")

        st.markdown("---")
        st.markdown("#### 📝 Weight Details Log")
        
        display_cols = [c for c in ["Kode Produksi", "Tanggal", "Weight In Gram", "Weight Out", "Sample", "Loss", "Operator"] if c in df_param.columns]
        st.dataframe(df_param[display_cols].tail(5), use_container_width=True, hide_index=True)

    # --- TAB 2: REACTOR PARAMETERS ---
    with tab_reaktor:
        st.markdown("#### ⚗️ Chemical Solutions & Heating Parameters")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        
        with col_r1:
            st.info("**🧪 Acid & Reagents Usage**")
            hno3_tank = get_val(last_row, ["HNO3 Tank", "HNO3_Tank"], 0)
            hno3_shower = get_val(last_row, ["HNO3 Shower", "HNO3_Shower"], 0)
            hcl = get_val(last_row, ["HCL"], 0)
            total_aq = get_val(last_row, ["Total Aquaregia", "Total_Aquaregia"], 0)
            water_add = get_val(last_row, ["Water_Add", "Water Add"], 0)
            
            st.write(f"• **HNO3 Tank:** {hno3_tank} L")
            st.write(f"• **HNO3 Shower:** {hno3_shower} L")
            st.write(f"• **HCL:** {hcl} L")
            st.write(f"• **Total Aquaregia:** {total_aq} L")
            st.write(f"• **Water Added:** {water_add} L")

        with col_r2:
            st.warning("**🔥 Heating & Reductant**")
            smb = get_val(last_row, ["SMB"], 0)
            heat_temp = get_val(last_row, ["Heating Temp", "Heating_Temp"], 0)
            heat_time = get_val(last_row, ["Heating Time", "Heating_Time"], 0)
            
            st.write(f"• **SMB (L/Kg):** {smb}")
            st.write(f"• **Heating Temp:** {heat_temp} °C")
            st.write(f"• **Heating Time:** {heat_time} Hours")

        with col_r3:
            st.success("**💨 Operational Notes**")
            notes = get_val(last_row, ["Notes", "Catatan"], "No special notes.")
            st.write(f"**Floor Remarks:**\n\n{notes}")

    # --- TAB 3: HISTORY ---
    with tab_log:
        st.markdown("#### 📜 All Parameter Records")
        st.dataframe(df_param, use_container_width=True, hide_index=True)

st.caption("🔄 Data automatically synchronized with Google Sheets 'Parameter' tab.")