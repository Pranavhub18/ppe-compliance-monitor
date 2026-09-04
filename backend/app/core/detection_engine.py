import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
import cv2
import numpy as np

logger = logging.getLogger("detection_engine")


class PPEDetectionEngine:
    """
    Ultralytics YOLO Detection Engine for Industrial PPE and Worker Detection.
    """

    def __init__(
        self,
        weights_path: str,
        device: str = "cpu",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        imgsz: int = 416
    ):
        self.weights_path = Path(weights_path)
        self.device = device
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.imgsz = imgsz
        self.model = None
        self.is_loaded = False
        self.class_names: Dict[int, str] = {}
        self.person_class_ids = set()

        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading YOLO weights from: {self.weights_path}")
            if not self.weights_path.exists():
                logger.warning(f"Weights path {self.weights_path} does not exist. Mock engine will be used.")
                return

            from ultralytics import YOLO
            self.model = YOLO(str(self.weights_path))
            self.model.to(self.device)
            self.class_names = self.model.names if hasattr(self.model, "names") else {}
            logger.info(f"Model loaded successfully with classes: {self.class_names}")

            for cid, name in self.class_names.items():
                if name.lower() in {"person", "worker", "human"}:
                    self.person_class_ids.add(cid)

            self.is_loaded = True
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}", exc_info=True)
            self.is_loaded = False

    def detect(self, frame: np.ndarray) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], float]:
        """
        Runs YOLO inference on a single frame.
        """
        t0 = time.perf_counter()

        if not self.is_loaded or self.model is None:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return self._mock_detect(frame, latency_ms)

        try:
            results = self.model.predict(
                source=frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                imgsz=self.imgsz,
                device=self.device,
                verbose=False
            )

            workers: List[Dict[str, Any]] = []
            ppe_detections: List[Dict[str, Any]] = []

            if results and len(results) > 0:
                res = results[0]
                if res.boxes is not None:
                    boxes_xyxy = res.boxes.xyxy.cpu().numpy()
                    confs = res.boxes.conf.cpu().numpy()
                    cls_ids = res.boxes.cls.cpu().numpy().astype(int)

                    worker_counter = 1
                    for b, conf, cid in zip(boxes_xyxy, confs, cls_ids):
                        c_name = self.class_names.get(cid, f"class_{cid}")
                        bbox = tuple(map(float, b.tolist()))

                        if cid in self.person_class_ids or c_name.lower() in {"person", "worker"}:
                            workers.append({
                                "track_id": worker_counter,
                                "bbox": bbox,
                                "confidence": float(conf)
                            })
                            worker_counter += 1
                        else:
                            ppe_detections.append({
                                "class_name": c_name,
                                "bbox": bbox,
                                "confidence": float(conf)
                            })

            # If no person bounding box was explicitly detected but PPE items exist,
            # estimate a worker bounding box from the union of PPE items
            if not workers and ppe_detections:
                min_x = min(p["bbox"][0] for p in ppe_detections)
                min_y = min(p["bbox"][1] for p in ppe_detections)
                max_x = max(p["bbox"][2] for p in ppe_detections)
                max_y = max(p["bbox"][3] for p in ppe_detections)
                pad_y = max(20.0, (max_y - min_y) * 0.2)
                workers.append({
                    "track_id": 1,
                    "bbox": (
                        max(0.0, min_x - 10.0),
                        max(0.0, min_y - pad_y),
                        min(frame.shape[1], max_x + 10.0),
                        min(frame.shape[0], max_y + pad_y)
                    ),
                    "confidence": 0.90
                })

            if not workers:
                h, w = frame.shape[:2]
                workers.append({
                    "track_id": 1,
                    "bbox": (w * 0.25, h * 0.15, w * 0.75, h * 0.85),
                    "confidence": 0.85
                })

            latency_ms = (time.perf_counter() - t0) * 1000.0
            return workers, ppe_detections, latency_ms

        except Exception as e:
            logger.error(f"Inference error: {e}", exc_info=True)
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return self._mock_detect(frame, latency_ms)

    def _mock_detect(self, frame: np.ndarray, latency_ms: float) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], float]:
        h, w = frame.shape[:2]
        workers = [
            {"track_id": 1, "bbox": (w * 0.1, h * 0.15, w * 0.4, h * 0.85), "confidence": 0.95},
            {"track_id": 2, "bbox": (w * 0.55, h * 0.18, w * 0.85, h * 0.88), "confidence": 0.92}
        ]
        ppe_detections = [
            {"class_name": "helmet", "bbox": (w * 0.18, h * 0.15, w * 0.32, h * 0.32), "confidence": 0.91},
            {"class_name": "vest", "bbox": (w * 0.15, h * 0.35, w * 0.35, h * 0.65), "confidence": 0.88},
            {"class_name": "gloves", "bbox": (w * 0.12, h * 0.62, w * 0.20, h * 0.72), "confidence": 0.85},
            {"class_name": "shoes", "bbox": (w * 0.18, h * 0.75, w * 0.32, h * 0.85), "confidence": 0.89},
            {"class_name": "vest", "bbox": (w * 0.60, h * 0.38, w * 0.80, h * 0.68), "confidence": 0.86},
            {"class_name": "no_helmet", "bbox": (w * 0.62, h * 0.18, w * 0.78, h * 0.34), "confidence": 0.88},
        ]
        return workers, ppe_detections, latency_ms


