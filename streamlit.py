import os
from dotenv import load_dotenv
from pymongo import MongoClient
from PyPDF2 import PdfReader
import streamlit as st
import google.generativeai as genai

# Load environment variables
load_dotenv()

# MongoDB connection
CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
client = MongoClient(CONNECTION_STRING)
db = client["brain_rot"]
collection = db["brain_rot_collection"]

# Generative AI configuration
genai.configure(api_key=os.getenv("GOOGLE_GENAI_API_KEY"))

# Helper function to extract text from PDF
def pdf_to_text(input_pdf):
    reader = PdfReader(input_pdf)
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text()
    return extracted_text

# Brain Rot Translator Function
def brain_rot_translate(input_text, decade_data=None):
    generation_config = {
        "temperature": 2.0,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    # Use decade data if available
    if decade_data:
        dataset_info = "\n".join([f"{entry['word']}: {entry['definition']}" for entry in decade_data])
        system_instruction = (
            "Using the following dataset, translate input text into 'brainrot' "
            "(brainrot refers to Gen Z/Gen Alpha internet slang):\n"
            f"{dataset_info}\n"
        )
    else:
        system_instruction = (
            "Translate the input text into 'brainrot' (Gen Z/Gen Alpha internet slang)."
        )

    # Set up the Generative AI model
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )

    # Start a chat session and generate the response
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(input_text)
    return response.text

# Streamlit app
def run_streamlit():
    # Set up the Streamlit app title
    st.title("Word Definitions Over the Years")

    # Sidebar to select decade
    st.sidebar.title("Explore by Decade")
    decade_options = [
        "1990-1999",
        "2000-2009",
        "2010-2019",
        "2020-2029",
    ]
    selected_decade = st.sidebar.selectbox("Select a Decade", decade_options)

    # Fetch Words by Decade
    if "decade_data" not in st.session_state:
        st.session_state["decade_data"] = None

    if st.sidebar.button("Fetch Words by Decade"):
        document = collection.find_one({"decade": selected_decade})
        if document and "words" in document:
            st.session_state["decade_data"] = document["words"]
            st.write(f"Words and Definitions for the Decade {selected_decade}:")
            for entry in st.session_state["decade_data"]:
                st.write(f"- **{entry['word']}**: {entry['definition']}")
        else:
            st.warning(f"No words found for the decade {selected_decade}.")
            st.session_state["decade_data"] = None

    # Brain Rot Translator Section
    st.title("Brain Rot Translator")
    text_input = st.text_input("Enter some text")
    uploaded_file = st.file_uploader("Upload a file (PDF or TXT)", type=["pdf", "txt"])

    input_text = ""
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            input_text = pdf_to_text(uploaded_file)
        else:
            input_text = uploaded_file.read().decode("utf-8")

        st.write("File uploaded successfully.")
        st.text_area("File Contents", input_text, height=200, disabled=True)

    if text_input:
        input_text = text_input
        st.text_area("Input Text", input_text, height=100, disabled=True)

    if input_text and st.button("Translate"):
        translated_text = brain_rot_translate(input_text, decade_data=st.session_state.get("decade_data"))
        st.text_area("Translated Output", translated_text, height=200)

# Run the Streamlit app
if __name__ == "__main__":
    run_streamlit()
