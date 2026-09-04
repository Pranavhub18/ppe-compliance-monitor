import React from 'react';
import { ActiveAlertItem } from '../types/dashboard';

interface ActiveAlertProps {
  alerts: ActiveAlertItem[];
  location: string;
  timestamp: string;
}

export const ActiveAlert: React.FC<ActiveAlertProps> = ({ alerts, location, timestamp }) => {
  const hasAlert = alerts && alerts.length > 0;
  const currentAlert = hasAlert ? alerts[0] : null;

  if (hasAlert && currentAlert) {
    return (
      <div style={{ background: 'var(--bg-danger)', border: '0.5px solid var(--border-danger)', borderRadius: '12px', padding: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <i className="ti ti-alert-triangle" style={{ fontSize: '16px', color: 'var(--text-danger)' }} aria-hidden="true" />
          <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-danger)' }}>Active violation</span>
          <span style={{ fontSize: '11px', background: 'var(--text-danger)', color: 'white', padding: '1px 6px', borderRadius: '10px', marginLeft: 'auto' }}>
            LIVE
          </span>
        </div>
        <p style={{ fontSize: '12px', color: 'var(--text-danger)', margin: '0 0 4px 0' }}>
          <strong>{currentAlert.worker_label || `Worker ${currentAlert.worker_id}`}</strong> — {currentAlert.description.replace(/^Worker \d+ — /, '')}
        </p>
        <p style={{ fontSize: '11px', color: 'var(--text-danger)', margin: 0, opacity: 0.8 }}>
          {currentAlert.location || location || 'Zone A — CAM-01'} — {currentAlert.timestamp || timestamp || '15:50:37'}
        </p>
      </div>
    );
  }

  return (
    <div style={{ background: 'var(--bg-success)', border: '0.5px solid var(--border-success)', borderRadius: '12px', padding: '12px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
        <i className="ti ti-shield-check" style={{ fontSize: '16px', color: 'var(--text-success)' }} aria-hidden="true" />
        <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-success)' }}>Compliance Status</span>
        <span style={{ fontSize: '11px', background: 'var(--text-success)', color: 'white', padding: '1px 6px', borderRadius: '10px', marginLeft: 'auto' }}>
          SECURE
        </span>
      </div>
      <p style={{ fontSize: '12px', color: 'var(--text-success)', margin: '0 0 4px 0' }}>
        All detected workers compliant with active safety standards
      </p>
      <p style={{ fontSize: '11px', color: 'var(--text-success)', margin: 0, opacity: 0.8 }}>
        {location || 'Zone A — CAM-01'} — {timestamp || 'Live'}
      </p>
    </div>
  );
};
