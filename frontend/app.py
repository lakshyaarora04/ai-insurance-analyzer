import streamlit as st

st.title("LLM Document Query System")

query = st.text_input("Enter your query:")
uploaded_file = st.file_uploader("Upload policy document (PDF or DOCX)")

if uploaded_file and query:
    st.write("Processing...")
    # TODO: Connect to backend
