"""FastAPI backend for AUTO_COLD_MAIL_GEN.

This module exposes minimal endpoints that wrap the existing `core/` functions so a React
frontend can call the business logic.

Note: imports from `core` are done lazily in endpoints where possible to reduce startup
cost and avoid importing heavy ML models at application import time.
"""
import sys
from pathlib import Path
import uuid
from typing import Dict, Any

import asyncio
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure repo root is importable (project structure has an inner folder named the same)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

app = FastAPI(title="AUTO_COLD_MAIL_GEN API")

# Allow local frontend dev servers (any origin for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging: console + file
LOG_PATH = Path(__file__).resolve().parents[0] / "backend.log"
logger = logging.getLogger("backend")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log full traceback to file and console
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    # Return a safe JSON error
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ping")
def ping():
    """Simple plain-text ping useful for tools that don't parse JSON."""
    return JSONResponse(content="ok", media_type="text/plain")


@app.on_event("startup")
def _startup():
    logger.info("Backend starting up")
    # Pre-warm embedding function and vector stores so first request is fast.
    try:
        from core.embeddings import get_embedding_function
        from core.stores import get_resume_store, get_jd_store

        get_embedding_function()
        get_resume_store()
        get_jd_store()
    except Exception:
        logger.exception("Failed to warm caches on startup")


@app.on_event("shutdown")
def _shutdown():
    logger.info("Backend shutting down")


@app.post("/upload/jd")
async def upload_jd(file: UploadFile = File(...)):
    data = await file.read()
    try:
        from core.parsers import parse_jd_pdf
        from core.stores import get_jd_store, upsert_doc

        parsed = parse_jd_pdf(data)
        # Auto-store the parsed JD
        _id = str(uuid.uuid4())
        text = parsed.get("description") or parsed.get("summary") or ""
        metadata = {k: parsed.get(k) for k in ["role", "company", "skills", "location"] if parsed.get(k)}
        # Ensure at least one metadata attribute to satisfy ChromaDB
        metadata.setdefault("doc_type", "jd")
        metadata.setdefault("file_name", getattr(file, "filename", "jd.pdf"))
        col = get_jd_store()
        upsert_doc(col, _id, text, metadata)
        logger.info(f"Stored JD with ID: {_id}")
        return {"ok": True, "parsed": parsed, "id": _id}
    except Exception as e:
        # Log the exception and return a friendly error to the client
        logger.exception("Failed to parse JD PDF")
        # Common pypdf error messages are user-facing; return a 400 for parse failures
        return JSONResponse(status_code=400, content={"error": f"PDF parse error: {e}"})


@app.post("/upload/resume")
async def upload_resume(file: UploadFile = File(...)):
    data = await file.read()
    try:
        from core.parsers import parse_resume_pdf
        from core.stores import get_resume_store, upsert_doc

        parsed = parse_resume_pdf(data)
        # Auto-store the parsed resume
        _id = str(uuid.uuid4())
        text = parsed.get("raw_text") or ""
        metadata = {k: parsed.get(k) for k in ["name", "emails", "skills", "education"] if parsed.get(k)}
        # Provide sensible defaults so metadata is never empty
        metadata.setdefault("doc_type", "resume")
        # If name not parsed, use file name (without extension) as a friendly label
        if not metadata.get("name"):
            try:
                from pathlib import Path as _Path
                metadata["name"] = _Path(getattr(file, "filename", "resume.pdf")).stem
            except Exception:
                metadata["name"] = getattr(file, "filename", "resume.pdf")
        metadata.setdefault("file_name", getattr(file, "filename", "resume.pdf"))
        col = get_resume_store()
        upsert_doc(col, _id, text, metadata)
        logger.info(f"Stored resume with ID: {_id}")
        return {"ok": True, "parsed": parsed, "id": _id}
    except Exception as e:
        logger.exception("Failed to parse resume PDF")
        return JSONResponse(status_code=400, content={"error": f"PDF parse error: {e}"})


@app.post("/store/jd")
async def store_jd(document: Dict[str, Any]):
    _id = document.get("id") or str(uuid.uuid4())
    text = document.get("text") or document.get("description") or document.get("summary") or ""
    metadata = document.get("metadata") or {k: document.get(k) for k in ["role", "company", "skills"] if document.get(k)}
    try:
        from core.stores import get_jd_store, upsert_doc

        col = get_jd_store()
        upsert_doc(col, _id, text, metadata)
        return {"ok": True, "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/store/resume")
