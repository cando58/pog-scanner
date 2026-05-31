import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# ---------- Page config ----------
st.set_page_config(page_title="POG Product Scanner Online", layout="wide")
st.title("📦 POG Product Scanner Online (STORE + ART_NO / EAN_CODE)")

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

# ---------- Input ----------
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
        art_text = art_no_input.strip()
        barcode_text = barcode_input.strip()

        # Nếu ART_NO được nhập → xóa barcode; nếu barcode → xóa ART_NO
        if art_text:
            barcode_text = ""
        elif barcode_text:
            art_text = ""

        def parse_ids(text):
            if not text:
                return []
            items = [i.strip() for i in text.replace("\n", ",").split(",") if i.strip()]
            return [int(i) for i in items if i.isdigit()]

        art_no_list = parse_ids(art_text)
        barcode_list = parse_ids(barcode_text)

        # Lookup dữ liệu
        new_result = pd.DataFrame()
        if art_no_list:
            new_result = df_store[df_store['ART_NO'].isin(art_no_list)]
        elif barcode_list:
            new_result = df_store[df_store['EAN_CODE'].isin(barcode_list)]

        # Cộng dồn kết quả liên tiếp
        st.session_state["result_df"] = pd.concat([st.session_state["result_df"], new_result]).drop_duplicates().reset_index(drop=True)
        st.session_state["art_no_input"] = art_text
        st.session_state["barcode_input"] = barcode_text

with col2:
    if st.button("Reset"):
        # Xóa toàn bộ session_state input và kết quả
        st.session_state["art_no_input"] = ""
        st.session_state["barcode_input"] = ""
        st.session_state["result_df"] = pd.DataFrame()
        st.success("Đã reset toàn bộ input và kết quả")  # thông báo

# ---------- Hiển thị kết quả ----------
if not st.session_state["result_df"].empty:
    st.subheader("Kết quả tìm kiếm")
    df_display = st.session_state["result_df"].copy()
    df_display.columns = [c.split('(')[0].strip() for c in df_display.columns]  # bỏ dấu ()
    st.dataframe(df_display.reset_index(drop=True), use_container_width=True)

st.markdown("---")
st.markdown("tui làm đó CANDO ✌️")
