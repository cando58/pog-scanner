import streamlit as st
import pandas as pd
from io import BytesIO
import requests

st.set_page_config(page_title="😍 POG Product Scanner Online (by CANDO)", layout="wide")
st.title("😍 POG Product Scanner Online (by CANDO)")

# ---------- Load dữ liệu từ Google Drive ----------
@st.cache_data(show_spinner=True)
def load_data_from_drive(file_id: str):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    return pd.read_excel(BytesIO(resp.content), engine="openpyxl")

file_id = "1yw8xkayu14zXy4syuO7Imrdz7FsD7o_L"
df = load_data_from_drive(file_id)
st.success("📥 Dữ liệu đã tải từ Google Drive!")

# ---------- Chọn STORE ----------
store_list = sorted(df['STORE'].dropna().unique().tolist())
selected_store = st.selectbox("Chọn STORE để tìm:", store_list)
df_store = df[df['STORE'] == selected_store]

# ---------- Session state ----------
for key in ["art_no_input", "barcode_input", "result_df", "reset_clicks"]:
    if key not in st.session_state:
        if key == "result_df":
            st.session_state[key] = pd.DataFrame()
        elif key == "reset_clicks":
            st.session_state[key] = 0
        else:
            st.session_state[key] = ""

# ---------- Input ----------
art_no_input = st.text_area(
    "Nhập MÃ HÀNG (ART_NO, nhiều mã cách nhau , hoặc xuống dòng)",
    value=st.session_state["art_no_input"], height=100
)
barcode_input = st.text_area(
    "Nhập BARCODE (EAN_CODE, nhiều mã cách nhau , hoặc xuống dòng)",
    value=st.session_state["barcode_input"], height=100
)

col1, col2 = st.columns([1,1])

# ---------- Tìm kiếm ----------
with col1:
    if st.button("Tìm kiếm"):
        art_text = art_no_input.strip()
        barcode_text = barcode_input.strip()

        # ART_NO nhập → xóa barcode, BARCODE nhập → xóa ART_NO
        if art_text:
            barcode_text = ""
        elif barcode_text:
            art_text = ""

        st.session_state["art_no_input"] = art_text
        st.session_state["barcode_input"] = barcode_text

        def parse_ids(text):
            if not text:
                return []
            items = [i.strip() for i in text.replace("\n", ",").split(",") if i.strip()]
            return [i for i in items if i.isdigit()]

        art_list = parse_ids(art_text)
        barcode_list = parse_ids(barcode_text)

        new_result = pd.DataFrame()
        if art_list:
            new_result = df_store[df_store['ART_NO'].astype(str).isin(art_list)]
        if barcode_list:
            new_result = pd.concat([
                new_result,
                df_store[df_store['EAN_CODE'].astype(str).isin(barcode_list)]
            ], ignore_index=True).drop_duplicates()

        # Append vào session_state (giữ tạm lỗi lần nhập thứ 2)
        st.session_state["result_df"] = pd.concat([
            st.session_state["result_df"], new_result
        ]).drop_duplicates().reset_index(drop=True)

# ---------- Reset ----------
with col2:
    if st.button("Reset (2 lần để xóa toàn bộ)"):
        st.session_state["reset_clicks"] += 1
        if st.session_state["reset_clicks"] >= 2:
            st.session_state["art_no_input"] = ""
            st.session_state["barcode_input"] = ""
            st.session_state["result_df"] = pd.DataFrame()
            st.session_state["reset_clicks"] = 0
            st.success("🔄 Đã reset toàn bộ input và kết quả (bấm 2 lần để xóa)")
        else:
            st.warning("⚠ Nhấn lần 2 để xóa toàn bộ input và kết quả")

# ---------- Hiển thị kết quả ----------
if not st.session_state["result_df"].empty:
    st.subheader("Kết quả tìm kiếm")
    df_display = st.session_state["result_df"].copy()
    df_display.columns = [c.split('(')[0].strip() for c in df_display.columns]
    st.dataframe(df_display.reset_index(drop=True), use_container_width=True)

st.markdown("---")
st.markdown("tui làm đó CANDO ✌️")
