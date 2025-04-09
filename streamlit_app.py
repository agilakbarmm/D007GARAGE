import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import base64

# ---------------------- SETUP ----------------------

# Komponen dan estimasi km berikutnya
komponen_km = {
    "Oli Mesin": 2000,
    "Oli Gardan": 4000,
    "Roller": 10000,
    "Vbelt": 10000,
    "Kampas Ganda": 12000,
    "Busi": 8000,
    "ACU": 16000,
    "Per CVT": 12000,
    "Per Kampas Ganda": 14000,
}

# Folder data per user
DATA_DIR = "data_user"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ---------------------- AUTH ----------------------

def load_users():
    user_file = os.path.join(DATA_DIR, "users.csv")
    if os.path.exists(user_file):
        return pd.read_csv(user_file)
    else:
        return pd.DataFrame(columns=["username", "password"])

def save_users(users_df):
    users_df.to_csv(os.path.join(DATA_DIR, "users.csv"), index=False)

def signup(username, password):
    users = load_users()
    if username in users["username"].values:
        return False
    new_user = pd.DataFrame([[username, password]], columns=["username", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    save_users(users)
    return True

def login(username, password):
    users = load_users()
    return ((users["username"] == username) & (users["password"] == password)).any()

# ---------------------- BACKGROUND ----------------------

def set_background():
    bg_url = "https://images.unsplash.com/photo-1605559424843-1c4b819fa2c4?auto=format&fit=crop&w=1500&q=80"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{bg_url}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .blur-bg {{
            backdrop-filter: blur(6px);
            background-color: rgba(255, 255, 255, 0.75);
            padding: 2rem;
            border-radius: 15px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background()

# ---------------------- LOGIN PAGE ----------------------

if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    st.markdown("<div class='blur-bg'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🛠️ 007GARAGE</h2>", unsafe_allow_html=True)
    menu = st.radio("Login / Signup", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if menu == "Login":
        if st.button("Login"):
            if login(username, password):
                st.session_state["user"] = username
                st.experimental_rerun()
            else:
                st.error("Username atau password salah.")
    else:
        if st.button("Signup"):
            if signup(username, password):
                st.success("Signup berhasil! Silakan login.")
            else:
                st.error("Username sudah digunakan.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------------- MAIN APP ----------------------

username = st.session_state["user"]
csv_file = os.path.join(DATA_DIR, f"{username}_riwayat.csv")
if not os.path.exists(csv_file):
    pd.DataFrame(columns=["Tanggal", "Komponen", "KM", "Catatan"]).to_csv(csv_file, index=False)

st.markdown("<div class='blur-bg'>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>🛠️ 007GARAGE</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Tambah Data Maintenance</h4>", unsafe_allow_html=True)

# Form Tambah Data
with st.form("form_maintenance"):
    tanggal = st.date_input("Tanggal", value=datetime.today())
    komponen = st.multiselect("Komponen", list(komponen_km.keys()))
    km = st.number_input("KM Saat Ini", min_value=0, step=100)
    catatan = st.text_area("Catatan Tambahan", placeholder="Opsional")
    simpan = st.form_submit_button("Simpan Data")

if simpan and komponen:
    df = pd.read_csv(csv_file)
    for item in komponen:
        estimasi_km = km + komponen_km[item]
        new_row = pd.DataFrame([[tanggal, item, km, catatan, estimasi_km]],
                               columns=["Tanggal", "Komponen", "KM", "Catatan", "Estimasi KM Berikut"])
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv_file, index=False)
    st.success("Data berhasil disimpan.")

# Pencarian
st.markdown("<h4>Riwayat Maintenance</h4>", unsafe_allow_html=True)
search = st.text_input("Cari Komponen atau Catatan")

df = pd.read_csv(csv_file)
if "Estimasi KM Berikut" not in df.columns:
    df["Estimasi KM Berikut"] = df["KM"] + df["Komponen"].map(komponen_km)

if search:
    df = df[df.apply(lambda x: search.lower() in str(x).lower(), axis=1)]

if not df.empty:
    for idx, row in df.iterrows():
        with st.expander(f"{row['Tanggal']} - {row['Komponen']} (KM: {row['KM']})"):
            st.markdown(f"**Catatan:** {row['Catatan']}")
            st.markdown(f"**Estimasi Servis Berikutnya:** {int(row['Estimasi KM Berikut'])} KM")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Edit", key=f"edit_{idx}"):
                    st.session_state["edit_index"] = idx
                    st.rerun()
            with col2:
                if st.button("Hapus", key=f"hapus_{idx}"):
                    df.drop(index=idx, inplace=True)
                    df.to_csv(csv_file, index=False)
                    st.success("Data berhasil dihapus.")
                    st.experimental_rerun()
else:
    st.info("Belum ada data maintenance.")

# Edit Form
if "edit_index" in st.session_state:
    idx = st.session_state["edit_index"]
    row = df.iloc[idx]

    st.markdown("<h4>Edit Data Maintenance</h4>", unsafe_allow_html=True)
    with st.form("edit_form"):
        tanggal_edit = st.date_input("Tanggal", value=pd.to_datetime(row["Tanggal"]))
        komponen_edit = st.selectbox("Komponen", list(komponen_km.keys()), index=list(komponen_km.keys()).index(row["Komponen"]))
        km_edit = st.number_input("KM", value=int(row["KM"]), step=100)
        catatan_edit = st.text_area("Catatan", value=row["Catatan"])
        simpan_update = st.form_submit_button("Update Data")

    if simpan_update:
        df.at[idx, "Tanggal"] = tanggal_edit
        df.at[idx, "Komponen"] = komponen_edit
        df.at[idx, "KM"] = km_edit
        df.at[idx, "Catatan"] = catatan_edit
        df.at[idx, "Estimasi KM Berikut"] = km_edit + komponen_km[komponen_edit]
        df.to_csv(csv_file, index=False)
        del st.session_state["edit_index"]
        st.success("Data berhasil diperbarui.")
        st.experimental_rerun()

st.markdown("</div>", unsafe_allow_html=True)
