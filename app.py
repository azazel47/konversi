import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from streamlit_paste_button import paste_image_button

# ================= CONFIG =================
st.set_page_config(page_title="Konversi Koordinat AI", layout="wide")

# 🔑 API KEY
genai.configure(api_key="AIzaSyAI2CXCmxwKqHcT2HpRJ_vWbue_iKEZ8Yw")

# ================= GEMINI =================
def process_coordinates(image_input):
    # Gunakan 'models/gemini-1.5-flash' (lengkap dengan prefix) 
    # atau 'gemini-1.5-flash-latest' untuk menghindari error 404
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('models/gemini-1.5-flash')

    prompt = """
    Anda adalah sistem ekstraksi data koordinat dari tabel.
    Ekstrak semua data dari gambar ke dalam tabel Markdown.

    Aturan WAJIB:
    1. Output HARUS tabel Markdown saja
    2. Kolom: id | bujur_derajat | bujur_menit | bujur_detik | BT_BB | lintang_derajat | lintang_menit | lintang_detik | LU_LS
    3. Jangan beri penjelasan apapun di luar tabel
    4. Gunakan titik (.) sebagai desimal
    5. BT_BB hanya: BT atau BB. LU_LS hanya: LU atau LS.
    """

    response = model.generate_content([prompt, image_input])
    return response.text

def markdown_to_df(md_text):
    try:
        lines = [l.strip() for l in md_text.strip().split("\n") if "|" in l]
        start_idx = 0
        for i, line in enumerate(lines):
            if "bujur" in line.lower():
                start_idx = i
                break
        
        data_lines = [l for l in lines[start_idx:] if "---" not in l]
        data = [line.split("|")[1:-1] for line in data_lines]

        df = pd.DataFrame(data[1:], columns=[c.strip() for c in data[0]])
        return df
    except:
        return None

# ================= UI =================
st.title("📋 Paste Screenshot Koordinat → Tabel (AI)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Input Gambar")
    paste_result = paste_image_button("Klik di sini lalu tekan Ctrl+V (Paste)")
    uploaded_file = st.file_uploader("Atau upload file", type=["png", "jpg", "jpeg"])

image_to_process = None
if paste_result.image_data is not None:
    image_to_process = paste_result.image_data
elif uploaded_file is not None:
    image_to_process = Image.open(uploaded_file)

# ================= PROCESS =================
if image_to_process:
    with col2:
        st.subheader("2. Preview Input")
        st.image(image_to_process, use_container_width=True)

    if st.button("🚀 Proses dengan AI", use_container_width=True):
        with st.spinner("🤖 AI sedang membaca tabel..."):
            try:
                hasil_raw = process_coordinates(image_to_process)
                df = markdown_to_df(hasil_raw)
                
                if df is not None and not df.empty:
                    # Menampilkan hasil HANYA dalam format kode Excel
                    st.markdown("### 📋 Hasil Konversi (Siap Paste ke Excel)")
                    st.info("Klik tombol copy di pojok kanan atas kotak di bawah, lalu paste di Excel.")
                    st.code(df.to_csv(sep="\t", index=False), language="text")
                else:
                    st.error("Gagal memproses tabel. Pastikan gambar tabel terlihat jelas.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")
