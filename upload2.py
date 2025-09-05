import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Kết nối Google Sheets ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope,
)
client = gspread.authorize(credentials)

# --- 2. Mở file Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY/edit?usp=sharing"
spreadsheet = client.open_by_url(sheet_url)

# --- 3. Lấy danh sách sheet ---
worksheets = spreadsheet.worksheets()
sheet_names = [ws.title for ws in worksheets]

# --- 4. Sidebar chọn sheet ---
selected_sheet = st.sidebar.selectbox("Chọn sheet để xem:", sheet_names)
worksheet = spreadsheet.worksheet(selected_sheet)

# --- 5. Đọc dữ liệu ---
records = worksheet.get_all_records()
df = pd.DataFrame(records)

# --- 6. Hiển thị dữ liệu ---
st.title("🔍 Quản lý dữ liệu Google Sheets")
st.subheader(f"Sheet đang xem: **{selected_sheet}**")
st.dataframe(df)

# --- 7. Hiển thị ảnh (nếu có cột image) ---
if "image" in df.columns:
    st.subheader("Hình ảnh minh hoạ")
    for idx, row in df.iterrows():
        img_url = row.get("image")
        name = row.get("name", "")
        if img_url:
            st.image(img_url, caption=name, use_column_width=True)

# --- 8. Tìm kiếm nhanh ---
st.subheader("🔎 Tìm kiếm")
search_term = st.text_input("Nhập id hoặc name để lọc:")
if search_term:
    filtered = df[df.apply(
        lambda row: search_term.lower() in str(row["id"]).lower() 
        or search_term.lower() in str(row["name"]).lower(), axis=1)]
    st.write(f"### Kết quả lọc cho '{search_term}':")
    st.dataframe(filtered)

# --- 9. Nhập dữ liệu mới ---
st.subheader("✍️ Thêm dữ liệu mới vào sheet")

with st.form("add_row_form"):
    new_id = st.text_input("ID sản phẩm")
    new_name = st.text_input("Tên sản phẩm")
    new_quanty= st.text_input("Số lượng")
    submitted = st.form_submit_button("Thêm")

    if submitted:
        # Chuẩn bị dòng dữ liệu mới
        new_row = [new_id, new_name, new quanty]

        # Thêm vào cuối sheet
        worksheet.append_row(new_row)

        st.success("✅ Đã thêm dữ liệu thành công! Vui lòng reload để xem kết quả.")
