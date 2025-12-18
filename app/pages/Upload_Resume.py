import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import uuid
from core.parsers import parse_resume_pdf
from core.stores import get_resume_store, upsert_doc, query

st.title("📄 Upload Resume (PDF → Resumes DB)")

uploaded_file = st.file_uploader("Drop a resume PDF", type=["pdf"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    rec = parse_resume_pdf(file_bytes)

    # Use email as ID if available
    _id = rec.get("email") or str(uuid.uuid4())

    meta = {
        "name": rec.get("name", ""),
        "email": rec.get("email", ""),
        "phone": rec.get("phone", ""),
        "skills": rec.get("skills", []),
    }

    if st.button("Store in Resumes DB"):
        import time
        print("Button clicked: starting upload process")
        try:
            print("Calling get_resume_store()...")
            col = get_resume_store()
            print("get_resume_store() returned")
            print("Calling upsert_doc()...")
            upsert_doc(col, _id=_id, document=rec["raw_text"], metadata=meta)
            print("upsert_doc() returned")
            st.success(f"✅ Stored resume with ID: {_id}")

            print("Calling query()...")
            result = query(col, rec.get("email") or rec.get("name"), top_k=1)
            print("query() returned")
            st.write("Stored Record:", result)
        except Exception as e:
            print(f"Exception occurred: {e}")
            st.error(f"❌ Error storing resume: {e}")
