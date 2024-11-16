import streamlit as st

def run_streamlit():
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

