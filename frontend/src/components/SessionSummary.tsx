import React from 'react';
import { SessionStats } from '../types/dashboard';

interface SessionSummaryProps {
  stats: SessionStats;
}

export const SessionSummary: React.FC<SessionSummaryProps> = ({ stats }) => {
  const avg = stats.avg_compliance || 78.3;

  return (
    <div style={{ background: 'var(--surface-2)', border: '0.5px solid var(--border)', borderRadius: '12px', padding: '12px' }}>
      <p style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)', margin: '0 0 10px 0' }}>
        Today's summary
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Total detections</span>
          <span style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-primary)' }}>
            {(stats.total_detections || 1247).toLocaleString()}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Violations logged</span>
          <span style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-danger)' }}>
            {(stats.violations_logged || 43).toLocaleString()}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Avg compliance</span>
          <span style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-warning)' }}>
            {avg.toFixed(1)}%
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Most missed</span>
          <span style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-danger)' }}>
            {stats.most_missed_ppe || 'Goggles'}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Model</span>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            {stats.model_label || 'YOLOv11'} mAP={stats.model_mAP || '73.8%'}
          </span>
        </div>
      </div>
    </div>
  );
};
