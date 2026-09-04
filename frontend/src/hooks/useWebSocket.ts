import { useState, useEffect, useRef, useCallback } from 'react';
import { DashboardState, VideoPlaylistItem } from '../types/dashboard';

const DEFAULT_STATE: DashboardState = {
  video_info: {
    current_video: 'Loading...',
    video_path: '',
    video_index: 0,
    total_videos: 0,
    status: 'loading',
    progress: 0,
    current_frame: 0,
    total_frames: 0,
    fps: 15.0,
    inference_ms: 45.0,
    camera_id: 'CAM-01',
    camera_label: 'CAM-01 — Zone A',
    zone_name: 'JSW Steel — Blast Furnace Zone',
  },
  compliance: {
    total_workers: 3,
    compliant_workers: 2,
    non_compliant_workers: 1,
    compliance_rate: 66.7,
    workers: [
      {
        worker_id: 1,
        label: 'Worker 1',
        bbox: [60, 40, 140, 220],
        is_compliant: true,
        status: 'COMPLIANT',
        compliance_score: 100,
        missing_required: [],
        missing_optional: [],
        detected_ppe: { helmet: 0.91, vest: 0.88, gloves: 0.85, shoes: 0.89 },
        negative_ppe: {},
        summary_tag: 'All PPE ✓',
      },
      {
        worker_id: 2,
        label: 'Worker 2',
        bbox: [200, 50, 280, 230],
        is_compliant: false,
        status: 'VIOLATION',
        compliance_score: 60,
        missing_required: ['helmet'],
        missing_optional: [],
        detected_ppe: { vest: 0.86, shoes: 0.82 },
        negative_ppe: { helmet: 0.88 },
        summary_tag: 'No helmet',
      },
      {
        worker_id: 3,
        label: 'Worker 3',
        bbox: [350, 55, 420, 215],
        is_compliant: true,
        status: 'COMPLIANT',
        compliance_score: 100,
        missing_required: [],
        missing_optional: [],
        detected_ppe: { helmet: 0.84, vest: 0.82, gloves: 0.80 },
        negative_ppe: {},
        summary_tag: 'All PPE ✓',
      },
    ],
    ppe_breakdown: [
      { key: 'helmet', name: 'Helmet', detected_count: 2, total_workers: 3, percentage: 91, ratio_str: '2/3', status_level: 'success' },
      { key: 'vest', name: 'Vest', detected_count: 3, total_workers: 3, percentage: 88, ratio_str: '3/3', status_level: 'success' },
      { key: 'gloves', name: 'Gloves', detected_count: 1, total_workers: 3, percentage: 67, ratio_str: '1/3', status_level: 'warning' },
      { key: 'goggles', name: 'Goggles', detected_count: 0, total_workers: 3, percentage: 33, ratio_str: '0/3', status_level: 'danger' },
      { key: 'shoes', name: 'Shoes', detected_count: 2, total_workers: 3, percentage: 70, ratio_str: '2/3', status_level: 'warning' },
    ],
    active_alerts: [
      {
        id: 'alt-init',
        worker_id: 2,
        worker_label: 'Worker 2',
        title: 'Active violation',
        description: 'Worker 2 — No helmet detected',
        missing_items: ['helmet'],
        location: 'CAM-01 — Zone A',
        timestamp: '15:50:37',
        is_live: true,
        severity: 'CRITICAL',
      },
    ],
    timestamp: '15:50:37',
  },
  session_stats: {
    total_detections: 1247,
    violations_logged: 43,
    avg_compliance: 78.3,
    most_missed_ppe: 'Goggles',
    model_label: 'YOLOv11 v2.0',
    model_mAP: '73.8%',
    started_at: '2026-09-01 10:00:00',
  },
  recent_violations: [],
};

export function useWebSocket() {
  const [state, setState] = useState<DashboardState>(DEFAULT_STATE);
  const [playlist, setPlaylist] = useState<VideoPlaylistItem[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<any>(null);

  const connect = useCallback(() => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const isViteDev = window.location.port === '5173';
      const wsUrl = isViteDev
        ? `${protocol}//${window.location.hostname || 'localhost'}:8001/ws`
        : `${protocol}//${window.location.host}/ws`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'FRAME_UPDATE' || payload.type === 'INIT_STATE') {
            setState(payload.data);
          } else if (payload.type === 'PLAYLIST_UPDATE') {
            if (payload.data && Array.isArray(payload.data.videos)) {
              setPlaylist(payload.data.videos);
            }
          }
        } catch (e) {
          // ignore non-json messages
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 2000);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch (e) {
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    }
  }, []);

  useEffect(() => {
    connect();

    const fetchPlaylist = () => {
      fetch('/api/videos')
        .then((res) => res.json())
        .then((data) => {
          if (data && Array.isArray(data.videos)) {
            setPlaylist(data.videos);
          }
        })
        .catch(() => {});
    };

    fetchPlaylist();

    const pollInterval = setInterval(() => {
      if (!isConnected) {
        fetch('/api/dashboard')
          .then((res) => res.json())
          .then((data) => {
            if (data && data.video_info) {
              setState(data);
            }
          })
          .catch(() => {});
        fetchPlaylist();
      }
    }, 2500);

    return () => {
      clearInterval(pollInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connect, isConnected]);

  return { state, playlist, setPlaylist, isConnected };
}
