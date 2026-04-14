import streamlit as st
import google.generativeai as genai
from PIL import Image

# Konfigurasi API Key (Dapatkan di aistudio.google.com)
genai.configure(api_key="AIzaSyAI2CXCmxwKqHcT2HpRJ_vWbue_iKEZ8YwY")

def process_coordinates(image_file):
    model = genai.GenerativeModel('gemini-1.5-flash')
    img = Image.open(image_file)
    
    prompt = """
    Ekstrak semua koordinat dari gambar ini ke dalam tabel Markdown.
    Aturan:
    1. Gunakan pemisah desimal koma (,) bukan titik.
    2. Susun kolom: id, bujur_derajat, bujur_menit, bujur_detik, BT_BB, lintang_derajat, lintang_menit, lintang_detik, LU_LS.
    3. Pastikan kolom Bujur (X) berada di sebelah kiri Lintang (Y).
    4. Ubah E menjadi BT, S menjadi LS, dan N menjadi LU.
    """
    
    response = model.generate_content([prompt, img])
    return response.text

# Interface Aplikasi
st.title("Coordinate to Excel Converter (Gemini Powered)")
uploaded_file = st.file_uploader("Upload gambar koordinat...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption='Gambar yang diunggah', use_column_width=True)
    if st.button('Konversi Sekarang'):
        with st.spinner('Gemini sedang membaca data...'):
            hasil = process_coordinates(uploaded_file)
            st.markdown(hasil)
