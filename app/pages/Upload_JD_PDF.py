# app/pages/Upload_JD_PDF.py
import streamlit as st
# Ensure parent directory is in sys.path for module resolution
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import os
import uuid
import json
import time
from core.parsers import parse_jd_pdf
from core.stores import get_jd_store, upsert_doc

st.title("📑 Upload JD (PDF → JDs DB)")

uploaded_file = st.file_uploader("JD PDF", type=["pdf"])

if uploaded_file:
    st.write(f"File name: {uploaded_file.name}")
    file_bytes = uploaded_file.read()

    # Initialize store latency history in session state
    if "store_latency_history" not in st.session_state:
        st.session_state["store_latency_history"] = []
    # Measure latency for parsing
    start_parse = time.time()
    jd = parse_jd_pdf(file_bytes)
    end_parse = time.time()
    parse_latency = end_parse - start_parse
    st.metric("Parse Latency (s)", f"{parse_latency:.2f}")

    st.subheader("Parsed JD JSON")
    st.json(jd)

    # Remove Output Length vs Quality line chart
    # Add Output Length vs Quality scatter plot
    import pandas as pd
    import matplotlib.pyplot as plt
    output_length = len(jd["description"]) if "description" in jd else 0
    output_quality = len(jd.get("skills", []))
    if "output_length_history" not in st.session_state:
        st.session_state["output_length_history"] = []
    if "output_quality_history" not in st.session_state:
        st.session_state["output_quality_history"] = []
    st.session_state["output_length_history"].append(output_length)
    st.session_state["output_quality_history"].append(output_quality)

    st.subheader("Output Length vs Quality (Scatter Plot)")
    df = pd.DataFrame({
        "Output Length": st.session_state["output_length_history"],
        "Quality": st.session_state["output_quality_history"]
    })
    fig, ax = plt.subplots()
    ax.scatter(df["Output Length"], df["Quality"], alpha=0.7)
    ax.set_xlabel("Output Length")
    ax.set_ylabel("Quality")
    ax.set_title("Output Length vs Quality")
    st.pyplot(fig)

    if st.button("Store in JDs DB"):
        try:
            col = get_jd_store()
            _id = str(uuid.uuid4())

            # Force metadata to be Chroma-safe
            meta = {
                "role": jd.get("role", ""),
                "experience": jd.get("experience", ""),
                "skills": json.dumps(jd.get("skills", []), ensure_ascii=False),  # Convert list to string
                "source_type": "pdf",
                "source_ref": uploaded_file.name
            }

            # Measure latency for storing
            start_store = time.time()
            upsert_doc(col, _id=_id, document=jd["description"], metadata=meta)
            end_store = time.time()
            store_latency = end_store - start_store
            st.metric("Store Latency (s)", f"{store_latency:.2f}")
            # Add latency to history and show line chart
            st.session_state["store_latency_history"].append(store_latency)
            st.subheader("Store Latency History (s)")
            st.line_chart(st.session_state["store_latency_history"])
            st.success("✅ Stored in Chroma successfully!")

        except Exception as e:
            st.error(f"Failed to store in Chroma\n\n{e}")
