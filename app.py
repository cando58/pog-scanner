import streamlit as st
import pandas as pd
from io import BytesIO
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

st.set_page_config(page_title="😍 POG Product Scanner Online (by CANDO)", layout="wide")
st.title("😍 POG Product Scanner Online (by CANDO)")

# ---------- Google Drive API setup ----------
# Lưu JSON credentials Service Account hoặc OAuth client vào Streamlit Secrets
# Ví dụ: st.secrets["gdrive_service_account_json"]
credentials_info = st.secrets["gdrive_service_account_json"]
credentials = Credentials.from_service_account_info(credentials_info, scopes=['https://www.googleapis.com/auth/drive.readonly'])
service = build('drive', 'v3', credentials=credentials)

# ---------- Load file từ Drive ----------
@st.cache_data(show_spinner=True)
def load_file_from_drive(file_id: str):
    request = service.files().get_media(fileId=file_id)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        st.progress(int(status.progress() * 100))
    fh.seek(0)
    df = pd.read_excel(fh, engine="openpyxl")
    return df

# ID file Google Drive
file_id = "1yw8xkayu14zXy4syuO7Imrdz7FsD7o_L"
df = load_file_from_drive(file_id)
st.success("📥 Dữ liệu đã tải xong và cache thành công!")

# ---------- Chọn STORE ----------
store_list = sorted(df['STORE'].dropna().unique())
selected_store = st.selectbox("Chọn STORE để tìm:", store_list)
df_store = df[df['STORE'] == selected_store]

# ---------- Session state ----------
for key in ["art_no_input","barcode_input","result_df","reset_counter"]:
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame() if key=="result_df" else 0 if key=="reset_counter" else ""

# ---------- Inputs ----------
art_no_input = st.text_area("Nhập MÃ HÀNG (ART_NO)", value=st.session_state["art_no_input"], height=100)
barcode_input = st.text_area("Nhập BARCODE (EAN_CODE)", value=st.session_state["barcode_input"], height=100)

col1,col2 = st.columns([1,1])

# ---------- Tìm ART_NO ----------
with col1:
    if st.button("Tìm ART_NO"):
        st.session_state["barcode_input"] = ""
        st.session_state["art_no_input"] = art_no_input.strip()
        art_list = [i.strip() for i in art_no_input.replace("\n",",").split(",") if i.strip().isdigit()]
        new_result = df_store[df_store['ART_NO'].astype(str).isin(art_list)]
        st.session_state["result_df"] = pd.concat([st.session_state["result_df"], new_result]).drop_duplicates().reset_index(drop=True)

# ---------- Tìm BARCODE ----------
with col2:
    if st.button("Tìm BARCODE"):
        st.session_state["art_no_input"] = ""
        st.session_state["barcode_input"] = barcode_input.strip()
        barcode_list = [i.strip() for i in barcode_input.replace("\n",",").split(",") if i.strip().isdigit()]
        new_result = df_store[df_store['EAN_CODE'].astype(str).isin(barcode_list)]
        st.session_state["result_df"] = pd.concat([st.session_state["result_df"], new_result]).drop_duplicates().reset_index(drop=True)

# ---------- Reset 2 lần ----------
if st.button("Reset"):
    st.session_state["reset_counter"] += 1
    if st.session_state["reset_counter"] >= 2:
        st.session_state["art_no_input"] = ""
        st.session_state["barcode_input"] = ""
        st.session_state["result_df"] = pd.DataFrame()
        st.session_state["reset_counter"] = 0
        st.success("Đã reset toàn bộ input và kết quả")
    else:
        st.warning("Nhấn lần 2 để xóa toàn bộ input và kết quả")

# ---------- Hiển thị kết quả ----------
if not st.session_state["result_df"].empty:
    st.subheader("Kết quả tìm kiếm")
    df_display = st.session_state["result_df"].copy()
    df_display.columns = [c.split("(")[0].strip() for c in df_display.columns]
    st.dataframe(df_display.reset_index(drop=True), use_container_width=True)

st.markdown("---")
st.markdown("tui làm đó CANDO ✌️")
