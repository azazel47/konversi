import streamlit as st
from openai import OpenAI
from PIL import Image
import pandas as pd
from streamlit_paste_button import paste_image_button
import base64
import io

# ================= CONFIG =================
st.set_page_config(page_title="Konversi Koordinat (OpenAI)", layout="wide")

# 🔑 API KEY OPENAI
# Dapatkan di https://platform.openai.com/api-keys
# Disarankan menggunakan st.secrets["OPENAI_API_KEY"] untuk deploy
OPENAI_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)

# ================= FUNCTIONS =================
def encode_image(image):
    """Konversi gambar PIL ke base64 untuk dikirim ke OpenAI"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def process_coordinates_openai(image_input):
    base64_image = encode_image(image_input)
    
    # Menggunakan gpt-4o-mini (sangat cepat, akurat, dan murah untuk OCR)
    # Anda juga bisa menggunakan "gpt-4o" untuk hasil yang lebih presisi
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": """Ekstrak data koordinat dari gambar ke tabel Markdown.
                            Kolom: id | bujur_derajat | bujur_menit | bujur_detik | BT_BB | lintang_derajat | lintang_menit | lintang_detik | LU_LS
                            Aturan:
                            1. Gunakan titik (.) untuk desimal.
                            2. Mata angin gunakan BT/BB/LU/LS.
                            3. HANYA berikan tabel Markdown saja tanpa penjelasan."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        raise e

def markdown_to_df(md_text):
    """Konversi teks Markdown dari AI menjadi Pandas DataFrame"""
    try:
        # Bersihkan baris yang tidak mengandung karakter tabel
        lines = [l.strip() for l in md_text.strip().split("\n") if "|" in l]
        
        # Cari baris yang mengandung kata kunci header
        start_idx = 0
        for i, line in enumerate(lines):
            if "bujur" in line.lower() or "id" in line.lower():
                start_idx = i
                break
        
        # Filter garis pemisah tabel (---)
        data_lines = [l for l in lines[start_idx:] if "---" not in l]
        
        # Pecah baris menjadi list data (menghilangkan elemen kosong di awal/akhir)
        data = [line.split("|")[1:-1] for line in data_lines]

        if len(data) < 2: return None
        
        # Buat DataFrame
        df = pd.DataFrame(data[1:], columns=[c.strip() for c in data[0]])
        return df
    except:
        return None

# ================= UI =================
st.title("📋 Paste Koordinat → Excel (OpenAI Vision)")

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

    if st.button("🚀 Proses ke Excel", use_container_width=True):
        with st.spinner("OpenAI sedang membaca data..."):
            try:
                hasil_raw = process_coordinates_openai(image_to_process)
                df = markdown_to_df(hasil_raw)
                
                if df is not None and not df.empty:
                    st.success("Berhasil diekstrak!")
                    
                    # Output akhir dalam format kode TSV (Tab Separated)
                    st.markdown("### 📋 Hasil Konversi (Siap Paste ke Excel)")
                    st.info("Klik tombol copy di pojok kanan atas, lalu paste langsung di Excel.")
                    
                    tsv_data = df.to_csv(sep="\t", index=False)
                    st.code(tsv_data, language="text")
                else:
                    st.error("AI tidak mengembalikan format tabel yang valid.")
                    with st.expander("Lihat Respon Mentah AI"):
                        st.text(hasil_raw)
                        
            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")