async def store_resume(document: Dict[str, Any]):
    _id = document.get("id") or str(uuid.uuid4())
    text = document.get("text") or document.get("raw_text") or ""
    metadata = document.get("metadata") or {k: document.get(k) for k in ["name", "emails", "skills"] if document.get(k)}
    try:
        from core.stores import get_resume_store, upsert_doc

        col = get_resume_store()
        upsert_doc(col, _id, text, metadata)
        return {"ok": True, "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list/resumes")
def list_resumes():
    """List all stored resume IDs with metadata."""
    try:
        from core.stores import get_resume_store

        col = get_resume_store()
        result = col.get()
        items = []
        if result and result.get("ids"): 
            for i, rid in enumerate(result["ids"]):
                meta = result.get("metadatas", [])[i] if i < len(result.get("metadatas", [])) else {}
                items.append({"id": rid, "name": meta.get("name", ""), "metadata": meta})
        return {"ok": True, "items": items}
    except Exception as e:
        if isinstance(e, asyncio.CancelledError):
            logger.warning("List resumes cancelled during shutdown")
            raise HTTPException(status_code=503, detail="Service shutting down")
        logger.exception("Failed to list resumes")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list/jds")
def list_jds():
    """List all stored JD IDs with metadata."""
    try:
        from core.stores import get_jd_store

        col = get_jd_store()
        result = col.get()
        items = []
        if result and result.get("ids"):
            for i, jid in enumerate(result["ids"]):
                meta = result.get("metadatas", [])[i] if i < len(result.get("metadatas", [])) else {}
                items.append({"id": jid, "role": meta.get("role", ""), "company": meta.get("company", ""), "metadata": meta})
        return {"ok": True, "items": items}
    except Exception as e:
        if isinstance(e, asyncio.CancelledError):
            logger.warning("List JDs cancelled during shutdown")
            raise HTTPException(status_code=503, detail="Service shutting down")
        logger.exception("Failed to list JDs")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def stats():
    """Basic counts for stored resumes and JDs."""
    try:
        from core.stores import get_resume_store, get_jd_store

        rcol = get_resume_store()
        jcol = get_jd_store()

        rresult = rcol.get()
        jresult = jcol.get()

        resume_count = len(rresult.get("ids", [])) if rresult else 0
        jd_count = len(jresult.get("ids", [])) if jresult else 0

        return {
            "ok": True,
            "resumes_count": resume_count,
            "jds_count": jd_count,
            "total_documents": resume_count + jd_count,
        }
    except Exception as e:
        logger.exception("Failed to get stats")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
def generate_email(payload: Dict[str, Any]):
    resume_id = payload.get("resume_id")
    jd_id = payload.get("jd_id")
    if not resume_id or not jd_id:
        raise HTTPException(status_code=400, detail="resume_id and jd_id required")
    try:
        from core.stores import get_resume_store, get_jd_store
        from core.llm import generate_cold_email

        rcol = get_resume_store()
        jcol = get_jd_store()
        rdoc = rcol.get(ids=[resume_id])
        jdoc = jcol.get(ids=[jd_id])
        if not rdoc or not rdoc.get("documents") or not rdoc["documents"]:
            raise HTTPException(status_code=404, detail="Resume not found")
        if not jdoc or not jdoc.get("documents") or not jdoc["documents"]:
            raise HTTPException(status_code=404, detail="JD not found")

        rmeta = rdoc.get("metadatas", [{}])[0] or {}
        jmeta = jdoc.get("metadatas", [{}])[0] or {}

        candidate_name = (rmeta.get("name") or "").strip()
        candidate_summary = rmeta.get("summary") or (rdoc["documents"][0][:400] if rdoc.get("documents") else "")
        jd_summary = jmeta.get("summary") or (jdoc["documents"][0][:400] if jdoc.get("documents") else "")
        jd_role = (jmeta.get("role") or "").strip()

        resume_skills = rmeta.get("skills") or []
        if isinstance(resume_skills, str):
            try:
                import json as _json

                resume_skills = _json.loads(resume_skills)
            except Exception:
                resume_skills = [s.strip() for s in resume_skills.split(",") if s.strip()]

        skills_for_llm = ", ".join(resume_skills if isinstance(resume_skills, list) else [resume_skills])

        subject, body = generate_cold_email(
            candidate_name,
            skills_for_llm,
            candidate_summary,
            jd_summary,
            jd_role,
            "",
        )
        
        # Ensure body is not empty
        if not body:
            logger.warning(f"Generated email body is empty for resume_id={resume_id}, jd_id={jd_id}")
            body = "I am very interested in this opportunity. Please let me know if you'd like to discuss further."
        
        return {"ok": True, "subject": subject, "body": body}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generating email for resume_id={resume_id}, jd_id={jd_id}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send")
