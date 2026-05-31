import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="POG Product Scanner", layout="wide")
st.title("📦 POG Product Scanner (STORE + ART_NO / EAN_CODE)")

# -------------------------
# Load dữ liệu Excel từ Google Drive
# -------------------------
file_id = "1yw8xkayu14zXy4syuO7Imrdz7FsD7o_L"
url = f"https://drive.google.com/uc?export=download&id=1yw8xkayu14zXy4syuO7Imrdz7FsD7o_L"
resp = requests.get(url)
df = pd.read_excel(BytesIO(resp.content), engine="openpyxl")

# -------------------------
# Chọn STORE
# -------------------------
store_list = sorted(df['STORE'].dropna().unique().tolist())
selected_store = st.selectbox("Chọn STORE để tìm:", store_list)
df_store = df[df['STORE'] == selected_store]

# -------------------------
# Khởi tạo session_state
# -------------------------
if 'art_no_input' not in st.session_state:
    st.session_state.art_no_input = ''
if 'barcode_input' not in st.session_state:
    st.session_state.barcode_input = ''

# Nút Reset → xóa 2 ô input
if st.button("Reset"):
    st.session_state.art_no_input = ''
    st.session_state.barcode_input = ''

# -------------------------
# Nhập ART_NO và BARCODE
# -------------------------
art_no_val = st.text_input("Nhập MÃ HÀNG", value=st.session_state.art_no_input, key="art_no_input")
barcode_val = st.text_input("Nhập BARCODE", value=st.session_state.barcode_input, key="barcode_input")

# Nếu nhập ART_NO → xóa BARCODE, nhập BARCODE → xóa ART_NO
if art_no_val.strip():
    st.session_state.barcode_input = ''
elif barcode_val.strip():
    st.session_state.art_no_input = ''

# -------------------------
# Lookup dữ liệu
# -------------------------
def safe_int(val):
    try:
        return int(val.strip())
    except:
        return None

art_no_lookup = safe_int(st.session_state.art_no_input)
barcode_lookup = safe_int(st.session_state.barcode_input)

product = None
if art_no_lookup is not None:
    product = df_store[df_store['ART_NO'] == art_no_lookup]
elif barcode_lookup is not None:
    product = df_store[df_store['EAN_CODE'] == barcode_lookup]

# -------------------------
# Hiển thị kết quả
# -------------------------
if product is not None and not product.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Product Info")
        st.write(f"Mã Hàng: {product['ART_NO'].values[0]}")
        st.write(f"Tên SP: {product['ART_DESCR'].values[0]}")
        st.write(f"Art STT: {product['ART_STATUS'].values[0]}")
        st.write(f"SEASON: {product['SEASON'].values[0]}")
        st.write(f"ORDER_FLAG: {product['ORDER_FLAG'].values[0]}")
        st.write(f"SUPPL_ART_NO: {product['SUPPL_ART_NO'].values[0]}")
        st.write(f"CORE: {product['CORE'].values[0]}")
    with col2:
        st.subheader("Stock Info")
        st.write(f"Stock: {product['ACTUAL_STOCK'].values[0]}")
        st.write(f"Dept: {product['UPD_BUYER_UID'].values[0]}")
        st.write(f"ON_PNG: {product['ON_PNG'].values[0]}")
        st.write(f"POG: {product['PLANO NAME'].values[0]}")
        st.write(f"Fixel ID: {product['Fixel ID'].values[0]}")
        st.write(f"Vị trí: {product['Vị trí'].values[0]}")
        st.write(f"Facing: {product['Facing'].values[0]}")
elif st.session_state.art_no_input or st.session_state.barcode_input:
    st.error("Không tìm thấy dữ liệu trong STORE đã chọn")

# Footer
st.markdown("---")
st.markdown("tui làm đó CANDO ✌️")
