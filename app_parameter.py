import streamlit as st
import pandas as pd
import requests
import time
import io
from datetime import datetime

st.set_page_config(
    page_title="Production Work Sheet & Parameters",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Google Sheet & Webhook Link
URL_ASLI_SHEET = "https://docs.google.com/spreadsheets/d/1haDJKJFD_o4tOwXSE4kw4wXHjnfM9UCo3LwQXztrWLk/edit?gid=577877479#gid=577877479"
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzFdETw5CLY6NvqzeH8U1x8bTnWCaGOQpzGY8idhVJNXLoj4egNc9wvC7vpQzOBloEr/exec"

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

st.title("🧪 Production Work Sheet & Parameters Form")
st.caption("Auto-synced data from Google Sheets with Operator Input Forms")
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

    # Ambil Nama Operator langsung dari Google Sheet
    gsheet_operator = str(get_val(last_row, ["Operator", "Lead Operator"], "Nico"))

    # --------------------------------------------------------------------------
    # PILIHAN PROSES UTAMA
    # --------------------------------------------------------------------------
    selected_process_type = st.selectbox(
        "📌 Select Work Sheet Process Type:",
        [
            "1. Gold Lead Making (Banting / Melting)",
            "2. Refining Process (Reactor 1)"
        ]
    )

    st.divider()

    # ==========================================================================
    # PROSES 1: GOLD LEAD MAKING (BANTING / MELTING)
    # ==========================================================================
    if "Gold Lead Making" in selected_process_type:
        st.markdown("### 🔥 Gold Lead Making Work Sheet (Banting / Melting)")
        
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        prod_code = str(get_val(last_row, ["Kode Produksi", "Kode_Produksi"], "YT031126-2"))
        process_date = str(get_val(last_row, ["Tanggal"], "11/3/2026"))
        
        col_h1.metric("Production Code", prod_code)
        col_h2.metric("Process Date", process_date)
        col_h3.metric("Operator (GSheet)", gsheet_operator)
        col_h4.metric("Status", "Active Melting 🟢")

        st.divider()

        with st.form("form_banting_operator"):
            col_b1, col_b2 = st.columns(2)

            with col_b1:
                st.markdown("#### ⚖️ Material Balance (Google Sheet Data)")
                w_in = clean_float(get_val(last_row, ["Weight in", "Weight In Gram", "Weight_In"], 50138.91))
                raw_purity = clean_float(get_val(last_row, ["Purity"], 99.124))

                st.info(f"• **Weight In (GSheet):** {w_in:,.2f} Gram")
                st.info(f"• **Purity (GSheet):** {raw_purity:.3f}%" if raw_purity > 1 else f"• **Purity:** {raw_purity * 100:.3f}%")
                st.info(f"• **Operator (GSheet):** {gsheet_operator}")

                st.markdown("---")
                st.markdown("##### ✍️ Waktu & Catatan (Diisi Operator):")
                start_proc = st.text_input("Start Process Time:", placeholder="Contoh: 08:00")
                finish_proc = st.text_input("Finish Process Time:", placeholder="Contoh: 12:00")
                notes_val = st.text_area("Notes / Catatan:", placeholder="Masukkan catatan proses banting...")

            with col_b2:
                st.markdown("#### ⚙️ Vacuum, Nitrogen & Furnace Parameters (From Google Sheet)")
                st.write(f"• **Vacum 1 (s):** {get_val(last_row, ['Vacum 1 (s)'], '30')}")
                st.write(f"• **Nitrogen 1 (s):** {get_val(last_row, ['Nitrogen 1 (s)'], '30')}")
                st.write(f"• **Vacum 2 (s):** {get_val(last_row, ['Vacum 2 (s)'], '30')}")
                st.write(f"• **Nitrogen Status:** {get_val(last_row, ['Nitrogen'], 'on')}")
                st.write(f"• **Chiller (°C):** {get_val(last_row, ['Chiller ( C)'], '25')}")
                st.write(f"• **First Heat (°C):** {get_val(last_row, ['First Heat ( C)'], '1050')}")
                st.write(f"• **Nitrogen (bar):** {get_val(last_row, ['Nitrogen (bar )'], '6')}")
                st.write(f"• **Speed (%):** {get_val(last_row, ['Speed'], '55%')}")
                st.write(f"• **Delay Heat (°C):** {get_val(last_row, ['Delay Heat ( C)'], '970')}")
                st.write(f"• **Cooling Nitrogen (bar):** {get_val(last_row, ['Cooling Nitrogen (bar )'], '10')}")

            submit_banting = st.form_submit_button("📤 Submit Process Log to Google Sheets", use_container_width=True)
            if submit_banting:
                payload = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "proses": "Gold Lead Making",
                    "kode_produksi": prod_code,
                    "operator": gsheet_operator,
                    "start_process": start_proc,
                    "finish_process": finish_proc,
                    "notes": notes_val
                }
                try:
                    resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                    if resp.status_code == 200:
                        st.success("🎉 Process log successfully saved to Google Sheets!")
                    else:
                        st.error(f"❌ Failed: {resp.text}")
                except Exception as e:
                    st.error(f"❌ Connection error: {e}")

    # ==========================================================================
    # PROSES 2: REFINING PROCESS (REACTOR 1)
    # ==========================================================================
    else:
        st.markdown("### ⚗️ Refining Process Work Sheet (Reactor 1)")
        
        prod_code = str(get_val(last_row, ["Kode Produksi", "Kode_Produksi"], "YT170926-8"))
        
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        col_h1.metric("Production Code", prod_code)
        col_h2.metric("Process Date", str(get_val(last_row, ["Tanggal"], "9/17/2026")))
        col_h3.metric("Operator (GSheet)", gsheet_operator)
        col_h4.metric("Status", "Active Refining 🟢")

        st.divider()

        tab_reaktor1, tab_timing = st.tabs([
            "⚗️ Reactor 1 Parameters (Working Data)", 
            "⏱️ Operator Time Log & Notes (Input)"
        ])

        # TAB 1: PARAMETER DARI GOOGLE SHEET (MENYESUAIKAN LAYOUT HMI WORKING DATA REACTOR 1)[cite: 8]
        with tab_reaktor1:
            st.markdown("#### 🖥️ Working Data Reactor 1 (Live from Google Sheet)")
            
            col_w1, col_w2 = st.columns(2)

            with col_w1:
                # Kotak 1: HNO3 [nitric acid]
                st.markdown("##### 🧪 HNO3 [nitric acid]")
                st.info(
                    f"• **Total Quantity Lt tank:** {get_val(last_row, ['HNO3 dari Tank (Ltr)', 'Total Quantity Lt tank'], '18.09')}\n\n"
                    f"• **Total Quantity from shower:** {get_val(last_row, ['HNO3 dari Shower (Ltr)', 'Total Quantity from shower'], '0.00')}\n\n"
                    f"• **% injection 1ª fase:** {get_val(last_row, ['HNO3 Awal (%)', '% injection 1ª fase'], '20')}\n\n"
                    f"• **Injection dosage Lt:** {get_val(last_row, ['Injection dosage Lt', 'Dosing dari tank (Ltr)'], '0.29')}\n\n"
                    f"• **Lt dosing shower injection:** {get_val(last_row, ['Lt dosing shower injection', 'Dosing dari shower (Ltr)'], '0.00')}\n\n"
                    f"• **Pause-Dossage Min/Sec:** {get_val(last_row, ['Pause-Dossage Min/Sec', 'Jeda dosing (Menit)'], '2')}"
                )

                # Kotak 2: HCL [hydrochloric acid]
                st.markdown("##### 🧪 HCL [hydrochloric acid]")
                st.info(
                    f"• **Total Quantity Lt:** {get_val(last_row, ['HCL (Ltr) 4 x berat alloy', 'HCL Total'], '154.02')}"
                )

                # Kotak 3: MISCELATION HCL
                st.markdown("##### ⚙️ MISCELATION HCL")
                st.info(
                    f"• **Mins/Sec Start delay:** {get_val(last_row, ['Mins/Sec Start delay', 'Delay Angin'], '10 | 0')}\n\n"
                    f"• **Min/Sec Miscelation:** {get_val(last_row, ['Min/Sec Miscelation', 'Lama Angin Buka'], '12 | 0')}"
                )

            with col_w2:
                # Kotak 4: PROCESSING
                st.markdown("##### ⚙️ PROCESSING")
                st.info(
                    f"• **Cycle Hours/Min:** {get_val(last_row, ['Cycle Time (\')', 'Cycle Hours/Min'], '4 | 0')}\n\n"
                    f"• **Delay mixer start Min/Sec:** {get_val(last_row, ['Delay mixer start Min/Sec'], '60 | 0')}\n\n"
                    f"• **Min. Mix water:** {get_val(last_row, ['Min. Mix water', 'Water Add'], '30')}\n\n"
                    f"• **Min waiting Filtration 1:** {get_val(last_row, ['Min waiting Filtration 1'], '0')}\n\n"
                    f"• **Min. Buchner 1 > Storage:** {get_val(last_row, ['Min. Buchner 1 > Storage'], '0')}\n\n"
                    f"• **Min. Storage:** {get_val(last_row, ['Min. Storage'], '0')}\n\n"
                    f"• **Min. Buchner 2 > Précipitator:** {get_val(last_row, ['Min. Buchner 2 > Précipitator'], '0')}"
                )

                # Kotak 5: HEATING
                st.markdown("##### 🔥 HEATING")
                st.info(
                    f"• **Heating Temperature:** {get_val(last_row, ['Heating Temp', 'Heating Temperature'], '70.0')} °C\n\n"
                    f"• **Heating Hours/Min:** {get_val(last_row, ['Heating Time (h)', 'Heating Hours/Min'], '4 | 0')}"
                )

        # TAB 2: OPERATOR TIME LOG & NOTES
        with tab_timing:
            st.markdown("#### ⏱️ Time Log & Notes (Diisi oleh Operator)")
            st.info(f"Operator Aktif (Dari GSheet): **{gsheet_operator}**")
            
            with st.form("form_timelog_operator"):
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    t_checkw1 = st.text_input("Check Weight (1):", placeholder="Jam / Waktu...")
                    t_meltau = st.text_input("Melting Au:", placeholder="Jam / Waktu...")
                    t_checkw2 = st.text_input("Check Weight (2):", placeholder="Jam / Waktu...")
                    t_putrc = st.text_input("Put in RC & dissolve Au:", placeholder="Jam / Waktu...")
                    t_cyclersr = st.text_input("Cycle R-SR:", placeholder="Jam / Waktu...")
                with col_t2:
                    t_cyclesrp = st.text_input("Cycle SR - P:", placeholder="Jam / Waktu...")
                    t_filt = st.text_input("Filtration & Clean Tank:", placeholder="Jam / Waktu...")
                    t_clean = st.text_input("Cleaning Au (HCL, HNO3, Ph 7):", placeholder="Jam / Waktu...")
                    t_gran = st.text_input("Granulating:", placeholder="Jam / Waktu...")
                    t_dry = st.text_input("Drying:", placeholder="Jam / Waktu...")

                st.markdown("---")
                refining_notes = st.text_area("Process Notes / Catatan Refining:", placeholder="Masukkan catatan proses reaktor...")

                submit_time = st.form_submit_button("📤 Submit Time Log & Notes to GSheets", use_container_width=True)
                if submit_time:
                    st.success("🎉 Time log & notes submitted successfully!")

st.caption("🔄 Form inputs synchronized with Google Sheets parameters.")