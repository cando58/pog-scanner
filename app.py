import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# ---------- Page config ----------
st.set_page_config(page_title="😍 POG Product Scanner Online (by CANDO)", layout="wide")
st.title("😍 POG Product Scanner Online (by CANDO)")

# ---------- Load dữ liệu từ Google Drive công khai ----------
@st.cache_data(show_spinner=True)
def load_data_from_drive(file_id: str):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    df = pd.read_excel(BytesIO(resp.content), engine="openpyxl")
    return df

file_id = "1yw8xkayu14zXy4syuO7Imrdz7FsD7o_L"  # File Google Drive phải chia sẻ công khai
df = load_data_from_drive(file_id)

# ---------- Chọn STORE ----------
store_list = sorted(df['STORE'].dropna().unique().tolist())
selected_store = st.selectbox("Chọn STORE để tìm:", store_list)
df_store = df[df['STORE'] == selected_store]

# ---------- Session state ----------
for key in ["art_no_input", "barcode_input", "result_df", "reset_counter"]:
    if key not in st.session_state:
        if key == "result_df":
            st.session_state[key] = pd.DataFrame()
        elif key == "reset_counter":
            st.session_state[key] = 0
        else:
            st.session_state[key] = ""

# ---------- Input ----------
art_no_input = st.text_area(
    "Nhập MÃ HÀNG (ART_NO, nhiều mã , hoặc xuống dòng)",
    value=st.session_state["art_no_input"],
    height=100
)
barcode_input = st.text_area(
    "Nhập BARCODE (EAN_CODE, nhiều mã , hoặc xuống dòng)",
    value=st.session_state["barcode_input"],
    height=100
)

col1, col2 = st.columns([1,1])

# ---------- Button Tìm kiếm ----------
with col1:
    if st.button("Tìm kiếm"):
        # Nhập ART_NO → bỏ BARCODE, nhập BARCODE → bỏ ART_NO
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

        # Lưu kết quả vào session_state
        st.session_state["result_df"] = result_df
        st.session_state["art_no_input"] = art_no_input
        st.session_state["barcode_input"] = barcode_input

# ---------- Button Reset ----------
with col2:
    if st.button("Reset"):
        st.session_state["result_df"] = pd.DataFrame()
        st.session_state["reset_counter"] += 1
        if st.session_state["reset_counter"] >= 2:
            st.session_state["art_no_input"] = ""
            st.session_state["barcode_input"] = ""
            st.session_state["reset_counter"] = 0
            st.success("Đã reset toàn bộ input và kết quả")
        else:
            st.warning("Nhấn lần 2 để xóa hoàn toàn input và kết quả")

# ---------- Hiển thị kết quả ----------
if not st.session_state["result_df"].empty:
    st.subheader("Kết quả tìm kiếm")
    df_display = st.session_state["result_df"].copy()
    # Bỏ tên cột trong ()
    df_display.columns = [c.split('(')[0].strip() for c in df_display.columns]
    st.dataframe(df_display.reset_index(drop=True), use_container_width=True)

st.markdown("---")
st.markdown("tui làm đó CANDO ✌️")
