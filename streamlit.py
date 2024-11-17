import openai
from pymongo import MongoClient
from PyPDF2 import PdfReader
import streamlit as st
import google.generativeai as genai
from openai import OpenAI
from helpers.frequency import word_frequency
import pandas as pd
import streamlit as st




openAI_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


CONNECTION_STRING = st.secrets["MONGO_CONNECTION_STRING"]
client = MongoClient(CONNECTION_STRING)
db = client["brain_rot"]
collection = db["brain_rot_collection"]
frequency_collection = db["brain_rot_frequency_collection"]

genai.configure(api_key=st.secrets["GOOGLE_GENAI_API_KEY"])

def pdf_to_text(input_pdf):
    reader = PdfReader(input_pdf)
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text()
    return extracted_text





import pandas as pd
import streamlit as st

def plot_streamlit_histogram(selected_decade):
    document = frequency_collection.find_one({"decade": selected_decade})
    
    if document is None:
        st.sidebar.error(f"No data found for the selected decade: {selected_decade}")
        return
    

    word_frequencies = document.get("words", {})
    

    sorted_words = sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)[:10]
    words, frequencies = zip(*sorted_words)


    data = pd.DataFrame({
        "Word": words,
        "Frequency": frequencies
    })

    # display the bar chart in the sidebar
    st.sidebar.subheader("Top 10 Word Frequencies")
    st.sidebar.bar_chart(data.set_index('Word')['Frequency'])


def brain_rot_translate(input_text, selected_decade, decade_data=None):
    generation_config = {
        "temperature": 2.0,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    if decade_data:
        dataset_info = "\n".join([f"{entry['word']}: {entry['definition']}" for entry in decade_data])
        system_instruction = (
            "Using the following dataset, translate input text into 'brainrot' - try not to use the words so uniformly: - use the ones that make sence given the context\n"
            "(brainrot refers to Gen Z/Gen Alpha internet slang):\n"
            f"{dataset_info}\n"
        )
    else:
        system_instruction = (
            "Translate the input text into 'brainrot' (Gen Z/Gen Alpha internet slang)."
        )

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )

    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(input_text)
    

    decade_data_words = [entry["word"] for entry in decade_data] if decade_data else []
    rot_frequency = word_frequency(response.text, decade_data_words)


    doc = frequency_collection.find_one({"decade": selected_decade})
    if doc:
        existing_frequencies = doc.get("words", {})
        for word, freq in rot_frequency.items():
            if word in existing_frequencies:
                existing_frequencies[word] += freq
            else:
                existing_frequencies[word] = freq

        frequency_collection.update_one(
            {"decade": selected_decade},
            {"$set": {"words": existing_frequencies}}
        )
    else:
        frequency_collection.insert_one({
            "decade": selected_decade,
            "words": rot_frequency
        })

    return response.text, rot_frequency


def generate_image_with_rate_limit(img_prompt):
    #if "OPENAI_API_KEY" not in st.secrets or not st.secrets["OPENAI_API_KEY"]:
    #    st.write("OpenAI API key not found. Please set the OPENAI_API_KEY")
    if not img_prompt or not img_prompt.strip():
        raise ValueError("Image prompt cannot be empty.")

    try:
        img_response = openAI_client.images.generate(
            model="dall-e-3",
            prompt="A surreal image of " + img_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return img_response.data[0].url
    
    except Exception as e:
        st.error("Rate limit exceeded. Please try again later.")


def run_streamlit():
    st.title("BRAIN.ROT.with.us")
    st.write("Welcome to BrainRot - the only internet solution that visualizes the state of degradation of the English language throughout the years.")
    st.write("This is a tool that translates text into 'brainrot' - Gen Z/Gen Alpha internet slang.")
    st.write("Consider our solution a case study of how exposure to the internet has affected the way we communicate.")
    st.write("The way it works is simple: you input some text, and we translate it into 'brainrot', and maybe visualize it - at your own risk...")
    st.write("The solution itself consists of an AI model that is trained on a dataset of words and definitions from different decades.")
    st.write("Hence, you can observe how slang use has evolved over time.")


    st.sidebar.title("Explore by Decade")
    decade_options = [
        "1990-1999",
        "2000-2009",
        "2010-2019",
        "2020-2029",
    ]
    selected_decade = st.sidebar.selectbox("Select a Decade", decade_options)

    if "decade_data" not in st.session_state or st.session_state.get("current_decade") != selected_decade:
        document = collection.find_one({"decade": selected_decade})
        if document and "words" in document:
            st.session_state["decade_data"] = document["words"]
        else:
            st.session_state["decade_data"] = []
        st.session_state["current_decade"] = selected_decade

    # fetch and display histogram
    if st.sidebar.button("Fetch Words by Decade"):
        st.sidebar.write(f"Words and Definitions for the Decade {selected_decade}:")
        if st.session_state["decade_data"]:
            for entry in st.session_state["decade_data"]:
                st.sidebar.write(f"- **{entry['word']}**: {entry['definition']}")
        else:
            st.sidebar.warning(f"No words found for the decade {selected_decade}.")

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

    generate_images_checkbox = st.checkbox("Generate Images Before and After Translation")

    translated_text = "" 
    word_frequencies = {}

    if input_text and st.button("Translate"):
        if generate_images_checkbox:
            with st.spinner("Generating pre-translation image..."):
                #st.write(input_text)
                #st.write(selected_decade)
                #st.write("LOOK HERE")
                pre_translation_image_url = generate_image_with_rate_limit(input_text)
                if pre_translation_image_url:
                    st.image(pre_translation_image_url, caption="Image Before Translation", use_column_width=True)

        #perform the translation
        translated_text, word_frequencies = brain_rot_translate(
            input_text, selected_decade, decade_data=st.session_state.get("decade_data")
        )
        st.text_area("Translated Output", translated_text, height=200)

        if generate_images_checkbox:
            with st.spinner("Generating post-translation image..."):
                post_translation_image_url = generate_image_with_rate_limit(translated_text)
                if post_translation_image_url:
                    st.image(post_translation_image_url, caption="Image After Translation", use_column_width=True)

        if word_frequencies:
            st.sidebar.subheader("Word Frequency Histogram")
            histogram_buf = plot_streamlit_histogram(selected_decade)
            if histogram_buf:
                st.sidebar.image(histogram_buf, caption="Top 10 Word Frequencies", use_column_width=True)

    if not input_text:
        st.sidebar.warning("Please enter or upload text for translation.")
    if not translated_text:
        st.sidebar.warning("No translation performed yet.")



if __name__ == "__main__":
    run_streamlit()
