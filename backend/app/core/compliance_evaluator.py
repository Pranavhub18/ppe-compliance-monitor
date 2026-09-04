from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional


@dataclass
class WorkerEvaluation:
    worker_id: int
    bbox: List[float]
    is_compliant: bool
    status: str                         # "COMPLIANT" or "VIOLATION"
    compliance_score: float             # 0.0 - 100.0%
    missing_required: List[str]         # ["helmet", ...]
    missing_optional: List[str]
    detected_ppe: Dict[str, float]
    negative_ppe: Dict[str, float]
    ppe_items: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "label": f"Worker {self.worker_id}",
            "bbox": [round(c, 1) for c in self.bbox],
            "is_compliant": self.is_compliant,
            "status": self.status,
            "compliance_score": round(self.compliance_score, 1),
            "missing_required": self.missing_required,
            "missing_optional": self.missing_optional,
            "detected_ppe": {k: round(v, 2) for k, v in self.detected_ppe.items()},
            "negative_ppe": {k: round(v, 2) for k, v in self.negative_ppe.items()},
            "summary_tag": "All PPE ✓" if self.is_compliant else f"Missing {', '.join(self.missing_required).capitalize()}"
        }


@dataclass
class PPEItemStat:
    item_key: str
    display_name: str
    detected_count: int
    total_workers: int
    percentage: float
    ratio_str: str
    status_level: str       # "success", "warning", "danger"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.item_key,
            "name": self.display_name,
            "detected_count": self.detected_count,
            "total_workers": self.total_workers,
            "percentage": round(self.percentage, 1),
            "ratio_str": self.ratio_str,
            "status_level": self.status_level
        }


@dataclass
class FrameComplianceState:
    total_workers: int
    compliant_workers: int
    non_compliant_workers: int
    compliance_rate: float
    violation_rate: float
    workers: List[WorkerEvaluation]
    ppe_breakdown: List[PPEItemStat]
    active_alerts: List[Dict[str, Any]]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_workers": self.total_workers,
            "compliant_workers": self.compliant_workers,
            "non_compliant_workers": self.non_compliant_workers,
            "compliance_rate": round(self.compliance_rate, 1),
            "violation_rate": round(self.violation_rate, 1),
            "workers": [w.to_dict() for w in self.workers],
            "ppe_breakdown": [p.to_dict() for p in self.ppe_breakdown],
            "active_alerts": self.active_alerts,
            "timestamp": self.timestamp
        }


class ComplianceEvaluator:
    """Evaluates frame-level and worker-level PPE safety compliance against rules."""

    def __init__(self, required_ppe: Optional[List[str]] = None, optional_ppe: Optional[List[str]] = None):
        self.required_ppe = [r.lower().strip() for r in (required_ppe or ["helmet", "vest", "gloves", "goggles", "shoes"])]
        self.optional_ppe = [o.lower().strip() for o in (optional_ppe or ["mask"])]

    def set_rules(self, required_ppe: List[str], optional_ppe: Optional[List[str]] = None):
        self.required_ppe = [r.lower().strip() for r in required_ppe if r.strip()]
        if optional_ppe is not None:
            self.optional_ppe = [o.lower().strip() for o in optional_ppe if o.strip()]

    def evaluate_frame(
        self,
        associated_workers: List[Dict[str, Any]],
        camera_label: str = "CAM-01 — Zone A"
    ) -> FrameComplianceState:
        now_str = datetime.now().strftime("%H:%M:%S")
        evaluated_workers: List[WorkerEvaluation] = []
        compliant_count = 0
        active_alerts: List[Dict[str, Any]] = []

        all_rules = self.required_ppe + self.optional_ppe
        gear_detected_counts = {gear: 0 for gear in all_rules}

        for w in associated_workers:
            w_id = int(w.get("track_id", 1))
            bbox = list(w.get("bbox", [0, 0, 0, 0]))
            detected = w.get("detected_ppe", {})
            negative = w.get("negative_ppe", {})
            ppe_items = w.get("ppe_items", [])

            missing_req = []
            missing_opt = []

            # Check required PPE
            for req in self.required_ppe:
                if req in negative or req not in detected:
                    missing_req.append(req)
                else:
                    gear_detected_counts[req] = gear_detected_counts.get(req, 0) + 1

            # Check optional PPE
            for opt in self.optional_ppe:
                if opt in negative or opt not in detected:
                    missing_opt.append(opt)
                else:
                    gear_detected_counts[opt] = gear_detected_counts.get(opt, 0) + 1

            is_compliant = (len(missing_req) == 0)
            if is_compliant:
                compliant_count += 1
            else:
                missing_str = ", ".join([m.capitalize() for m in missing_req])
                active_alerts.append({
                    "id": f"alt_{w_id}_{int(datetime.now().timestamp())}",
                    "worker_id": w_id,
                    "worker_label": f"Worker {w_id}",
                    "title": "Active violation",
                    "description": f"Worker {w_id} — Missing {missing_str}",
                    "missing_items": missing_req,
                    "location": camera_label,
                    "timestamp": now_str,
                    "is_live": True,
                    "severity": "CRITICAL" if "helmet" in missing_req or "vest" in missing_req else "HIGH"
                })

            req_len = max(1, len(self.required_ppe))
            comp_score = max(0.0, (req_len - len(missing_req)) / req_len * 100.0)

            evaluated_workers.append(WorkerEvaluation(
                worker_id=w_id,
                bbox=bbox,
                is_compliant=is_compliant,
                status="COMPLIANT" if is_compliant else "VIOLATION",
                compliance_score=comp_score,
                missing_required=missing_req,
                missing_optional=missing_opt,
                detected_ppe=detected,
                negative_ppe=negative,
                ppe_items=ppe_items
            ))

        total_workers = len(evaluated_workers)
        non_compliant_count = total_workers - compliant_count
        overall_rate = (compliant_count / total_workers * 100.0) if total_workers > 0 else 100.0
        violation_rate = (non_compliant_count / total_workers * 100.0) if total_workers > 0 else 0.0

        breakdown_items: List[PPEItemStat] = []
        for gear in self.required_ppe:
            det_cnt = gear_detected_counts.get(gear, 0)
            pct = (det_cnt / total_workers * 100.0) if total_workers > 0 else 100.0
            ratio = f"{det_cnt}/{total_workers}" if total_workers > 0 else "0/0"
            if pct >= 80.0:
                level = "success"
            elif pct >= 50.0:
                level = "warning"
            else:
                level = "danger"

            breakdown_items.append(PPEItemStat(
                item_key=gear,
                display_name=gear.capitalize(),
                detected_count=det_cnt,
                total_workers=total_workers,
                percentage=pct,
                ratio_str=ratio,
                status_level=level
            ))

        return FrameComplianceState(
            total_workers=total_workers,
            compliant_workers=compliant_count,
            non_compliant_workers=non_compliant_count,
            compliance_rate=overall_rate,
            violation_rate=violation_rate,
            workers=evaluated_workers,
            ppe_breakdown=breakdown_items,
            active_alerts=active_alerts,
            timestamp=now_str
        )
