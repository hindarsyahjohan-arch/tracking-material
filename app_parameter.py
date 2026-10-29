import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Lembar Kerja & Parameter Reaktor - Refining",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧪 Lembar Kerja Digital: Refining & Parameter Reaktor 1")
st.caption("Monitoring Parameter Proses Kimia, Neraca Massa, dan Kontrol Operasional")
st.divider()

# ==============================================================================
# HEADER DATA BATCH & OPERATOR
# ==============================================================================
st.markdown("### 📌 Header Batch Produksi")

col_h1, col_h2, col_h3, col_h4 = st.columns(4)
with col_h1:
    st.metric("Kode Produksi", "YT170926 -8")
with col_h2:
    st.metric("Tanggal Proses", "2026-09-17")
with col_h3:
    st.metric("Operator Utama", "Riski & Mahmud")
with col_h4:
    st.metric("Status Reaktor", "Berjalan Normal 🟢")

st.divider()

# ==============================================================================
# TABS INTERAKTIF UNTUK KATEGORI DATA
# ==============================================================================
tab1, tab2, tab3 = st.columns([1, 1, 1])

tab_neraca, tab_reaktor, tab_timeline = st.tabs([
    "⚖️ Neraca Massa & Material Balance", 
    "⚙️ Parameter Kimia & Reaktor 1", 
    "⏱️ Timeline & Log Operasional"
])

# ------------------------------------------------------------------------------
# TAB 1: NERACA MASSA
# ------------------------------------------------------------------------------
with tab_neraca:
    st.markdown("#### 📊 Ringkasan Material Balance (Gram)")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Weight In (Awal)", "40,544.72 g")
    col_m2.metric("Purity Alloy", "99.107 %")
    col_m3.metric("Estimasi 99.99 (Au)", "40,182.64 g")
    col_m4.metric("Total Loss (Banting)", "0.51 g", delta="-0.001 %", delta_color="inverse")

    st.markdown("---")
    st.markdown("#### 📋 Detail Tahapan Banting & Refining")
    
    df_neraca = pd.DataFrame({
        "Tahapan Proses": ["Banting / Preparasi", "Refining Process"],
        "Kode Produksi": ["YT170926 -8", "YT170926 -8"],
        "Weight In (g)": [40544.72, 40543.32],
        "Weight Out (g)": [40543.32, 40182.64],
        "Sample (g)": [0.89, 0.00],
        "Loss (g)": [0.51, 0.00],
        "Operator": ["Nico & Riski", "Riski & Mahmud"]
    })
    
    st.dataframe(df_neraca, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# TAB 2: PARAMETER REAKTOR 1
# ------------------------------------------------------------------------------
with tab_reaktor:
    st.markdown("#### ⚗️ Parameter Larutan Kimia & Dosing Sodium")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    
    with col_r1:
        st.info("**🧪 Penggunaan Asam & Reagen**")
        st.write("• **HNO3 Tank:** 18.30 Ltr (0.47)")
        st.write("• **HNO3 Shower:** 6.46 Ltr")
        st.write("• **HCL (4x Alloy):** 183.24 Ltr")
        st.write("• **Total Aquaregia:** 208.00 Ltr")
        st.write("• **Penambahan Water:** 208.00 Ltr")
        st.write("**Total Volume Cairan:** `416.00 Ltr`")

    with col_r2:
        st.warning("**🔥 Pemanasan & Dosing Sodium**")
        st.write("• **Total Sodium:** 20.61 Kg (103.07 Ltr)")
        st.write("• **Dosing Tahap 1:** 0.57 Ltr (Durasi: 45 mnt)")
        st.write("• **Dosing Tahap 2:** 0.57 Ltr (Durasi: 45 mnt)")
        st.write("• **Heating Temp:** 70 °C")
        st.write("• **Heating Time:** 3 Jam")
        st.write("• **Jeda Mixer:** 60 Menit")

    with col_r3:
        st.success("**💨 Kontrol Udara & Siklus Reaktor**")
        st.write("• **Delay Angin:** 10 Menit")
        st.write("• **Lama Angin Buka:** 15 Menit")
        st.write("• **Delay Oxygen:** 10 Menit")
        st.write("• **Injection / Pause:** 20 Detik / 10 Menit")
        st.write("• **Cycle Time Total:** 600 Menit (10 Jam)")
        st.write("• **Lama Proses:** 3 Jam")

# ------------------------------------------------------------------------------
# TAB 3: TIMELINE & LOG WAKTU
# ------------------------------------------------------------------------------
with tab_timeline:
    st.markdown("#### ⏳ Log Jadwal & Tahapan Pekerjaan Lapangan")
    
    timeline_data = [
        {"Waktu / Jam": "10:32 - 10:45", "Aktivitas / Langkah SOP": "Check Weight Material Awal", "Penanggung Jawab": "Nico"},
        {"Waktu / Jam": "11:50 - 13:50", "Aktivitas / Langkah SOP": "Melting Au (Peleburan Alloy)", "Penanggung Jawab": "Riski"},
        {"Waktu / Jam": "13:54 - 14:17", "Aktivitas / Langkah SOP": "Check Weight Hasil Banting", "Penanggung Jawab": "Riski"},
        {"Waktu / Jam": "Proses Reaktor", "Aktivitas / Langkah SOP": "Put in RC & Dissolve Au (Pelarutan Aquaregia)", "Penanggung Jawab": "Riski & Mahmud"},
        {"Waktu / Jam": "Proses Reaktor", "Aktivitas / Langkah SOP": "Cycle R-SR & SR-P (Reduksi & Pengendapan)", "Penanggung Jawab": "Riski & Mahmud"},
        {"Waktu / Jam": "Tahap Akhir", "Aktivitas / Langkah SOP": "Filtration & Cleaning Au (HCL, HNO3, Hot Water pH 7)", "Penanggung Jawab": "Mahmud"},
        {"Waktu / Jam": "Tahap Akhir", "Aktivitas / Langkah SOP": "Granulating & Drying (Pengeringan Bubuk)", "Penanggung Jawab": "Mahmud"}
    ]
    
    st.table(timeline_data)

st.divider()

# ==============================================================================
# CATATAN KENDALA & AKSbottom
# ==============================================================================
st.markdown("### 📝 Catatan Operasional & Verifikasi QC")
catatan = st.text_area(
    "Catatan Khusus Lapangan / Abnormalitas Reaktor:",
    value="Proses reduksi berjalan lancar. Pembilasan air panas hingga pH 7 tercapai sempurna.",
    height=100
)

if st.button("💾 Simpan & Perbarui Parameter", use_container_width=True):
    st.success("✅ Data Lembar Kerja & Parameter Reaktor berhasil diperbarui!")