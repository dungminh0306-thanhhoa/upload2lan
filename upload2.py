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

if df.empty:
    st.warning("Google Sheet đang rỗng, hãy thêm dữ liệu mới 👇")
else:
    # Hiển thị & chỉnh sửa từng mã hàng
    for ma_hang in df["Mã hàng"].unique():
        st.subheader(f"📌 Mã hàng: {ma_hang}")

        df_mahang = df[df["Mã hàng"] == ma_hang]

        # Cho phép thêm / sửa / xoá trực tiếp
        edited_df = st.data_editor(
            df_mahang, num_rows="dynamic", key=f"edit_{ma_hang}"
        )

        # =========================
        # ĐỒNG BỘ TỰ ĐỘNG VỚI GOOGLE SHEET
        # =========================
        if not edited_df.equals(df_mahang):
            df_all = df[df["Mã hàng"] != ma_hang]
            st.session_state.df = pd.concat([df_all, edited_df], ignore_index=True)

            # Ghi lại toàn bộ DataFrame vào Google Sheet
            sheet.clear()
            sheet.update(
                [st.session_state.df.columns.values.tolist()] +
                st.session_state.df.values.tolist()
            )

            df = st.session_state.df
            st.success(f"✅ Đã đồng bộ thay đổi của {ma_hang} với Google Sheet")

    st.markdown("---")

# =========================
# FORM THÊM DỮ LIỆU MỚI
# =========================
st.header("➕ Thêm mã hàng mới")

with st.form("add_new"):
    col1, col2 = st.columns(2)

    with col1:
        ma_hang_new = st.text_input("Mã hàng")
        ten_nguyen_phu_lieu = st.text_input("Tên nguyên phụ liệu")
    with col2:
        so_luong = st.number_input("Số lượng", min_value=0, step=1, value=0)
        ghi_chu = st.text_input("Ghi chú")

    submitted = st.form_submit_button("Thêm vào Google Sheet")

    if submitted:
        if not ma_hang_new:
            st.error("❌ Vui lòng nhập Mã hàng")
        else:
            # Chuẩn bị dòng mới
            new_row = {
                "Mã hàng": ma_hang_new,
                "Tên nguyên phụ liệu": ten_nguyen_phu_lieu,
                "Số lượng": so_luong,
                "Ghi chú": ghi_chu
            }

            # Append vào Google Sheet
            headers = sheet.row_values(1)  # lấy header
            row_to_add = [new_row.get(col, "") for col in headers]
            sheet.append_row(row_to_add)

            # Cập nhật DataFrame trong app
            new_df = pd.DataFrame([new_row])
            st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)

            st.success(f"✅ Đã thêm mã hàng {ma_hang_new} vào Google Sheet và app")
