import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

st.set_page_config(
    page_title="Operator Checklist - Filter Emas", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Tempelkan Web App URL dari Google Apps Script Langkah 1 di sini
WEBHOOK_URL = https://script.google.com/macros/s/AKfycbzFdETw5CLY6NvqzeH8U1x8bTnWCaGOQpzGY8idhVJNXLoj4egNc9wvC7vpQzOBloEr/exec

st.title("🛠️ Form Checklist Operator Produksi")
st.subheader("Proses: Filter Emas & Reduksi Kimia")

st.warning("""
⚠️ **PERINGATAN K3:**  
Gas **NOX** sangat beracun dan korosif! Pastikan **masker respirator terpasang rapat**, **bukaan damper tepat di Posisi 3**, dan **sistem aspirator hisap berfungsi penuh**.
""")

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

with st.form("form_checklist_operator"):
    st.markdown("### 📋 1. Header Data Operasional")
    
    col1, col2 = st.columns(2)
    with col1:
        tanggal_shift = st.date_input("Tanggal Work Order:", datetime.now())
        shift = st.selectbox("Pilih Shift Kerja:", ["Shift 1 (Pagi)", "Shift 2 (Sore)", "Shift 3 (Malam)"])
        nama_operator = st.text_input("Nama Operator:", placeholder="Masukkan nama Anda...")
        
    with col2:
        nomor_batch = st.text_input("Nomor Batch Material:", placeholder="Contoh: BATCH-2026-001")
        kode_mesin = st.text_input("Kode Mesin / Stasiun:", placeholder="Contoh: MCN-FLT-01")
        verifikator_qc = st.text_input("Nama Verifikator / QC Lapangan:", placeholder="Nama QC Shift...")

    st.divider()
    st.markdown("### ⚙️ 2. Butir Pemeriksaan SOP")

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

    catatan_kendala = st.text_area(
        "Catatan Kendala / Keterangan Tambahan Lapangan:", 
        placeholder="Tuliskan jika ada kendala..."
    )

    submit_button = st.form_submit_button("📤 Submit & Kirim Checklist ke Pusat", use_container_width=True)

    if submit_button:
        if not nama_operator or not nomor_batch or not kode_mesin:
            st.error("❌ **Gagal Kirim:** Nama Operator, Nomor Batch, dan Kode Mesin wajib diisi!")
        else:
            total_rej = sum(1 for val in checklist_results.values() if val == "REJ")
            status_akhir = "NORMAL / PASSED" if total_rej == 0 else f"WARNING ({total_rej} Item REJ)"
            timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            payload = {
                "timestamp": timestamp_now,
                "tanggal": str(tanggal_shift),
                "shift": shift,
                "batch": nomor_batch,
                "operator": nama_operator,
                "kode_mesin": kode_mesin,
                "qc_verifikator": verifikator_qc,
                "status_akhir": status_akhir,
                "catatan": catatan_kendala
            }

            try:
                # Mengirim data ke Google Sheets via Apps Script Web App
                response = requests.post(WEBHOOK_URL, json=payload)
                if response.status_code == 200 and response.json().get("result") == "success":
                    st.success("🎉 **Data Checklist Operator Berhasil Disimpan ke Google Sheets!**")
                    st.balloons()
                else:
                    st.error(f"❌ Gagal menyimpan ke Google Sheets. Respon server: {response.text}")
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan koneksi: {e}")