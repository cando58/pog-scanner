import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="POG Product Scanner Online", layout="wide")
st.title("😍 POG Product Scanner Online (by CANDO)")

# ---------- Load dữ liệu từ Google Drive với progress ----------
def load_data_with_progress(file_id):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url, stream=True)
    total_length = response.headers.get('content-length')

    if total_length is None:  # không biết size
        return pd.read_excel(BytesIO(response.content), engine="openpyxl")
    else:
        total_length = int(total_length)
        chunk_size = 1024 * 1024  # 1 MB
        data = BytesIO()
        progress_bar = st.progress(0)
        downloaded = 0

        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                data.write(chunk)
                downloaded += len(chunk)
                progress_bar.progress(min(int(downloaded / total_length * 100), 100))

        data.seek(0)
        return pd.read_excel(data, engine="openpyxl")

# ---------- Load dữ liệu ----------
file_id = "1yw8xkayu14zXy4syuO7Imrdz7FsD7o_L"
df = load_data_with_progress(file_id)
st.success("Đã tải dữ liệu thành công!")
st.write(df.head())
