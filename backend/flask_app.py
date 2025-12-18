"""
Enhanced Flask API backend for MailGen - HireSense HR Tech
This serves as an alternative to the FastAPI backend with better integration for Flutter
"""
import sys
from pathlib import Path
import uuid
import json
from typing import Dict, Any

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

# Ensure repo root is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

app = Flask(__name__)
CORS(app)

# Configure file uploads
UPLOAD_FOLDER = Path(__file__).resolve().parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'MailGen Backend'})


@app.route('/ping', methods=['GET'])
def ping():
    """Simple ping endpoint"""
    return 'ok'


@app.route('/upload/resume', methods=['POST'])
def upload_resume():
    """Upload and parse a resume PDF"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(filepath))
        
        # Parse resume
        from core.parsers import parse_resume_pdf
        from core.stores import get_resume_store, upsert_doc
        
        with open(filepath, 'rb') as f:
            data = f.read()
        
        parsed = parse_resume_pdf(data)
        
        # Store in database
        _id = str(uuid.uuid4())
        text = parsed.get('raw_text') or ''
        metadata = {
            k: parsed.get(k) 
            for k in ['name', 'emails', 'skills', 'education', 'experience'] 
            if parsed.get(k)
        }
        metadata['summary'] = text[:500] if text else ''
        
        col = get_resume_store()
        upsert_doc(col, _id, text, metadata)
        
        logger.info(f'Stored resume with ID: {_id}')
        
        # Clean up temporary file
        filepath.unlink(missing_ok=True)
        
        return jsonify({
            'ok': True,
            'parsed': parsed,
            'id': _id,
            'message': 'Resume uploaded successfully'
        }), 200
        
    except Exception as e:
        logger.exception('Failed to parse resume PDF')
        return jsonify({'error': f'PDF parse error: {str(e)}'}), 400


@app.route('/upload/jd', methods=['POST'])
def upload_jd():
    """Upload and parse a job description PDF"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(filepath))
        
        # Parse JD
        from core.parsers import parse_jd_pdf, clean_html_text, _guess_role
        from core.stores import get_jd_store, upsert_doc
        
        with open(filepath, 'rb') as f:
            data = f.read()
        
        parsed = parse_jd_pdf(data)
        
        # Store in database
        _id = str(uuid.uuid4())
        text = parsed.get('description') or parsed.get('summary') or ''
        metadata = {
            k: parsed.get(k) 
            for k in ['role', 'company', 'skills', 'location', 'experience_level'] 
            if parsed.get(k)
        }
        metadata['summary'] = text[:500] if text else ''
        
        col = get_jd_store()
        upsert_doc(col, _id, text, metadata)
        
        logger.info(f'Stored JD with ID: {_id}')
        
        # Clean up temporary file
        filepath.unlink(missing_ok=True)
        
        return jsonify({
            'ok': True,
            'parsed': parsed,
            'id': _id,
            'message': 'Job description uploaded successfully'
        }), 200
        
    except Exception as e:
        logger.exception('Failed to parse JD PDF')
        return jsonify({'error': f'PDF parse error: {str(e)}'}), 400


@app.route('/list/resumes', methods=['GET'])
def list_resumes():
    """List all stored resumes"""
    try:
        from core.stores import get_resume_store
        
        col = get_resume_store()
        result = col.get()
        items = []
        
        if result and result.get('ids'):
            for i, rid in enumerate(result['ids']):
                meta = result.get('metadatas', [])[i] if i < len(result.get('metadatas', [])) else {}
                items.append({
                    'id': rid,
                    'name': meta.get('name', 'Resume'),
                    'metadata': meta
                })
        
        return jsonify({'ok': True, 'items': items}), 200
        
    except Exception as e:
        logger.exception('Failed to list resumes')
        return jsonify({'error': str(e)}), 500


