import streamlit as st
import pandas as pd
import re
import pytesseract
from PIL import Image
import numpy as np
import cv2
from streamlit_paste_button import paste_image_button

# ================= CONFIG =================
st.set_page_config(page_title="Konversi Koordinat", layout="wide")

# Fix path Tesseract (untuk Streamlit Cloud / Linux)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.title("📍 Konversi Koordinat dari Screenshot / Teks")

# ================= PILIH MODE =================
mode = st.radio("Metode Input:", ["Paste Gambar", "Paste Teks"])

# ================= PARSER =================
def parse_dms(text):
    pattern = re.compile(
        r"(\\d+)[°\\s]+(\\d+)[']+(\\d+(?:\\.\\d+)?)[\\\"]?\\s*([NS])\\s*"
        r"(\\d+)[°\\s]+(\\d+)[']+(\\d+(?:\\.\\d+)?)[\\\"]?\\s*([EW])"
    )
    results = []
    for i, match in enumerate(pattern.findall(text), start=1):
        lat_d, lat_m, lat_s, lat_dir, lon_d, lon_m, lon_s, lon_dir = match
        results.append({
            "id": i,
            "bujur_derajat": lon_d,
            "bujur_menit": lon_m,
            "bujur_detik": lon_s,
            "BT_BB": lon_dir,
            "lintang_derajat": lat_d,
            "lintang_menit": lat_m,
            "lintang_detik": lat_s,
            "LU_LS": lat_dir
        })
    return pd.DataFrame(results)


def parse_decimal(text):
    pattern = re.compile(r"(-?\\d+\\.\\d+)[,\\s]+(-?\\d+\\.\\d+)")
    results = []
    for i, match in enumerate(pattern.findall(text), start=1):
        x, y = match
        results.append({
            "id": i,
            "x": float(x),
            "y": float(y)
        })
    return pd.DataFrame(results)

# ================= INPUT =================
text = ""
image = None

if mode == "Paste Gambar":
    st.subheader("📋 Paste Screenshot (Ctrl+V)")

    paste_result = paste_image_button("Klik di sini lalu Ctrl+V")

    if paste_result.image_data is not None:
        image = paste_result.image_data
        st.success("✅ Gambar berhasil di-paste")

    st.markdown("### atau upload gambar")
    uploaded_file = st.file_uploader("Upload gambar", type=["png","jpg","jpeg"])

    if uploaded_file and image is None:
        image = Image.open(uploaded_file)

    # ================= OCR =================
    if image is not None:
        st.image(image, caption="Gambar Input", use_container_width=True)

        img = np.array(image)

        # preprocessing biar OCR lebih akurat
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5,5), 0)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        text = pytesseract.image_to_string(gray)

        with st.expander("🔍 Hasil OCR"):
            st.text(text)

elif mode == "Paste Teks":
    text = st.text_area("Paste teks koordinat di sini:")

# ================= PROSES =================
if text:
    df_dms = parse_dms(text)
    df_decimal = parse_decimal(text)

    if not df_dms.empty:
        st.success("✅ Format DMS terdeteksi")
        st.dataframe(df_dms, use_container_width=True)

        st.markdown("### 📋 Copy ke Excel")
        st.code(df_dms.to_csv(sep="\\t", index=False))

    elif not df_decimal.empty:
        st.success("✅ Format Decimal Degree terdeteksi")
        st.dataframe(df_decimal, use_container_width=True)

        st.markdown("### 📋 Copy ke Excel")
        st.code(df_decimal.to_csv(sep="\\t", index=False))

    else:
        st.error("❌ Format koordinat tidak dikenali")

st.caption("Gunakan Chrome untuk paste gambar terbaik (Ctrl+V)")
