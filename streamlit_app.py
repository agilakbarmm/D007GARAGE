import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="D007Garage Maintenance Tracker", layout="centered")

# File CSV untuk menyimpan data
CSV_FILE = "riwayat_maintenance.csv"

# Inisialisasi file jika belum ada
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Tanggal", "Komponen", "KM", "Catatan"])
    df_init.to_csv(CSV_FILE, index=False)

st.title("D007Garage Maintenance Tracker")
st.subheader("Tambah Data Maintenance")

# Form input
with st.form("form_maintenance"):
    tanggal = st.date_input("Tanggal Penggantian", value=datetime.today())
    komponen_list = [
        "Oli Mesin", "Oli Gardan", "Roller", "Vbelt", "Kampas Ganda",
        "Busi", "Aki", "Per CVT", "Per Kampas Ganda"
    ]
    komponen = st.multiselect("Komponen", komponen_list)
    km = st.number_input("KM Saat Ini", min_value=0, step=100)
    catatan = st.text_area("Catatan Tambahan", placeholder="Opsional")

    submit = st.form_submit_button("Simpan Data")

if submit and komponen:
    df = pd.read_csv(CSV_FILE)
    for item in komponen:
        new_data = pd.DataFrame([[tanggal, item, km, catatan]], columns=["Tanggal", "Komponen", "KM", "Catatan"])
        df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    st.success("Data berhasil disimpan.")

st.subheader("Riwayat Maintenance")

# Load dan tampilkan data
df = pd.read_csv(CSV_FILE)

if not df.empty:
    for idx, row in df.iterrows():
        with st.expander(f"{row['Tanggal']} - {row['Komponen']} (KM: {row['KM']})"):
            st.markdown(f"**Catatan:** {row['Catatan']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Edit", key=f"edit_{idx}"):
                    st.session_state["edit_index"] = idx
            with col2:
                if st.button("Hapus", key=f"hapus_{idx}"):
                    df.drop(index=idx, inplace=True)
                    df.to_csv(CSV_FILE, index=False)
                    st.success("Data berhasil dihapus.")
                    st.experimental_rerun()

# Edit data
if "edit_index" in st.session_state:
    idx = st.session_state["edit_index"]
    row = df.iloc[idx]
    st.subheader("Edit Data Maintenance")
    with st.form("edit_form"):
        tanggal_edit = st.date_input("Tanggal", value=pd.to_datetime(row["Tanggal"]))
        komponen_edit = st.selectbox("Komponen", komponen_list, index=komponen_list.index(row["Komponen"]))
        km_edit = st.number_input("KM", value=int(row["KM"]), step=100)
        catatan_edit = st.text_area("Catatan", value=row["Catatan"])
        update = st.form_submit_button("Update Data")

    if update:
        df.at[idx, "Tanggal"] = tanggal_edit
        df.at[idx, "Komponen"] = komponen_edit
        df.at[idx, "KM"] = km_edit
        df.at[idx, "Catatan"] = catatan_edit
        df.to_csv(CSV_FILE, index=False)
        st.success("Data berhasil diperbarui.")
        del st.session_state["edit_index"]
        st.experimental_rerun()
