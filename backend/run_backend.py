import sys
import uvicorn
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.config import settings

if __name__ == "__main__":
    print("=" * 60)
    print(f" Starting {settings.app.name}")
    print(f" Target Zone: {settings.app.zone_name}")
    print(f" Camera ID:   {settings.app.camera_id}")
    print(f" Listening on http://{settings.app.host}:{settings.app.port}")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=False,
        ws="auto",
        log_level="info"
    )
