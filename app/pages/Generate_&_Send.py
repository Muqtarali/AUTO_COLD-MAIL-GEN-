# app/pages/Generate_&_Send.py
# Ensure parent directory is in sys.path for module resolution
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import os
import json
import streamlit as st
from core.stores import get_jd_store, get_resume_store, query
from core.llm import generate_cold_email
from core.emailer import send_email  # unified send (Gmail API preferred)

st.set_page_config(page_title="Generate & Send Cold Email", page_icon="📧")
st.title("📧 Generate & Send Cold Email")

# ---------- helpers ----------
def safe_meta_value(val):
    """Convert lists/dicts (JSON in Chroma) back to readable form for display."""
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return ", ".join(map(str, parsed))
            if isinstance(parsed, dict):
                return json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            return val
    return val if val is not None else ""

def to_list(val):
    """Turn metadata value into a list (supports JSON string, comma string, scalar, None)."""
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
        return [s.strip() for s in val.split(",") if s.strip()]
    return [str(val).strip()] if str(val).strip() else []

def ordered_skill_view(resume_skills, jd_skills, top_k=12):
    """Return matched, resume_only, jd_only ordered lists (lowercased dedup)."""
    norm = lambda s: s.strip().lower()
    rmap = {norm(s): s for s in resume_skills if s}
    jmap = {norm(s): s for s in jd_skills if s}
    matched_keys = [k for k in rmap if k in jmap]
    resume_only_keys = [k for k in rmap if k not in jmap]
    jd_only_keys = [k for k in jmap if k not in rmap]

    matched = [rmap[k] for k in matched_keys][:top_k]
    resume_only = [rmap[k] for k in resume_only_keys][:max(0, top_k - len(matched))]
    jd_only = [jmap[k] for k in jd_only_keys][:max(0, top_k - len(matched))]
    return matched, resume_only, jd_only

def pick_first_email(meta):
    emails = to_list(meta.get("emails")) or to_list(meta.get("email"))
    return emails[0] if emails else ""

# ---------- search: resumes ----------
resume_search = st.text_input("Search resumes (by skill, name, keyword)")
if resume_search:
    rcol = get_resume_store()
    rres = query(rcol, resume_search)
    if rres.get("ids") and rres["ids"][0]:
        st.write("### Matching Resumes")
        for idx, rid in enumerate(rres["ids"][0]):
            meta = rres["metadatas"][0][idx]
            st.write(
                f"**ID:** {rid} | "
                f"Name: {safe_meta_value(meta.get('name',''))} | "
                f"Email(s): {safe_meta_value(meta.get('emails',''))}"
            )
    else:
        st.warning("No matching resumes found.")

# ---------- search: JDs ----------
jd_search = st.text_input("Search job descriptions")
if jd_search:
    jcol = get_jd_store()
    jres = query(jcol, jd_search)
    if jres.get("ids") and jres["ids"][0]:
        st.write("### Matching JDs")
        for idx, jid in enumerate(jres["ids"][0]):
            meta = jres["metadatas"][0][idx]
            st.write(
                f"**ID:** {jid} | "
                f"Role: {safe_meta_value(meta.get('role',''))} | "
                f"Company: {safe_meta_value(meta.get('company',''))}"
            )
    else:
        st.warning("No matching JDs found.")

# ---------- selections ----------
resume_id = st.text_input("Enter Resume ID from above results")
jd_id = st.text_input("Enter JD ID from above results")
recipient_email = st.text_input("📨 Recipient email (hiring manager/recruiter)")

# ---------- generate ----------
subject = st.session_state.get("subject", "")
body = st.session_state.get("body", "")

