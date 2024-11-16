import os
from dotenv import load_dotenv
from pymongo import MongoClient
from PyPDF2 import PdfReader
import streamlit as st
import google.generativeai as genai


load_dotenv()


CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
client = MongoClient(CONNECTION_STRING)
db = client["brain_rot"]
collection = db["brain_rot_collection"]


genai.configure(api_key=os.getenv("GOOGLE_GENAI_API_KEY"))


def pdf_to_text(input_pdf):
    reader = PdfReader(input_pdf)
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text()
    return extracted_text


def brain_rot_translate(input_text):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction="Using this dataset, translate input text into 'brainrot' (brainrot refers to Gen Z/Gen Alpha internet slang).",
    )

    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(input_text)
    return response.text


def run_streamlit():
    st.title("Word Definitions Over the Years")

    # Fetch Words by Decade
    st.sidebar.title("Explore by Decade")
    decade_options = [
        "1990-1999",
        "2000-2009",
        "2010-2019",
        "2020-2029",
    ]
    decade = st.sidebar.selectbox("Select a Decade", decade_options)
    fetch_submitted_decade = st.sidebar.button("Fetch Words by Decade")

    if fetch_submitted_decade:
        document = collection.find_one({"decade": decade})
        if document and "words" in document:
            st.write(f"Words and Definitions for the Decade {decade}:")
            for entry in document["words"]:
                st.write(f"- **{entry['word']}**: {entry['definition']}")
        else:
            st.warning(f"No words found for the decade {decade}.")



    # Brain Rot Translator
    st.title("Brain Rot Translator")
    text_input = st.text_input("Enter some text")
    uploaded_file = st.file_uploader("Upload a file (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            input_text = pdf_to_text(uploaded_file)
        else:
            input_text = uploaded_file.read().decode("utf-8")
        
        st.write("File uploaded successfully.")
        st.text_area("File Contents", input_text, height=200, disabled=True)

        if st.button("Translate"):
            translated_text = brain_rot_translate(input_text)
            st.text_area("Translated Output", translated_text, height=200)

    # Manual Translation
    if text_input:
        st.text_area("Input Text", text_input, height=100, disabled=True)
        if st.button("Translate Text"):
            translated_text = brain_rot_translate(text_input)
            st.text_area("Translated Output", translated_text, height=200)

if __name__ == "__main__":
    run_streamlit()
