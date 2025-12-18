from __future__ import annotations
import io, re
from typing import Dict, Any, Tuple, List, Optional

try:
    from pypdf import PdfReader
except Exception as e:
    raise ImportError("pypdf is required: pip install pypdf") from e

try:
    from bs4 import BeautifulSoup
except Exception as e:
    raise ImportError("beautifulsoup4 lxml required: pip install beautifulsoup4 lxml") from e

__all__ = [
    "extract_text_from_pdf",
    "clean_html_text",
    "parse_resume_pdf",
    "parse_resume_text",
    "parse_jd_pdf",
    "parse_jd_text",
]

EMAIL_RE     = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE     = re.compile(r"\+?\d[\d\-\s()]{7,}\d")
URL_RE       = re.compile(r"(https?://[^\s)>\]}]+)")
GITHUB_RE    = re.compile(r"(https?://(?:www\.)?github\.com/[A-Za-z0-9_.\-]+)", re.I)
LINKEDIN_RE  = re.compile(r"(https?://(?:www\.)?linkedin\.com/[A-Za-z0-9_/\-?=%.#]+)", re.I)

ROLE_KV_RE     = re.compile(r"(?:^|\b)(?:role|position|job\s*title|title)\s*[:\-]\s*(.+)", re.I)
COMPANY_KV_RE  = re.compile(r"(?:^|\b)(?:company|employer|organization|organisation)\s*[:\-]\s*(.+)", re.I)
LOCATION_KV_RE = re.compile(r"(?:^|\b)(?:location)\s*[:\-]\s*(.+)", re.I)

COMPANY_HIRING_RE = re.compile(r"([A-Z][A-Za-z0-9&.\- ]{1,60})\s+(?:is\s+hiring|seeks|seeking|looking\s+for)\b", re.I)
ROLE_INLINE_RE    = re.compile(r"([A-Za-z/ +\-]{0,40})(engineer|developer|scientist|manager|analyst|architect|lead|specialist|intern)([A-Za-z/ +\-]{0,40})", re.I)

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+#./\-]{0,63}")

SEC_SKILLS = re.compile(r"^\s*(skills?|technical\s+skills?|tech\s+stack|core\s+competencies|competencies)\s*:?\s*$", re.I)
SEC_EDU    = re.compile(r"^\s*(education|educational\s+qualifications|academics)\s*:?\s*$", re.I)
SEC_CERT   = re.compile(r"^\s*(certifications?|licenses?)\s*:?\s*$", re.I)
SEC_EXP    = re.compile(r"^\s*(experience|work\s+experience|professional\s+experience|employment)\s*:?\s*$", re.I)
SEC_SUM    = re.compile(r"^\s*(summary|professional\s+summary|profile|about)\s*:?\s*$", re.I)
SEC_REQ    = re.compile(r"^\s*(requirements?|responsibilities|what\s+you(?:’|')?ll\s+do|what\s+we\s+expect)\s*:?\s*$", re.I)
SEC_LOC    = re.compile(r"^\s*(location)\s*:?\s*$", re.I)
SEC_COMP   = re.compile(r"^\s*(company|about\s+us)\s*:?\s*$", re.I)
SEC_TITLE  = re.compile(r"^\s*(role|job\s*title|position|title)\s*:?\s*$", re.I)

STOP = {
    "and","or","of","the","a","an","to","with","in","on","for","by","at","from","as","etc","etc.",
    "good","excellent","strong","solid","experience","experiences","familiar","familiarity","exposure",
    "expert","expertise","beginner","intermediate","advanced","proficient","knowledge","working",
    "hands-on","years","year","month","months","ability","team","collaboration","communication",
    "problem","solving","problem-solving","role","roles","responsibilities","responsibility","stack",
    "technology","technologies","framework","frameworks","tools","libraries","library","environment",
    "currently","professional","project","projects","and/or","and/or."
}

def extract_text_from_pdf(file_bytes: bytes) -> str:
    if not file_bytes:
        return ""
    reader = PdfReader(io.BytesIO(file_bytes))
    try:
        if getattr(reader, "is_encrypted", False):
            try: reader.decrypt("")
            except Exception: return ""
    except Exception:
        pass
    parts: List[str] = []
    for p in (reader.pages or []):
        try: parts.append(p.extract_text() or "")
        except Exception: continue
    return "\n".join(parts).strip()

def clean_html_text(html: str) -> str:
    if not html: return ""
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script","style","noscript"]): t.decompose()
    txt = soup.get_text("\n")
    return "\n".join(l.strip() for l in txt.splitlines() if l.strip())

def _lines(text: str) -> List[str]:
    return [l.rstrip() for l in (text or "").splitlines()]

