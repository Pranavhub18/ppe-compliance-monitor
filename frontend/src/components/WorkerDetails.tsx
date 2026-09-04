import React from 'react';
import { WorkerItem } from '../types/dashboard';

interface WorkerDetailsProps {
  workers: WorkerItem[];
}

export const WorkerDetails: React.FC<WorkerDetailsProps> = ({ workers }) => {
  const defaultWorkers = [
    { worker_id: 1, label: 'Worker 1', is_compliant: true, summary_tag: 'All PPE ✓', missing_required: [] },
    { worker_id: 2, label: 'Worker 2', is_compliant: false, summary_tag: 'No helmet', missing_required: ['helmet'] },
    { worker_id: 3, label: 'Worker 3', is_compliant: true, summary_tag: 'All PPE ✓', missing_required: [] },
  ];

  const displayList = workers && workers.length > 0 ? workers : defaultWorkers;

  return (
    <div style={{ background: 'var(--surface-2)', border: '0.5px solid var(--border)', borderRadius: '12px', padding: '12px' }}>
      <p style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)', margin: '0 0 10px 0' }}>
        Worker details
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {displayList.map((w: any) => {
          const isComp = w.is_compliant;
          const bg = isComp ? 'var(--bg-success)' : 'var(--bg-danger)';
          const textCol = isComp ? 'var(--text-success)' : 'var(--text-danger)';
          const dotCol = isComp ? '#22c55e' : '#ef4444';

          const tagText = isComp
            ? 'All PPE ✓'
            : w.missing_required && w.missing_required.length > 0
            ? `No ${w.missing_required.map((m: string) => m.toLowerCase()).join(', ')}`
            : 'Violation';

          return (
            <div
              key={w.worker_id}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '6px 8px',
                background: bg,
                borderRadius: 'var(--radius)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: dotCol }} />
                <span style={{ fontSize: '12px', color: 'var(--text-primary)' }}>
                  {w.label || `Worker ${w.worker_id}`}
                </span>
              </div>
              <span style={{ fontSize: '11px', color: textCol }}>
                {tagText}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
