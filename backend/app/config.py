import os
from pathlib import Path
from typing import List
import yaml
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    name: str = "PPE Compliance Monitor"
    zone_name: str = "JSW Steel — Blast Furnace Zone"
    camera_id: str = "CAM-01"
    model_label: str = "YOLOv11 v2.0"
    host: str = Field(default_factory=lambda: os.environ.get("HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.environ.get("PORT", 8001)))
    debug: bool = False


class ModelConfig(BaseModel):
    weights_path: str = "models/new_best(2).pt"
    secondary_weights_path: str = "models/new_best(2).pt"
    device: str = "cpu"
    conf_threshold: float = 0.25
    iou_threshold: float = 0.45
    imgsz: int = 416


class RulesConfig(BaseModel):
    required_ppe: List[str] = Field(default_factory=lambda: ["helmet", "vest", "gloves", "goggles", "shoes"])
    optional_ppe: List[str] = Field(default_factory=lambda: ["mask"])


class VideoConfig(BaseModel):
    video_dir: str = "videos"
    target_fps: float = 20.0
    process_every_n_frames: int = 1
    loop_playlist: bool = True
    auto_next_video: bool = True
    stream_quality: int = 85
    max_stream_width: int = 960


class WebSocketConfig(BaseModel):
    enabled: bool = True
    broadcast_interval_frames: int = 1


class Settings(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    rules: RulesConfig = Field(default_factory=RulesConfig)
    video: VideoConfig = Field(default_factory=VideoConfig)
    websocket: WebSocketConfig = Field(default_factory=WebSocketConfig)

    # Root demo directory
    base_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)

    @classmethod
    def load(cls, config_path: Path = None) -> "Settings":
        base_dir = Path(__file__).resolve().parent.parent.parent
        if config_path is None:
            config_path = base_dir / "config" / "config.yaml"

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f) or {}
                if "PORT" in os.environ:
                    raw_data.setdefault("app", {})["port"] = int(os.environ["PORT"])
                if "HOST" in os.environ:
                    raw_data.setdefault("app", {})["host"] = os.environ["HOST"]
                return cls(base_dir=base_dir, **raw_data)
        return cls(base_dir=base_dir)

    def resolve_path(self, relative_or_absolute: str) -> Path:
        p = Path(relative_or_absolute)
        if p.is_absolute():
            return p
        return (self.base_dir / p).resolve()


# Global settings singleton
settings = Settings.load()
