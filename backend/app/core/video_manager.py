import logging
from pathlib import Path
from typing import List, Dict, Optional, Any

logger = logging.getLogger("video_manager")


class VideoManager:
    """
    Manages video playlist discovery, queuing, navigation, and continuous auto-discovery.
    """

    SUPPORTED_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".webm"}

    def __init__(self, video_dir: Path, loop_playlist: bool = True):
        self.video_dir = Path(video_dir)
        self.loop_playlist = loop_playlist
        self.playlist: List[Path] = []
        self.current_idx: int = 0

        self.reload_videos()

    def reload_videos(self) -> bool:
        """
        Scans video directory and updates playlist.
        Returns True if playlist changed.
        """
        if not self.video_dir.exists():
            logger.warning(f"Video directory does not exist: {self.video_dir}")
            had_files = len(self.playlist) > 0
            self.playlist = []
            return had_files

        current_names = [p.name for p in self.playlist]
        new_files = [
            f for f in sorted(self.video_dir.iterdir())
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ]
        new_names = [f.name for f in new_files]

        if current_names != new_names:
            logger.info(f"Video directory changed! Found {len(new_files)} videos (was {len(self.playlist)}).")
            current_file = self.get_current_video()
            self.playlist = new_files

            if current_file and current_file in self.playlist:
                self.current_idx = self.playlist.index(current_file)
            elif self.playlist:
                self.current_idx = min(self.current_idx, len(self.playlist) - 1)
            else:
                self.current_idx = 0
            return True

        return False

    def check_for_updates(self) -> bool:
        """Polls video directory for newly added or removed video files."""
        return self.reload_videos()

    @property
    def total_videos(self) -> int:
        return len(self.playlist)

    def get_current_video(self) -> Optional[Path]:
        if not self.playlist:
            return None
        return self.playlist[self.current_idx % len(self.playlist)]

    def get_current_index(self) -> int:
        return self.current_idx

    def next_video(self) -> Optional[Path]:
        self.check_for_updates()
        if not self.playlist:
            return None
        self.current_idx = (self.current_idx + 1) % len(self.playlist)
        return self.get_current_video()

    def prev_video(self) -> Optional[Path]:
        self.check_for_updates()
        if not self.playlist:
            return None
        self.current_idx = (self.current_idx - 1 + len(self.playlist)) % len(self.playlist)
        return self.get_current_video()

    def set_index(self, index: int) -> Optional[Path]:
        self.check_for_updates()
        if not self.playlist:
            return None
        self.current_idx = max(0, min(index, len(self.playlist) - 1))
        return self.get_current_video()

    def set_by_name(self, filename: str) -> Optional[Path]:
        self.check_for_updates()
        for idx, p in enumerate(self.playlist):
            if p.name == filename or p.stem == filename:
                self.current_idx = idx
                return p
        return None

    def get_playlist_info(self) -> List[Dict[str, Any]]:
        self.check_for_updates()
        result = []
        for idx, p in enumerate(self.playlist):
            try:
                size_mb = round(p.stat().st_size / (1024 * 1024), 2)
            except Exception:
                size_mb = 0.0

            result.append({
                "index": idx,
                "filename": p.name,
                "title": p.stem.replace("_", " ").replace("-", " ").capitalize(),
                "size_mb": size_mb,
                "is_current": (idx == self.current_idx)
            })
        return result
