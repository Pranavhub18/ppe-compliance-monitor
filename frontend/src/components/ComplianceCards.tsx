import React from 'react';
import { ComplianceData } from '../types/dashboard';

interface ComplianceCardsProps {
  compliance: ComplianceData;
}

export const ComplianceCards: React.FC<ComplianceCardsProps> = ({ compliance }) => {
  const rate = Math.round(compliance.compliance_rate || 0);
  const rateColor = rate >= 85 ? 'var(--text-success)' : rate >= 50 ? 'var(--text-warning)' : 'var(--text-danger)';

  const violationPct = compliance.violation_rate !== undefined
    ? Math.round(compliance.violation_rate)
    : compliance.total_workers > 0
    ? Math.round((compliance.non_compliant_workers / compliance.total_workers) * 100)
    : 0;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
      <div style={{ background: 'var(--bg-success)', border: '0.5px solid var(--border-success)', borderRadius: '12px', padding: '12px', textAlign: 'center' }}>
        <p style={{ fontSize: '11px', color: 'var(--text-success)', margin: '0 0 4px 0' }}>Compliant</p>
        <p style={{ fontSize: '28px', fontWeight: 500, color: 'var(--text-success)', margin: 0 }}>
          {compliance.compliant_workers}
        </p>
      </div>
      <div style={{ background: 'var(--bg-danger)', border: '0.5px solid var(--border-danger)', borderRadius: '12px', padding: '12px', textAlign: 'center' }}>
        <p style={{ fontSize: '11px', color: 'var(--text-danger)', margin: '0 0 4px 0' }}>Violation</p>
        <p style={{ fontSize: '28px', fontWeight: 500, color: 'var(--text-danger)', margin: 0 }}>
          {violationPct}%
        </p>
      </div>
      <div style={{ background: 'var(--surface-1)', border: '0.5px solid var(--border)', borderRadius: '12px', padding: '12px', textAlign: 'center' }}>
        <p style={{ fontSize: '11px', color: 'var(--text-secondary)', margin: '0 0 4px 0' }}>Total workers</p>
        <p style={{ fontSize: '28px', fontWeight: 500, color: 'var(--text-primary)', margin: 0 }}>
          {compliance.total_workers}
        </p>
      </div>
      <div style={{ background: 'var(--surface-1)', border: '0.5px solid var(--border)', borderRadius: '12px', padding: '12px', textAlign: 'center' }}>
        <p style={{ fontSize: '11px', color: 'var(--text-secondary)', margin: '0 0 4px 0' }}>Rate</p>
        <p style={{ fontSize: '28px', fontWeight: 500, color: rateColor, margin: 0 }}>
          {rate}%
        </p>
      </div>
    </div>
  );
};
