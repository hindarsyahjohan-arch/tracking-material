import streamlit as st
import pandas as pd
from datetime import datetime
import io
import requests
import time

st.set_page_config(page_title="Admin Panel - Material Tracking", layout="wide")

# ==============================================================================
# ⚠️ PENTING: TEMPELKAN LINK EDIT/SHARE ASLI DARI GOOGLE SHEETS PRIBADI ANDA DI SINI
# ==============================================================================
URL_ASLI_SHEET = "https://docs.google.com/spreadsheets/d/1haDJKJFD_o4tOwXSE4kw4wXHjnfM9UCo3LwQXztrWLk/edit?usp=sharing"

PROCESS_LIST = [
    "1. Material Receiving",
    "2. Gold Leaf Making",
    "3. Aquaregia Process",
    "4. Reduction Aquaregia",
    "5. Au Sponge Cleaning",
    "6. Granulating",
    "7. ICP Testing",
    "8. Cast Bar Making"
]

def load_data():
    try:
        if "/edit" in URL_ASLI_SHEET:
            base_url = URL_ASLI_SHEET.split("/edit")[0]
        else:
            base_url = URL_ASLI_SHEET
            
        # Trik bypass cache paksa real-time (0 detik delay)
        url_realtime = f"{base_url}/export?format=csv&t={int(time.time())}"
        
        response = requests.get(url_realtime, timeout=10)
        
        if "html" in response.headers.get('Content-Type', '').lower() or "<!doctype html>" in response.text.lower():
            st.error("🔒 Akses Google Sheets Terkunci. Pastikan setelan berbagi sudah diubah menjadi 'Anyone with the link'.")
            return pd.DataFrame()
            
        raw_data = io.StringIO(response.text)
        data = pd.read_csv(raw_data, on_bad_lines='skip')
        
        # Bersihkan spasi gaib di nama kolom
        data.columns = [str(col).strip() for col in data.columns]
        
        # Sinkronisasi nama kolom (Anti-Typo)
        rename_dict = {
            'Material Id': 'Material ID',
            'Weight': 'Weight (gr)',
            'Check-In Time': 'Check-In Time',
            'Last Update Time': 'Last Update Time'
        }
        data = data.rename(columns=rename_dict)
        
        if 'Material ID' in data.columns:
            data = data.dropna(subset=['Material ID'])
            # Bersihkan spasi gaib di dalam isi data kolom Material ID dan Current Process
            data['Material ID'] = data['Material ID'].astype(str).str.strip()
            if 'Current Process' in data.columns:
                data['Current Process'] = data['Current Process'].astype(str).str.strip()
            
        return data
    except Exception as e:
        st.error(f"⚠️ Deteksi Masalah Sinkronisasi: {e}")
        return pd.DataFrame()

st.title("📝 Admin Panel & Process Guide (PORT: 8501)")
st.markdown("Halaman pantau antrean khusus Admin. Silakan lakukan perubahan data langsung pada file Google Sheets Anda.")
st.divider()

# Memuat data terbaru dari Google Sheets
df_admin = load_data()

# Menu Navigasi Admin
action = st.radio("Pilih Menu Admin:", ["Lihat Status Antrean", "Panduan Update Proses"], horizontal=True)
st.divider()

if action == "Lihat Status Antrean":
    st.subheader("🗄️ Data Aktif yang Terbaca di Google Sheets")
    if df_admin.empty:
        st.info("Menunggu data dari Google Sheets...")
    else:
        st.dataframe(df_admin, use_container_width=True, hide_index=True)

elif action == "Panduan Update Proses":
    st.subheader("🔄 Alat Bantu Navigasi Alur Proses Produksi")
    
    if df_admin.empty or 'Current Process' not in df_admin.columns:
        st.warning("Belum ada data material aktif atau kolom 'Current Process' tidak ditemukan di Google Sheets.")
    else:
        # Dropdown pilihan Material ID
        id_list = df_admin['Material ID'].unique()
        id_update = st.selectbox("Pilih Material ID yang Ingin Anda Cek:", id_list)
        
        # Mengambil status proses saat ini untuk ID yang dipilih
        current_process = df_admin.loc[df_admin['Material ID'] == id_update, 'Current Process'].values[0]
        
        st.info(f"📍 Posisi Aktual untuk Material **{id_update}** saat ini berada di tahap: **{current_process}**")
        
        # Validasi pencocokan dengan daftar 8 proses utama sistem
        if current_process in PROCESS_LIST:
            current_index = PROCESS_LIST.index(current_process)
            
            # Jika belum mencapai tahap akhir (Cast Bar)
            if current_index < len(PROCESS_LIST) - 1:
                next_process = PROCESS_LIST[current_index + 1]
                st.markdown(f"""
                ### 📋 Langkah Selanjutnya untuk Admin:
                1. Buka file **Google Sheets** Anda.
                2. Cari baris dengan Material ID **{id_update}**.
                3. Ubah kolom *Current Process* dari `{current_process}` menjadi:
                   👉 **`{next_process}`**
                4. Jangan lupa perbarui juga kolom *Last Update Time* di Google Sheets dengan jam saat ini.
                """)
            else:
                st.success("🏆 Sukses! Material ini telah mencapai tahap final produksi (8. Cast Bar Making - Completed).")
        else:
            st.error(f"❌ Teks proses `{current_process}` di Google Sheets Anda tidak cocok dengan daftar standar sistem.")
            st.info("💡 **Solusi:** Pastikan penulisan proses di Google Sheets sama persis dengan daftar berikut (perhatikan angka, titik, dan spasi):\n"
                    f"`{', '.join(PROCESS_LIST)}`")
