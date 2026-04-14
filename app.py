import streamlit as st
from openai import OpenAI
from PIL import Image
import pandas as pd
from streamlit_paste_button import paste_image_button
import base64
import io

# ================= CONFIG =================
st.set_page_config(page_title="Konversi Koordinat (DeepSeek)", layout="wide")

# 🔑 API KEY DEEPSEEK
# Sebaiknya gunakan st.secrets["DEEPSEEK_API_KEY"] jika di deploy
DEEPSEEK_API_KEY = "sk-248f95011d424e16965cf22091a96d6a"

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com" # Endpoint resmi DeepSeek
)

# ================= FUNCTIONS =================
def encode_image(image):
    """Konversi gambar PIL ke base64 untuk dikirim ke API"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def process_coordinates_deepseek(image_input):
    base64_image = encode_image(image_input)
    
    # DeepSeek-V3 atau DeepSeek-VL adalah model yang mendukung visi
    # Pastikan model yang Anda gunakan mendukung input gambar
    response = client.chat.completions.create(
        model="deepseek-chat", # Sesuaikan dengan model vision DeepSeek yang tersedia
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Ekstrak data koordinat dari gambar ini ke tabel Markdown. Kolom: id | bujur_derajat | bujur_menit | bujur_detik | BT_BB | lintang_derajat | lintang_menit | lintang_detik | LU_LS. Gunakan titik (.) desimal dan mata angin BT/BB/LU/LS. Jangan beri penjelasan."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        max_tokens=1000,
    )
    return response.choices[0].message.content

def markdown_to_df(md_text):
    try:
        lines = [l.strip() for l in md_text.strip().split("\n") if "|" in l]
        start_idx = next(i for i, line in enumerate(lines) if "bujur" in line.lower())
        data_lines = [l for l in lines[start_idx:] if "---" not in l]
        data = [line.split("|")[1:-1] for line in data_lines]
        return pd.DataFrame(data[1:], columns=[c.strip() for c in data[0]])
    except:
        return None

# ================= UI =================
st.title("📋 Paste Koordinat → Excel (Powered by DeepSeek)")

col1, col2 = st.columns(2)
with col1:
    paste_result = paste_image_button("Klik & Ctrl+V (Paste)")
    uploaded_file = st.file_uploader("Atau Upload", type=["png", "jpg", "jpeg"])

image_to_process = None
if paste_result.image_data is not None:
    image_to_process = paste_result.image_data
elif uploaded_file is not None:
    image_to_process = Image.open(uploaded_file)

if image_to_process:
    with col2:
        st.image(image_to_process, caption="Preview Input", use_container_width=True)

    if st.button("🚀 Proses ke Excel", use_container_width=True):
        with st.spinner("DeepSeek sedang menganalisis gambar..."):
            try:
                hasil_raw = process_coordinates_deepseek(image_to_process)
                df = markdown_to_df(hasil_raw)
                
                if df is not None:
                    st.success("Berhasil! Hasil siap copy:")
                    st.code(df.to_csv(sep="\t", index=False), language="text")
                else:
                    st.error("Gagal mengekstrak tabel. Pastikan format gambar jelas.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")
