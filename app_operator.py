import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Operator Checklist - Filter Emas", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# KONFIGURASI KONEKSI GOOGLE SHEETS (GSPREAD)
# ==============================================================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def init_connection():
    try:
        # Menggunakan kredensial dari Streamlit Secrets atau file lokal JSON
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception:
        return None

# ==============================================================================
# HEADER & INFORMASI PROSES (SOP)
# ==============================================================================
st.title("🛠️ Form Checklist Operator Produksi")
st.subheader("Proses: Filter Emas & Reduksi Kimia")
st.caption("Aplikasi Input Lapangan (Tablet Operator Floor)")

# Peringatan Keselamatan Kerja (K3) dari SOP
st.warning("""
⚠️ **PERINGATAN K3 (SANGAT IMPORTANT):**  
Gas **NOX** sangat beracun dan korosif! Pastikan **masker respirator terpasang rapat**, **bukaan damper tepat di Posisi 3**, dan **sistem aspirator hisap berfungsi penuh** sebelum proses reduksi dimulai.
""")

st.divider()

# Daftar 13 Poin Checklist sesuai dokumen SOP
CHECKLIST_ITEMS = [
    "1. Memeriksa kecukupan volume & stok bahan pereduksi SMB (200 grm/ltr)",
    "2. Memastikan posisi bukaan mechanical damper di Posisi 3",
    "3. Mengatur setelan putaran mixer tepat di posisi 3 Step",
    "4. Menginput nilai parameter sodium untuk reaksi tahap pertama",
    "5. Menjalankan (Start) parameter sodium tahap pertama",
    "6. Mengawasi proses reduksi Tahap I hingga keluarnya gas NOX secara aman",
    "7. Menginput nilai parameter sodium untuk reaksi tahap kedua",
    "8. Menjalankan (Start) parameter sodium tahap kedua",
    "9. Memantau perubahan warna cairan aquaregia hingga kuning bening sempurna",
    "10. Melakukan sirkulasi & menambahkan sodium sedikit jika cairan masih keruh",
    "11. Membuka katup valve Tank S (1, 2, 3, 4) yang dialokasikan",
    "12. Menyalakan pompa pendorong utama dan membuka katup valve Tank P (1, 2)",
    "13. Menurunkan & membilas bubuk coklat dengan air demin menggunakan pipa/tongkat"
]

# ==============================================================================
# FORM INPUT OPERATOR
# ==============================================================================
with st.form("form_checklist_operator"):
    st.markdown("### 📋 1. Header Data Operasional")
    
    col1, col2 = st.columns(2)
    with col1:
        tangal_shift = st.date_input("Tanggal Work Order:", datetime.now())
        shift = st.selectbox("Pilih Shift Kerja:", ["Shift 1 (Pagi)", "Shift 2 (Sore)", "Shift 3 (Malam)"])
        nama_operator = st.text_input("Nama Operator:", placeholder="Masukkan nama Anda...")
        
    with col2:
        nomor_batch = st.text_input("Nomor Batch Material:", placeholder="Contoh: BATCH-2026-001")
        kode_mesin = st.text_input("Kode Mesin / Stasiun:", placeholder="Contoh: MCN-FLT-01")
        verifikator_qc = st.text_input("Nama Verifikator / QC Lapangan:", placeholder="Nama QC Shift...")

    st.divider()
    st.markdown("### ⚙️ 2. Butir Pemeriksaan / Langkah SOP")
    st.info("Pilih status kelayakan **[ OK ]** jika sesuai SOP, atau **[ REJ / Reject ]** jika terdapat kendala/abnormalitas.")

    checklist_results = {}
    
    for idx, item_text in enumerate(CHECKLIST_ITEMS, 1):
        c_text, c_status = st.columns([3, 1])
        with c_text:
            st.write(f"**{item_text}**")
        with c_status:
            checklist_results[f"Poin_{idx}"] = st.radio(
                f"Status_{idx}", 
                ["OK", "REJ"], 
                horizontal=True, 
                label_visibility="collapsed",
                key=f"item_{idx}"
            )
        st.markdown("---")

    st.markdown("### 📝 3. Catatan & Status Akhir Operator")
    catatan_kendala = st.text_area(
        "Catatan Kendala / Keterangan Tambahan Lapangan:", 
        placeholder="Tuliskan di sini jika ada penambahan sodium ekstra, tekanan pompa abnormal, atau penyimpangan lainnya..."
    )

    submit_button = st.form_submit_button("📤 Submit & Kirim Checklist ke Pusat", use_container_width=True)

    if submit_button:
        # Validasi Form
        if not nama_operator or not nomor_batch or not kode_mesin:
            st.error("❌ **Gagal Kirim:** Nama Operator, Nomor Batch, dan Kode Mesin wajib diisi!")
        else:
            # Pengecekan apakah ada status REJ
            total_rej = sum(1 for val in checklist_results.values() if val == "REJ")
            status_akhir = "NORMAL / PASSED" if total_rej == 0 else f"WARNING ({total_rej} Item REJ)"

            timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Mengumpulkan data baris
            row_data = [
                timestamp_now,
                str(tangal_shift),
                shift,
                nomor_batch,
                kode_mesin,
                nama_operator,
                verifikator_qc,
                status_akhir,
                catatan_kendala
            ] + list(checklist_results.values())

            # Pengiriman data ke Google Sheets
            client = init_connection()
            if client:
                try:
                    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1haDJKJFD_o4tOwXSE4kw4wXHjnfM9UCo3LwQXztrWLk/edit?usp=sharing"
                    sheet = client.open_by_url(spreadsheet_url).worksheet("Checklist_Log")
                    sheet.append_row(row_data)
                    st.success("✅ **Berhasil:** Data checklist operator telah tersimpan di server pusat Google Sheets!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ **Gagal menyimpan ke Google Sheets:** {e}")
            else:
                # Fallback mode jika Service Account belum dikonfigurasi
                st.success("✅ **[MODE DEMO]** Data berhasil diproses secara lokal!")
                st.json({
                    "Timestamp": timestamp_now,
                    "Batch": nomor_batch,
                    "Operator": nama_operator,
                    "Hasil_Checklist": checklist_results,
                    "Status_Akhir": status_akhir
                })