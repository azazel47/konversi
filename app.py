import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from streamlit_paste_button import paste_image_button

# ================= CONFIG =================
st.set_page_config(page_title="Konversi Koordinat AI", layout="wide")

# 🔑 GANTI API KEY
genai.configure(api_key="AIzaSyAI2CXCmxwKqHcT2HpRJ_vWbue_iKEZ8Yw")

# ================= GEMINI =================
def process_coordinates(image):
    model = genai.GenerativeModel('gemini-1.5-pro')

    prompt = """
    Anda adalah sistem ekstraksi data koordinat dari tabel.

    Ekstrak semua data dari gambar ke dalam tabel Markdown.

    Aturan WAJIB:
    1. Output HARUS tabel Markdown saja
    2. Kolom:
       id | bujur_derajat | bujur_menit | bujur_detik | BT_BB | lintang_derajat | lintang_menit | lintang_detik | LU_LS
    3. Jangan beri penjelasan
    4. Jangan ubah angka
    5. Gunakan titik (.) sebagai desimal
    6. BT_BB hanya: BT atau BB
    7. LU_LS hanya: LU atau LS
    """

    response = model.generate_content([prompt, image])
    return response.text


def markdown_to_df(md_text):
    lines = md_text.strip().split("\n")
    lines = [l for l in lines if "|" in l and "---" not in l]
    data = [line.split("|")[1:-1] for line in lines]

    return pd.DataFrame(
        data[1:], 
        columns=[c.strip() for c in data[0]]
    )

# ================= UI =================
st.title("📋 Paste Screenshot Koordinat → Tabel (AI)")

# 🔥 PASTE BUTTON (INI KUNCI)
st.subheader("📋 Paste Screenshot (Ctrl+V)")
paste_result = paste_image_button("Klik di sini lalu tekan Ctrl+V")

image = None

if paste_result.image_data is not None:
    image = paste_result.image_data
    st.success("✅ Gambar berhasil di-paste")

# fallback upload
uploaded_file = st.file_uploader("Atau upload gambar", type=["png", "jpg", "jpeg"])
if uploaded_file and image is None:
    image = Image.open(uploaded_file)

# ================= PROCESS =================
if image:
    st.image(image, caption="Gambar Input", use_container_width=True)

    if st.button("🚀 Proses dengan AI"):
        with st.spinner("🤖 AI sedang membaca tabel..."):
            hasil = process_coordinates(image)

        st.markdown("### 📋 Hasil AI")
        st.markdown(hasil)

        try:
            df = markdown_to_df(hasil)

            st.markdown("### 📊 Tabel Terstruktur")
            st.dataframe(df, use_container_width=True)

            st.markdown("### 📋 Copy ke Excel")
            st.code(df.to_csv(sep="\t", index=False))

        except:
            st.warning("⚠️ Gagal parsing tabel, cek format output AI")

st.caption("Gunakan browser Chrome untuk hasil paste terbaik")
