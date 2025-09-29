import streamlit as st
import pandas as pd
import os
import random
from PIL import Image

# --- CONFIG ---
DATASET_FOLDER = 'C:/Users/Acer/OneDrive/Desktop/NCKH/Dataset/ViVQA4Edu'
CSV_PATH = 'C:/Users/Acer/OneDrive/Desktop/NCKH/Dataset/ViVQA4Edu-CSV/Verify/Verify_100.csv'
LABEL_SAVE_PATH = 'D:/IT/GITHUB/ResearchProject-VLM/labels_output.csv'

# ==== LOAD CSV & DỮ LIỆU ====
df = pd.read_csv(CSV_PATH)
df = df.dropna(subset=['ImageID', 'Question', 'Answer'])

# Load nhãn đã gán
if os.path.exists(LABEL_SAVE_PATH):
    labeled_df = pd.read_csv(LABEL_SAVE_PATH)
    labeled_ids = set(labeled_df['ImageID'] + '_' + labeled_df['Question'])
else:
    labeled_df = pd.DataFrame()
    labeled_ids = set()

# ==== SIDEBAR: Chọn N mẫu ====
st.sidebar.title("🎯 Chọn dữ liệu")
N = st.sidebar.number_input("Số mẫu muốn gán nhãn", value=10, min_value=1, step=1)

if st.sidebar.button("🔀 Chọn ngẫu nhiên N mẫu"):
    unlabeled_df = df[~((df['ImageID'] + '_' + df['Question']).isin(labeled_ids))]
    sampled_df = unlabeled_df.sample(n=min(N, len(unlabeled_df)), random_state=random.randint(0, 9999))
    st.session_state['sampled_df'] = sampled_df.reset_index(drop=True)
    st.session_state['index'] = 0
    st.success("Đã chọn ngẫu nhiên N mẫu!")

# Kiểm tra session
if 'sampled_df' not in st.session_state:
    st.warning("Vui lòng chọn ngẫu nhiên N mẫu ở sidebar.")
    st.stop()

sampled_df = st.session_state['sampled_df']
index = st.session_state.get('index', 0)

# ==== Hiển thị ảnh + thông tin ====
st.title("🔖 Công cụ gán nhãn dữ liệu ViEduVQA")

row = sampled_df.iloc[index]
image_id = row['ImageID']
question = row['Question']
answer = row['Answer']
image_path = os.path.join(DATASET_FOLDER, image_id.split('_')[0], image_id + '.png')

# Form toàn bộ label
with st.form("label_form"):
    cols = st.columns([1.2, 2])

    with cols[0]:
        if os.path.exists(image_path):
            st.image(Image.open(image_path), caption=image_id, use_column_width=True)
        else:
            st.error("Không tìm thấy ảnh: " + image_path)

    with cols[1]:
        st.markdown(f"**Câu hỏi:** {question}")
        st.markdown(f"**Câu trả lời:** {answer}")

        st.subheader("1. Độ đúng của câu trả lời")
        correctness = st.radio("Đúng hay sai?", ['Đúng', 'Sai'], key=f'correct_{index}')

        st.subheader("2. Mức độ tự nhiên")
        naturalness = st.radio("Câu trả lời tự nhiên không?", ['Tự nhiên', 'Không tự nhiên'], key=f'nat_{index}')

        st.subheader("3. Độ phức tạp")
        complexity = st.radio("Câu hỏi - trả lời đơn giản hay phức tạp?", ['Đơn giản', 'Phức tạp'], key=f'comp_{index}')

        st.subheader("4. Loại câu hỏi")
        qtype = st.selectbox("Chọn loại:", ['LOC', 'CNT', 'OBJ', 'ACT', 'INF', 'REL', 'TXT', 'OTH'], key=f'qtype_{index}')

        st.subheader("5. Lỗi câu trả lời")
        atype = st.selectbox("Chọn lỗi (nếu có):", [
            'Không có lỗi', 'Sai sự thật', 'Thiếu thông tin', 'Thừa thông tin',
            'Mơ hồ', 'Lỗi ngữ pháp-chính tả', 'Không trả lời'
        ], key=f'atype_{index}')

    submitted = st.form_submit_button("💾 Lưu và chuyển tiếp")

    if submitted:
        new_row = {
            'ImageID': image_id,
            'Question': question,
            'Answer': answer,
            'Correctness': correctness,
            'Naturalness': naturalness,
            'Complexity': complexity,
            'QuestionType': qtype,
            'AnswerErrorType': atype
        }

        # Ghi vào file
        write_header = not os.path.exists(LABEL_SAVE_PATH)
        pd.DataFrame([new_row]).to_csv(LABEL_SAVE_PATH, mode='a', index=False, header=write_header)
        st.success("✅ Đã lưu nhãn!")

        # Tăng index để chuyển câu tiếp theo
        if index + 1 < len(sampled_df):
            st.session_state['index'] += 1
        else:
            st.session_state['index'] = 0
            st.success("🎉 Đã hoàn tất N mẫu!")
        st.experimental_set_query_params(updated=True)  # Trigger UI refresh

# ==== XEM LẠI NHÃN ====
st.sidebar.markdown("---")
st.sidebar.title("📋 Nhãn đã gán")
if st.sidebar.button("Xem tất cả nhãn"):
    if not labeled_df.empty:
        st.dataframe(labeled_df)
    else:
        st.info("Chưa có nhãn nào được gán.")