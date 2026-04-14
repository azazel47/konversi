import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd

# ================= CONFIG =================
st.set_page_config(page_title="Konversi Koordinat AI", layout="wide")

# 👉 GANTI dengan API KEY kamu
genai.configure(api_key="AIzaSyAI2CXCmxwKqHcT2HpRJ_vWbue_iKEZ8Yw")

# ================= FUNCTION =================
def process_coordinates(image_file):
    model = genai.GenerativeModel('gemini-1.5-pro')
    img = Image.open(image_file)

    prompt = """
    Anda adalah sistem ekstraksi data koordinat dari tabel.

    Tugas:
    Ekstrak SEMUA data dari gambar ke dalam format tabel.

    Aturan WAJIB:
    1. Output HARUS dalam format tabel Markdown.
    2. Kolom HARUS PERSIS:
       id | bujur_derajat | bujur_menit | bujur_detik | BT_BB | lintang_derajat | lintang_menit | lintang_detik | LU_LS
    3. Jangan menambahkan penjelasan apapun.
    4. Jangan mengubah nilai angka.
    5. Gunakan titik (.) sebagai desimal.
    6. BT_BB hanya berisi: BT atau BB
    7. LU_LS hanya berisi: LU atau LS
    8. Urutan kolom tidak boleh berubah.
    9. Semua baris harus lengkap.
    10. Jika teks kurang jelas, isi dengan nilai paling mendekati.

    Output hanya tabel saja.
    """

    response = model.generate_content([prompt, img])
    return response.text


def markdown_to_df(md_text):
    lines = md_text.strip().split("\n")
    lines = [l for l in lines if "|" in l]
    lines = [l for l in lines if "---" not in l]

    data = [line.split("|")[1:-1] for line in lines]

    df = pd.DataFrame(
        data[1:], 
        columns=[c.strip() for c in data[0]]
    )

    return df


# ================= UI =================
st.title("📍 Konversi Koordinat dari Screenshot (AI Powered)")

uploaded_file = st.file_uploader(
    "Upload gambar koordinat (tabel / screenshot)", 
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    st.image(uploaded_file, caption="Gambar Input", use_container_width=True)

    if st.button("🚀 Konversi Sekarang"):
        with st.spinner("🤖 AI sedang membaca tabel..."):
            hasil = process_coordinates(uploaded_file)

        st.markdown("### 📋 Hasil dari AI")
        st.markdown(hasil)

        try:
            df = markdown_to_df(hasil)

            st.markdown("### 📊 Tabel Terstruktur")
            st.dataframe(df, use_container_width=True)

            st.markdown("### 📋 Copy ke Excel")
            st.code(df.to_csv(sep="\t", index=False))

        except:
            st.warning("⚠️ Format tabel tidak bisa diparse otomatis")

st.caption("Gunakan gambar tabel yang jelas untuk hasil terbaik")
