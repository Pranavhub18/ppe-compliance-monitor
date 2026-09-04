import React from 'react';
import { VideoInfo, SessionStats } from '../types/dashboard';

interface HeaderProps {
  videoInfo: VideoInfo;
  sessionStats: SessionStats;
  isConnected: boolean;
}

export const Header: React.FC<HeaderProps> = ({ videoInfo, sessionStats, isConnected }) => {
  return (
    <div
      style={{
        background: 'var(--surface-2)',
        borderBottom: '0.5px solid var(--border)',
        padding: '12px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div
          style={{
            background: 'var(--bg-danger)',
            borderRadius: '50%',
            width: '10px',
            height: '10px',
            animation: 'pulse 1.5s infinite',
          }}
        />
        <span style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>
          PPE Compliance Monitor
        </span>
        <span
          style={{
            fontSize: '12px',
            color: 'var(--text-secondary)',
            background: 'var(--surface-1)',
            padding: '2px 8px',
            borderRadius: 'var(--radius)',
            border: '0.5px solid var(--border)',
          }}
        >
          {videoInfo.zone_name || 'JSW Steel — Blast Furnace Zone'}
        </span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
          <i className="ti ti-clock" aria-hidden="true" style={{ marginRight: '4px' }} />
          Live — {videoInfo.fps > 0 ? `${videoInfo.fps} FPS` : '15 FPS'}
        </span>
        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
          <i className="ti ti-cpu" aria-hidden="true" style={{ marginRight: '4px' }} />
          {sessionStats.model_label || 'YOLOv11 v2.0'}
        </span>
      </div>
    </div>
  );
};
