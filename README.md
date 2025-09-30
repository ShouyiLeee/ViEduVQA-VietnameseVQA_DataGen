# ViEduVQA-VietnameseVQA_DataGen

## 📌 Introduction
**ViEduVQA-VietnameseVQA_DataGen** is a research project aiming to build a **Vietnamese Visual Question Answering (VQA) dataset** in the context of **primary education**.  
This project leverages **Multimodal Large Language Models (MLLMs)** such as **Google Gemini** to **automatically generate question–answer pairs (Q&A)** from images in **Vietnamese primary school textbooks**.  

The dataset can be used for:
- **Vietnamese VQA tasks** in education.
- **Image Captioning** tasks.
- Research on **data labeling with LLMs**.
- Building **RAG (Retrieval-Augmented Generation)** systems to improve VQA accuracy.


---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/ShouyiLeee/ViEduVQA-VietnameseVQA_DataGen.git
cd ViEduVQA-VietnameseVQA_DataGen
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

Requirements:
- Python ≥ 3.9  
- Google Colab (recommended) or Jupyter Notebook  
- **Google Gemini API Key** (`GOOGLE_API_KEY`)

---

## 🚀 Usage

### 🔹 1. Mount Google Drive (if using Colab)
```python
from google.colab import drive
drive.mount('/content/drive')
```

### 🔹 2. Load images from dataset
```python
from utils import load_image_from_subfolders

folder_path = "Dataset/images"
image_paths = load_image_from_subfolders(folder_path)
```

### 🔹 3. Generate questions from images
```python
from question_generator import generate_questions

questions = generate_questions(image_paths, start=0, end=100)
```

### 🔹 4. Generate answers for the questions
```python
from answer_generator import generate_answers

answers = generate_answers(image_paths, questions)
```

### 🔹 5. Export dataset to CSV
```python
from utils import export_to_csv

export_to_csv(imageID_list, questions, answers, "vqa_dataset.csv")
```

---

## 📊 Dataset Example
After running the pipeline, the dataset looks like this:

| ImageID                | Question                                                     | Answer                                                |  
|------------------------|-------------------------------------------------------------|------------------------------------------------------|  
| Education_000000000001 | Question 1: What is the woman wearing in the picture?        | Answer 1: The woman is wearing a blue Ao Dai.        |  
| Education_000000000002 | Question 1: What is the little girl on stage doing?          | Answer 1: The little girl is singing.                |  
| Education_000000000003 | Question 1: What are the students in the classroom doing?    | Answer 1: The students are taking a test.            |  

---

## 📥 Dataset Access
The released dataset is available on Hugging Face:  
👉 [ViEduVQA on Hugging Face](https://huggingface.co/datasets/D-Truong/ViEduVQA)

---

## 📖 Applications
- Build **Vietnamese VQA datasets** for educational research.  
- Train and evaluate **VQA models**.  
- Automatically generate **questions from textbooks** to support learning.  
- Research on **semi-automatic data labeling using MLLMs**.  

---

## 🛠️ Future Work
- Expand dataset to other education levels (secondary, high school).  
- Integrate **automatic + semi-automatic labeling** pipelines to reduce LLM errors.  
- Add **self-checking modules** to evaluate Q&A quality.  
- Provide dataset access via **Hugging Face Datasets API**.  

---

## 📜 Citation
If you use this dataset or code in your research, please cite:  

```bibtex
@inproceedings{ViEduVQA2025,
  title     = {ViEduVQA: Vietnamese Visual Question Answering Dataset for Primary Education},
  author    = {Truong, Le Trong Dai and others},
  booktitle = {Proceedings of the 17th International IEEE Conference on Knowledge and Systems Engineering (KSE 2025)},
  year      = {2025}
}
```