def send_endpoint(payload: Dict[str, Any]):
    logger.info(f"Raw payload: {payload}")
    logger.info(f"Received send request with payload keys: {payload.keys()}")
    to = payload.get("to")
    subject = payload.get("subject")
    body = payload.get("body")
    auto_reply_enabled = payload.get("auto_reply_enabled", False)

    # Debug: log body length to diagnose empty payload issues
    try:
        logger.info(
            "send payload details | to=%s subject_len=%s body_len=%s auto_reply=%s",
            to,
            len(subject or ""),
            len(body or ""),
            auto_reply_enabled,
        )
    except Exception:
        logger.exception("Failed to log send payload details")
    
    logger.info(f"to: {bool(to)}, subject: {bool(subject)}, body: {bool(body)}")
    logger.info(f"First 100 chars of subject: {(subject or '')[:100]}")
    logger.info(f"First 100 chars of body: {(body or '')[:100]}")
    
    if not to or not subject or not body:
        detail = "Missing required fields: "
        if not to:
            detail += "to, "
        if not subject:
            detail += "subject, "
        if not body:
            detail += "body, "
        detail = detail.rstrip(", ")
        logger.error(f"Bad request: {detail}")
        raise HTTPException(status_code=400, detail=detail)
    try:
        from core.emailer import send_email
        from core.conversation_store import create_conversation
        from core.email_monitor import get_email_monitor
        from core.selenium_watcher import get_selenium_watcher
        from core.config import SETTINGS
        import os

        # Use credentials from payload or .env or config
        smtp_from = payload.get("from") or os.getenv("GMAIL_USER") or SETTINGS.smtp_from
        smtp_pass = payload.get("password") or os.getenv("GMAIL_PASSWORD") or SETTINGS.smtp_app_password
        
        if not smtp_from or not smtp_pass:
            raise HTTPException(
                status_code=400, 
                detail="Gmail credentials not found. Please set GMAIL_USER and GMAIL_PASSWORD in .env file or provide them in the request"
            )
        
        ok, err = send_email(smtp_from, smtp_pass, to, subject, body)
        
        if ok:
            # If auto-reply is enabled, create conversation and start monitoring
            if auto_reply_enabled:
                conversation_id = str(uuid.uuid4())
                
                logger.info(f"Creating conversation {conversation_id} for auto-reply")
                
                # Create conversation record with credentials
                create_conversation(
                    conversation_id=conversation_id,
                    sender_email=smtp_from,
                    recipient_email=to,
                    original_subject=subject,
                    original_body=body,
                    auto_reply_enabled=True,
                    sender_password=smtp_pass
                )
                
                logger.info(f"Starting IMAP monitoring for conversation {conversation_id}")
                
                # Start monitoring for replies
                monitor = get_email_monitor()
                monitor.start_monitoring(
                    conversation_id=conversation_id,
                    email_address=smtp_from,
                    password=smtp_pass,
                    original_subject=subject,
                    recipient_email=to,
                    callback=handle_reply_callback
                )

                use_selenium = os.getenv("USE_SELENIUM_WATCHER", "false").lower() == "true"
                if use_selenium:
                    watcher = get_selenium_watcher()
                    watcher.start_watch(
                        conversation_id=conversation_id,
                        recipient_email=to,
                        subject=subject,
                        callback=handle_reply_callback,
                    )
                
                logger.info(f"Auto-reply enabled for conversation {conversation_id}")
                
                return {"ok": True, "conversation_id": conversation_id, "auto_reply_enabled": True}
            
            return {"ok": True}
        else:
            raise HTTPException(status_code=500, detail=err)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to send email")
        raise HTTPException(status_code=500, detail=str(e))


