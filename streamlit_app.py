import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.markdown(
    """
    <div style='text-align: center; margin-top: -30px;'>
        <h1 style='font-size: 3em;'>🛠️ 007GARAGE</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# ====== FILE CSV ======
CSV_FILE = "riwayat_maintenance.csv"
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Tanggal", "Komponen", "KM", "Catatan"])
    df_init.to_csv(CSV_FILE, index=False)

st.subheader("Tambah Data Maintenance")

# ====== FORM INPUT ======
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

# ====== SIMPAN DATA ======
if submit and komponen:
    df = pd.read_csv(CSV_FILE)
    for item in komponen:
        new_data = pd.DataFrame([[tanggal, item, km, catatan]], columns=["Tanggal", "Komponen", "KM", "Catatan"])
        df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    st.success("Data berhasil disimpan.")

# ====== RIWAYAT ======
st.subheader("Riwayat Maintenance")
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

# ====== EDIT ======
if "edit_index" in st.session_state:
    idx = st.session_state["edit_index"]
    row = df.iloc[idx]
    st.subheader("Edit Data Maintenance")
    with st.form("edit_form"):
        tanggal_edit = st.date_input("Tanggal", value=pd.to_datetime(row["Tanggal"]))
        komponen_list = [
            "Oli Mesin", "Oli Gardan", "Roller", "Vbelt", "Kampas Ganda",
            "Busi", "Aki", "Per CVT", "Per Kampas Ganda"
        ]
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
        del st.session_state["edit_index"]
        st.success("Data berhasil diperbarui.")
        st.experimental_rerun()
