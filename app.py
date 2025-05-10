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

    if "selected_files" not in st.session_state:
        st.session_state.selected_files = []

    # Step 1: Display available exam codes (file names)
    files = load_question_papers()
    exam_codes = [f.replace(".docx", "") for f in files]
    st.sidebar.header("Search and Select Exam Code")

    # Search box for exam codes with real-time suggestions
    search_code = st.sidebar.text_input("Enter Exam Code:")
    
    # Dynamically filter and display matching codes based on user input
    if search_code:
        matching_codes = [code for code in exam_codes if search_code.lower() in code.lower()]
    else:
        matching_codes = exam_codes

    if matching_codes:
        # Let the user choose an exam code
        exam_code = st.selectbox("Select Exam Code", matching_codes, key=f"exam_code_{len(st.session_state.selected_files)}")

        # Load the questions from the selected file
        if exam_code:
            st.session_state.selected_code = exam_code
            st.session_state.questions = get_questions_from_docx(f"{QUESTION_PAPER_DIR}/{exam_code}.docx")

            st.write(f"Exam Code: {exam_code}")
            st.write(f"Total Questions in the file: {len(st.session_state.questions)}")

            num_questions = st.number_input("How many questions to select?", min_value=1, max_value=len(st.session_state.questions), step=1, key=f"num_questions_{len(st.session_state.selected_files)}")

            # Button to add selected questions to the list
            if st.button(f"Add Questions from {exam_code}"):
                selected = random.sample(st.session_state.questions, num_questions)
                st.session_state.selected_files.append({
                    "exam_code": exam_code,
                    "selected_questions": selected,
                    "num_questions": num_questions
                })
                st.write(f"Selected {num_questions} questions from {exam_code}")

        # Button to add more questions
        if st.button("Add More"):
            st.session_state.selected_code = ""  # Reset for the next round of file selection

    # Step 2: Show selected files and questions
    if st.session_state.selected_files:
        st.subheader("Selected Exam Codes and Number of Questions")

        # Display the list of selected files with an editable number of questions
        data = []
        for idx, selected_file in enumerate(st.session_state.selected_files, start=1):
            row = [
                idx,
                selected_file["exam_code"],
                st.text_input(f"Enter number of questions for {selected_file['exam_code']}", value=selected_file["num_questions"], key=f"num_q_{idx}")
            ]
            data.append(row)

        # Display a table of selected files
        st.write("No. | Exam code | Number of questions")
        for row in data:
            st.write(f"{row[0]} | {row[1]} | {row[2]}")

    # Step 3: Proceed button to generate combined document
    if st.button("Proceed to next step"):
        if not st.session_state.selected_files:
            st.warning("Please select at least one set of questions.")
        else:
            combined_doc_path = generate_combined_document([(file['exam_code'], file['selected_questions']) for file in st.session_state.selected_files])
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
