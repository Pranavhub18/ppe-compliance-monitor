import React, { useState, useEffect } from 'react';
import { ViolationEvent } from '../types/dashboard';

interface ExportReportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ExportReportModal: React.FC<ExportReportModalProps> = ({ isOpen, onClose }) => {
  const [events, setEvents] = useState<ViolationEvent[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetch('/api/events')
        .then((res) => res.json())
        .then((data) => {
          setEvents(Array.isArray(data) ? data : []);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const downloadCSV = () => {
    window.open('/api/export/report?format=csv', '_blank');
  };

  const downloadJSON = () => {
    window.open('/api/export/report?format=json', '_blank');
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0,0,0,0.7)',
        backdropFilter: 'blur(5px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
      }}
    >
      <div
        className="fade-in"
        style={{
          background: 'var(--surface-1)',
          border: '1px solid var(--border)',
          borderRadius: '16px',
          width: '100%',
          maxWidth: '720px',
          padding: '24px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <i className="ti ti-report-analytics" style={{ fontSize: '20px', color: 'var(--text-danger)' }} />
            <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
              PPE Violation Audit Log
            </h3>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              fontSize: '18px',
            }}
          >
            <i className="ti ti-x" />
          </button>
        </div>

        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
          Live safety audit record containing timestamped violation events captured by the YOLO PPE detection model.
        </p>

        {/* Table Container */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            background: 'var(--surface-0)',
            marginBottom: '18px',
          }}
        >
          {loading ? (
            <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
              Loading violation records...
            </div>
          ) : events.length === 0 ? (
            <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
              No violations recorded in the current session.
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'left' }}>
              <thead>
                <tr style={{ background: 'var(--surface-2)', borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                  <th style={{ padding: '8px 12px' }}>Event ID</th>
                  <th style={{ padding: '8px 12px' }}>Time</th>
                  <th style={{ padding: '8px 12px' }}>Worker</th>
                  <th style={{ padding: '8px 12px' }}>Missing Gear</th>
                  <th style={{ padding: '8px 12px' }}>Score</th>
                  <th style={{ padding: '8px 12px' }}>Video Source</th>
                </tr>
              </thead>
              <tbody>
                {events.map((ev, idx) => (
                  <tr
                    key={ev.id || idx}
                    style={{
                      borderBottom: '1px solid rgba(255,255,255,0.05)',
                      background: idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
                    }}
                  >
                    <td style={{ padding: '8px 12px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{ev.id}</td>
                    <td style={{ padding: '8px 12px', fontFamily: 'var(--font-mono)' }}>{ev.timestamp}</td>
                    <td style={{ padding: '8px 12px', fontWeight: 500, color: 'var(--text-primary)' }}>Worker {ev.worker_id}</td>
                    <td style={{ padding: '8px 12px', color: 'var(--text-danger)', fontWeight: 600 }}>{ev.missing_ppe}</td>
                    <td style={{ padding: '8px 12px', fontFamily: 'var(--font-mono)', color: 'var(--text-warning)' }}>{ev.compliance_score}</td>
                    <td style={{ padding: '8px 12px', color: 'var(--text-muted)', fontSize: '11px' }}>{ev.video}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Total Logged Events: <strong>{events.length}</strong>
          </span>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={downloadJSON}
              style={{
                fontSize: '12px',
                padding: '8px 14px',
                borderRadius: 'var(--radius)',
                background: 'var(--surface-2)',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <i className="ti ti-code" /> Export JSON
            </button>
            <button
              onClick={downloadCSV}
              style={{
                fontSize: '12px',
                padding: '8px 16px',
                borderRadius: 'var(--radius)',
                background: 'var(--bg-accent)',
                color: 'var(--text-accent)',
                border: '1px solid var(--border-accent)',
                cursor: 'pointer',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <i className="ti ti-download" /> Download CSV Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
