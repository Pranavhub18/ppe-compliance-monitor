export interface VideoInfo {
  current_video: string;
  video_path: string;
  video_index: number;
  total_videos: number;
  status: 'playing' | 'paused' | 'stopped' | 'loading' | 'no_videos';
  progress: number;
  current_frame: number;
  total_frames: number;
  fps: number;
  inference_ms: number;
  camera_id: string;
  camera_label: string;
  zone_name: string;
}

export interface WorkerItem {
  worker_id: number;
  label: string;
  bbox: [number, number, number, number];
  is_compliant: boolean;
  status: 'COMPLIANT' | 'VIOLATION';
  compliance_score: number;
  missing_required: string[];
  missing_optional: string[];
  detected_ppe: Record<string, number>;
  negative_ppe: Record<string, number>;
  summary_tag: string;
}

export interface PPEBreakdownItem {
  key: string;
  name: string;
  detected_count: number;
  total_workers: number;
  percentage: number;
  ratio_str: string;
  status_level: 'success' | 'warning' | 'danger';
}

export interface ActiveAlertItem {
  id: string;
  worker_id: number;
  worker_label: string;
  title: string;
  description: string;
  missing_items: string[];
  location: string;
  timestamp: string;
  is_live: boolean;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM';
}

export interface ComplianceData {
  total_workers: number;
  compliant_workers: number;
  non_compliant_workers: number;
  compliance_rate: number;
  violation_rate?: number;
  workers: WorkerItem[];
  ppe_breakdown: PPEBreakdownItem[];
  active_alerts: ActiveAlertItem[];
  timestamp: string;
}

export interface SessionStats {
  total_detections: number;
  violations_logged: number;
  avg_compliance: number;
  most_missed_ppe: string;
  model_label: string;
  model_mAP: string;
  started_at: string;
}

export interface ViolationEvent {
  id: string;
  timestamp: string;
  video: string;
  camera_id: string;
  worker_id: number;
  status: string;
  missing_ppe: string;
  confidence: number;
  compliance_score: string;
}

export interface DashboardState {
  video_info: VideoInfo;
  compliance: ComplianceData;
  session_stats: SessionStats;
  recent_violations: ViolationEvent[];
}

export interface VideoPlaylistItem {
  index: number;
  filename: string;
  title: string;
  size_mb: number;
  is_current: boolean;
}
