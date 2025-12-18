import streamlit as st
st.set_page_config(page_title="Cold Mail Generator", page_icon="📧", layout="wide")

st.title("📧 Cold Mail Generator")

st.markdown("""
Ingest **resumes** and **job descriptions** into separate Chroma stores,
then generate tailored **cold emails** with **Groq**. Optionally send via **Gmail SMTP**.

Use the sidebar:
- Upload_Resume
- Upload_JD_PDF
- ATS SCORE
- Generate_&_Send
""")
