import streamlit as st
import uuid
import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import sys
import pandas as pd
import os
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from core.parsers import clean_html_text, _guess_role  # keep your imports

# _guess_skills may not exist in your latest parser; if it does, we’ll still use it.
try:
    from core.parsers import _guess_skills
except Exception:
    _guess_skills = None  # optional

from core.stores import get_jd_store, upsert_doc

st.set_page_config(page_title="Scrape JD URL", page_icon="�")
st.title("🌐 Scrape JD URL → JDs DB")

# -------------- helpers (local; no other modules modified) --------------
def _jsonld_company(soup: BeautifulSoup) -> str:
    """Try to read company from JSON-LD script blocks (hiringOrganization / organization / name)."""
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.get_text(strip=True))
        except Exception:
            continue
        # normalize to list
        items = data if isinstance(data, list) else [data]
        for obj in items:
            if not isinstance(obj, dict):
                continue
            # common places
            for key in ("hiringOrganization", "organization", "publisher", "author"):
                if isinstance(obj.get(key), dict):
                    name = obj[key].get("name") or obj[key].get("legalName")
                    if name and 2 <= len(name) <= 80:
                        return name.strip()
            # direct name on an Organization or JobPosting node
            if obj.get("@type") in ("Organization", "JobPosting"):
                name = obj.get("name") or (obj.get("hiringOrganization") or {}).get("name")
                if name and 2 <= len(name) <= 80:
                    return name.strip()
    return ""

def _og_site_company(soup: BeautifulSoup) -> str:
    meta = soup.find("meta", attrs={"property": "og:site_name"}) or soup.find("meta", attrs={"name": "og:site_name"})
    if meta and meta.get("content"):
        val = meta["content"].strip()
        if 2 <= len(val) <= 80:
            return val
    return ""

def _title_company(soup: BeautifulSoup) -> str:
    if soup.title and soup.title.string:
        raw = soup.title.string.strip()
        # split on common separators: " - ", " | ", " — "
        head = re.split(r"\s[-|–—]\s", raw)[0].strip()
        # remove role-like suffixes like "Careers at X", "Jobs at X"
        head = re.sub(r"(careers?|jobs?)\s+at\s+", "", head, flags=re.I)
        if 2 <= len(head) <= 80:
            return head
    return ""

def _text_company_heuristics(text: str) -> str:
    # Company: XYZ
    m = re.search(r"(?:Company|Employer|Organization|Organisation)\s*[:\-]\s*([A-Z][A-Za-z0-9&.,\-\s]{2,80})", text, re.I)
    if m:
        return m.group(1).strip()

    # XYZ is hiring / seeks / looking for
    m = re.search(r"([A-Z][A-Za-z0-9&.\-\s]{2,80})\s+(?:is\s+hiring|seeks|seeking|looking\s+for)\b", text, re.I)
    if m:
        return m.group(1).strip()

    # "... at <Company>" (avoid capturing role tokens before "at")
    m = re.search(r"\bat\s+([A-Z][A-Za-z0-9&.\-\s]{2,80})\b", text, re.I)
    if m:
        return m.group(1).strip()

    return ""

def _pick_company(candidates):
    # choose the most plausible (prefer non-generic, mid-length)
    bad = {"careers", "jobs", "apply", "hiring", "about", "portal"}
    scores = []
    for c in candidates:
        if not c:
            continue
        clean = re.sub(r"\s+", " ", c).strip()
        if clean.lower() in bad:
            continue
        # simple score = length penalty + caps bias
        score = min(len(clean), 50) + (2 if clean[:1].isupper() else 0)
        scores.append((score, clean))
    if not scores:
        return ""
    scores.sort(reverse=True)
    return scores[0][1]

# -----------------------------------------------------------------------

url = st.text_input("Job posting URL", placeholder="https://example.com/job-profile/...")

if st.button("Scrape and Store"):
    if not url.strip():
        st.error("Please enter a valid job posting URL.")
    else:
        try:
            st.info("Launching headless Chrome to scrape page...")

            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(url)
            time.sleep(2.5)  # allow JS to load

            html = driver.page_source or ""
            driver.quit()

            # Parse HTML for company signals BEFORE flattening
            soup = BeautifulSoup(html, "lxml")
            cands = [
                _jsonld_company(soup),
                _og_site_company(soup),
                _title_company(soup),
            ]
            # Clean to plain text and run text heuristics (fallback)
            text = clean_html_text(html)
            cands.append(_text_company_heuristics(text))

            company = _pick_company(cands)

            # Extract role and skills just like before
            role = _guess_role(text)
            if _guess_skills:
                skills = _guess_skills(text)
            else:
                # minimal dynamic tokens if _guess_skills not available
                toks = re.findall(r"[A-Za-z][A-Za-z0-9+#./\-]{1,63}", text)
                skills = sorted(set(t for t in toks if len(t) > 1))[:50]

            st.subheader("Extracted JD Details")
            st.write("**Company:**", company or "—")
            st.write("**Role:**", role or "—")
            st.write("**Skills:**", skills or "—")
            st.text_area("Description", (text[:2000] + "...") if len(text) > 2000 else text, height=300)

            # Store in DB
            col = get_jd_store()
            _id = str(uuid.uuid4())
            meta = {
                "jd_id": _id,
                "source_type": "url",
                "source_ref": url,
                "company": company,
                "role": role,
                "experience": "",
                "skills": skills,  # lists are JSON-encoded by stores._coerce_metadata
                "summary": text[:800],
            }
            upsert_doc(col, _id=_id, document=text, metadata=meta)

            st.success("✅ JD scraped and stored successfully!")

            # Accuracy/Result display
            st.write(f"Extracted company: {company if company else '—'}")
            st.write(f"Extracted role: {role if role else '—'}")
            st.write(f"Number of skills extracted: {len(skills) if skills else 0}")
            st.write(f"Description length: {len(text)} characters")

        except Exception as e:
            st.error(f"Scrape failed\n\n{e}")

# -----------------------------------------------------------------------

# Example: Replace with your actual data collection logic
# skills_extracted_list = [number_of_skills_from_run1, number_of_skills_from_run2, ...]
skills_extracted_list = [10, 15, 20, 18, 25, 30, 28, 32, 35, 33]  # Example data

runs = list(range(1, len(skills_extracted_list) + 1))

fig, ax = plt.subplots()
ax.plot(runs, skills_extracted_list, marker='o', color='blue', label='Skills Extracted')
ax.set_xlabel('Run')
ax.set_ylabel('Number of Skills')
ax.set_title('Skills Extracted Over Multiple Runs')
ax.legend()
ax.grid(True)

st.pyplot(fig)
