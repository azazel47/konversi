import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from streamlit_paste_button import paste_image_button
import io

# ================= CONFIG =================
st.set_page_config(page_title="Konversi Koordinat AI", layout="wide")

# 🔑 API KEY (Pastikan tidak ada spasi di awal/akhir)
genai.configure(api_key="AIzaSyAI2CXCmxwKqHcT2HpRJ_vWbue_iKEZ8Yw")

# ================= GEMINI =================
def process_coordinates(image_input):
    # Menggunakan flash karena lebih cepat dan handal untuk OCR tabel
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = """
    Anda adalah sistem ekstraksi data koordinat dari tabel.
    Ekstrak semua data dari gambar ke dalam tabel Markdown.

    Aturan WAJIB:
    1. Output HARUS tabel Markdown saja
    2. Kolom: id | bujur_derajat | bujur_menit | bujur_detik | BT_BB | lintang_derajat | lintang_menit | lintang_detik | LU_LS
    3. Jangan beri penjelasan apapun di luar tabel
    4. Gunakan titik (.) sebagai pemisah desimal
    5. BT_BB hanya: BT atau BB. LU_LS hanya: LU atau LS.
    """

    # Memastikan input adalah gambar PIL
    response = model.generate_content([prompt, image_input])
    return response.text

def markdown_to_df(md_text):
    try:
        lines = [l.strip() for l in md_text.strip().split("\n") if "|" in l]
        # Cari baris yang mengandung header (id/bujur)
        start_idx = 0
        for i, line in enumerate(lines):
            if "bujur" in line.lower():
                start_idx = i
                break
        
        # Filter garis pemisah tabel (---)
        data_lines = [l for l in lines[start_idx:] if "---" not in l]
        data = [line.split("|")[1:-1] for line in data_lines]

        df = pd.DataFrame(data[1:], columns=[c.strip() for c in data[0]])
        return df
    except Exception as e:
        return None

# ================= UI =================
st.title("📋 Paste Screenshot Koordinat → Tabel (AI)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Input Gambar")
    paste_result = paste_image_button("Klik di sini lalu tekan Ctrl+V (Paste)")
    uploaded_file = st.file_uploader("Atau upload file", type=["png", "jpg", "jpeg"])

image_to_process = None

# Prioritas Paste, lalu Upload
if paste_result.image_data is not None:
    image_to_process = paste_result.image_data
elif uploaded_file is not None:
    image_to_process = Image.open(uploaded_file)

# ================= PROCESS =================
if image_to_process:
    with col2:
        st.subheader("2. Preview & Hasil")
        st.image(image_to_process, caption="Gambar Input", use_container_width=True)

    if st.button("🚀 Proses dengan AI", use_container_width=True):
        with st.spinner("🤖 AI sedang membaca tabel..."):
            try:
                hasil_raw = process_coordinates(image_to_process)
                st.markdown("### 📋 Hasil AI")
                st.markdown(hasil_raw)

                df = markdown_to_df(hasil_raw)
                if df is not None and not df.empty:
                    st.markdown("### 📊 Tabel Terstruktur")
                    st.dataframe(df, use_container_width=True)

                    st.markdown("### 📋 Copy ke Excel (Tab Separated)")
                    # Tab separated lebih mudah di paste langsung ke Excel
                    st.code(df.to_csv(sep="\t", index=False), language="text")
                else:
                    st.error("AI memberikan format yang tidak bisa dibaca sebagai tabel.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")
                st.info("Saran: Coba gunakan model 'gemini-1.5-flash' jika 'pro' bermasalah.")