def _split_inline(s: str) -> List[str]:
    parts = re.split(r"[,\u2022;|/•·\-–—]+", s)
    return [p.strip() for p in parts if p.strip()]

def _normalise_token(tok: str) -> str:
    t = tok.strip().strip("()[]{}:;\"'`“”")
    t = re.sub(r"[.\-]{2,}", lambda m: m.group(0)[0], t)
    return t

def _is_skill_like(tok: str) -> bool:
    if not tok: return False
    low = tok.lower()
    if low in STOP: return False
    if len(tok) < 2 or len(tok) > 64: return False
    if tok.isdigit(): return False
    return True

def _dedup_order(seq: List[str], key_fn=None) -> List[str]:
    seen = set(); out = []
    for x in seq:
        k = key_fn(x) if key_fn else x
        if k not in seen:
            seen.add(k); out.append(x)
    return out

def _extract_section_blocks(lines: List[str], header_re: re.Pattern, max_follow: int = 24) -> List[str]:
    blocks: List[str] = []; n = len(lines); i = 0
    def _is_any_header(s: str) -> bool:
        return any(h.match(s) for h in [SEC_SKILLS, SEC_EDU, SEC_CERT, SEC_EXP, SEC_SUM, SEC_REQ, SEC_LOC, SEC_COMP, SEC_TITLE])
    while i < n:
        if header_re.match(lines[i] or ""):
            chunk: List[str] = []
            for j in range(i + 1, min(i + 1 + max_follow, n)):
                ln = lines[j].strip()
                if not ln: break
                if _is_any_header(ln): break
                chunk.append(ln)
            if chunk: blocks.append("\n".join(chunk))
        i += 1
    return blocks

def _extract_emails(text: str) -> List[str]:
    return _dedup_order(EMAIL_RE.findall(text or ""))

def _extract_phones(text: str) -> List[str]:
    return _dedup_order(PHONE_RE.findall(text or ""))

def _extract_links(text: str) -> Dict[str, List[str]]:
    urls = _dedup_order(URL_RE.findall(text or ""))
    gh   = _dedup_order(GITHUB_RE.findall(text or ""))
    li   = _dedup_order(LINKEDIN_RE.findall(text or ""))
    portfolio = [u for u in urls if "github.com" not in u.lower() and "linkedin.com" not in u.lower()]
    return {"all": urls[:80], "github": gh[:20], "linkedin": li[:20], "portfolio": portfolio[:40]}

def _extract_summary(text: str) -> str:
    blocks = _extract_section_blocks(_lines(text), SEC_SUM, max_follow=16)
    if blocks: return blocks[0][:800]
    picks = [l for l in _lines(text) if l.strip()][:3]
    return " ".join(picks)[:800]

def _extract_education(text: str) -> List[str]:
    out: List[str] = []
    blocks = _extract_section_blocks(_lines(text), SEC_EDU, max_follow=40)
    DEG_RE = re.compile(r"(B\.?Tech|B\.?E\.?|BSc|MSc|M\.?Tech|M\.?E\.?|MBA|Ph\.?D|Bachelor|Master|Diploma|Associate|BCA|MCA)", re.I)
    for b in blocks:
        for ln in b.splitlines():
            if DEG_RE.search(ln): out.append(ln.strip())
    return _dedup_order(out)

def _extract_certifications(text: str) -> List[str]:
    out: List[str] = []
    blocks = _extract_section_blocks(_lines(text), SEC_CERT, max_follow=24)
    for b in blocks:
        for ln in b.splitlines():
            ln = ln.strip()
            if len(ln) >= 3: out.append(ln)
    return _dedup_order(out)

def _extract_companies_from_exp(text: str) -> List[str]:
    out: List[str] = []
    blocks = _extract_section_blocks(_lines(text), SEC_EXP, max_follow=80)
    ORG = re.compile(r"\b([A-Z][A-Za-z0-9&.\-]{1,})\b")
    for b in blocks:
        for m in ORG.finditer(b):
            w = m.group(1)
            if len(w) >= 2 and w.lower() not in STOP:
                out.append(w)
    return _dedup_order(out)[:50]

def _extract_experience_years(text: str) -> Optional[float]:
    m = re.findall(r"(\d+(?:\.\d+)?)\s*(?:\+?\s*)?(?:years?|yrs)\b", text or "", re.I)
    try:
        vals = [float(x) for x in m]
        if vals: return max(vals)
    except Exception:
        pass
    return None

def _extract_location(text: str) -> str:
    for ln in _lines(text)[:80]:
        kv = LOCATION_KV_RE.search(ln)
        if kv:
            x = kv.group(1).strip()
            if 2 <= len(x) <= 80: return x
    blocks = _extract_section_blocks(_lines(text), SEC_LOC, max_follow=4)
    if blocks:
        cand = blocks[0].splitlines()[0].strip()
        if 2 <= len(cand) <= 80: return cand
    return ""

