import streamlit as st
from docx import Document
import os
import random

# Path to the folder containing question papers
QUESTION_PAPER_DIR = "./docs"

# Function to parse the .docx file and get all the questions
def get_questions_from_docx(file_path):
    doc = Document(file_path)
    questions = []
    for para in doc.paragraphs:
        if para.text.strip():  # Ignore empty paragraphs
            questions.append(para.text.strip())
    return questions

# Load available question paper files from the docs folder
def load_question_papers():
    files = [f for f in os.listdir(QUESTION_PAPER_DIR) if f.endswith(".docx")]
    return files

# Combine selected questions and create a new document
def generate_combined_document(selected_questions):
    doc = Document()
    for idx, questions in selected_questions:
        doc.add_heading(f"Questions from {idx}", level=1)
        for question in questions:
            doc.add_paragraph(question)
    doc_path = "combined_questions.docx"
    doc.save(doc_path)
    return doc_path

# Streamlit UI
def main():
    st.title("Question Setter")

    # Step 1: Display available exam codes (file names)
    files = load_question_papers()
    exam_codes = [f.replace(".docx", "") for f in files]

    # Sidebar for search functionality
    st.sidebar.header("Search and Select Exam Code")
    search_code = st.sidebar.text_input("Enter Exam Code:")
    
    # Filter exam codes based on user input
    if search_code:
        matching_codes = [code for code in exam_codes if search_code.lower() in code.lower()]
    else:
        matching_codes = exam_codes

    # Display the filtered matching exam codes
    st.sidebar.subheader("Matching Exam Codes:")
    for code in matching_codes:
        st.sidebar.write(f"- {code}")

    # Initialize session state if not already
    if 'selected_questions' not in st.session_state:
        st.session_state.selected_questions = {}
    if 'exam_codes_to_select' not in st.session_state:
        st.session_state.exam_codes_to_select = []

    # Step 2: Add selected exam code to the list
    if search_code and st.sidebar.button("Add Exam Code"):
        if search_code not in st.session_state.exam_codes_to_select:
            st.session_state.exam_codes_to_select.append(search_code)
            st.sidebar.write(f"{search_code} added to selection.")
        else:
            st.sidebar.write(f"{search_code} is already added.")
    
    # Step 3: Allow user to select number of questions from each added exam code
    for exam_code in st.session_state.exam_codes_to_select:
        st.write(f"Exam Code: {exam_code}")
        file_path = f"{QUESTION_PAPER_DIR}/{exam_code}.docx"
        questions = get_questions_from_docx(file_path)
        st.write(f"Total Questions in the file: {len(questions)}")

        num_questions = st.number_input(f"How many questions to select from {exam_code}?", min_value=1, max_value=len(questions), step=1)

        if st.button(f"Add to Selection from {exam_code}"):
            selected = random.sample(questions, num_questions)
            st.session_state.selected_questions[exam_code] = selected
            st.write(f"Selected {num_questions} questions from {exam_code}")

    # Step 4: Show selected questions list
    st.subheader("Selected Questions")
    if st.session_state.selected_questions:
        for code, questions in st.session_state.selected_questions.items():
            st.write(f"Questions from {code}:")
            for idx, question in enumerate(questions, start=1):
                st.write(f"{idx}. {question}")
    else:
        st.write("No questions selected yet.")

    # Step 5: Proceed button to generate combined document
    if st.button("Proceed to Generate"):
        if not st.session_state.selected_questions:
            st.warning("Please select at least one set of questions.")
        else:
            combined_doc_path = generate_combined_document(st.session_state.selected_questions)
            st.write("Questions Combined Successfully!")
            st.write(f"Download your combined document here:")
            st.download_button(
                label="Download Combined Questions",
                data=open(combined_doc_path, "rb").read(),
                file_name="combined_questions.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

if __name__ == "__main__":
    main()
