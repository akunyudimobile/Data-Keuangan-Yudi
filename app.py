import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
import json

# Setup Halaman
st.set_page_config(page_title="Finance Tracker", layout="wide")

# Konfigurasi Akses Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

def get_google_sheet():
    # Mengambil kredensial dari Streamlit Secrets
    # Pastikan di Streamlit Cloud -> Settings -> Secrets diisi key: gcp_service_account
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    client = gspread.authorize(creds)
    # ID Sheet dari link yang Anda berikan
    sheet = client.open_by_key("1Ig-coNVWo1F-1JsCTalmnp0qLcLiR28-D5yN4fxkduk")
    return sheet

# Navigasi Sidebar
menu = ["Dashboard", "Input Transaksi", "Manajemen Kewajiban"]
choice = st.sidebar.selectbox("Menu", menu)

st.title("Aplikasi Keuangan Pribadi")

try:
    sheet = get_google_sheet()
    
    if choice == "Dashboard":
        st.subheader("Ringkasan Keuangan")
        df_transaksi = pd.DataFrame(sheet.worksheet("Transaksi").get_all_records())
        
        if not df_transaksi.empty:
            total_masuk = df_transaksi[df_transaksi['Tipe'] == 'Pemasukan']['Nominal'].sum()
            total_keluar = df_transaksi[df_transaksi['Tipe'] == 'Pengeluaran']['Nominal'].sum()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Pemasukan", f"Rp {total_masuk:,}")
            col2.metric("Total Pengeluaran", f"Rp {total_keluar:,}")
            col3.metric("Saldo", f"Rp {total_masuk - total_keluar:,}")
            
            # Grafik Distribusi
            fig = px.pie(df_transaksi, values='Nominal', names='Kategori', title='Distribusi Pengeluaran')
            st.plotly_chart(fig)
        else:
            st.write("Belum ada data transaksi.")

    elif choice == "Input Transaksi":
        st.subheader("Tambah Transaksi Baru")
        with st.form("form_transaksi"):
            tanggal = st.date_input("Tanggal")
            kategori = st.text_input("Kategori")
            tipe = st.selectbox("Tipe", ["Pemasukan", "Pengeluaran"])
            nominal = st.number_input("Nominal", min_value=0)
            keterangan = st.text_area("Keterangan")
            submit = st.form_submit_button("Simpan")
            
            if submit:
                # Menambahkan baris ke sheet 'Transaksi'
                sheet.worksheet("Transaksi").append_row(["", str(tanggal), kategori, tipe, nominal, keterangan])
                st.success("Data berhasil disimpan!")

    elif choice == "Manajemen Kewajiban":
        st.subheader("Daftar Kewajiban")
        df_kewajiban = pd.DataFrame(sheet.worksheet("Kewajiban").get_all_records())
        st.dataframe(df_kewajiban)

except Exception as e:
    st.error(f"Terjadi kesalahan koneksi: {e}")
    st.info("Pastikan Anda sudah mengatur 'gcp_service_account' di Streamlit Secrets dengan format JSON yang benar.")
