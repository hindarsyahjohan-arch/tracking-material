import streamlit as st
import pandas as pd
import requests
import time
import io

st.set_page_config(
    page_title="Parameter Reaktor & Lembar Kerja",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Link Google Sheet
URL_ASLI_SHEET = "https://docs.google.com/spreadsheets/d/1haDJKJFD_o4tOwXSE4kw4wXHjnfM9UCo3LwQXztrWLk/edit?gid=577877479#gid=577877479"

@st.cache_data(ttl=10) # Refresh otomatis tiap 10 detik
def load_parameter_data():
    try:
        base_url = URL_ASLI_SHEET.split("/edit")[0]
        # Mengambil dari tab 'Parameter' (gid=577877479)
        url_csv = f"{base_url}/gviz/tq?tqx=out:csv&sheet=Parameter&t={int(time.time())}"
        response = requests.get(url_csv, timeout=10)
        
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            # Hapus spasi berlebih pada nama kolom
            df.columns = [str(col).strip() for col in df.columns]
            return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

df_param = load_parameter_data()

st.title("🧪 Display Parameter Reaktor & Lembar Kerja")
st.caption("Monitoring Real-time untuk Tablet Operator Floor")
st.divider()

if df_param.empty:
    st.warning("⚠️ Belum ada data di tab 'Parameter' atau koneksi terhalang.")
    st.info("Pastikan data di Google Sheet tab 'Parameter' sudah terisi.")
else:
    # Ambil data baris paling akhir
    last_row = df_param.iloc[-1]
    
    # Fungsi pencarian nilai kolom yang aman
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
    st.markdown("### 📌 Header Batch Produksi Terkini")
    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    
    col_h1.metric("Kode Produksi", str(get_val(last_row, ["Kode Produksi", "Kode_Produksi"])))
    col_h2.metric("Tanggal Proses", str(get_val(last_row, ["Tanggal"])))
    col_h3.metric("Operator Utama", str(get_val(last_row, ["Operator"])))
    col_h4.metric("Status Reaktor", str(get_val(last_row, ["Status Reaktor", "Status_Reaktor"], "Aktif 🟢")))

    st.divider()

    # --------------------------------------------------------------------------
    # 2. TABS DETAIL PARAMETER
    # --------------------------------------------------------------------------
    tab_neraca, tab_reaktor, tab_log = st.tabs([
        "⚖️ Neraca Massa & Material Balance", 
        "⚙️ Parameter Kimia & Reaktor 1", 
        "📋 Riwayat Batch Parameter"
    ])

    # --- TAB 1: NERACA MASSA ---
    with tab_neraca:
        st.markdown("#### 📊 Material Balance (Banting & Refining)")
        
        w_in = clean_float(get_val(last_row, ["Weight In Gram", "Weight_In", "Weight In"], 0))
        raw_purity = clean_float(get_val(last_row, ["Purity"], 0))
        
        purity_decimal = raw_purity / 100.0 if raw_purity > 1 else raw_purity
        est_24k = w_in * purity_decimal
        
        w_out = clean_float(get_val(last_row, ["Weight Out", "Weight_Out"], 0))
        loss = clean_float(get_val(last_row, ["Loss"], 0))
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Weight In (Gram)", f"{w_in:,.2f} g")
        col_m2.metric("Purity Alloy", f"{raw_purity:.3f}%" if raw_purity > 1 else f"{raw_purity * 100:.3f}%")
        col_m3.metric("Estimasi Au (99.99)", f"{est_24k:,.2f} g")
        col_m4.metric("Losses (Banting)", f"{loss:.2f} g", delta_color="inverse")

        st.markdown("---")
        st.markdown("#### 📝 Data Rincian Timbangan")
        
        # Tampilkan tabel dengan kolom yang ada di Sheet
        display_cols = [c for c in ["Kode Produksi", "Tanggal", "Weight In Gram", "Weight Out", "Sample", "Loss", "Operator"] if c in df_param.columns]
        st.dataframe(df_param[display_cols].tail(5), use_container_width=True, hide_index=True)

    # --- TAB 2: PARAMETER REAKTOR ---
    with tab_reaktor:
        st.markdown("#### ⚗️ Parameter Larutan Kimia & Pemanasan")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        
        with col_r1:
            st.info("**🧪 Penggunaan Asam & Reagen**")
            hno3_tank = get_val(last_row, ["HNO3 Tank", "HNO3_Tank"], 0)
            hno3_shower = get_val(last_row, ["HNO3 Shower", "HNO3_Shower"], 0)
            hcl = get_val(last_row, ["HCL"], 0)
            total_aq = get_val(last_row, ["Total Aquaregia", "Total_Aquaregia"], 0)
            water_add = get_val(last_row, ["Water_Add", "Water Add"], 0)
            
            st.write(f"• **HNO3 Tank:** {hno3_tank} Ltr")
            st.write(f"• **HNO3 Shower:** {hno3_shower} Ltr")
            st.write(f"• **HCL:** {hcl} Ltr")
            st.write(f"• **Total Aquaregia:** {total_aq} Ltr")
            st.write(f"• **Water Add:** {water_add} Ltr")

        with col_r2:
            st.warning("**🔥 Pemanasan & Bahan Reduksi**")
            smb = get_val(last_row, ["SMB"], 0)
            heat_temp = get_val(last_row, ["Heating Temp", "Heating_Temp"], 0)
            heat_time = get_val(last_row, ["Heating Time", "Heating_Time"], 0)
            
            st.write(f"• **SMB (Ltr/Kg):** {smb}")
            st.write(f"• **Heating Temp:** {heat_temp} °C")
            st.write(f"• **Heating Time:** {heat_time} Jam")

        with col_r3:
            st.success("**💨 Catatan Operasional**")
            notes = get_val(last_row, ["Notes", "Catatan"], "Tidak ada catatan khusus.")
            st.write(f"**Keterangan Lapangan:**\n\n{notes}")

    # --- TAB 3: RIWAYAT BATCH ---
    with tab_log:
        st.markdown("#### 📜 Tabel Semua Data Parameter")
        st.dataframe(df_param, use_container_width=True, hide_index=True)

st.caption("🔄 Data otomatis terhubung dengan Google Sheets tab 'Parameter'.")