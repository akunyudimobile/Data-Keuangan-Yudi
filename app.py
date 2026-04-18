import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
import json

# Setup Halaman
st.set_page_config(page_title="Finance Tracker Pro", layout="wide")

# Konfigurasi Akses Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

def get_google_sheet():
    # Pastikan di Streamlit Cloud -> Settings -> Secrets diisi key: gcp_service_account
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1Ig-coNVWo1F-1JsCTalmnp0qLcLiR28-D5yN4fxkduk")
    return sheet

# Navigasi Sidebar dengan Ikon
st.sidebar.title("Navigasi")
menu = ["📊 Dashboard", "➕ Input Transaksi", "📋 Manajemen Kewajiban"]
choice = st.sidebar.selectbox("Pilih Menu", menu)

st.title("💰 Aplikasi Keuangan Pribadi")

try:
    sheet = get_google_sheet()
    
    # 1. Dashboard
    if choice == "📊 Dashboard":
        st.subheader("Ringkasan Keuangan")
        df_transaksi = pd.DataFrame(sheet.worksheet("Transaksi").get_all_records())
        
        if not df_transaksi.empty:
            total_masuk = df_transaksi[df_transaksi['Tipe'] == 'Pemasukan']['Nominal'].sum()
            total_keluar = df_transaksi[df_transaksi['Tipe'] == 'Pengeluaran']['Nominal'].sum()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Pemasukan", f"Rp {total_masuk:,}")
            col2.metric("Total Pengeluaran", f"Rp {total_keluar:,}")
            col3.metric("Saldo Bersih", f"Rp {total_masuk - total_keluar:,}")
            
            st.markdown("---")
            # Grafik Distribusi
            fig = px.pie(df_transaksi, values='Nominal', names='Kategori', title='Distribusi Pengeluaran')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data transaksi yang tercatat.")

    # 2. Input Transaksi
    elif choice == "➕ Input Transaksi":
        st.subheader("Tambah Transaksi Baru")
        with st.form("form_transaksi", clear_on_submit=True):
            tanggal = st.date_input("Tanggal")
            kategori = st.text_input("Kategori (Contoh: Makan, Transport, Gaji)")
            tipe = st.selectbox("Tipe", ["Pemasukan", "Pengeluaran"])
            nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
            keterangan = st.text_area("Keterangan")
            submit = st.form_submit_button("Simpan Data")
            
            if submit:
                if kategori:
                    sheet.worksheet("Transaksi").append_row(["", str(tanggal), kategori, tipe, nominal, keterangan])
                    st.success("Data berhasil disimpan ke Google Sheets!")
                else:
                    st.error("Kategori tidak boleh kosong.")

    # 3. Manajemen Kewajiban
    elif choice == "📋 Manajemen Kewajiban":
        st.subheader("Daftar Kewajiban & Tagihan")
        df_kewajiban = pd.DataFrame(sheet.worksheet("Kewajiban").get_all_records())
        if not df_kewajiban.empty:
            st.dataframe(df_kewajiban, use_container_width=True)
        else:
            st.info("Tidak ada kewajiban saat ini.")

except Exception as e:
    st.error("Terjadi kesalahan koneksi ke database.")
    st.expander("Detail Error").write(str(e))
    st.info("Pastikan 'gcp_service_account' sudah terisi dengan benar di Streamlit Secrets.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: grey;'>Finance Tracker Pro | Dikelola secara Cloud</p>", unsafe_allow_html=True)