if st.button("Generate Email"):
    if not resume_id or not jd_id:
        st.error("Please enter both Resume ID and JD ID")
    else:
        st.info("Step 1: Getting resume and JD stores...")
        try:
            rcol = get_resume_store()
            st.info("Step 2: Resume store loaded.")
            jcol = get_jd_store()
            st.info("Step 3: JD store loaded.")

            rdoc = rcol.get(ids=[resume_id])
            st.info(f"Step 4: Resume doc loaded for ID {resume_id}.")
            jdoc = jcol.get(ids=[jd_id])
            st.info(f"Step 5: JD doc loaded for ID {jd_id}.")

            if not rdoc["documents"]:
                st.error("Resume not found")
                st.stop()
            if not jdoc["documents"]:
                st.error("JD not found")
                st.stop()

            rmeta = rdoc["metadatas"][0] or {}
            jmeta = jdoc["metadatas"][0] or {}

            candidate_name = (rmeta.get("name") or "").strip()
            candidate_summary = safe_meta_value(rmeta.get("summary",""))
            jd_summary = jmeta.get("summary") or (jdoc["documents"][0][:500] if jdoc["documents"] else "")
            jd_role = (jmeta.get("role") or "").strip()

            resume_skills = to_list(rmeta.get("skills"))
            jd_skills = to_list(jmeta.get("skills"))

            matched, resume_only, jd_only = ordered_skill_view(resume_skills, jd_skills, top_k=12)
            annotated_skills = [f"{s} (match)" for s in matched] + resume_only + jd_only
            skills_for_llm = ", ".join(annotated_skills)

            links = rmeta.get("links", "")
            portfolio_str = json.dumps(links, ensure_ascii=False) if isinstance(links, dict) else (links or "")

            st.info("Step 6: Calling LLM to generate email...")
            subject, body = generate_cold_email(
                candidate_name,
                skills_for_llm,
                candidate_summary if len(candidate_summary) <= 400 else candidate_summary[:400],
                jd_summary,
                jd_role,
                portfolio_str
            )
            st.info("Step 7: LLM response received.")

            st.session_state["subject"] = subject
            st.session_state["body"] = body

            st.subheader("Matched Skills Used")
            st.write("**Matched:** ", ", ".join(matched) if matched else "—")
            st.write("**Resume-only:** ", ", ".join(resume_only) if resume_only else "—")
            st.write("**JD-only (context):** ", ", ".join(jd_only) if jd_only else "—")

            st.subheader("Generated Email")
            st.write(f"**Subject:** {subject}")
            st.text_area("Body", body, height=220)

            # Accuracy/Result display for generation
            st.success("Email generated successfully!")
            st.write(f"Length of generated body: {len(body)} characters")
            st.write(f"Number of matched skills: {len(matched)}")
            st.write(f"Number of resume-only skills: {len(resume_only)}")
            st.write(f"Number of JD-only skills: {len(jd_only)}")


            # If error from LLM, show it
            if subject == "Groq API Error":
                st.error(body)
        except Exception as e:
            st.error(f"Error in email generation: {e}")

# ---------- send ----------
if st.button("Send Email Now"):
    st.info("Step 8: Preparing to send email...")
    sender_email = os.getenv("SMTP_FROM", "").strip()
    sender_pass = os.getenv("SMTP_APP_PASSWORD", "").strip()
    to_addr = os.getenv("SMTP_TO_OVERRIDE", "").strip() or recipient_email.strip()

    # Diagnostics: Show loaded SMTP credentials
    st.write(f"SMTP_FROM: {sender_email}")
    st.write(f"SMTP_APP_PASSWORD length: {len(sender_pass)}")
    st.write(f"SMTP_TO_OVERRIDE: {os.getenv('SMTP_TO_OVERRIDE', '')}")
    st.write(f"Recipient email: {to_addr}")

    if not to_addr:
        st.error("Enter a recipient email")
    elif not sender_email or not sender_pass:
        st.error("SMTP_FROM / SMTP_APP_PASSWORD missing in environment/.env")
    else:
        st.info(f"Step 9: Sending email to {to_addr}...")
        try:
            ok, error_msg = send_email(
                smtp_from=sender_email,
                smtp_password=sender_pass,
                smtp_to=to_addr,
                subject=subject,
                body=body
            )
            if ok:
                st.success(f"✅ Email sent to {to_addr}")
                st.balloons()
                st.write("Email sending result: Success")
            else:
                st.error(f"❌ Email sending failed.\n{error_msg}")
                st.write("Email sending result: Failed")
        except Exception as e:
            st.error(f"Error in email sending: {e}")
