import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Scoopy Maintenance Tracker", layout="wide")
st.title("Scoopy Maintenance Tracker")

# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Tanggal", "Komponen", "KM Sekarang", "Interval KM", "KM Selanjutnya", "Catatan"])

st.sidebar.header("Tambah Data Maintenance")
tanggal = st.sidebar.date_input("Tanggal Penggantian", value=datetime.date.today())
komponen = st.sidebar.selectbox("Komponen", [
    "Oli Mesin", "Oli Gardan", "Busi", "Filter Udara", "V-Belt",
    "Roller CVT", "Kampas Ganda (Clutch)", "Kampas Rem Depan",
    "Kampas Rem Belakang", "Aki"])
km_sekarang = st.sidebar.number_input("KM Saat Ini", min_value=0, step=100)
catatan = st.sidebar.text_input("Catatan Tambahan")

interval_km_map = {
    "Oli Mesin": 2500,
    "Oli Gardan": 8000,
    "Busi": 8000,
    "Filter Udara": 12000,
    "V-Belt": 20000,
    "Roller CVT": 20000,
    "Kampas Ganda (Clutch)": 30000,
    "Kampas Rem Depan": 15000,
    "Kampas Rem Belakang": 15000,
    "Aki": 20000,
}

if st.sidebar.button("Simpan"):
    interval_km = interval_km_map.get(komponen, 0)
    km_selanjutnya = km_sekarang + interval_km
    new_entry = pd.DataFrame({
        "Tanggal": [tanggal],
        "Komponen": [komponen],
        "KM Sekarang": [km_sekarang],
        "Interval KM": [interval_km],
        "KM Selanjutnya": [km_selanjutnya],
        "Catatan": [catatan]
    })
    st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
    st.success("Data berhasil disimpan!")

st.subheader("Riwayat Maintenance")
st.dataframe(st.session_state.data, use_container_width=True)

st.subheader("Reminder Penggantian Komponen")
current_km = st.number_input("Masukkan KM Sekarang untuk Reminder", min_value=0, step=100)
reminder_df = st.session_state.data[st.session_state.data["KM Selanjutnya"] <= current_km + 1000]
if not reminder_df.empty:
    st.warning("Ada komponen yang akan segera diganti atau sudah waktunya!")
    st.dataframe(reminder_df, use_container_width=True)
else:
    st.success("Belum ada komponen yang perlu diganti dalam 1000 KM ke depan.")

st.subheader("Export Data")
if st.download_button("Download sebagai Excel", data=st.session_state.data.to_excel(index=False), file_name="maintenance_scoopy.xlsx"):
    st.success("File berhasil diunduh!")
