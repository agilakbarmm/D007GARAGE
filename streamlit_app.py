import streamlit as st
from datetime import datetime
import pandas as pd
import os

st.set_page_config(
    page_title="D007Garage Maintenance Tracker",
    page_icon="🛠️",
    layout="centered"
)

# Judul Aplikasi
st.markdown(
    """
    <div style="text-align:center;">
        <h1 style="font-size:2.5em; margin-bottom:0;">D007Garage</h1>
        <h2 style="font-size:1.5em; margin-top:0;">Maintenance Tracker</h2>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("### Tambah Data Maintenance")

# Input Form
with st.form("form_input"):
    tanggal = st.date_input("Tanggal Penggantian", value=datetime.today())
    komponen = st.selectbox("Komponen", ["Oli Mesin", "Kampas Rem", "Busi", "Ban", "Aki", "Filter Udara", "Rantai", "Lainnya"])
    km_saat_ini = st.number_input("KM Saat Ini", min_value=0, step=100)
    catatan = st.text_area("Catatan Tambahan", placeholder="Opsional")

    submitted = st.form_submit_button("Simpan Data")

# Simpan ke file CSV
file_path = "data_maintenance.csv"

if submitted:
    new_data = {
        "Tanggal": tanggal.strftime("%Y-%m-%d"),
        "Komponen": komponen,
        "KM": km_saat_ini,
        "Catatan": catatan
    }

    if os.path.exists(file_path):
        df_lama = pd.read_csv(file_path)
        df_baru = pd.DataFrame([new_data])
        df = pd.concat([df_lama, df_baru], ignore_index=True)
    else:
        df = pd.DataFrame([new_data])

    df.to_csv(file_path, index=False)
    st.success("Data berhasil disimpan!")

# Menampilkan Data Maintenance
st.markdown("### Riwayat Maintenance")
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.dataframe(df)
else:
    st.info("Belum ada data maintenance.")
