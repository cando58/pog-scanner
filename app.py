import streamlit as st
import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from io import BytesIO

# ---------- Page config ----------
st.set_page_config(page_title="😍 POG Product Scanner Online (by CANDO)", layout="wide")
st.title("😍 POG Product Scanner Online (by CANDO)")

# ---------- OAuth Google Drive ----------
@st.cache_resource
def init_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Lần đầu sẽ mở trình duyệt login Google
    return GoogleDrive(gauth)

drive = init_drive()

# ---------- Load file XLSX từ Google Drive ----------
@st.cache_data(show_spinner=True)
def load_data_from_drive(file_id: str):
    file = drive.CreateFile({'id': file_id})
    file_content = BytesIO()
    file.GetContentFile('temp.xlsx')  # lưu tạm file
    df = pd.read_excel('temp.xlsx', engine='openpyxl')
    return df

file_id = "1yw8xkayu14zXy4syuO7Imrdz7FsD7o_L"  # ID file Google Drive
df = load_data_from_drive(file_id)

# ---------- Chọn STORE ----------
store_list = sorted(df['STORE'].dropna().unique().tolist())
selected_store = st.selectbox("Chọn STORE để tìm:", store_list)
df_store = df[df['STORE'] == selected_store]

# ---------- Session state ----------
for key in ["art_no_input", "barcode_input", "result_df", "reset_count"]:
    if key not in st.session_state:
        if key == "result_df":
            st.session_state[key] = pd.DataFrame()
        elif key == "reset_count":
            st.session_state[key] = 0
        else:
            st.session_state[key] = ""

# ---------- Inputs ----------
art_no_input = st.text_area(
    "Nhập MÃ HÀNG (ART_NO) - nhiều mã, dấu , hoặc xuống dòng",
    value=st.session_state["art_no_input"],
    height=100
)
barcode_input = st.text_area(
    "Nhập BARCODE (EAN_CODE) - nhiều mã, dấu , hoặc xuống dòng",
    value=st.session_state["barcode_input"],
    height=100
)

col1, col2 = st.columns([1,1])

with col1:
    if st.button("Tìm kiếm"):
        # Nhập ART_NO → bỏ BARCODE, Nhập BARCODE → bỏ ART_NO
        if art_no_input.strip():
            barcode_input = ""
            st.session_state["barcode_input"] = ""
        elif barcode_input.strip():
            art_no_input = ""
            st.session_state["art_no_input"] = ""

        # Hàm parse input
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
        st.session_state["reset_count"] += 1
        if st.session_state["reset_count"] == 1:
            # Lần 1 chỉ xóa kết quả
            st.session_state["result_df"] = pd.DataFrame()
            st.warning("Đã xóa kết quả tìm kiếm, nhấn nút Reset lần nữa để xóa hết nội dung nhập.")
        elif st.session_state["reset_count"] >= 2:
            # Lần 2 xóa toàn bộ
            st.session_state["art_no_input"] = ""
            st.session_state["barcode_input"] = ""
            st.session_state["result_df"] = pd.DataFrame()
            st.success("Đã reset toàn bộ input và kết quả.")
            st.session_state["reset_count"] = 0  # reset lại bộ đếm

# ---------- Hiển thị kết quả ----------
if not st.session_state["result_df"].empty:
    st.subheader("Kết quả tìm kiếm")
    df_display = st.session_state["result_df"].copy()
    df_display.columns = [c.split('(')[0].strip() for c in df_display.columns]  # bỏ () trong tên cột
    st.dataframe(df_display.reset_index(drop=True), use_container_width=True)

st.markdown("---")
st.markdown("tui làm đó CANDO ✌️")
