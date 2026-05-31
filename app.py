import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# --- Page config ---
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

# ---------- Khởi tạo session_state ----------
if "art_no_input" not in st.session_state:
    st.session_state["art_no_input"] = ""
if "barcode_input" not in st.session_state:
    st.session_state["barcode_input"] = ""
if "result_df" not in st.session_state:
    st.session_state["result_df"] = pd.DataFrame()

# ---------- Form nhập liệu ----------
with st.form(key="search_form"):
    art_no_input = st.text_area(
        "Nhập MÃ HÀNG (có thể nhiều mã, dấu , hoặc xuống dòng)",
        value=st.session_state["art_no_input"],
        key="art_no_input_area",
        height=100
    )
    barcode_input = st.text_area(
        "Nhập BARCODE (có thể nhiều mã, dấu , hoặc xuống dòng)",
        value=st.session_state["barcode_input"],
        key="barcode_input_area",
        height=100
    )
    submitted = st.form_submit_button("Tìm kiếm")
    reset = st.form_submit_button("Reset")

# ---------- Reset input + kết quả ----------
if reset:
    st.session_state["art_no_input"] = ""
    st.session_state["barcode_input"] = ""
    st.session_state["result_df"] = pd.DataFrame()
    st.success("Đã reset toàn bộ")

# ---------- Xử lý logic tìm kiếm ----------
if submitted:
    # Nếu nhập ART_NO → bỏ barcode, nếu nhập barcode → bỏ ART_NO
    art_no_text = art_no_input.strip()
    barcode_text = barcode_input.strip()

    # Hàm parse input thành danh sách số
    def parse_ids(text):
        if not text:
            return []
        items = [i.strip() for i in text.replace("\n", ",").split(",") if i.strip()]
        return [int(i) for i in items if i.isdigit()]

    art_no_list = parse_ids(art_no_text)
    barcode_list = parse_ids(barcode_text)

    # Lookup dữ liệu
    result_df = pd.DataFrame()
    if art_no_list:
        barcode_list = []  # bỏ barcode khi dùng ART_NO
        st.session_state["barcode_input"] = ""
        result_df = df_store[df_store['ART_NO'].isin(art_no_list)]
    elif barcode_list:
        art_no_list = []  # bỏ ART_NO khi dùng barcode
        st.session_state["art_no_input"] = ""
        result_df = df_store[df_store['EAN_CODE'].isin(barcode_list)]

    # Lưu kết quả vào session_state
    st.session_state["result_df"] = result_df

# ---------- Hiển thị kết quả ----------
if not st.session_state["result_df"].empty:
    st.subheader("Kết quả tìm kiếm")
    # Hiển thị bảng reset index, bỏ dấu ()
    df_display = st.session_state["result_df"].copy()
    df_display.columns = [c.split('(')[0].strip() for c in df_display.columns]
    st.dataframe(df_display.reset_index(drop=True))

st.markdown("---")
st.markdown("tui làm đó CANDO ✌️")
