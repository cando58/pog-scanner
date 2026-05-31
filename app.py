import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import requests
from io import BytesIO

st.set_page_config(page_title="POG Product Scanner", layout="wide")
st.title("📦 POG Product Scanner (STORE + Camera + Manual)")

# -------------------------
# 1. Load Excel từ Google Drive
# -------------------------
file_id = "1yw8xkayu14zXy4syuO7Imrdz7FsD7o_L"  # ID file Google Drive
url = f"https://drive.google.com/uc?export=download&id=1yw8xkayu14zXy4syuO7Imrdz7FsD7o_L"
resp = requests.get(url)
df = pd.read_excel(BytesIO(resp.content), engine="openpyxl")

# -------------------------
# 2. Chọn STORE
# -------------------------
store_list = sorted(df['STORE'].dropna().unique().tolist())
selected_store = st.selectbox("Chọn STORE để quét:", store_list)
df_store = df[df['STORE'] == selected_store]

# -------------------------
# 3. Nhập barcode thủ công hoặc upload hình
# -------------------------
st.subheader("Nhập barcode trực tiếp hoặc chụp hình barcode")

# 3a. Nhập trực tiếp
manual_barcode = st.text_input("Nhập mã hàng (EAN_CODE) trực tiếp")

# 3b. Upload hình barcode
uploaded_file = st.file_uploader(
    "Hoặc chụp barcode bằng camera / chọn hình từ thư viện",
    type=["png","jpg","jpeg"]
)

barcode_from_image = None
if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, use_container_width=True)
    # OCR chuyển ảnh barcode sang số
    barcode_from_image = pytesseract.image_to_string(img, config='--psm 8 digits')
    barcode_from_image = barcode_from_image.strip()
    if barcode_from_image:
        st.success(f"Barcode từ hình: {barcode_from_image}")
    else:
        st.warning("Không quét được barcode từ hình")

# -------------------------
# 4. Chọn barcode để lookup
# -------------------------
barcode = manual_barcode if manual_barcode else barcode_from_image

if barcode:
    try:
        barcode_int = int(barcode)
    except:
        barcode_int = barcode

    product = df_store[df_store['EAN_CODE'] == barcode_int]

    if not product.empty:
        st.subheader("Thông tin sản phẩm")
        st.write(f"Mã Hàng: {product['ART_NO'].values[0]}")
        st.write(f"Tên SP: {product['ART_DESCR'].values[0]}")
        st.write(f"Art STT: {product['ART_STATUS'].values[0]}")
        st.write(f"SEASON: {product['SEASON'].values[0]}")
        st.write(f"ORDER_FLAG: {product['ORDER_FLAG'].values[0]}")
        st.write(f"SUPPL_ART_NO: {product['SUPPL_ART_NO'].values[0]}")
        st.write(f"CORE: {product['CORE'].values[0]}")
        st.write(f"Stock: {product['ACTUAL_STOCK'].values[0]}")
        st.write(f"Dept: {product['UPD_BUYER_UID'].values[0]}")
        st.write(f"ON_PNG: {product['ON_PNG'].values[0]}")
        st.write(f"POG: {product['PLANO NAME'].values[0]}")
        st.write(f"Fixel ID: {product['Fixel ID'].values[0]}")
        st.write(f"Vị trí: {product['Vị trí'].values[0]}")
        st.write(f"Facing: {product['Facing'].values[0]}")
    else:
        st.error("Barcode không có trong STORE đã chọn")