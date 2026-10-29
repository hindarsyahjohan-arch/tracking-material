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

URL_ASLI_SHEET = "https://docs.google.com/spreadsheets/d/1haDJKJFD_o4tOwXSE4kw4wXHjnfM9UCo3LwQXztrWLk/edit?gid=577877479#gid=577877479"

@st.cache_data(ttl=10)
def load_parameter_data():
    try:
        base_url = URL_ASLI_SHEET.split("/edit")[0]
        url_csv = f"{base_url}/gviz/tq?tqx=out:csv&sheet=Sheet_Parameter&t={int(time.time())}"
        response = requests.get(url_csv, timeout=10)
        
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            # Membersihkan spasi di nama kolom agar seragam
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
    st.warning("⚠️ Belum ada data di tab 'Sheet_Parameter' atau tab belum dibuat di Google Sheets.")
    st.info("Silakan buat tab bernama **Sheet_Parameter** di Google Sheets dan isi data parameter produksi.")
else:
    # Ambil baris terakhir
    last_row = df_param.iloc[-1]
    
    # Fungsi pencarian kolom yang fleksibel (mendukung dengan spasi atau underscore)
    def get_val(df_row, possible_keys, default=0):
        for key in possible_keys:
            if key in df_row:
                return df_row[key]
        return default

    # --------------------------------------------------------------------------
    # 1. HEADER DATA BATCH & OPERATOR
    # --------------------------------------------------------------------------
    st.markdown("### 📌 Header Batch Produksi Terkini")
    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    
    col_h1.metric("Kode Produksi", str(get_val(last_row, ["Kode_Produksi", "Kode Produksi", "Batch"], "-")))
    col_h2.metric("Tanggal Proses", str(get_val(last_row, ["Tanggal", "Date"], "-")))
    col_h3.metric("Operator Utama", str(get_val(last_row, ["Operator", "Operator Utama"], "-")))
    col_h4.metric("Status Reaktor", str(get_val(last_row, ["Status_Reaktor", "Status Reaktor", "Status"], "Aktif 🟢")))

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
        
        def clean_float(val):
            try:
                if pd.isna(val):
                    return 0.0
                cleaned = str(val).replace('%', '').replace(',', '').strip()
                return float(cleaned)
            except:
                return 0.0

        w_in = clean_float(get_val(last_row, ["Weight_In", "Weight In", "In"]))
        raw_purity = str(get_val(last_row, ["Purity", "Kadar"], 0)).replace('%', '').strip()
        purity = clean_float(raw_purity)
        
        purity_decimal = purity / 100.0 if purity > 1 else purity
        est_24k = w_in * purity_decimal
        loss = clean_float(get_val(last_row, ["Loss", "Selisih"], 0))
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Weight In (Gram)", f"{w_in:,.2f} g")
        col_m2.metric("Purity Alloy", f"{purity:.3f}%" if purity > 1 else f"{purity * 100:.3f}%")
        col_m3.metric("Estimasi Au (99.99)", f"{est_24k:,.2f} g")
        col_m4.metric("Losses (Banting)", f"{loss:.2f} g", delta_color="inverse")

        st.markdown("---")
        st.markdown("#### 📝 Data Rincian Timbangan")
        # Menampilkan tabel dengan pengecekan kolom yang tersedia agar tidak error lagi
        available_cols = [c for c in df_param.columns if c in ["Kode_Produksi", "Kode Produksi", "Tanggal", "Weight_In", "Weight In", "Weight_Out", "Weight Out", "Sample", "Loss", "Operator"]]
        st.dataframe(df_param[available_cols].tail(5), use_container_width=True, hide_index=True)

    # --- TAB 2: PARAMETER REAKTOR ---
    with tab_reaktor:
        st.markdown("#### ⚗️ Parameter Larutan Kimia & Pemanasan")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        
        with col_r1:
            st.info("**🧪 Penggunaan Asam & Reagen**")
            st.write(f"• **HNO3 Tank:** {get_val(last_row, ['HNO3_Tank', 'HNO3 Tank'], 0)} Ltr")
            st.write(f"• **HNO3 Shower:** {get_val(last_row, ['HNO3_Shower', 'HNO3 Shower'], 0)} Ltr")
            st.write(f"• **HCL (4x Alloy):** {get_val(last_row, ['HCL'], 0)} Ltr")
            st.write(f"• **Total Aquaregia:** {get_val(last_row, ['Total_Aquaregia', 'Total Aquaregia'], 0)} Ltr")
            st.write(f"• **Penambahan Water:** {get_val(last_row, ['Water_Add', 'Water Add'], 0)} Ltr")
            st.write(f"**Total Volume Liquid:** `{get_val(last_row, ['Total_Liquid', 'Total Liquid'], 0)} Ltr`")

        with col_r2:
            st.warning("**🔥 Pemanasan & Dosing Sodium**")
            st.write(f"• **Sodium Total:** {get_val(last_row, ['Sodium_Kg', 'Sodium (kg)'], 0)} Kg ({get_val(last_row, ['Sodium_Ltr', 'Sodium (Ltr)'], 0)} Ltr)")
            st.write(f"• **Heating Temp:** {get_val(last_row, ['Heating_Temp', 'Heating Temp'], 0)} °C")
            st.write(f"• **Heating Time:** {get_val(last_row, ['Heating_Time', 'Heating Time (h)'], 0)} Jam")

        with col_r3:
            st.success("**💨 Catatan Operasional**")
            st.write(f"**Keterangan Lapangan:**\n\n{get_val(last_row, ['Catatan', 'Keterangan'], 'Tidak ada catatan khusus.')}")

    # --- TAB 3: RIWAYAT BATCH ---
    with tab_log:
        st.markdown("#### 📜 Tabel Semua Data Parameter")
        st.dataframe(df_param, use_container_width=True, hide_index=True)

st.caption("🔄 Data otomatis terhubung dengan Google Sheets tab 'Sheet_Parameter'.")