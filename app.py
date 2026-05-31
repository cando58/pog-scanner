import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="POG Product Scanner", layout="wide")
st.title("📦 POG Product Scanner (STORE + ART_NO / EAN_CODE)")

# -------------------------
# Load Excel từ Google Drive
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
# Session state cho input
# -------------------------
if 'art_no_input' not in st.session_state:
    st.session_state.art_no_input = ''
if 'barcode_input' not in st.session_state:
    st.session_state.barcode_input = ''

# Nút Reset
if st.button("Reset"):
    st.session_state.art_no_input = ''
    st.session_state.barcode_input = ''

# -------------------------
# Input ART_NO và BARCODE
# -------------------------
art_no_input = st.text_area(
    "Nhập MÃ HÀNG (có thể nhiều mã, cách nhau bằng dấu phẩy hoặc xuống dòng)",
    value=st.session_state.art_no_input,
    key="art_no_input"
)

barcode_input = st.text_area(
    "Nhập BARCODE (có thể nhiều mã, cách nhau bằng dấu phẩy hoặc xuống dòng)",
    value=st.session_state.barcode_input,
    key="barcode_input"
)

# Nếu nhập ART_NO → xóa barcode; nhập barcode → xóa ART_NO
if art_no_input.strip():
    st.session_state.barcode_input = ''
elif barcode_input.strip():
    st.session_state.art_no_input = ''

# -------------------------
# Chia chuỗi thành danh sách số
# -------------------------
def parse_multiple_ids(text):
    if not text:
        return []
    # loại bỏ khoảng trắng và xuống dòng, tách theo dấu , hoặc xuống dòng
    items = [i.strip() for i in text.replace("\n", ",").split(",") if i.strip()]
    return [int(i) for i in items if i.isdigit()]

art_no_list = parse_multiple_ids(st.session_state.art_no_input)
barcode_list = parse_multiple_ids(st.session_state.barcode_input)

# -------------------------
# Lookup dữ liệu
# -------------------------
if art_no_list:
    result_df = df_store[df_store['ART_NO'].isin(art_no_list)]
elif barcode_list:
    result_df = df_store[df_store['EAN_CODE'].isin(barcode_list)]
else:
    result_df = pd.DataFrame()

# -------------------------
# Hiển thị bảng
# -------------------------
if not result_df.empty:
    st.subheader("Kết quả tìm kiếm")
    st.dataframe(result_df.reset_index(drop=True))
elif st.session_state.art_no_input or st.session_state.barcode_input:
    st.error("Không tìm thấy dữ liệu trong STORE đã chọn")

# Footer
st.markdown("---")
st.markdown("tui làm đó CANDO ✌️")