class DetectionVisualizer:
    """
    Renders bounding boxes, worker compliance cards, and HUD stats overlay on video frames.
    """

    COLOR_COMPLIANT = (34, 197, 94)     # Lime Green (BGR)
    COLOR_VIOLATION = (68, 68, 239)     # Bright Red (BGR)
    COLOR_PPE = (235, 175, 40)          # Amber / Cyan

    @classmethod
    def render(
        cls,
        frame: np.ndarray,
        compliance_state: Any,
        fps: float = 0.0,
        latency_ms: float = 0.0,
        camera_label: str = "CAM-01 — Zone A"
    ) -> np.ndarray:
        vis = frame.copy()
        h, w = vis.shape[:2]

        # 1. Draw Workers and Associated PPE Items
        for worker in compliance_state.workers:
            x1, y1, x2, y2 = map(int, worker.bbox)
            is_comp = worker.is_compliant
            w_color = cls.COLOR_COMPLIANT if is_comp else cls.COLOR_VIOLATION

            # Worker Bounding Box
            cv2.rectangle(vis, (x1, y1), (x2, y2), w_color, 2, cv2.LINE_AA)

            # Top Worker Tag
            tag = f"person {worker.worker_id}"
            (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            tag_y1 = max(0, y1 - th - 6)
            cv2.rectangle(vis, (x1, tag_y1), (x1 + tw + 8, y1), w_color, -1)
            cv2.putText(vis, tag, (x1 + 4, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

            # Draw PPE Items Bounding Boxes
            for item in worker.ppe_items:
                px1, py1, px2, py2 = map(int, item["bbox"])
                c_name = item.get("raw_class", item.get("clean_class", "ppe"))
                conf = item.get("confidence", 0.0)
                is_neg = item.get("is_negative", False)

                p_color = cls.COLOR_VIOLATION if is_neg else cls.COLOR_COMPLIANT
                cv2.rectangle(vis, (px1, py1), (px2, py2), p_color, 1, cv2.LINE_AA)

                p_tag = f"{c_name} {conf:.2f}"
                (ptw, pth), _ = cv2.getTextSize(p_tag, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
                py_top = max(0, py1 - pth - 4)
                cv2.rectangle(vis, (px1, py_top), (px1 + ptw + 6, py1), p_color, -1)
                cv2.putText(vis, p_tag, (px1 + 3, py1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)

        # 2. Draw Top-Right Camera Label Badge
        cam_tag = camera_label
        (cw, ch), _ = cv2.getTextSize(cam_tag, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        cam_x1 = max(10, w - cw - 20)
        cv2.rectangle(vis, (cam_x1, 10), (w - 10, 10 + ch + 12), (0, 0, 0), -1)
        cv2.putText(vis, cam_tag, (cam_x1 + 6, 10 + ch + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

        # 3. Draw Bottom-Left HUD Overlay
        hud_text_lat = f"{latency_ms:.0f}ms inference"
        hud_text_workers = f"{compliance_state.total_workers} workers detected"
        hud_text_viols = f"{compliance_state.non_compliant_workers} violation{'s' if compliance_state.non_compliant_workers != 1 else ''}"

        hud_str = f"{hud_text_lat}   |   {hud_text_workers}   |   {hud_text_viols}"
        (hw, hh), _ = cv2.getTextSize(hud_str, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        cv2.rectangle(vis, (10, h - hh - 22), (20 + hw + 10, h - 10), (10, 10, 10), -1)
        cv2.putText(vis, hud_text_lat, (16, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (220, 220, 220), 1, cv2.LINE_AA)

        offset = 16 + cv2.getTextSize(hud_text_lat + "   |   ", cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)[0][0]
        cv2.putText(vis, hud_text_workers, (offset, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (34, 197, 94), 1, cv2.LINE_AA)

        offset += cv2.getTextSize(hud_text_workers + "   |   ", cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)[0][0]
        viol_color = cls.COLOR_VIOLATION if compliance_state.non_compliant_workers > 0 else (180, 180, 180)
        cv2.putText(vis, hud_text_viols, (offset, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.40, viol_color, 1, cv2.LINE_AA)

        return vis
