import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

st.set_page_config(
    page_title="Operator Checklist - Produksi Emas", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Tempelkan Web App URL dari Google Apps Script Anda
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzFdETw5CLY6NvqzeH8U1x8bTnWCaGOQpzGY8idhVJNXLoj4egNc9wvC7vpQzOBloEr/exec"

st.title("🛠️ Form Checklist Operator Produksi")

# ==============================================================================
# 1. PILIHAN TAHAPAN PROSES PRODUKSI
# ==============================================================================
pilihan_proses = st.selectbox(
    "Pilih Tahapan / Proses Produksi:",
    [
        "1. Proses Banting (Melting Centrifugal)[cite: 3]",
        "2. Proses Aquaregia Dalam Reaktor[cite: 4]",
        "3. Proses Pemindahan Ke Tangki Reduksi[cite: 8]",
        "4. Proses Filter Emas & Reduksi Kimia[cite: 5]",
        "5. Proses Pembuatan Granul Emas[cite: 6]",
        "6. Proses Pembuatan Emas Batangan[cite: 7]"
    ]
)

st.divider()

# ==============================================================================
# 2. KONFIGURASI K3 & DAFTAR CHECKLIST BERDASARKAN PROSES
# ==============================================================================
CHECKLIST_ITEMS = []

if "Proses Banting" in pilihan_proses:
    st.subheader("Proses: Banting (Melting Centrifugal)")
    st.warning("""
    ⚠️ **PERINGATAN K3:**  
    Dilarang keras melakukan pengurasan / membuka pintu chamber jika suhu di dalam reaktor/chamber di atas **370°C**![cite: 3]
    """)
    CHECKLIST_ITEMS = [
        "1. Cek kebersihan lubang center piece (Bebas dari kerak)",
        "2. Kondisi kerapatan Chamber Bawah (Sudah terkunci & tertutup rapat)",
        "3. Kondisi kerapatan Chamber Melting (Sudah terkunci & tertutup rapat)",
        "4. Sistem sirkulasi water chiller (Berjalan lancar, selang tidak tertekuk)",
        "5. Kelayakan fisik crucible wadah lebur (Tidak retak / tidak menipis)",
        "6. Kelayakan fisik penutup stopper lebur (Fungsi mekanis normal)",
        "7. Uji putaran centrifugal (Berputar simetris pada rasio 55%)",
        "8. Indikator Suhu Air Chiller awal (standar target 25°C)",
        "9. Kondisi vakum udara awal (Durasi tarikan awal stabil selama 30 detik)",
        "10. Aliran pasokan gas Nitrogen awal (Tekanan normal selama 30 detik)",
        "11. Pencapaian target suhu Melting lebur awal (Mencapai batas 1050°C)",
        "12. Penurunan & penahanan suhu penuangan Pouring (Stabil di angka 970°C)",
        "13. Perubahan bukaan gas Nitrogen cooling cepat (Pindah dari 6 bar ke 10 bar)",
        "14. Batas ambang suhu aman pengurasan ruang mesin (Turun mencapai 370°C)"
    ]

elif "Proses Aquaregia Dalam Reaktor" in pilihan_proses:
    st.subheader("Proses: Aquaregia Dalam Reaktor")
    st.warning("""
    ⚠️ **PERINGATAN KESELAMATAN (K3):**  
    Wajib menggunakan APD lengkap pelindung asam dan gas (**Respirator, Sarung Tangan Kimia, Goggles**) selama proses operasional reaktor berlangsung![cite: 4]
    """)
    CHECKLIST_ITEMS = [
        "1. Memeriksa kebocoran chamber reaktor",
        "2. Memeriksa ketersediaan stok HNO3 dan HCL",
        "3. Memeriksa stok air demin",
        "4. Memeriksa fungsi unit water chiller",
        "5. Memastikan posisi aspirator pada level LOW",
        "6. Memeriksa fungsi angin miscelation HCL",
        "7. Memeriksa kalibrasi flowmeter hcl & hno3",
        "8. Memeriksa fungsi pasokan gas oksigen",
        "9. Memasukkan material bantingan ke dalam barrel",
        "10. Mengunci rapat penutup reaktor 1 dan reaktor 2",
        "11. Menginput parameter operasional pada panel",
        "12. Menjalankan siklus mesin (Siklus 10 jam / < 40°C)"
    ]

elif "Proses Pemindahan Ke Tangki Reduksi" in pilihan_proses:
    st.subheader("Proses: Pemindahan Ke Tangki Reduksi")
    st.warning("""
    ⚠️ **PERINGATAN KESELAMATAN (K3):**  
    Wajib cek kebocoran valve SR & Reduksi sebelum menyalakan pompa. Gunakan safety goggles dan apron asam![cite: 8]
    """)
    CHECKLIST_ITEMS = [
        "1. [PRA] Memeriksa kondisi filter (TIDAK TERSUMBAT)",
        "2. [PRA] Memeriksa kondisi fisik Tangki SR (TIDAK BOCOR)",
        "3. [PRA] Memeriksa kondisi fisik Tangki Reduksi (TIDAK BOCOR)",
        "4. Menyalakan pompa SR & mengatur tekanan angin ke 2 - 2.5 bar",
        "5. Membuka valve reaktor hingga seluruh cairan pindah ke SR",
        "6. Mematikan pompa SR setelah cairan dipastikan terpindah semua",
        "7. Menyalakan pompa chamber AGCL & buka valve arah tangki SR",
        "8. Membuka tutup reaktor atas secara hati-hati",
        "9. Menutup valve filter & memasukkan air demin 10 Liter (rasio 1:1)",
        "10. Mendiamkan cairan untuk proses pengendapan selama 2 - 4 jam",
        "11. Menyalakan damper aspirator & merubah level ke posisi MEDIUM",
        "12. Membersihkan bagian dalam reaktor menggunakan air demin",
        "13. Menutup valve reaktor bawah & membersihkan sisa AR di AGCL",
        "14. Mematikan pompa, menutup valve SR & tambah air demin sesuai rasio",
        "15. Menyalakan pompa reduksi, buka valve filter, pindah cairan ke tank",
        "16. Membersihkan tangki SR & filter reduksi dengan air demin, matikan pompa"
    ]

elif "Proses Filter Emas & Reduksi Kimia" in pilihan_proses:
    st.subheader("Proses: Filter Emas & Reduksi Kimia")
    st.warning("""
    ⚠️ **PERINGATAN K3:**  
    Gas **NOX** sangat beracun dan korosif! Pastikan **bukaan damper tepat di Posisi 3** dan **sistem aspirator hisap berfungsi penuh** sebelum proses reduksi dimulai[cite: 5].
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

elif "Proses Pembuatan Granul Emas" in pilihan_proses:
    st.subheader("Proses: Pembuatan Granul Emas")
    st.warning("""
    ⚠️ **PANDUAN KESELAMATAN (K3):**  
    BAHAYA OPERASIONAL SUHU TINGGI (**700°C - 900°C**)! Wajib gunakan sarung tangan anti-panas dan *face shield* saat menuang logam[cite: 6].
    """)
    CHECKLIST_ITEMS = [
        "1. Memeriksa kesiapan dan aliran air chiller (Normal/Tidak Tersumbat)",
        "2. Memeriksa pasokan air chamber melting dalam kondisi siap pakai",
        "3. Memastikan wadah crucible bersih total dari sisa material logam",
        "4. Menyiapkan baskom ukuran besar dan 4 baskom kecil non-logam",
        "5. Menyiapkan lembaran kertas pelapis untuk wadah stainless oven",
        "6. Memindahkan bubuk coklat ke wadah kecil non-logam secara hati-hati",
        "7. Menyalakan unit heating mesin peleburan",
        "8. Memasukkan bubuk coklat ke chamber atas perlahan (tidak penuh)",
        "9. Menaikkan suhu bertahap dari 700°C s/d 900°C (interval 5-10°C)",
        "10. Menutup chamber atas setelah bubukan habis dan menunggu sampai cair",
        "11. Membuka tuas stopper dan memastikan seluruh cairan turun habis",
        "12. Menguras dan membersihkan air pada unit chamber melting",
        "13. Membagi granul basah ke 4 baskom kecil non-logam & mengelapnya",
        "14. Mengoven granul pada suhu 100°C - 150°C selama 1.5 - 2 jam",
        "15. Meniriskan granul selama 30 - 50 menit hingga siap ditimbang"
    ]

elif "Proses Pembuatan Emas Batangan" in pilihan_proses:
    st.subheader("Proses: Pembuatan Emas Batangan")
    st.warning("""
    ⚠️ **PERINGATAN KESELAMATAN (K3):**  
    BAHAYA SUHU TINGGI DAN LOGAM CAIR! Wajib mengenakan pakaian pelindung panas penuh (*Aluminized Suit*), sarung tangan tahan panas tinggi, dan *face shield*[cite: 7].
    """)
    CHECKLIST_ITEMS = [
        "1. Memastikan timbangan analitik dalam kondisi bersih dan terkalibrasi harian",
        "2. Menakar granul emas sesuai dengan varian berat pesanan (100g, 1kg, dll)",
        "3. Memastikan kondisi molding/cetakan bersih dan bebas dari sisa kerak logam",
        "4. Memeriksa dan mengatur Inner plate temp. set-point tepat pada suhu 73 °C",
        "5. Memeriksa dan mengatur Outer plate temp. set point tepat pada suhu 80 °C",
        "6. Mengonfigurasi parameter Set-point VMF converter ke nilai standar 92 %",
        "7. Memantau batasan toleransi Max opening inner plate tidak melebihi 19 %",
        "8. Memantau batasan toleransi Max opening outer plate tidak melebihi 17 %",
        "9. Menjalankan siklus pemanasan dengan target Melting time selama 480 – 500 s",
        "10. Menuangkan cairan emas murni ke cetakan, dinginkan, dan timbang berat akhir"
    ]

# ==============================================================================
# 3. FORM INPUT OPERATOR
# ==============================================================================
with st.form("form_checklist_operator"):
    st.markdown("### 📋 Header Data Operasional")
    
    col1, col2 = st.columns(2)
    with col1:
        tanggal_shift = st.date_input("Tanggal Work Order:", datetime.now())
        shift = st.selectbox("Pilih Shift Kerja:", ["Shift 1 (Pagi)", "Shift 2 (Sore)", "Shift 3 (Malam)"])
        nama_operator = st.text_input("Nama Operator:", placeholder="Masukkan nama Anda...")
        
    with col2:
        nomor_batch = st.text_input("Nomor Batch Material:", placeholder="Contoh: BATCH-2026-001")
        kode_mesin = st.text_input("Kode Mesin / Stasiun:", placeholder="Contoh: MCN-01 / Reaktor 1")
        verifikator_qc = st.text_input("Nama Verifikator / QC Lapangan:", placeholder="Nama QC Shift...")

    st.divider()
    st.markdown("### ⚙️ Butir Pemeriksaan SOP")

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
                key=f"item_{idx}_{pilihan_proses}"
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
                "proses": pilihan_proses,  # Mengirimkan informasi jenis tahapan proses
                "batch": nomor_batch,
                "operator": nama_operator,
                "kode_mesin": kode_mesin,
                "qc_verifikator": verifikator_qc,
                "status_akhir": status_akhir,
                "catatan": catatan_kendala
            }

            try:
                response = requests.post(WEBHOOK_URL, json=payload)
                if response.status_code == 200 and response.json().get("result") == "success":
                    st.success("🎉 **Data Checklist Operator Berhasil Disimpan ke Google Sheets!**")
                    st.balloons()
                else:
                    st.error(f"❌ Gagal menyimpan ke Google Sheets. Respon server: {response.text}")
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan koneksi: {e}")