@app.route('/list/jds', methods=['GET'])
def list_jds():
    """List all stored job descriptions"""
    try:
        from core.stores import get_jd_store
        
        col = get_jd_store()
        result = col.get()
        items = []
        
        if result and result.get('ids'):
            for i, jid in enumerate(result['ids']):
                meta = result.get('metadatas', [])[i] if i < len(result.get('metadatas', [])) else {}
                items.append({
                    'id': jid,
                    'role': meta.get('role', 'Job Description'),
                    'company': meta.get('company', ''),
                    'metadata': meta
                })
        
        return jsonify({'ok': True, 'items': items}), 200
        
    except Exception as e:
        logger.exception('Failed to list JDs')
        return jsonify({'error': str(e)}), 500


@app.route('/generate', methods=['POST'])
def generate_email():
    """Generate a cold email from resume and JD"""
    try:
        data = request.get_json()
        resume_id = data.get('resume_id')
        jd_id = data.get('jd_id')
        
        if not resume_id or not jd_id:
            return jsonify({'error': 'resume_id and jd_id required'}), 400
        
        from core.stores import get_resume_store, get_jd_store
        from core.llm import generate_cold_email
        
        rcol = get_resume_store()
        jcol = get_jd_store()
        
        rdoc = rcol.get(ids=[resume_id])
        jdoc = jcol.get(ids=[jd_id])
        
        if not rdoc or not rdoc.get('documents') or not rdoc['documents']:
            return jsonify({'error': 'Resume not found'}), 404
        
        if not jdoc or not jdoc.get('documents') or not jdoc['documents']:
            return jsonify({'error': 'JD not found'}), 404
        
        rmeta = rdoc.get('metadatas', [{}])[0] or {}
        jmeta = jdoc.get('metadatas', [{}])[0] or {}
        
        candidate_name = (rmeta.get('name') or '').strip()
        candidate_summary = rmeta.get('summary') or (rdoc['documents'][0][:400] if rdoc.get('documents') else '')
        jd_summary = jmeta.get('summary') or (jdoc['documents'][0][:400] if jdoc.get('documents') else '')
        jd_role = (jmeta.get('role') or '').strip()
        
        resume_skills = rmeta.get('skills') or []
        if isinstance(resume_skills, str):
            try:
                resume_skills = json.loads(resume_skills)
            except Exception:
                resume_skills = [s.strip() for s in resume_skills.split(',') if s.strip()]
        
        skills_for_llm = ', '.join(resume_skills if isinstance(resume_skills, list) else [resume_skills])
        
        subject, body = generate_cold_email(
            candidate_name,
            skills_for_llm,
            candidate_summary,
            jd_summary,
            jd_role,
            '',
        )
        
        return jsonify({
            'ok': True,
            'subject': subject,
            'body': body
        }), 200
        
    except Exception as e:
        logger.exception('Failed to generate email')
        return jsonify({'error': str(e)}), 500


@app.route('/send', methods=['POST'])
def send_email():
    """Send an email"""
    try:
        data = request.get_json()
        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        
        if not to or not subject or not body:
            return jsonify({'error': 'to, subject, and body are required'}), 400
        
        from core.emailer import send_email as send_email_func
        
        smtp_from = data.get('from')
        smtp_pass = data.get('password')
        
        ok, err = send_email_func(smtp_from, smtp_pass, to, subject, body)
        
        if ok:
            return jsonify({'ok': True, 'message': 'Email sent successfully'}), 200
        else:
            return jsonify({'error': err}), 500
            
    except Exception as e:
        logger.exception('Failed to send email')
        return jsonify({'error': str(e)}), 500


@app.route('/stats', methods=['GET'])
def stats():
    """Get statistics about stored documents"""
    try:
        from core.stores import get_resume_store, get_jd_store
        
        rcol = get_resume_store()
        jcol = get_jd_store()
        
        rresult = rcol.get()
        jresult = jcol.get()
        
        resume_count = len(rresult.get('ids', [])) if rresult else 0
        jd_count = len(jresult.get('ids', [])) if jresult else 0
        
        return jsonify({
            'ok': True,
            'resumes_count': resume_count,
            'jds_count': jd_count,
            'total_documents': resume_count + jd_count
        }), 200
        
    except Exception as e:
        logger.exception('Failed to get stats')
        return jsonify({'error': str(e)}), 500


@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler"""
    logger.exception('Unhandled exception')
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
