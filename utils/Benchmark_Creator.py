import streamlit as st
import pandas as pd
import os
import random
from PIL import Image
import numpy as np
from collections import Counter
import openpyxl
from pathlib import Path

# --- CONFIG ---
DATASET_FOLDER = 'C:/Users/Acer/OneDrive/Desktop/NCKH/Dataset/ViVQA4Edu'
CSV_PATH = 'C:/Users/Acer/OneDrive/Desktop/NCKH/Dataset/ViVQA4Edu-CSV/Verify/Verify_100.csv'
BENCHMARK_SAVE_PATH = r'D:\IT\GITHUB\FinalProject_DataLabeling\benchmark_dataset.csv'
STATS_SAVE_PATH = r'D:\IT\GITHUB\FinalProject_DataLabeling\benchmark_stats.xlsx'

# Set page config
st.set_page_config(
    page_title="Benchmark Creator",
    page_icon="📊",
    layout="wide"
)

# Tiêu đề trang
st.title("🔖 Công cụ tạo Benchmark Dataset ViEduVQA")

# Initialize session state variables if they don't exist
if 'selected_images' not in st.session_state:
    st.session_state.selected_images = None
if 'image_qa_pairs' not in st.session_state:
    st.session_state.image_qa_pairs = None
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'labeling_complete' not in st.session_state:
    st.session_state.labeling_complete = False
if 'labeled_data' not in st.session_state:
    st.session_state.labeled_data = []

# Function to get image IDs from dataset folder
def get_image_ids_by_category():
    categories = {}
    for folder in os.listdir(DATASET_FOLDER):
        folder_path = os.path.join(DATASET_FOLDER, folder)
        if os.path.isdir(folder_path):
            images = [f.split('.')[0] for f in os.listdir(folder_path) if f.endswith('.png')]
            categories[folder] = images
    return categories

# Function to identify images that have QA pairs in the CSV
def get_images_with_qa_pairs(categories, csv_path):
    # Load CSV data
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['ImageID', 'Question', 'Answer'])
    
    # Create dictionary to store images with QA pairs by category
    images_with_qa = {}
    
    for category, images in categories.items():
        images_with_qa[category] = []
        for image_id in images:
            if not df[df['ImageID'] == image_id].empty:
                images_with_qa[category].append(image_id)
    
    return images_with_qa

# Function to sample images - ensure we get EXACTLY 50 per category for 250 total
def sample_images_for_benchmark(categories, n_per_category=50):
    # First, get images that have QA pairs
    images_with_qa = get_images_with_qa_pairs(categories, CSV_PATH)
    
    selected_images = {}
    insufficient_categories = []
    
    for category, images in images_with_qa.items():
        if len(images) >= n_per_category:
            selected = random.sample(images, n_per_category)
            selected_images[category] = selected
        else:
            insufficient_categories.append((category, len(images)))
            selected_images[category] = images  # Take all available images
    
    # If any category has insufficient images, notify the user
    if insufficient_categories:
        for category, count in insufficient_categories:
            st.warning(f"Loại {category} chỉ có {count} ảnh có cặp QA, ít hơn yêu cầu {n_per_category}")
        st.error("Không đủ ảnh có cặp QA để tạo benchmark dataset. Vui lòng kiểm tra dữ liệu.")
        return None
        
    return selected_images

# Function to match images with QA pairs
def match_images_with_qa_pairs(selected_images, csv_path):
    # Load CSV data
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['ImageID', 'Question', 'Answer'])
    
    # Create a list to store image-QA pairs
    image_qa_pairs = []
    
    # For each category and its images
    for category, images in selected_images.items():
        for image_id in images:
            # Find matching QA pairs
            image_rows = df[df['ImageID'] == image_id]
            if not image_rows.empty:
                # Take only the first QA pair for this image
                first_row = image_rows.iloc[0]
                image_qa_pairs.append({
                    'Category': category,
                    'ImageID': image_id,
                    'Question': first_row['Question'],
                    'Answer': first_row['Answer'],
                    'ImagePath': os.path.join(DATASET_FOLDER, category, image_id + '.png')
                })
    
    # Kiểm tra tổng số ảnh và thông báo
    total_image_qa_pairs = len(image_qa_pairs)
    if total_image_qa_pairs != 250:
        st.error(f"Chỉ tạo được {total_image_qa_pairs} cặp ảnh-QA thay vì 250 cặp yêu cầu.")
        return None
    
    return image_qa_pairs

# Function to move to next item
def next_item():
    if st.session_state.current_index < len(st.session_state.image_qa_pairs) - 1:
        st.session_state.current_index += 1
        st.rerun()
    else:
        st.session_state.labeling_complete = True
        st.rerun()

