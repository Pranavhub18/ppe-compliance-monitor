import os
import sys
from pathlib import Path

# Add project root and backend to sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
backend_dir = ROOT_DIR / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import uvicorn
# pyrefly: ignore [missing-import]
import gradio as gr
from backend.app.config import settings
from backend.app.main import app, configure_spa_fallback

# Ensure the React SPA catch-all route is properly configured at root
configure_spa_fallback(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")

    print("=" * 65)
    print(" 🚀 Starting Industrial PPE Kit Detection System")
    print(f" 🌐 Dashboard: http://{host}:{port}/")
    print(f" 📚 API Docs:  http://{host}:{port}/docs")
    print(f" 🧠 Weights:   models/new_best(2).pt")
    print("=" * 65)

    uvicorn.run(app, host=host, port=port, log_level="info", ws="auto")
