import time
import threading
import logging
from pathlib import Path
from typing import Optional, Any
import cv2
import numpy as np

from .video_manager import VideoManager
from .detection_engine import PPEDetectionEngine, DetectionVisualizer
from .spatial_associator import SpatialPPEAssociator
from .compliance_evaluator import ComplianceEvaluator
from .state_manager import state_manager
from .websocket_hub import ws_hub
from ..config import Settings, settings

logger = logging.getLogger("video_processor")


class ContinuousVideoProcessor:
    """
    Dedicated background video processing pipeline with synchronized dual-stream
    (Before: Original Raw Feed, After: YOLO AI Detection Feed), real-time PPE compliance
    evaluation, MJPEG frame encoding, and continuous dynamic video queue auto-discovery.
    """

    def __init__(self, config: Settings = settings):
        self.config = config
        self.video_manager = VideoManager(
            video_dir=config.resolve_path(config.video.video_dir),
            loop_playlist=config.video.loop_playlist
        )
        self.detection_engine = PPEDetectionEngine(
            weights_path=str(config.resolve_path(config.model.weights_path)),
            device=config.model.device,
            conf_threshold=config.model.conf_threshold,
            iou_threshold=config.model.iou_threshold,
            imgsz=config.model.imgsz
        )
        self.associator = SpatialPPEAssociator()
        self.evaluator = ComplianceEvaluator(
            required_ppe=config.rules.required_ppe,
            optional_ppe=config.rules.optional_ppe
        )

        # Processing Thread & Controls
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._switch_video_event = threading.Event()
        self._speed_multiplier: float = 1.0

        # Dual frame buffers for synchronized Before & After streaming
        self._frame_lock = threading.Lock()
        self._latest_annotated_jpeg: Optional[bytes] = None  # After (AI Detection)
        self._latest_raw_jpeg: Optional[bytes] = None        # Before (Original Video)
        self._latest_annotated_img: Optional[np.ndarray] = None

        # FPS tracking
        self._fps_history = []
        self._is_running = False

    def start(self):
        """Starts video processing loop in background thread."""
        if self._is_running:
            self.resume()
            return

        self._stop_event.clear()
        self._pause_event.clear()
        self._is_running = True
        self._thread = threading.Thread(target=self._run_loop, name="VideoProcessorThread", daemon=True)
        self._thread.start()
        logger.info("Video processor thread started.")

    def pause(self):
        """Pauses video processing."""
        self._pause_event.set()
        state_manager.update_video_info(status="paused")
        logger.info("Video processing paused.")

    def resume(self):
        """Resumes video processing."""
        self._pause_event.clear()
        state_manager.update_video_info(status="playing")
        logger.info("Video processing resumed.")

    def stop(self):
        """Stops video processing completely."""
        self._stop_event.set()
        self._pause_event.clear()
        self._is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        state_manager.update_video_info(status="stopped", progress=0.0)
        logger.info("Video processor stopped.")

    def next_video(self):
        """Skips to next video in queue."""
        self.video_manager.next_video()
        self._switch_video_event.set()
        logger.info("Skipping to next video.")

    def prev_video(self):
        """Returns to previous video in queue."""
        self.video_manager.prev_video()
        self._switch_video_event.set()
        logger.info("Returning to previous video.")

    def restart_video(self):
        """Restarts current video from beginning."""
        self._switch_video_event.set()
        logger.info("Restarting current video.")

    def select_video(self, index_or_name: Any):
        """Selects video by index or filename."""
        if isinstance(index_or_name, int):
            self.video_manager.set_index(index_or_name)
        else:
            self.video_manager.set_by_name(str(index_or_name))
        self._switch_video_event.set()

    def set_speed(self, speed: float):
        self._speed_multiplier = max(0.25, min(4.0, float(speed)))
        logger.info(f"Playback speed set to {self._speed_multiplier}x")

    def update_rules(self, required_ppe: list, optional_ppe: Optional[list] = None):
        self.evaluator.set_rules(required_ppe, optional_ppe)
        logger.info(f"Updated PPE rules: required={required_ppe}")

    def update_conf_threshold(self, conf: float):
        self.detection_engine.conf_threshold = max(0.05, min(0.95, float(conf)))
        logger.info(f"Updated model confidence threshold to {conf}")

    def get_latest_annotated_jpeg(self) -> Optional[bytes]:
        """Returns the AFTER (AI Detection) annotated frame."""
        with self._frame_lock:
            return self._latest_annotated_jpeg

    def get_latest_raw_jpeg(self) -> Optional[bytes]:
        """Returns the BEFORE (Original Raw) frame."""
        with self._frame_lock:
            return self._latest_raw_jpeg

    def _broadcast_playlist_update(self):
        """Broadcasts updated playlist queue to all connected clients."""
        playlist_data = self.video_manager.get_playlist_info()
        state_manager.update_video_info(
            total_videos=len(playlist_data),
            video_index=self.video_manager.get_current_index()
        )
        if self.config.websocket.enabled:
            ws_hub.broadcast_sync({
                "type": "PLAYLIST_UPDATE",
                "data": {
                    "videos": playlist_data,
                    "total": len(playlist_data),
                    "current_index": self.video_manager.get_current_index()
                }
            })

    def _run_loop(self):
        """Continuous video loop across queue with auto-discovery of newly added videos."""
        last_check_time = 0.0

        while not self._stop_event.is_set():
            now = time.time()
            if now - last_check_time > 2.0:
                last_check_time = now
                if self.video_manager.check_for_updates():
                    self._broadcast_playlist_update()

            current_path = self.video_manager.get_current_video()
            if not current_path or not current_path.exists():
                logger.warning("No video found in queue. Checking directory in 2 seconds...")
                state_manager.update_video_info(status="no_videos", current_video="No video available")
                time.sleep(2.0)
                continue

            self._process_single_video(current_path)

            if not self.config.video.auto_next_video:
                break

    def _process_single_video(self, video_path: Path):
        """Processes one video until EOF or user skip."""
        logger.info(f"Opening video: {video_path.name}")
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.error(f"Cannot open video file: {video_path}")
            self.video_manager.next_video()
            return

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100
        native_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        target_fps = min(self.config.video.target_fps, native_fps)

        state_manager.update_video_info(
            current_video=video_path.name,
            video_path=str(video_path),
            video_index=self.video_manager.get_current_index(),
            total_videos=self.video_manager.total_videos,
            status="playing",
            current_frame=0,
            total_frames=total_frames,
            progress=0.0
        )
        self._broadcast_playlist_update()

        frame_idx = 0
        self._switch_video_event.clear()
        last_dir_check = time.time()

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.config.video.stream_quality]

        while not self._stop_event.is_set():
            if self._switch_video_event.is_set():
                self._switch_video_event.clear()
                break

            if self._pause_event.is_set():
                time.sleep(0.1)
                continue

            # Periodically scan for newly added videos in folder
            t_now = time.time()
            if t_now - last_dir_check > 2.5:
                last_dir_check = t_now
                if self.video_manager.check_for_updates():
                    self._broadcast_playlist_update()

            t_start = time.perf_counter()

            ret, frame = cap.read()
            if not ret:
                logger.info(f"Reached EOF for {video_path.name}")
                if self.config.video.auto_next_video:
                    self.video_manager.next_video()
                break

            frame_idx += 1
            progress_pct = round((frame_idx / max(1, total_frames)) * 100.0, 1)

            # Resize frame if larger than max stream width for fast throughput
            h, w = frame.shape[:2]
            max_w = self.config.video.max_stream_width
            if w > max_w:
                scale = max_w / float(w)
                frame = cv2.resize(frame, (max_w, int(h * scale)), interpolation=cv2.INTER_AREA)

            # 1. Encode BEFORE (Original Raw Video)
            _, raw_jpeg_buffer = cv2.imencode(".jpg", frame, encode_param)
            raw_jpeg_bytes = raw_jpeg_buffer.tobytes()

            # 2. PPE & Worker Detection Inference
            workers, ppe_detections, latency_ms = self.detection_engine.detect(frame)

            # 3. Spatial Association
            associated_workers = self.associator.associate(workers, ppe_detections)

            # 4. Safety Compliance Evaluation
            compliance_state = self.evaluator.evaluate_frame(
                associated_workers,
                camera_label=f"{self.config.app.camera_id} — Zone A"
            )

            # 5. Measure achieved FPS
            t_infer = time.perf_counter()
            actual_fps = 1.0 / max(1e-4, (t_infer - t_start))
            self._fps_history.append(actual_fps)
            if len(self._fps_history) > 20:
                self._fps_history.pop(0)
            avg_fps = sum(self._fps_history) / len(self._fps_history)

            # 6. Render AFTER (AI Detection with Bounding Boxes & HUD)
            annotated_frame = DetectionVisualizer.render(
                frame=frame,
                compliance_state=compliance_state,
                fps=avg_fps,
                latency_ms=latency_ms,
                camera_label=f"{self.config.app.camera_id} — Zone A"
            )

            # 7. Encode AFTER (Annotated Video)
            _, annotated_jpeg_buffer = cv2.imencode(".jpg", annotated_frame, encode_param)
            annotated_jpeg_bytes = annotated_jpeg_buffer.tobytes()

            with self._frame_lock:
                self._latest_raw_jpeg = raw_jpeg_bytes
                self._latest_annotated_jpeg = annotated_jpeg_bytes
                self._latest_annotated_img = annotated_frame

            # 8. Update State Manager
            state_manager.update_video_info(
                current_frame=frame_idx,
                total_frames=total_frames,
                progress=progress_pct
            )
            state_manager.update_frame(compliance_state, avg_fps, latency_ms)

            # 9. Broadcast Telemetry to WebSocket Clients
            if self.config.websocket.enabled:
                dashboard_payload = state_manager.get_full_dashboard_state()
                ws_hub.broadcast_sync({
                    "type": "FRAME_UPDATE",
                    "data": dashboard_payload
                })

            # Frame Pacing
            t_elapsed = time.perf_counter() - t_start
            delay_needed = (1.0 / max(1.0, self.config.video.target_fps * self._speed_multiplier)) - t_elapsed
            if delay_needed > 0:
                time.sleep(delay_needed)

        cap.release()


# Global Processor Singleton
video_processor = ContinuousVideoProcessor()
