"""
Startup script for the MailGen backend server.
This avoids the Windows multiprocessing KeyboardInterrupt issue.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[".", "../core"],  # Only watch specific directories
        log_level="info",
        use_colors=True,
    )
