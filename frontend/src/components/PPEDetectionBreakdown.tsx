import React from 'react';
import { PPEBreakdownItem } from '../types/dashboard';

interface PPEDetectionBreakdownProps {
  breakdown: PPEBreakdownItem[];
}

export const PPEDetectionBreakdown: React.FC<PPEDetectionBreakdownProps> = ({ breakdown }) => {
  const defaultItems: PPEBreakdownItem[] = [
    { key: 'helmet', name: 'Helmet', detected_count: 2, total_workers: 3, percentage: 91, ratio_str: '2/3', status_level: 'success' },
    { key: 'vest', name: 'Vest', detected_count: 3, total_workers: 3, percentage: 88, ratio_str: '3/3', status_level: 'success' },
    { key: 'gloves', name: 'Gloves', detected_count: 1, total_workers: 3, percentage: 67, ratio_str: '1/3', status_level: 'warning' },
    { key: 'goggles', name: 'Goggles', detected_count: 0, total_workers: 3, percentage: 33, ratio_str: '0/3', status_level: 'danger' },
    { key: 'shoes', name: 'Shoes', detected_count: 2, total_workers: 3, percentage: 70, ratio_str: '2/3', status_level: 'warning' },
  ];

  const items = breakdown && breakdown.length > 0 ? breakdown : defaultItems;

  const getBarColor = (level: string) => {
    switch (level) {
      case 'success':
        return '#22c55e';
      case 'warning':
        return '#f59e0b';
      case 'danger':
        return '#ef4444';
      default:
        return '#22c55e';
    }
  };

  const getTextColorVar = (level: string) => {
    switch (level) {
      case 'success':
        return 'var(--text-success)';
      case 'warning':
        return 'var(--text-warning)';
      case 'danger':
        return 'var(--text-danger)';
      default:
        return 'var(--text-success)';
    }
  };

  return (
    <div style={{ background: 'var(--surface-2)', borderRadius: '12px', border: '0.5px solid var(--border)', padding: '14px' }}>
      <p style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)', margin: '0 0 12px 0' }}>
        PPE detection accuracy — current frame
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {items.map((item) => (
          <div key={item.key} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)', width: '60px' }}>
              {item.name}
            </span>
            <div style={{ flex: 1, background: 'var(--surface-1)', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
              <div
                style={{
                  width: `${Math.min(100, Math.max(0, item.percentage))}%`,
                  height: '100%',
                  background: getBarColor(item.status_level),
                  borderRadius: '4px',
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
            <span style={{ fontSize: '12px', color: 'var(--text-primary)', width: '32px' }}>
              {Math.round(item.percentage)}%
            </span>
            <span style={{ fontSize: '11px', color: getTextColorVar(item.status_level) }}>
              {item.ratio_str}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