def _guess_company(text: str) -> str:
    for ln in _lines(text)[:80]:
        kv = COMPANY_KV_RE.search(ln)
        if kv:
            x = kv.group(1).strip()
            if 2 <= len(x) <= 80: return x
    m = COMPANY_HIRING_RE.search(text or "")
    if m:
        x = m.group(1).strip()
        if 2 <= len(x) <= 80: return x
    first = next((l.strip() for l in _lines(text) if l.strip()), "")
    if 2 <= len(first.split()) <= 6 and not EMAIL_RE.search(first):
        return first
    return ""

def _guess_role(text: str) -> str:
    for ln in _lines(text)[:80]:
        kv = ROLE_KV_RE.search(ln)
        if kv:
            x = kv.group(1).strip()
            if 2 <= len(x) <= 80: return x
    m = ROLE_INLINE_RE.search(text or "")
    if m:
        x = (m.group(1) + m.group(2) + m.group(3)).strip()
        return re.sub(r"\s+", " ", x).title()
    blocks = _extract_section_blocks(_lines(text), SEC_TITLE, max_follow=4)
    if blocks:
        cand = blocks[0].splitlines()[0].strip()
        if 2 <= len(cand) <= 80: return cand
    first = next((l.strip() for l in _lines(text) if l.strip()), "")
    if 2 <= len(first.split()) <= 8:
        return first.title()
    return ""

def _extract_skills_dynamic(text: str, prefer_sections: bool = True, max_skills: int = 140) -> List[str]:
    lines = _lines(text)
    skill_tokens: List[str] = []
    if prefer_sections:
        for block in _extract_section_blocks(lines, SEC_SKILLS, max_follow=28):
            for ln in block.splitlines():
                for part in _split_inline(ln):
                    for tok in TOKEN_RE.findall(part):
                        tok = _normalise_token(tok)
                        if _is_skill_like(tok): skill_tokens.append(tok)
    global_tokens: List[str] = []
    for tok in TOKEN_RE.findall(text or ""):
        tok = _normalise_token(tok)
        if _is_skill_like(tok): global_tokens.append(tok)
    merged = skill_tokens + global_tokens
    final = _dedup_order(
        [t for t in merged if t.lower() not in STOP],
        key_fn=lambda s: re.sub(r"[.\-_/ ]", "", s.lower()),
    )
    return final[:max_skills]

def parse_resume_text(text: str) -> Dict[str, Any]:
    text = text or ""
    emails = _extract_emails(text); phones = _extract_phones(text)
    links  = _extract_links(text)
    name = ""
    for line in _lines(text):
        s = line.strip()
        if not s: continue
        if EMAIL_RE.search(s): continue
        if 2 <= len(s.split()) <= 6 and 2 <= len(s) <= 64:
            name = s; break
    skills      = _extract_skills_dynamic(text, prefer_sections=True)
    education   = _extract_education(text)
    certs       = _extract_certifications(text)
    companies   = _extract_companies_from_exp(text)
    years       = _extract_experience_years(text)
    summary     = _extract_summary(text)
    location    = _extract_location(text)
    role_guess    = _guess_role(text)
    company_guess = _guess_company(text)
    return {
        "name": name,
        "emails": emails,
        "phones": phones,
        "summary": summary,
        "skills": skills,
        "education": education,
        "certifications": certs,
        "companies": companies,
        "experience_years": years,
        "links": links,
        "location": location,
        "current_role": role_guess,
        "current_company": company_guess,
        "raw_text": text,
    }

def parse_resume_pdf(file_bytes: bytes) -> Dict[str, Any]:
    return parse_resume_text(extract_text_from_pdf(file_bytes))

def parse_jd_text(text: str) -> Dict[str, Any]:
    text = text or ""
    role     = _guess_role(text)
    company  = _guess_company(text)
    skills   = _extract_skills_dynamic(text, prefer_sections=True)
    years    = _extract_experience_years(text)
    location = _extract_location(text)
    req_blocks = _extract_section_blocks(_lines(text), SEC_REQ, max_follow=40)
    jd_summary = (req_blocks[0] if req_blocks else " ".join([l for l in _lines(text) if l.strip()][:6]))[:1000]
    return {
        "role": role,
        "company": company,
        "experience": f"{years} years" if years is not None else "",
        "skills": skills,
        "location": location,
        "summary": jd_summary,
        "description": text,
    }

def parse_jd_pdf(file_bytes: bytes) -> Dict[str, Any]:
    return parse_jd_text(extract_text_from_pdf(file_bytes))