def handle_reply_callback(conversation_id: str, from_email: str, reply_text: str):
    """Callback when a reply is received - stores message, generates and sends auto-response."""
    try:
        from core.conversation_store import get_conversation, add_message_to_conversation
        from core.llm import generate_reply_to_email
        from core.emailer import send_email
        
        conversation = get_conversation(conversation_id)
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found in callback")
            return
        
        logger.info(f"Handle reply callback: conversation_id={conversation_id}, from={from_email}, reply_len={len(reply_text)}")
        
        # IMPORTANT: Add received message to conversation FIRST so it shows in UI
        add_message_to_conversation(
            conversation_id=conversation_id,
            from_email=from_email,
            to_email=conversation['sender_email'],
            subject=f"Re: {conversation['original_subject']}",
            body=reply_text,
            message_type='received'
        )
        logger.info(f"Added received message to conversation {conversation_id}")
        
        # Check if auto-reply is still enabled
        if not conversation.get('auto_reply_enabled'):
            logger.info(f"Auto-reply disabled for {conversation_id}, skipping response")
            return
        
        # Build conversation context
        messages = conversation.get('messages', [])
        context = "\n\n".join([
            f"{'Sent' if msg['type'] == 'sent' else 'Received'}: {msg['body'][:200]}"
            for msg in messages[-3:]  # Last 3 messages for context
        ])
        
        # Generate reply using LLM
        logger.info(f"Generating reply for {conversation_id} using LLM")
        reply_subject, reply_body = generate_reply_to_email(
            original_email_body=conversation['original_body'],
            received_reply=reply_text,
            conversation_context=context
        )
        logger.info(f"Generated reply: subject={reply_subject}, body_len={len(reply_body)}")
        
        # Send auto-reply using stored credentials
        sender_password = conversation.get('sender_password')
        if not sender_password:
            logger.error(f"No sender_password stored for conversation {conversation_id}")
            return
            
        ok, err = send_email(
            smtp_from=conversation['sender_email'],
            smtp_password=sender_password,
            smtp_to=from_email,
            subject=reply_subject,
            body=reply_body
        )
        
        if ok:
            # Add sent reply to conversation
            add_message_to_conversation(
                conversation_id=conversation_id,
                from_email=conversation['sender_email'],
                to_email=from_email,
                subject=reply_subject,
                body=reply_body,
                message_type='auto_reply'
            )
            logger.info(f"Auto-reply sent for conversation {conversation_id} to {from_email}")
        else:
            logger.error(f"Failed to send auto-reply: {err}")
            
    except Exception as e:
        logger.exception(f"Error handling reply callback: {e}")


@app.get("/conversations")
def list_conversations_endpoint():
    """List all conversations with auto-reply tracking."""
    try:
        from core.conversation_store import list_conversations
        conversations = list_conversations()
        return {"ok": True, "conversations": conversations}
    except Exception as e:
        logger.exception("Failed to list conversations")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{conversation_id}")
def get_conversation_endpoint(conversation_id: str):
    """Get a specific conversation with all messages."""
    try:
        from core.conversation_store import get_conversation
        conversation = get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"ok": True, "conversation": conversation}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get conversation")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversations/{conversation_id}/toggle")
def toggle_auto_reply_endpoint(conversation_id: str, payload: Dict[str, Any]):
    """Enable or disable auto-reply for a conversation."""
    enabled = payload.get("enabled", False)
    try:
        from core.conversation_store import toggle_auto_reply, get_conversation
        from core.email_monitor import get_email_monitor
        from core.selenium_watcher import get_selenium_watcher
        
        conversation = get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        toggle_auto_reply(conversation_id, enabled)
        
        monitor = get_email_monitor()
        if enabled:
            # Restart monitoring if it was stopped
            # Note: Would need stored credentials for this to work
            pass
        else:
            monitor.stop_monitoring(conversation_id)
            try:
                get_selenium_watcher().stop_watch(conversation_id)
            except Exception:
                logger.warning("Failed to stop selenium watcher", exc_info=True)
        
        return {"ok": True, "conversation_id": conversation_id, "auto_reply_enabled": enabled}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to toggle auto-reply")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversations/{conversation_id}/reply")
def manual_reply_endpoint(conversation_id: str, payload: Dict[str, Any]):
    """Send a manual reply to the latest sender in this conversation."""
    body = payload.get("body")
    if not body:
        raise HTTPException(status_code=400, detail="body is required")

    try:
        from core.conversation_store import get_conversation, add_message_to_conversation
        from core.emailer import send_email

        conversation = get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        sender_email = conversation.get("sender_email")
        sender_password = conversation.get("sender_password")
        original_subject = conversation.get("original_subject", "")

        if not sender_email or not sender_password:
            raise HTTPException(status_code=400, detail="Missing sender credentials for this conversation")

        # Reply to the last received email; fallback to original recipient
        messages = conversation.get("messages", [])
        last_received = next((m for m in reversed(messages) if m.get("type") == "received"), None)
        to_email = last_received.get("from") if last_received else conversation.get("recipient_email")

        if not to_email:
            raise HTTPException(status_code=400, detail="No recipient found to reply to")

        subject = f"Re: {original_subject}" if original_subject else "Re:"

        ok, err = send_email(
            smtp_from=sender_email,
            smtp_password=sender_password,
            smtp_to=to_email,
            subject=subject,
            body=body,
        )

        if not ok:
            raise HTTPException(status_code=500, detail=err or "Failed to send reply")

        add_message_to_conversation(
            conversation_id=conversation_id,
            from_email=sender_email,
            to_email=to_email,
            subject=subject,
            body=body,
            message_type="sent",
        )

        return {"ok": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to send manual reply")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
