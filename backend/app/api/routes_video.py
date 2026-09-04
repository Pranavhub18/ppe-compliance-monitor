import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..core.video_processor import video_processor
from ..core.state_manager import state_manager

router = APIRouter(prefix="/api/videos", tags=["Videos"])


class SelectVideoRequest(BaseModel):
    index: int = None
    filename: str = None


@router.get("")
async def get_video_playlist():
    """Returns list of all available demo videos in queue."""
    return {
        "videos": video_processor.video_manager.get_playlist_info(),
        "total": video_processor.video_manager.total_videos,
        "current_index": video_processor.video_manager.get_current_index()
    }


@router.get("/current")
async def get_current_video_info():
    """Returns current playing video information and progress."""
    state = state_manager.get_full_dashboard_state()
    return state.get("video_info", {})


@router.post("/select")
async def select_video(req: SelectVideoRequest):
    """Switches active video to specific index or filename."""
    if req.index is not None:
        video_processor.select_video(req.index)
        return {"status": "ok", "message": f"Switched to video index {req.index}"}
    elif req.filename:
        video_processor.select_video(req.filename)
        return {"status": "ok", "message": f"Switched to video {req.filename}"}
    raise HTTPException(status_code=400, detail="Must provide index or filename")


def mjpeg_live_stream_generator():
    """Yields AFTER (AI Detection) MJPEG stream frames."""
    last_frame = None
    while True:
        frame_bytes = video_processor.get_latest_annotated_jpeg()
        if frame_bytes is not None:
            last_frame = frame_bytes
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
        elif last_frame is not None:
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + last_frame + b"\r\n")
        time.sleep(0.033)


def mjpeg_raw_stream_generator():
    """Yields BEFORE (Original Raw Video) MJPEG stream frames."""
    last_frame = None
    while True:
        frame_bytes = video_processor.get_latest_raw_jpeg()
        if frame_bytes is not None:
            last_frame = frame_bytes
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
        elif last_frame is not None:
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + last_frame + b"\r\n")
        time.sleep(0.033)


@router.get("/stream/live")
async def get_live_stream():
    """
    AFTER Stream: Real-time MJPEG live stream of video with YOLO detection bounding boxes & HUD.
    """
    return StreamingResponse(
        mjpeg_live_stream_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/stream/raw")
async def get_raw_stream():
    """
    BEFORE Stream: Real-time MJPEG live stream of original video without any overlays.
    """
    return StreamingResponse(
        mjpeg_raw_stream_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
