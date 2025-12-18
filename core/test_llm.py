# core/test_llm.py
from __future__ import annotations
import os, json
from typing import Dict, Any, Tuple
from groq import Groq

# Fallback: deterministic stubs when key missing
_GROQ_KEY = os.getenv("GROQ_API_KEY", "")
_client = Groq(api_key=_GROQ_KEY) if _GROQ_KEY else None

def _chat(prompt: str) -> str:
    if not _client:
        # Deterministic stub so UI doesn't break without key
        return '{"stub": true}'
    r = _client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role":"user","content":prompt}],
        temperature=0.4,
        top_p=1,
        max_completion_tokens=1500,
        stream=False,
    )
    return r.choices[0].message.content

def gen_mcqs(language: str, jd_topics: str) -> Dict[str, Any]:
    from core.test_prompts import MCQ_GEN_PROMPT
    out = _chat(MCQ_GEN_PROMPT.format(language=language, jd_topics=jd_topics))
    try:
        data = json.loads(out)
        assert isinstance(data.get("questions"), list) and len(data["questions"]) >= 10
        return data
    except Exception:
        # Minimal fallback: 10 trivial MCQs
        qs = []
        for i in range(10):
            qs.append({
                "q": f"{language}: placeholder MCQ {i+1}",
                "options": {"A":"opt1","B":"opt2","C":"opt3","D":"opt4"},
                "answer": "A",
                "explain": "fallback"
            })
        return {"questions": qs}

def gen_dsa_hard(language: str, jd_topics: str) -> Dict[str, Any]:
    from core.test_prompts import DSA_GEN_PROMPT
    out = _chat(DSA_GEN_PROMPT.format(language=language, jd_topics=jd_topics))
    try:
        data = json.loads(out)
        assert isinstance(data.get("questions"), list) and len(data["questions"]) == 3
        return data
    except Exception:
        return {"questions":[
            {"q":"Design an O(log n) range query structure with lazy updates."},
            {"q":"Find minimum window covering K sequences; analyze complexity."},
            {"q":"Implement LRU + LFU hybrid cache; prove complexity bounds."},
        ]}

def eval_dsa(language: str, questions_json: Dict[str,Any], answers: list[str]) -> Dict[str, Any]:
    from core.test_prompts import DSA_EVAL_PROMPT
    qs = [q["q"] for q in questions_json["questions"]]
    prompt = DSA_EVAL_PROMPT.format(language=language, questions=json.dumps(qs, ensure_ascii=False), answers=json.dumps(answers, ensure_ascii=False))
    out = _chat(prompt)
    try:
        data = json.loads(out)
        return data
    except Exception:
        return {"scores":[{"score":6,"reason":"fallback"} for _ in range(3)], "total":18}

def gen_prog_task(language: str, jd_topics: str) -> Dict[str, Any]:
    from core.test_prompts import PROG_PROMPT
    out = _chat(PROG_PROMPT.format(language=language, jd_topics=jd_topics))
    try:
        data = json.loads(out)
        assert "question" in data
        return data
    except Exception:
        return {"question": f"Write a {language} function to validate balanced parentheses with Unicode brackets."}

def eval_prog(language: str, task: str, answer: str) -> Dict[str, Any]:
    from core.test_prompts import PROG_EVAL_PROMPT
    out = _chat(PROG_EVAL_PROMPT.format(language=language, task=task, answer=answer, jd_topics=""))
    try:
        data = json.loads(out)
        return data
    except Exception:
        return {"breakdown":{"correctness":8,"quality":3,"edges":3},"total":14,"notes":"fallback"}
