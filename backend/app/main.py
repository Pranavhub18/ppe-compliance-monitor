import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings
from .core.video_processor import video_processor
from .core.websocket_hub import ws_hub
from .core.state_manager import state_manager
from .api.routes_dashboard import router as dashboard_router
from .api.routes_video import router as video_router
from .api.routes_demo import router as demo_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
)
logger = logging.getLogger("ppe_demo_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing PPE Demo Backend...")
    loop = asyncio.get_running_loop()
    ws_hub.set_event_loop(loop)

    # Start video processing loop
    video_processor.start()
    yield

    # Shutdown: gracefully stop video processor
    logger.info("Shutting down PPE Demo Backend...")
    video_processor.stop()


app = FastAPI(
    title="PPE Compliance Demo API",
    description="Backend API and synchronized dual-streaming engine for Industrial PPE Kit Detection Demo",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(dashboard_router)
app.include_router(video_router)
app.include_router(demo_router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-time WebSocket endpoint streaming frame detections, KPIs, alerts, and playlist updates.
    """
    await ws_hub.connect(websocket)
    try:
        init_state = state_manager.get_full_dashboard_state()
        await websocket.send_json({"type": "INIT_STATE", "data": init_state})

        # Also push current playlist info
        playlist_data = video_processor.video_manager.get_playlist_info()
        await websocket.send_json({
            "type": "PLAYLIST_UPDATE",
            "data": {
                "videos": playlist_data,
                "total": len(playlist_data),
                "current_index": video_processor.video_manager.get_current_index()
            }
        })

        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_hub.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_hub.disconnect(websocket)


def configure_spa_fallback(app_instance: FastAPI):
    """
    Mounts static assets and configures the SPA fallback route,
    ensuring it stays at the end of app_instance.routes so API and Gradio routes take precedence.
    """
    frontend_dist = settings.base_dir / "frontend" / "dist"
    if not frontend_dist.exists():
        return

    # Mount /assets if not already mounted
    if not any(getattr(r, "path", None) == "/assets" for r in app_instance.router.routes):
        assets_dir = frontend_dist / "assets"
        if assets_dir.exists():
            app_instance.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # Remove any existing serve_spa route to re-append at the end
    app_instance.router.routes = [r for r in app_instance.router.routes if getattr(r, "name", None) != "serve_spa"]

    @app_instance.get("/{full_path:path}", name="serve_spa")
    async def serve_spa(full_path: str):
        file_p = frontend_dist / full_path
        if file_p.exists() and file_p.is_file():
            return FileResponse(file_p)
        return FileResponse(frontend_dist / "index.html")


# Configure SPA on main app instance
configure_spa_fallback(app)

