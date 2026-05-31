import streamlit as st
import pandas as pd

st.set_page_config(page_title="POG Product Scanner", layout="wide")
st.title("📦 POG Product Scanner (STORE + ART_NO / EAN_CODE)")

# ---------- Load dữ liệu từ file Excel đã upload ----------
df = pd.read_excel("data.xlsx", engine="openpyxl")

# ---------- Chọn STORE ----------
store_list = sorted(df['STORE'].dropna().unique().tolist())
selected_store = st.selectbox("Chọn STORE để tìm:", store_list)
df_store = df[df['STORE'] == selected_store]

# ---------- Session state chỉ giữ kết quả ----------
if "result_df" not in st.session_state:
    st.session_state["result_df"] = pd.DataFrame()

# ---------- Hai ô input ----------
art_no_input = st.text_area("Nhập MÃ HÀNG (ART_NO)", height=100)
barcode_input = st.text_area("Nhập BARCODE (EAN_CODE)", height=100)

col1, col2 = st.columns([1,1])

# ---------- Nút Tìm kiếm ----------
with col1:
    if st.button("Tìm kiếm"):
        # Nhập ART_NO → xóa barcode
        if art_no_input.strip():
            barcode_input = ""
        # Nhập barcode → xóa ART_NO
        elif barcode_input.strip():
            art_no_input = ""

        # Parse input thành list số
        def parse_ids(text):
            if not text:
                return []
            items = [i.strip() for i in text.replace("\n", ",").split(",") if i.strip()]
            return [i for i in items if i.isdigit()]

        art_list = parse_ids(art_no_input)
        barcode_list = parse_ids(barcode_input)

        result_df = pd.DataFrame()
        if art_list:
            result_df = df_store[df_store['ART_NO'].astype(str).isin(art_list)]
        elif barcode_list:
            result_df = df_store[df_store['EAN_CODE'].astype(str).isin(barcode_list)]

        # Append kết quả mới vào bảng cũ
        st.session_state["result_df"] = pd.concat(
            [st.session_state["result_df"], result_df]
        ).drop_duplicates().reset_index(drop=True)

# ---------- Nút Reset ----------
with col2:
    if st.button("Reset"):
        st.session_state["result_df"] = pd.DataFrame()
        art_no_input = ""
        barcode_input = ""

# ---------- Hiển thị kết quả ----------
if not st.session_state["result_df"].empty:
    st.subheader("Kết quả tìm kiếm")
    df_display = st.session_state["result_df"].copy()
    df_display.columns = [c.split('(')[0].strip() for c in df_display.columns]
    st.dataframe(df_display, use_container_width=True)

st.markdown("---")
st.markdown("tui làm đó CANDO ✌️")
