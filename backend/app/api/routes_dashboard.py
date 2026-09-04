import io
import csv
from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from ..core.state_manager import state_manager

router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get("/dashboard")
async def get_dashboard():
    """Returns complete real-time dashboard telemetry and state."""
    return state_manager.get_full_dashboard_state()


@router.get("/detection/current")
async def get_current_detection():
    """Returns worker detections from the active frame."""
    state = state_manager.get_full_dashboard_state()
    return state.get("compliance", {})


@router.get("/events")
async def get_events():
    """Returns logged safety violation events."""
    return state_manager.get_violations_report()


@router.get("/stats")
async def get_session_stats():
    """Returns today's cumulative session statistics."""
    state = state_manager.get_full_dashboard_state()
    return state.get("session_stats", {})


@router.get("/export/report")
async def export_violations_report(format: str = "csv"):
    """
    Exports logged safety violations in CSV or JSON format.
    """
    events = state_manager.get_violations_report()

    if format.lower() == "json":
        return JSONResponse(content={"total_violations": len(events), "events": events})

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Event ID", "Timestamp", "Video", "Camera", "Worker ID", "Status", "Missing PPE", "Compliance Score"])

    for ev in events:
        writer.writerow([
            ev.get("id", ""),
            ev.get("timestamp", ""),
            ev.get("video", ""),
            ev.get("camera_id", ""),
            ev.get("worker_id", ""),
            ev.get("status", ""),
            ev.get("missing_ppe", ""),
            ev.get("compliance_score", "")
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ppe_violations_report.csv"}
    )
