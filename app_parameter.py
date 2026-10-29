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

# URL Google Sheets Anda
URL_ASLI_SHEET = "https://docs.google.com/spreadsheets/d/1haDJKJFD_o4tOwXSE4kw4wXHjnfM9UCo3LwQXztrWLk/edit?gid=802911412#gid=802911412"

@st.cache_data(ttl=10) # Refresh data otomatis tiap 10 detik dari Google Sheets
def load_parameter_data():
    try:
        base_url = URL_ASLI_SHEET.split("/edit")[0]
        # Membaca tab 'Sheet_Parameter'
        url_csv = f"{base_url}/gviz/tq?tqx=out:csv&sheet=Sheet_Parameter&t={int(time.time())}"
        response = requests.get(url_csv, timeout=10)
        
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            df.columns = [str(col).strip() for col in df.columns]
            return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

# Load data dari Google Sheets
df_param = load_parameter_data()

st.title("🧪 Display Parameter Reaktor & Lembar Kerja")
st.caption("Monitoring Real-time untuk Tablet Operator Floor")
st.divider()

if df_param.empty:
    st.warning("⚠️ Belum ada data di tab 'Sheet_Parameter' atau tab belum dibuat di Google Sheets.")
    st.info("Silakan buat tab bernama **Sheet_Parameter** di Google Sheets dan isi data parameter produksi.")
else:
    # Ambil data baris paling terakhir (Batch Terbaru)
    last_row = df_param.iloc[-1]
    
    # --------------------------------------------------------------------------
    # 1. HEADER DATA BATCH & OPERATOR
    # --------------------------------------------------------------------------
    st.markdown("### 📌 Header Batch Produksi Terkini")
    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    
    col_h1.metric("Kode Produksi", str(last_row.get("Kode_Produksi", "-")))
    col_h2.metric("Tanggal Proses", str(last_row.get("Tanggal", "-")))
    col_h3.metric("Operator Utama", str(last_row.get("Operator", "-")))
    col_h4.metric("Status Reaktor", str(last_row.get("Status_Reaktor", "Aktif 🟢")))

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
        
        # Fungsi pembersih data numerik agar aman dari error string/persen
        def clean_float(val):
            try:
                if pd.isna(val):
                    return 0.0
                # Hapus tanda persen, koma, spasi, lalu ubah ke float
                cleaned = str(val).replace('%', '').replace(',', '').strip()
                return float(cleaned)
            except:
                return 0.0

        w_in = clean_float(last_row.get("Weight_In", 0))
        raw_purity = str(last_row.get("Purity", 0)).replace('%', '').strip()
        purity = clean_float(raw_purity)
        
        # Jika purity ditulis dalam bentuk persen desimal atau puluhan (misal: 99.107 atau 0.99107)
        if purity > 1:
            purity_decimal = purity / 100.0
        else:
            purity_decimal = purity

        est_24k = w_in * purity_decimal
        loss = clean_float(last_row.get("Loss", 0))
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Weight In (Gram)", f"{w_in:,.2f} g")
        col_m2.metric("Purity Alloy", f"{purity:.3f}%" if purity > 1 else f"{purity * 100:.3f}%")
        col_m3.metric("Estimasi Au (99.99)", f"{est_24k:,.2f} g")
        col_m4.metric("Losses (Banting)", f"{loss:.2f} g", delta_color="inverse")

        st.markdown("---")
        st.markdown("#### 📝 Data Rincian Timbangan")
        st.dataframe(df_param[["Kode_Produksi", "Tanggal", "Weight_In", "Weight_Out", "Sample", "Loss", "Operator"]].tail(5), use_container_width=True, hide_index=True)

    # --- TAB 2: PARAMETER REAKTOR ---
    with tab_reaktor:
        st.markdown("#### ⚗️ Parameter Larutan Kimia & Pemanasan")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        
        with col_r1:
            st.info("**🧪 Penggunaan Asam & Reagen**")
            st.write(f"• **HNO3 Tank:** {last_row.get('HNO3_Tank', 0)} Ltr")
            st.write(f"• **HNO3 Shower:** {last_row.get('HNO3_Shower', 0)} Ltr")
            st.write(f"• **HCL (4x Alloy):** {last_row.get('HCL', 0)} Ltr")
            st.write(f"• **Total Aquaregia:** {last_row.get('Total_Aquaregia', 0)} Ltr")
            st.write(f"• **Penambahan Water:** {last_row.get('Water_Add', 0)} Ltr")
            st.write(f"**Total Volume Liquid:** `{last_row.get('Total_Liquid', 0)} Ltr`")

        with col_r2:
            st.warning("**🔥 Pemanasan & Dosing Sodium**")
            st.write(f"• **Sodium Total:** {last_row.get('Sodium_Kg', 0)} Kg ({last_row.get('Sodium_Ltr', 0)} Ltr)")
            st.write(f"• **Heating Temp:** {last_row.get('Heating_Temp', 0)} °C")
            st.write(f"• **Heating Time:** {last_row.get('Heating_Time', 0)} Jam")

        with col_r3:
            st.success("**💨 Catatan Operasional**")
            st.write(f"**Keterangan Lapangan:**\n\n{last_row.get('Catatan', 'Tidak ada catatan khusus.')}")

    # --- TAB 3: RIWAYAT BATCH ---
    with tab_log:
        st.markdown("#### 📜 Tabel Semua Data Parameter")
        st.dataframe(df_param, use_container_width=True, hide_index=True)

st.caption("🔄 Data otomatis terhubung dengan Google Sheets tab 'Sheet_Parameter'.")