import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Quản lý nguyên phụ liệu", layout="wide")

# =========================
# KẾT NỐI GOOGLE SHEET
# =========================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

SHEET_ID = "1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY"   # thay bằng ID thật
sheet = client.open_by_key(SHEET_ID).sheet1

# =========================
# ĐỌC DỮ LIỆU LẦN ĐẦU
# =========================
if "df" not in st.session_state:
    data = sheet.get_all_records()
    st.session_state.df = pd.DataFrame(data)

df = st.session_state.df

st.title("📦 Quản lý nguyên phụ liệu theo mã hàng")

st.info("Bạn có thể thêm dòng mới, sửa dữ liệu hoặc xoá dòng trực tiếp. "
        "Mọi thay đổi sẽ được đồng bộ lên Google Sheet.")

# =========================
# HIỂN THỊ VÀ CHO PHÉP CHỈNH SỬA TRỰC TIẾP
# =========================
edited_df = st.data_editor(
    df,
    num_rows="dynamic",   # cho phép thêm dòng mới
    use_container_width=True,
    key="editor"
)

# =========================
# ĐỒNG BỘ VỚI GOOGLE SHEET
# =========================
if not edited_df.equals(df):
    st.session_state.df = edited_df

    # Xóa toàn bộ dữ liệu cũ
    sheet.clear()

    # Ghi header + dữ liệu mới
    sheet.update(
        [edited_df.columns.values.tolist()] +
        edited_df.fillna("").values.tolist()
    )

    st.success("✅ Đã đồng bộ thay đổi với Google Sheet")
