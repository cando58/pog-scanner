import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# ---------- Page config ----------
st.set_page_config(page_title="POG Product Scanner Online", layout="wide")
st.title("😘 POG Product Scanner Online (ByCanDo)")

# ---------- Load dữ liệu từ Google Drive ----------
file_id = "1yw8xkayu14zXy4syuO7Imrdz7FsD7o_L"
url = f"https://drive.google.com/uc?export=download&id={file_id}"
resp = requests.get(url)
df = pd.read_excel(BytesIO(resp.content), engine="openpyxl")

# ---------- Chọn STORE ----------
store_list = sorted(df['STORE'].dropna().unique().tolist())
selected_store = st.selectbox("Chọn STORE để tìm:", store_list)
df_store = df[df['STORE'] == selected_store]

# ---------- Session state khởi tạo ----------
for key in ["art_no_input", "barcode_input", "result_df"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "result_df" else pd.DataFrame()

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

# ---------- Tìm kiếm ----------
with col1:
    if st.button("Tìm kiếm"):
        # ART_NO → xóa barcode, BARCODE → xóa ART_NO nếu nhập theo thứ tự
        if art_no_input.strip() and barcode_input.strip():
            # Nếu cả 2 ô đều nhập, chỉ dùng ô đang được sửa gần nhất
            if st.session_state["last_input"] == "art":
                barcode_input = ""
            else:
                art_no_input = ""

        # Lưu loại input vừa nhập
        if art_no_input.strip():
            st.session_state["last_input"] = "art"
        elif barcode_input.strip():
            st.session_state["last_input"] = "barcode"

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
            barcode_input = ""
        elif barcode_list:
            result_df = df_store[df_store['EAN_CODE'].isin(barcode_list)]
            art_no_input = ""

        # Lưu session_state
        st.session_state["result_df"] = result_df
        st.session_state["art_no_input"] = art_no_input
        st.session_state["barcode_input"] = barcode_input

# ---------- Reset ----------
with col2:
    if st.button("Reset"):
        st.session_state["art_no_input"] = ""
        st.session_state["barcode_input"] = ""
        st.session_state["result_df"] = pd.DataFrame()
        st.session_state["last_input"] = ""
        st.success("Đã reset toàn bộ input và kết quả")

# ---------- Hiển thị kết quả ----------
if not st.session_state["result_df"].empty:
    st.subheader("Kết quả tìm kiếm")
    df_display = st.session_state["result_df"].copy()
    # Loại bỏ tên cột trong dấu ()
    df_display.columns = [c.split('(')[0].strip() for c in df_display.columns]
    st.dataframe(df_display.reset_index(drop=True), use_container_width=True)

st.markdown("---")
st.markdown("Tui làm đó CANDO 🫶")