# Function to go back to previous item
def prev_item():
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1
        st.rerun()

# Function to save labeled data
def save_benchmark():
    df = pd.DataFrame(st.session_state.labeled_data)
    df.to_csv(BENCHMARK_SAVE_PATH, index=False)
    return df

# Function to generate statistics
def generate_statistics(df):
    total_samples = len(df)
    incorrect_samples = len(df[df['IsCorrect'] == 'Sai'])
    
    # Statistics by category
    category_stats = df.groupby('Category')['IsCorrect'].apply(
        lambda x: (len(x), sum(x == 'Sai'), sum(x == 'Sai') / len(x) * 100 if len(x) > 0 else 0)
    ).reset_index()
    category_stats.columns = ['Category', 'Statistics']
    category_stats[['Tổng', 'Số lỗi', 'Tỉ lệ lỗi (%)']] = pd.DataFrame(category_stats['Statistics'].tolist(), index=category_stats.index)
    category_stats = category_stats.drop('Statistics', axis=1)
    
    # Statistics by error type
    error_types = df[df['IsCorrect'] == 'Sai']['ErrorType'].value_counts().reset_index()
    error_types.columns = ['Loại lỗi', 'Số lượng']
    
    # Thống kê độ tự nhiên
    naturalness_counts = df['Naturalness'].value_counts().reset_index()
    naturalness_counts.columns = ['Độ tự nhiên', 'Số lượng']
    
    # Thống kê độ phức tạp
    complexity_counts = df['Complexity'].value_counts().reset_index()
    complexity_counts.columns = ['Độ phức tạp', 'Số lượng']
    
    # Create statistics dictionary
    stats = {
        'total_samples': total_samples,
        'incorrect_samples': incorrect_samples,
        'error_rate': incorrect_samples / total_samples * 100 if total_samples > 0 else 0,
        'category_stats': category_stats,
        'error_types': error_types,
        'naturalness_counts': naturalness_counts,
        'complexity_counts': complexity_counts
    }
    
    return stats

# Function to save statistics
def save_statistics(stats):
    # Ensure directory exists
    Path(os.path.dirname(STATS_SAVE_PATH)).mkdir(parents=True, exist_ok=True)
    
    # Overall stats
    overall = pd.DataFrame({
        'Thống kê': ['Tổng số mẫu', 'Số mẫu có lỗi', 'Tỉ lệ lỗi (%)'],
        'Giá trị': [stats['total_samples'], stats['incorrect_samples'], f"{stats['error_rate']:.2f}"]
    })
    
    # Save to Excel
    with pd.ExcelWriter(STATS_SAVE_PATH, engine='openpyxl') as writer:
        overall.to_excel(writer, sheet_name='Tổng quan', index=False)
        stats['category_stats'].to_excel(writer, sheet_name='Thống kê theo loại', index=False)
        stats['error_types'].to_excel(writer, sheet_name='Thống kê lỗi', index=False)
        stats['naturalness_counts'].to_excel(writer, sheet_name='Độ tự nhiên', index=False)
        stats['complexity_counts'].to_excel(writer, sheet_name='Độ phức tạp', index=False)
    
    return True

# SIDEBAR
st.sidebar.title("🎯 Tạo Benchmark")

# Step 1: Sample images
if st.sidebar.button("🔄 Chọn ngẫu nhiên 250 ảnh (50 mỗi loại)"):
    with st.spinner("Đang chọn ảnh ngẫu nhiên..."):
        categories = get_image_ids_by_category()
        st.session_state.selected_images = sample_images_for_benchmark(categories)
        
        if st.session_state.selected_images is not None:
            st.session_state.image_qa_pairs = match_images_with_qa_pairs(st.session_state.selected_images, CSV_PATH)
            st.session_state.current_index = 0
            st.session_state.labeled_data = []
            st.session_state.labeling_complete = False
            st.rerun()

# Display progress
if st.session_state.image_qa_pairs is not None:
    progress_value = st.session_state.current_index / len(st.session_state.image_qa_pairs)
    st.sidebar.progress(progress_value)
    st.sidebar.text(f"Tiến độ: {st.session_state.current_index + 1}/{len(st.session_state.image_qa_pairs)}")

# Main content
if st.session_state.image_qa_pairs is None:
    st.info("Vui lòng nhấn 'Chọn ngẫu nhiên 250 ảnh' ở sidebar để bắt đầu.")

