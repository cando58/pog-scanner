import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="POG Product Scanner", layout="wide")
st.title("📦 POG Product Scanner (STORE + ART_NO / EAN_CODE)")

# ---------- Load dữ liệu từ Google Drive ----------
file_id = "1yw8xkayu14zXy4syuO7Imrdz7FsD7o_L"
url = f"https://drive.google.com/uc?export=download&id={file_id}"
resp = requests.get(url)
df = pd.read_excel(BytesIO(resp.content), engine="openpyxl")

# ---------- Chọn STORE ----------
store_list = sorted(df['STORE'].dropna().unique().tolist())
selected_store = st.selectbox("Chọn STORE để tìm:", store_list)
df_store = df[df['STORE'] == selected_store]

# ---------- Session state ----------
if "art_no_input" not in st.session_state:
    st.session_state["art_no_input"] = ""
if "barcode_input" not in st.session_state:
    st.session_state["barcode_input"] = ""
if "result_df" not in st.session_state:
    st.session_state["result_df"] = pd.DataFrame()

# ---------- Nhập liệu ----------
art_no_input = st.text_area(
    "Nhập MÃ HÀNG (có thể nhiều mã, dấu , hoặc xuống dòng)",
    value=st.session_state["art_no_input"],
    height=100
)

barcode_input = st.text_area(
    "Nhập BARCODE (có thể nhiều mã, dấu , hoặc xuống dòng)",
    value=st.session_state["barcode_input"],
    height=100
)

col1, col2 = st.columns([1,1])
with col1:
    if st.button("Tìm kiếm"):
        # Nếu nhập ART_NO → xóa barcode, nếu nhập barcode → xóa ART_NO
        if art_no_input.strip():
            st.session_state["barcode_input"] = ""
        elif barcode_input.strip():
            st.session_state["art_no_input"] = ""

        # Parse input thành danh sách số
        def parse_ids(text):
            if not text:
                return []
            items = [i.strip() for i in text.replace("\n", ",").split(",") if i.strip()]
            return [int(i) for i in items if i.isdigit()]

        art_no_list = parse_ids(art_no_input)
        barcode_list = parse_ids(barcode_input)

        # Lookup dữ liệu
        result_df = pd.DataFrame()
        if art_no_list:
            result_df = df_store[df_store['ART_NO'].isin(art_no_list)]
        elif barcode_list:
            result_df = df_store[df_store['EAN_CODE'].isin(barcode_list)]

        st.session_state["result_df"] = result_df
        st.session_state["art_no_input"] = art_no_input
        st.session_state["barcode_input"] = barcode_input

with col2:
    if st.button("Reset"):
        # Xóa toàn bộ session_state input + kết quả
        st.session_state["art_no_input"] = ""
        st.session_state["barcode_input"] = ""
        st.session_state["result_df"] = pd.DataFrame()
        st.success("Đã reset toàn bộ")

# ---------- Hiển thị kết quả ----------
if not st.session_state["result_df"].empty:
    st.subheader("Kết quả tìm kiếm")
    st.dataframe(st.session_state["result_df"].reset_index(drop=True))

st.markdown("---")
st.markdown("tui làm đó CANDO ✌️")
