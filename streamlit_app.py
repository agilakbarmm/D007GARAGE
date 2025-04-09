import streamlit as st import pandas as pd from datetime import datetime import os

===== BACKGROUND IMAGE WITH BLUR =====

page_bg_img = f"""

<style>
[data-testid="stAppViewContainer"] > .main {{
    background-image: url("https://images.unsplash.com/photo-1605902711622-cfb43c4437d1?auto=format&fit=crop&w=1350&q=80");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    backdrop-filter: blur(5px);
    color: white;
}}

h1, h2, h3, h4, h5, h6, .stTextInput, .stNumberInput, .stDateInput, .stTextArea {{
    color: white;
}}
</style>"""

st.markdown(page_bg_img, unsafe_allow_html=True)

===== USER AUTH =====

USERS_FILE = "users.csv" if not os.path.exists(USERS_FILE): df_users = pd.DataFrame(columns=["username", "password"]) df_users.to_csv(USERS_FILE, index=False)

===== SESSION STATE =====

if "logged_in" not in st.session_state: st.session_state.logged_in = False if "username" not in st.session_state: st.session_state.username = ""

===== LOGIN & SIGNUP FORM =====

def login_form(): st.title("🛠️ 007GARAGE") st.markdown("#### Login Pengguna") username = st.text_input("Username") password = st.text_input("Password", type="password") if st.button("Login"): df_users = pd.read_csv(USERS_FILE) if not df_users[(df_users.username == username) & (df_users.password == password)].empty: st.session_state.logged_in = True st.session_state.username = username st.success("Login berhasil.") st.experimental_rerun() else: st.error("Username atau password salah.")

st.markdown("---")
st.markdown("#### Belum punya akun?")
new_user = st.text_input("Buat Username Baru", key="new_user")
new_pass = st.text_input("Buat Password", type="password", key="new_pass")
if st.button("Daftar"):
    df_users = pd.read_csv(USERS_FILE)
    if new_user in df_users.username.values:
        st.warning("Username sudah terdaftar.")
    else:
        df_users = df_users.append({"username": new_user, "password": new_pass}, ignore_index=True)
        df_users.to_csv(USERS_FILE, index=False)
        st.success("Pendaftaran berhasil. Silakan login.")

===== MAIN APP =====

def main_app(): st.markdown(""" <div style='text-align: center;'> <h1 style='font-size: 3em;'>🛠️ 007GARAGE</h1> </div> """, unsafe_allow_html=True)

CSV_FILE = f"data_{st.session_state.username}.csv"
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Tanggal", "Komponen", "KM", "Catatan"])
    df_init.to_csv(CSV_FILE, index=False)

st.markdown("""
    <div style='text-align: center; font-size: 20px;'>
        <strong>Tambah Data Maintenance</strong>
    </div>
""", unsafe_allow_html=True)

with st.form("form_maintenance"):
    tanggal = st.date_input("Tanggal Penggantian", value=datetime.today())
    komponen_list = ["Oli Mesin", "Oli Gardan", "Roller", "Vbelt", "Kampas Ganda", "Busi", "Aki", "Per CVT", "Per Kampas Ganda"]
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

# ===== SEARCH =====
st.subheader("Riwayat Maintenance")
df = pd.read_csv(CSV_FILE)
search = st.text_input("Cari berdasarkan komponen...")
if search:
    df = df[df["Komponen"].str.contains(search, case=False, na=False)]

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

if "edit_index" in st.session_state:
    idx = st.session_state.edit_index
    row = df.iloc[idx]
    st.markdown("<h3 style='text-align: center;'>Edit Data Maintenance</h3>", unsafe_allow_html=True)
    with st.form("edit_form"):
        tanggal_edit = st.date_input("Tanggal", value=pd.to_datetime(row["Tanggal"]))
        komponen_list = ["Oli Mesin", "Oli Gardan", "Roller", "Vbelt", "Kampas Ganda", "Busi", "Aki", "Per CVT", "Per Kampas Ganda"]
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

===== MAIN =====

if not st.session_state.logged_in: login_form() else: main_app()

