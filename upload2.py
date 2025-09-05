import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Cấu hình kết nối tới Google Sheets ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Bí mật tài khoản dịch vụ sẽ được lưu trong secrets của Streamlit
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope,
)
client = gspread.authorize(credentials)

# --- 2. Mở file Google Sheets theo URL ---
sheet_url = "https://docs.google.com/spreadsheets/d/1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY/edit?usp=sharing"
spreadsheet = client.open_by_url(sheet_url)

# --- 3. Lấy danh sách sheet (tab) -->
worksheets = spreadsheet.worksheets()
sheet_names = [ws.title for ws in worksheets]

# --- 4. Sidebar cho phép chọn sheet ---
selected_sheet = st.sidebar.selectbox("Chọn sheet để xem:", sheet_names)

# --- 5. Đọc dữ liệu từ sheet đã chọn ---
worksheet = spreadsheet.worksheet(selected_sheet)
records = worksheet.get_all_records()
df = pd.DataFrame(records)

# --- 6. Hiển thị dữ liệu ---
st.title("🔍 Xem dữ liệu từ Google Sheets")
st.write(f"**File:** theo mã hàng")
st.subheader(f"Sheet đang xem: **{selected_sheet}**")
st.dataframe(df)

# --- 7. (Tuỳ chọn) Hiển thị ảnh nếu có cột URL ảnh ---
if "image" in df.columns:
    st.subheader("Hình ảnh minh hoạ")
    for idx, row in df.iterrows():
        img_url = row.get("image")
        name = row.get("name", "")
        if img_url:
            st.image(img_url, caption=name, use_column_width=True)

# --- 8. (Tuỳ chọn) Lọc theo tên sản phẩm hoặc mã ---
st.subheader("Tìm kiếm nhanh")
search_term = st.text_input("Nhập id hoặc name để lọc:")
if search_term:
    filtered = df[df.apply(lambda row: search_term.lower() in str(row["id"]).lower() or search_term.lower() in str(row["name"]).lower(), axis=1)]
    st.write(f"### Kết quả lọc cho '{search_term}':")
    st.dataframe(filtered)
