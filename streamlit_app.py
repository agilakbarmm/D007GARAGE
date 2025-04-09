import streamlit as st import pandas as pd from datetime import datetime, timedelta import os import base64

---------------------- SETUP ----------------------

st.set_page_config(page_title="007GARAGE", layout="centered")

Background image

def set_background(image_path): with open(image_path, "rb") as image_file: encoded = base64.b64encode(image_file.read()).decode() st.markdown( f""" <style> .stApp {{ background-image: url("data:image/jpg;base64,{encoded}"); background-size: cover; }} .blur-layer {{ background-color: rgba(255, 255, 255, 0.75); padding: 1rem; border-radius: 10px; }} </style> """, unsafe_allow_html=True )

set_background("bengkel.jpg")  # Pastikan file 'bengkel.jpg' ada di repo

---------------------- FILE CSV ----------------------

CSV_FILE = "riwayat_maintenance.csv" if not os.path.exists(CSV_FILE): df_init = pd.DataFrame(columns=["User", "Tanggal", "Komponen", "KM", "Catatan"]) df_init.to_csv(CSV_FILE, index=False)

---------------------- AUTH SYSTEM ----------------------

USER_DB = "users.csv" if not os.path.exists(USER_DB): pd.DataFrame(columns=["username", "password"]).to_csv(USER_DB, index=False)

def signup(username, password): df_users = pd.read_csv(USER_DB) if username in df_users["username"].values: return False df_users = df_users.append({"username": username, "password": password}, ignore_index=True) df_users.to_csv(USER_DB, index=False) return True

def login(username, password): df_users = pd.read_csv(USER_DB) return any((df_users["username"] == username) & (df_users["password"] == password))

if "user" not in st.session_state: st.session_state.user = None

---------------------- LOGIN & SIGNUP UI ----------------------

if st.session_state.user is None: st.markdown(""" <div class='blur-layer' style='text-align: center;'> <h1 style='font-size: 3em;'>🛠️ 007GARAGE</h1> <p>Login untuk melanjutkan</p> </div> """, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Login", "Sign Up"])

with tab1:
    user_login = st.text_input("Username")
    pass_login = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(user_login, pass_login):
            st.session_state.user = user_login
            st.experimental_rerun()
        else:
            st.error("Username atau password salah")

with tab2:
    user_reg = st.text_input("Buat Username")
    pass_reg = st.text_input("Buat Password", type="password")
    if st.button("Sign Up"):
        if signup(user_reg, pass_reg):
            st.success("Berhasil daftar. Silakan login.")
        else:
            st.error("Username sudah terdaftar.")

st.stop()

---------------------- MAIN APP ----------------------

st.markdown("""

<div class='blur-layer'>
    <div style='text-align: center;'>
        <h1 style='font-size: 2.5em;'>🛠️ 007GARAGE</h1>
        <p>Selamat datang, <strong>{}</strong>!</p>
    </div>
</div>
""".format(st.session_state.user), unsafe_allow_html=True)st.markdown("""

<div style='text-align: center; font-size: 18px; margin-top: 20px; margin-bottom: 10px;'>
    <strong>Tambah Data Maintenance</strong>
</div>
""", unsafe_allow_html=True)---------------------- FORM INPUT ----------------------

komponen_estimasi = { "Oli Mesin": 2000, "Oli Gardan": 8000, "Roller": 24000, "Vbelt": 24000, "Kampas Ganda": 18000, "Busi": 8000, "Aki": 20000, "Per CVT": 24000, "Per Kampas Ganda": 24000, }

with st.form("form_maintenance"): tanggal = st.date_input("Tanggal Penggantian", value=datetime.today()) komponen = st.multiselect("Komponen", list(komponen_estimasi.keys())) km = st.number_input("KM Saat Ini", min_value=0, step=100) catatan = st.text_area("Catatan Tambahan", placeholder="Opsional") submit = st.form_submit_button("Simpan Data")

---------------------- SIMPAN DATA ----------------------

if submit and komponen: df = pd.read_csv(CSV_FILE) for item in komponen: new_data = pd.DataFrame([[st.session_state.user, tanggal, item, km, catatan]], columns=["User", "Tanggal", "Komponen", "KM", "Catatan"]) df = pd.concat([df, new_data], ignore_index=True) df.to_csv(CSV_FILE, index=False) st.success("Data berhasil disimpan.")

---------------------- PENCARIAN DAN RIWAYAT ----------------------

st.markdown("<hr>", unsafe_allow_html=True) st.subheader("Riwayat Maintenance")

df = pd.read_csv(CSV_FILE) df = df[df["User"] == st.session_state.user]

search_query = st.text_input("Cari komponen atau catatan") if search_query: df = df[df.apply(lambda x: search_query.lower() in str(x).lower(), axis=1)]

if not df.empty: for idx, row in df.iterrows(): estimasi_km = komponen_estimasi.get(row["Komponen"], 2000) + int(row["KM"]) with st.expander(f"{row['Tanggal']} - {row['Komponen']} (KM: {row['KM']})"): st.markdown(f"Catatan: {row['Catatan']}") st.markdown(f"Estimasi Servis Berikutnya: {estimasi_km} KM") col1, col2 = st.columns(2) with col1: if st.button("Edit", key=f"edit_{idx}"): st.session_state["edit_index"] = idx with col2: if st.button("Hapus", key=f"hapus_{idx}"): df.drop(index=idx, inplace=True) df.to_csv(CSV_FILE, index=False) st.success("Data berhasil dihapus.") st.experimental_rerun()

---------------------- EDIT DATA ----------------------

if "edit_index" in st.session_state: idx = st.session_state["edit_index"] row = df.iloc[idx] st.subheader("Edit Data Maintenance") with st.form("edit_form"): tanggal_edit = st.date_input("Tanggal", value=pd.to_datetime(row["Tanggal"])) komponen_edit = st.selectbox("Komponen", list(komponen_estimasi.keys()), index=list(komponen_estimasi.keys()).index(row["Komponen"])) km_edit = st.number_input("KM", value=int(row["KM"]), step=100) catatan_edit = st.text_area("Catatan", value=row["Catatan"]) update = st.form_submit_button("Update Data")

if update:
    df.at[idx, "Tanggal"] = tanggal_edit
    df.at[idx, "Komponen"] = komponen_edit
    df.at[idx, "KM"] = km_edit
    df.at[idx, "Catatan"] = catatan_edit
    df.to_csv(CSV_FILE, index=False)
    del st.session_state["edit_index"]
    st.success("Data berhasil diperbarui.")
    st.experimental_rerun()

st.markdown(""" <style> textarea, input, .stButton>button { font-size: 16px !important; } </style> """, unsafe_allow_html=True)

---------------------- LOGOUT ----------------------

st.markdown("<hr>", unsafe_allow_html=True) if st.button("Logout"): st.session_state.user = None st.experimental_rerun()

