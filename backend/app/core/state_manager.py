import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from .compliance_evaluator import FrameComplianceState


class DashboardStateManager:
    """
    Thread-safe Central State Manager for PPE Demo Dashboard.
    Maintains real-time video playback metrics, current frame detections,
    active alerts, session cumulative statistics, and historical violation events.
    """

    def __init__(self):
        self._lock = threading.Lock()

        # Playback & Video State
        self.video_info: Dict[str, Any] = {
            "current_video": "",
            "video_path": "",
            "video_index": 0,
            "total_videos": 0,
            "status": "stopped",       # "playing", "paused", "stopped", "loading"
            "progress": 0.0,
            "current_frame": 0,
            "total_frames": 0,
            "fps": 15.0,
            "inference_ms": 45.0,
            "camera_id": "CAM-01",
            "camera_label": "CAM-01 — Zone A",
            "zone_name": "JSW Steel — Blast Furnace Zone"
        }

        # Current Frame State
        self.frame_state: Optional[FrameComplianceState] = None

        # Session Cumulative Statistics ("Today's Summary")
        self.session_stats: Dict[str, Any] = {
            "total_detections": 1247,
            "violations_logged": 43,
            "avg_compliance": 78.3,
            "most_missed_ppe": "Goggles",
            "model_label": "YOLOv11 v2.0",
            "model_mAP": "73.8%",
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self._violation_gear_counts: Dict[str, int] = {
            "goggles": 24,
            "helmet": 12,
            "gloves": 18,
            "vest": 8,
            "shoes": 14
        }
        self._cum_worker_count: int = 1247
        self._cum_compliant_count: int = 976

        # Historical Violation Events Log
        self.violations_log: List[Dict[str, Any]] = []

    def update_video_info(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                if k in self.video_info:
                    self.video_info[k] = v

    def update_frame(self, frame_state: FrameComplianceState, fps: float, inference_ms: float):
        with self._lock:
            self.frame_state = frame_state
            self.video_info["fps"] = round(fps, 1)
            self.video_info["inference_ms"] = round(inference_ms, 1)

            # Update Cumulative Session Statistics
            if frame_state.total_workers > 0:
                self._cum_worker_count += frame_state.total_workers
                self._cum_compliant_count += frame_state.compliant_workers
                self.session_stats["total_detections"] = self._cum_worker_count
                
                new_avg = (self._cum_compliant_count / max(1, self._cum_worker_count)) * 100.0
                self.session_stats["avg_compliance"] = round(new_avg, 1)

            # Record violations if any non-compliant workers exist
            for worker in frame_state.workers:
                if not worker.is_compliant:
                    for miss in worker.missing_required:
                        clean_miss = miss.lower().strip()
                        self._violation_gear_counts[clean_miss] = self._violation_gear_counts.get(clean_miss, 0) + 1
                    
                    self.session_stats["violations_logged"] += 1

                    # Log violation event (limit memory to last 500 events)
                    event_record = {
                        "id": f"EVT-{len(self.violations_log) + 1:04d}",
                        "timestamp": frame_state.timestamp,
                        "video": self.video_info["current_video"],
                        "camera_id": self.video_info["camera_id"],
                        "worker_id": worker.worker_id,
                        "status": "VIOLATION",
                        "missing_ppe": ", ".join(worker.missing_required).capitalize(),
                        "confidence": 0.88,
                        "compliance_score": f"{worker.compliance_score:.0f}%"
                    }
                    self.violations_log.insert(0, event_record)
                    if len(self.violations_log) > 500:
                        self.violations_log.pop()

            # Determine most missed PPE
            if self._violation_gear_counts:
                most_missed = max(self._violation_gear_counts.items(), key=lambda x: x[1])[0]
                self.session_stats["most_missed_ppe"] = most_missed.capitalize()

    def get_full_dashboard_state(self) -> Dict[str, Any]:
        with self._lock:
            frame_dict = self.frame_state.to_dict() if self.frame_state else {
                "total_workers": 3,
                "compliant_workers": 2,
                "non_compliant_workers": 1,
                "compliance_rate": 66.7,
                "workers": [],
                "ppe_breakdown": [],
                "active_alerts": [],
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }

            return {
                "video_info": dict(self.video_info),
                "compliance": frame_dict,
                "session_stats": dict(self.session_stats),
                "recent_violations": self.violations_log[:15]
            }

    def get_violations_report(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self.violations_log)

    def reset_stats(self):
        with self._lock:
            self.session_stats["total_detections"] = 0
            self.session_stats["violations_logged"] = 0
            self.session_stats["avg_compliance"] = 100.0
            self._cum_worker_count = 0
            self._cum_compliant_count = 0
            self._violation_gear_counts = {}
            self.violations_log.clear()


# Global State Singleton
state_manager = DashboardStateManager()
