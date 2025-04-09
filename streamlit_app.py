import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import base64

st.set_page_config(page_title="D007Garage Maintenance Tracker", layout="centered")

# Header rapi dan responsif untuk tampilan HP
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 1rem;'>
        <h2 style='margin-bottom: 0.2rem;'>🛵 D007Garage</h2>
        <p style='font-size: 1.2rem; font-weight: bold;'>Maintenance Tracker</p>
    </div>
    <hr style='border: 1px solid #444;'>
    """,
    unsafe_allow_html=True
)

st.title("D007Garage Maintenance Tracker")

# Inisialisasi data jika belum ada
if "maintenance_data" not in st.session_state:
    st.session_state.maintenance_data = pd.DataFrame(columns=[
        "Tanggal Penggantian", "Komponen", "KM Saat Ini", "Catatan", "KM Selanjutnya", "Estimasi Tanggal Selanjutnya"
    ])

# Fungsi untuk menambahkan data maintenance
def tambah_data(tanggal, komponen, km_saat_ini, catatan):
    interval_km = 2000
    km_selanjutnya = km_saat_ini + interval_km
    estimasi_tanggal = tanggal + timedelta(days=60)
    
    data_baru = pd.DataFrame([{
        "Tanggal Penggantian": tanggal,
        "Komponen": komponen,
        "KM Saat Ini": km_saat_ini,
        "Catatan": catatan,
        "KM Selanjutnya": km_selanjutnya,
        "Estimasi Tanggal Selanjutnya": estimasi_tanggal
    }])
    
    st.session_state.maintenance_data = pd.concat([st.session_state.maintenance_data, data_baru], ignore_index=True)

# Form input
st.subheader("Tambah Data Maintenance")
with st.form("form_maintenance"):
    tanggal = st.date_input("Tanggal Penggantian", value=datetime.today())
    komponen = st.selectbox("Komponen", ["Oli Mesin", "Kampas Rem", "Busi", "Filter Udara", "Aki"])
    km_saat_ini = st.number_input("KM Saat Ini", min_value=0, step=100)
    catatan = st.text_area("Catatan Tambahan", placeholder="Opsional")
    submit = st.form_submit_button("Simpan Data", use_container_width=True)
    
    if submit:
        tambah_data(tanggal, komponen, km_saat_ini, catatan)
        st.success("Data berhasil disimpan!")

# Menampilkan data
st.subheader("Riwayat Maintenance")
df = st.session_state.maintenance_data

if df.empty:
    st.info("Belum ada data maintenance.")
else:
    st.dataframe(df)

    # Fungsi untuk mengunduh sebagai Excel
    def convert_df_to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Data")
        processed_data = output.getvalue()
        return processed_data

    excel_data = convert_df_to_excel(df)
    st.download_button(
        label="Download Data sebagai Excel",
        data=excel_data,
        file_name="data_maintenance.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
