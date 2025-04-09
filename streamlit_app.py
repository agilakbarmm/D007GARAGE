import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="007Garage", layout="centered")

# Background blur
bg_image_url = "https://images.unsplash.com/photo-1597003758344-937e7cf07074"
page_bg = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background-image: url("{bg_image_url}");
    background-size: cover;
    background-position: center;
    filter: blur(4px);
    position: fixed;
    width: 100%;
    height: 100%;
    z-index: -1;
}}
.blur-bg {{
    background-color: rgba(255,255,255,0.85);
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
}}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# File penyimpanan
CSV_FILE = "riwayat_motor.csv"
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Tanggal", "Komponen", "KM", "Catatan"]).to_csv(CSV_FILE, index=False)

# Komponen & estimasi km
KOMPONEN_KM = {
    "Oli Mesin": 2000,
    "Oli Gardan": 4000,
    "Roller": 8000,
    "Vbelt": 10000,
    "Kampas Ganda": 12000,
    "Busi": 6000,
    "Aki": 12000,
    "Per CVT": 8000,
    "Per Kampas Ganda": 8000
}
KOMPONEN_LIST = list(KOMPONEN_KM.keys())

# ---------------- MAIN APP ---------------- #
st.markdown("<div class='blur-bg'>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>🛠️ 007GARAGE</h1>", unsafe_allow_html=True)

# ===== Tambah Data =====
st.markdown("<h4 style='text-align: center;'>Tambah Data Maintenance</h4>", unsafe_allow_html=True)

with st.form("form_maintenance"):
    tanggal = st.date_input("Tanggal Penggantian", value=datetime.today())
    komponen = st.multiselect("Komponen yang Diganti", KOMPONEN_LIST)
    km = st.number_input("KM Saat Ini", min_value=0, step=100)
    catatan = st.text_area("Catatan Tambahan", placeholder="Opsional")
    simpan = st.form_submit_button("Simpan Data")

if simpan and komponen:
    df = pd.read_csv(CSV_FILE)
    for item in komponen:
        new_row = {
            "Tanggal": tanggal,
            "Komponen": item,
            "KM": km,
            "Catatan": catatan
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    st.success("Data berhasil disimpan.")

# ===== Riwayat & Pencarian =====
st.markdown("### Riwayat Maintenance")
df = pd.read_csv(CSV_FILE)

search = st.text_input("Cari berdasarkan komponen atau catatan...")
if search:
    df = df[df.apply(lambda row: search.lower() in str(row["Komponen"]).lower() or search.lower() in str(row["Catatan"]).lower(), axis=1)]

if df.empty:
    st.info("Belum ada data.")
else:
    for idx, row in df.iterrows():
        est_km = row["KM"] + KOMPONEN_KM.get(row["Komponen"], 2000)
        with st.expander(f"{row['Tanggal']} - {row['Komponen']} (KM: {row['KM']})"):
            st.markdown(f"**Catatan:** {row['Catatan']}")
            st.markdown(f"**Estimasi Ganti Berikutnya:** KM {est_km}")
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

# ===== Edit Data =====
if "edit_index" in st.session_state:
    idx = st.session_state["edit_index"]
    row = df.iloc[idx]
    st.markdown("### Edit Data Maintenance")
    with st.form("edit_form"):
        tanggal_edit = st.date_input("Tanggal", value=pd.to_datetime(row["Tanggal"]))
        komponen_edit = st.selectbox("Komponen", KOMPONEN_LIST, index=KOMPONEN_LIST.index(row["Komponen"]))
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

st.markdown("</div>", unsafe_allow_html=True)
