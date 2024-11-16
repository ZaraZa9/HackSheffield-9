import streamlit as st
from pymongo import MongoClient

def run_streamlit():
    CONNECTION_STRING = "mongodb+srv://weitongsun01:qDUa12YFsLz1NCgd@cluster0.hxmx9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(CONNECTION_STRING)


    db = client["brain_rot"]
    collection = db["brain_rot_collection"]


    st.title("Word Definitions Over the Years")


    with st.form("add_word_form"):
        year = st.number_input("Year", min_value=1900, max_value=2100, step=1, value=2023)
        word = st.text_input("Word")
        definition = st.text_area("Definition")
        submitted = st.form_submit_button("Add Word")

        if submitted:
            document = collection.find_one({"year": year})
            if document:
                collection.update_one(
                    {"year": year},
                    {"$push": {"words": {"word": word, "definition": definition}}}
                )
            else:
                collection.insert_one({
                    "year": year,
                    "words": [{"word": word, "definition": definition}]
                })
            st.success(f"Added word '{word}' for the year {year}.")




    with st.form("fetch_word_form"):
        fetch_year = st.number_input("Fetch Words by Year", min_value=1900, max_value=2100, step=1, value=2023)
        fetch_submitted = st.form_submit_button("Fetch Words")

        if fetch_submitted:
            document = collection.find_one({"year": fetch_year})
            if document and "words" in document:
                st.write(f"Words and Definitions for the Year {fetch_year}:")
                for entry in document["words"]:
                    st.write(f"- **{entry['word']}**: {entry['definition']}")
            else:
                st.warning(f"No words found for the year {fetch_year}.")






    st.title("Brain Rot Translator")
    a = st.sidebar.date_input('Start date', value=None, min_value=None, max_value=None, key=None)
    text_input = st.text_input('Enter some text')
    if text_input is not None:
        st.text(f"Text input:\n{text_input}")
    st.write("Upload your input file here (only .txt files).")
    uploaded_file = st.file_uploader("Choose a file", type="txt")

    if uploaded_file:
      
        input_text = uploaded_file.read().decode("utf-8")
        
        st.write("File uploaded successfully.")
        
       
        st.text_area("File Contents", input_text, height=200, disabled=True)

        if st.button("Translate"):
            
            translated_text = brain_rot_translate(input_text) 
            st.text_area("Translated Output", translated_text, height=200)




def brain_rot_translate(input_text):
    """
    Placeholder translation function.
    """
    return input_text[::-1]

if __name__ == "__main__":
    run_streamlit()