elif st.session_state.labeling_complete:
    st.success("🎉 Hoàn thành gán nhãn! Bên dưới là kết quả.")
    
    # Save benchmark
    labeled_df = save_benchmark()
    st.write("### Benchmark Dataset")
    st.dataframe(labeled_df)
    
    # Generate and display statistics
    stats = generate_statistics(labeled_df)
    
    st.write("### Thống kê")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tổng số mẫu", stats['total_samples'])
        st.metric("Số mẫu có lỗi", stats['incorrect_samples'])
    with col2:
        st.metric("Tỉ lệ lỗi", f"{stats['error_rate']:.2f}%")
    
    st.write("### Thống kê theo loại")
    st.dataframe(stats['category_stats'])
    
    st.write("### Thống kê lỗi")
    st.dataframe(stats['error_types'])
    
    st.write("### Thống kê độ tự nhiên")
    st.dataframe(stats['naturalness_counts'])
    
    st.write("### Thống kê độ phức tạp")
    st.dataframe(stats['complexity_counts'])
    
    # Save statistics
    if st.button("💾 Lưu thống kê"):
        save_statistics(stats)
        st.success(f"Đã lưu thống kê vào {STATS_SAVE_PATH}")

else:
    # Get current image-QA pair
    current_pair = st.session_state.image_qa_pairs[st.session_state.current_index]
    
    # Display image and QA pair
    st.subheader(f"Ảnh thuộc loại: {current_pair['Category']}")
    
    # Form toàn bộ label
    with st.form(key=f"label_form_{st.session_state.current_index}"):
        cols = st.columns([1.2, 2])
        
        with cols[0]:
            if os.path.exists(current_pair['ImagePath']):
                st.image(Image.open(current_pair['ImagePath']), caption=current_pair['ImageID'], use_column_width=True)
            else:
                st.error(f"Không tìm thấy ảnh: {current_pair['ImagePath']}")
        
        with cols[1]:
            st.markdown(f"**Câu hỏi:** {current_pair['Question']}")
            st.markdown(f"**Câu trả lời:** {current_pair['Answer']}")
            
            st.subheader("1. Độ đúng của câu trả lời")
            correctness = st.radio("Đúng hay sai?", ['Đúng', 'Sai'], key=f'correct_{st.session_state.current_index}')
             
            st.subheader("2. Loại câu hỏi")
            qtype = st.selectbox("Chọn loại:", ['LOC', 'CNT', 'OBJ', 'ACT', 'INF', 'REL', 'TXT', 'OTH'], key=f'qtype_{st.session_state.current_index}')
            
            error_type = None

            st.subheader("3. Lỗi câu trả lời")
            error_type = st.selectbox("Chọn lỗi:", [
                    'Không có lỗi', 'Sai sự thật', 'Thiếu thông tin', 'Thừa thông tin',
                    'Mơ hồ', 'Lỗi ngữ pháp-chính tả', 'Không trả lời'
                ], key=f'error_{st.session_state.current_index}')
            
            st.subheader("Đề xuất cải thiện")
            suggested_question = st.text_area("Câu hỏi cải thiện:", 
                                            value=current_pair['Question'],
                                            key=f"sugg_q_{st.session_state.current_index}")
            
            suggested_answer = st.text_area("Câu trả lời cải thiện:",
                                           value=current_pair['Answer'],
                                           key=f"sugg_a_{st.session_state.current_index}")
        
        # Form buttons
        col_prev, col_submit, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            prev_button = st.form_submit_button("⬅️ Trước")
        
        with col_submit:
            submit_button = st.form_submit_button("💾 Lưu và tiếp tục")
        
        with col_next:
            next_button = st.form_submit_button("➡️ Bỏ qua")
        
        if submit_button:
            # Save current labeling data
            labeled_item = {
                'Category': current_pair['Category'],
                'ImageID': current_pair['ImageID'],
                'Question': current_pair['Question'],
                'Answer': current_pair['Answer'],
                'IsCorrect': correctness,
                'QuestionType': qtype,
                'ErrorType': error_type if correctness == 'Sai' else "Không có lỗi",
                'SuggestedQuestion': suggested_question,
                'SuggestedAnswer': suggested_answer
            }
            
            # Check if we're editing an existing item
            if st.session_state.current_index < len(st.session_state.labeled_data):
                st.session_state.labeled_data[st.session_state.current_index] = labeled_item
            else:
                st.session_state.labeled_data.append(labeled_item)
            
            next_item()
        
        elif next_button:
            next_item()
        
        elif prev_button:
            prev_item()

# SIDEBAR: Xem lại dữ liệu đã gán nhãn
if st.session_state.labeled_data:
    st.sidebar.markdown("---")
    st.sidebar.title("📋 Dữ liệu đã gán nhãn")
    if st.sidebar.button("Xem tất cả dữ liệu đã gán nhãn"):
        if st.session_state.labeled_data:
            labeled_df = pd.DataFrame(st.session_state.labeled_data)
            st.sidebar.dataframe(labeled_df)
        else:
            st.sidebar.info("Chưa có dữ liệu nào được gán nhãn.")