import streamlit as st
import pandas as pd
import re
from PIL import Image
import pytesseract

st.set_page_config(page_title="Konversi Koordinat", layout="wide")

st.title("📍 Konversi Koordinat dari Gambar / Teks")

# ================= PILIH INPUT =================
mode = st.radio("Metode Input:", ["Paste Gambar", "Paste Teks"])

# ================= FUNGSI PARSER =================
def parse_dms(text):
    pattern = re.compile(r"(\d+)[°\s]+(\d+)[']+(\d+(?:\.\d+)?)[\"]?\s*([NS])\s*(\d+)[°\s]+(\d+)[']+(\d+(?:\.\d+)?)[\"]?\s*([EW])")
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
    pattern = re.compile(r"(-?\d+\.\d+)[,\s]+(-?\d+\.\d+)")
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

if mode == "Paste Gambar":
    st.info("📋 Paste gambar langsung dengan Ctrl+V atau drag ke bawah")
    uploaded_file = st.file_uploader("Paste / drag gambar", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar", use_container_width=True)

        text = pytesseract.image_to_string(image)

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
        st.code(df_dms.to_csv(sep="\t", index=False))

    elif not df_decimal.empty:
        st.success("✅ Format Decimal Degree terdeteksi")
        st.dataframe(df_decimal, use_container_width=True)

        st.markdown("### 📋 Copy ke Excel")
        st.code(df_decimal.to_csv(sep="\t", index=False))

    else:
        st.error("❌ Format koordinat tidak dikenali")

st.caption("Tips: gunakan gambar yang jelas agar OCR lebih akurat")
