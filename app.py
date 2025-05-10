import streamlit as st
import pandas as pd
from docx import Document
import os
import random

# Load metadata
metadata = pd.read_csv("metadata.csv")

# Session state
if "selected" not in st.session_state:
    st.session_state.selected = []

st.title("📘 Question Setter App")

# Search box
query = st.text_input("Search by Exam Code or File Name")

# Search and filter
if query:
    results = metadata[
        metadata["Exam Code"].str.contains(query, case=False) |
        metadata["File Name"].str.contains(query, case=False)
    ]
else:
    results = metadata.copy()

# Show search results
st.subheader("Search Results")
for i, row in results.iterrows():
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"**{row['Exam Code']}** – {row['File Name']}")
    with col2:
        if st.button("Add", key=f"add_{i}"):
            if row['Exam Code'] not in st.session_state.selected:
                st.session_state.selected.append(row['Exam Code'])

# Show selected items
st.subheader("Selected Files")
for code in st.session_state.selected:
    filename = metadata[metadata["Exam Code"] == code]["File Name"].values[0]
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"{code} – {filename}")
    with col2:
        if st.button("❌", key=f"remove_{code}"):
            st.session_state.selected.remove(code)

# Proceed and Generate
if st.session_state.selected:
    st.markdown("---")
    num = st.number_input("Number of questions", min_value=1, value=5)
    if st.button("Generate"):
        # Extract questions
        all_questions = []
        for code in st.session_state.selected:
            filepath = f"docs/{code}.docx"
            if os.path.exists(filepath):
                doc = Document(filepath)
                for para in doc.paragraphs:
                    text = para.text.strip()
                    if text:
                        all_questions.append(text)
        if not all_questions:
            st.warning("No content found in selected files.")
        else:
            random.shuffle(all_questions)
            final_questions = all_questions[:int(num)]
            new_doc = Document()
            for i, q in enumerate(final_questions, 1):
                new_doc.add_paragraph(f"{i}. {q}")
            output_path = "generated_questions.docx"
            new_doc.save(output_path)
            with open(output_path, "rb") as f:
                st.download_button("📥 Download Generated File", f, file_name="QuestionSet.docx")

