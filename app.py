import streamlit as st
from groq import Groq
from PIL import Image
import pandas as pd
from streamlit_paste_button import paste_image_button
import base64
import io

# ================= CONFIG =================
st.set_page_config(page_title="Konversi Koordinat (Groq AI)", layout="wide")

# 🔑 API KEY GROQ (Dapatkan gratis di https://console.groq.com/keys)
# Jika dideploy ke Streamlit Cloud, gunakan st.secrets["GROQ_API_KEY"]
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

# ================= FUNCTIONS =================
def encode_image(image):
    """Konversi gambar PIL ke base64 untuk dikirim ke Groq"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def process_coordinates_groq(image_input):
    base64_image = encode_image(image_input)
    
    # Menggunakan Llama 3.2 Vision 11B (Gratis & Cepat di Groq)
    try:
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview", 
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
                            3. Hanya berikan tabel Markdown tanpa penjelasan tambahan."""
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
            temperature=0, # Set 0 agar ekstraksi lebih konsisten/kaku
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise e

def markdown_to_df(md_text):
    """Konversi teks Markdown dari AI menjadi Pandas DataFrame"""
    try:
        # Ambil baris yang berisi karakter tabel '|'
        lines = [l.strip() for l in md_text.strip().split("\n") if "|" in l]
        
        # Cari header (biasanya baris pertama yang mengandung kata kunci)
        start_idx = 0
        for i, line in enumerate(lines):
            if "bujur" in line.lower() or "id" in line.lower():
                start_idx = i
                break
        
        # Buang garis pemisah tabel (---)
        data_lines = [l for l in lines[start_idx:] if "---" not in l]
        
        # Pecah baris menjadi list data
        data = [line.split("|")[1:-1] for line in data_lines]

        # Buat DataFrame (Baris 0 sebagai header, sisanya data)
        df = pd.DataFrame(data[1:], columns=[c.strip() for c in data[0]])
        return df
    except:
        return None

# ================= UI =================
st.title("📋 Paste Koordinat → Excel (Groq Vision)")

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
        with st.spinner("Groq sedang menganalisis koordinat..."):
            try:
                # 1. Jalankan AI
                hasil_raw = process_coordinates_groq(image_to_process)
                
                # 2. Konversi ke DataFrame
                df = markdown_to_df(hasil_raw)
                
                if df is not None and not df.empty:
                    st.success("Berhasil diekstrak!")
                    
                    # 3. Output akhir (Hanya kotak kode untuk copy ke Excel)
                    st.markdown("### 📋 Hasil Konversi (Siap Paste ke Excel)")
                    st.info("Klik tombol copy di pojok kanan atas kotak di bawah, lalu paste di Excel.")
                    
                    # Konversi ke Tab Separated agar pas dipaste ke Excel
                    tsv_data = df.to_csv(sep="\t", index=False)
                    st.code(tsv_data, language="text")
                else:
                    st.error("Gagal mengubah hasil AI menjadi tabel. Coba ulangi proses.")
                    # Jika gagal, tampilkan raw output untuk debug
                    with st.expander("Lihat Jawaban AI"):
                        st.text(hasil_raw)
                        
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ Kuota Groq Terlampaui. Tunggu 1 menit lalu coba lagi.")
                else:
                    st.error(f"Terjadi kesalahan: {str(e)}")
