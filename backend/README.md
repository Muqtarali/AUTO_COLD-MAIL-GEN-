# Backend (FastAPI)

Quick notes to run the API locally for development.

Start the backend (from the inner project folder where this file lives):

```powershell
Set-Location -LiteralPath "c:\Users\user\Downloads\AUTO_COLD MAIL GEN\AUTO_COLD MAIL GEN"
python -m uvicorn backend.app:app --reload --port 8001
```

Health endpoint: http://127.0.0.1:8001/health

OpenAPI docs: http://127.0.0.1:8001/docs

Logs (rotating): `backend/backend.log`

If you hit crashes, check `backend/backend.log` for full tracebacks.
