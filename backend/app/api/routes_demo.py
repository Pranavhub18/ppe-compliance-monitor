from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from ..core.video_processor import video_processor
from ..core.state_manager import state_manager

router = APIRouter(prefix="/api/demo", tags=["Demo Controls"])


class SpeedRequest(BaseModel):
    speed: float = 1.0


class ConfigUpdateRequest(BaseModel):
    required_ppe: Optional[List[str]] = None
    optional_ppe: Optional[List[str]] = None
    conf_threshold: Optional[float] = None
    target_fps: Optional[float] = None


@router.post("/start")
async def start_demo():
    """Starts or resumes demo video processing."""
    video_processor.start()
    return {"status": "ok", "message": "Demo started"}


@router.post("/pause")
async def pause_demo():
    """Pauses demo video processing."""
    video_processor.pause()
    return {"status": "ok", "message": "Demo paused"}


@router.post("/stop")
async def stop_demo():
    """Stops demo video processing."""
    video_processor.stop()
    return {"status": "ok", "message": "Demo stopped"}


@router.post("/next")
async def next_video():
    """Skips to next video in queue."""
    video_processor.next_video()
    return {"status": "ok", "message": "Advanced to next video"}


@router.post("/prev")
async def prev_video():
    """Goes back to previous video in queue."""
    video_processor.prev_video()
    return {"status": "ok", "message": "Returned to previous video"}


@router.post("/restart")
async def restart_video():
    """Restarts current video from beginning."""
    video_processor.restart_video()
    return {"status": "ok", "message": "Restarted current video"}


@router.post("/speed")
async def set_playback_speed(req: SpeedRequest):
    """Sets video playback speed (0.5x, 1x, 2x)."""
    video_processor.set_speed(req.speed)
    return {"status": "ok", "message": f"Playback speed set to {req.speed}x"}


@router.post("/config")
async def update_demo_config(req: ConfigUpdateRequest):
    """Updates active PPE rules and model thresholds dynamically."""
    if req.required_ppe is not None:
        video_processor.update_rules(req.required_ppe, req.optional_ppe)
    if req.conf_threshold is not None:
        video_processor.update_conf_threshold(req.conf_threshold)
    if req.target_fps is not None:
        video_processor.config.video.target_fps = max(5.0, min(60.0, float(req.target_fps)))
    return {
        "status": "ok",
        "message": "Configuration updated successfully",
        "required_ppe": video_processor.evaluator.required_ppe,
        "conf_threshold": video_processor.detection_engine.conf_threshold
    }


@router.post("/reset-stats")
async def reset_session_stats():
    """Resets today's summary counters."""
    state_manager.reset_stats()
    return {"status": "ok", "message": "Session stats reset"}
