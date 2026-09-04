import math
from typing import Dict, List, Tuple, Any


def compute_box_iou(boxA: Tuple[float, float, float, float], boxB: Tuple[float, float, float, float]) -> float:
    """Computes Intersection-over-Union between two boxes [x1, y1, x2, y2]."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_w = max(0.0, xB - xA)
    inter_h = max(0.0, yB - yA)
    inter_area = inter_w * inter_h

    areaA = max(1e-5, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    areaB = max(1e-5, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    return inter_area / float(areaA + areaB - inter_area)


def compute_point_distance_score(point: Tuple[float, float], box: Tuple[float, float, float, float], sigma: float = 75.0) -> float:
    """Computes Gaussian proximity score between a 2D point and the center of a bounding box."""
    cx = (box[0] + box[2]) / 2.0
    cy = (box[1] + box[3]) / 2.0
    dist_sq = (cx - point[0]) ** 2 + (cy - point[1]) ** 2
    return math.exp(-dist_sq / (2.0 * (sigma ** 2)))


class SpatialPPEAssociator:
    """
    Associates PPE detection bounding boxes to detected workers
    using anatomical zones and spatial proximity heuristics.
    """

    HEAD_CLASSES = {"helmet", "no_helmet", "goggles", "no_goggles", "mask", "no_mask"}
    TORSO_CLASSES = {"vest", "no_vest", "suit", "no_suit"}
    HAND_CLASSES = {"gloves", "glove", "no_gloves", "no_glove"}
    FEET_CLASSES = {"shoes", "no_shoes", "boots", "no_boots"}

    def __init__(self, iou_weight: float = 0.65, distance_sigma: float = 80.0, match_thresh: float = 0.20):
        self.iou_weight = iou_weight
        self.distance_sigma = distance_sigma
        self.match_thresh = match_thresh

    def _normalize_class_name(self, raw_name: str) -> Tuple[str, bool]:
        """
        Normalizes class names into standard PPE keys.
        Returns (clean_item_name, is_negative_violation_class).
        """
        name = raw_name.lower().strip().replace("-", "_")
        is_negative = name.startswith("no_")

        if name in {"glove", "gloves", "no_glove", "no_gloves"}:
            return "gloves", is_negative
        if name in {"shoe", "shoes", "boot", "boots", "no_shoes", "no_boots"}:
            return "shoes", is_negative
        if name in {"helmet", "no_helmet"}:
            return "helmet", is_negative
        if name in {"vest", "no_vest"}:
            return "vest", is_negative
        if name in {"goggles", "goggle", "no_goggles", "no_goggle"}:
            return "goggles", is_negative
        if name in {"mask", "no_mask"}:
            return "mask", is_negative
        if name in {"suit", "no_suit"}:
            return "suit", is_negative

        clean = name.replace("no_", "")
        return clean, is_negative

    def _get_anatomical_regions(self, bbox: Tuple[float, float, float, float]) -> Dict[str, Tuple[float, float, float, float]]:
        x1, y1, x2, y2 = bbox
        w = max(1.0, x2 - x1)
        h = max(1.0, y2 - y1)

        pad_x = max(15.0, w * 0.12)
        pad_head_top = max(25.0, h * 0.12)

        return {
            "head": (
                max(0.0, x1 - pad_x),
                max(0.0, y1 - pad_head_top),
                x2 + pad_x,
                y1 + h * 0.32
            ),
            "torso": (
                max(0.0, x1 - pad_x),
                y1 + h * 0.18,
                x2 + pad_x,
                y1 + h * 0.68
            ),
            "hands": (
                max(0.0, x1 - pad_x * 1.5),
                y1 + h * 0.35,
                x2 + pad_x * 1.5,
                y1 + h * 0.85
            ),
            "feet": (
                max(0.0, x1 - pad_x),
                y2 - h * 0.32,
                x2 + pad_x,
                y2 + pad_x
            )
        }

    def associate(
        self,
        workers: List[Dict[str, Any]],
        ppe_detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Associates each detected PPE item with the most suitable worker candidate.
        """
        if not workers:
            return []

        # Initialize PPE storage for each worker
        for w in workers:
            w["detected_ppe"] = {}      # {standard_name: conf}
            w["negative_ppe"] = {}      # {standard_name: conf}
            w["ppe_items"] = []         # detailed detections for rendering

        worker_regions = [self._get_anatomical_regions(w["bbox"]) for w in workers]

        for ppe in ppe_detections:
            raw_name = ppe["class_name"]
            p_box = ppe["bbox"]
            conf = float(ppe["confidence"])
            clean_name, is_neg = self._normalize_class_name(raw_name)

            best_worker_idx = -1
            best_score = -1.0

            for idx, (w, regions) in enumerate(zip(workers, worker_regions)):
                raw_lower = raw_name.lower().replace("-", "_")

                if raw_lower in self.HEAD_CLASSES or clean_name in {"helmet", "goggles", "mask"}:
                    target_region = regions["head"]
                elif raw_lower in self.TORSO_CLASSES or clean_name in {"vest", "suit"}:
                    target_region = regions["torso"]
                elif raw_lower in self.HAND_CLASSES or clean_name in {"gloves"}:
                    target_region = regions["hands"]
                elif raw_lower in self.FEET_CLASSES or clean_name in {"shoes"}:
                    target_region = regions["feet"]
                else:
                    target_region = w["bbox"]

                # Calculate region IoU and center distance score
                iou = compute_box_iou(p_box, target_region)
                reg_center = (
                    (target_region[0] + target_region[2]) / 2.0,
                    (target_region[1] + target_region[3]) / 2.0
                )
                dist_score = compute_point_distance_score(reg_center, p_box, sigma=self.distance_sigma)
                total_score = self.iou_weight * iou + (1.0 - self.iou_weight) * dist_score

                # Also consider overall worker box containment
                w_iou = compute_box_iou(p_box, w["bbox"])
                score = max(total_score, w_iou * 0.8)

                if score > best_score:
                    best_score = score
                    best_worker_idx = idx

            # Attach to target worker if score exceeds threshold
            if best_worker_idx >= 0 and best_score >= self.match_thresh:
                target_w = workers[best_worker_idx]
                target_w["ppe_items"].append({
                    "raw_class": raw_name,
                    "clean_class": clean_name,
                    "is_negative": is_neg,
                    "bbox": p_box,
                    "confidence": conf,
                    "score": round(best_score, 3)
                })

                if is_neg:
                    target_w["negative_ppe"][clean_name] = max(
                        target_w["negative_ppe"].get(clean_name, 0.0), conf
                    )
                else:
                    target_w["detected_ppe"][clean_name] = max(
                        target_w["detected_ppe"].get(clean_name, 0.0), conf
                    )

        return workers
