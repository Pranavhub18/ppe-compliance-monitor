import React, { useState } from 'react';

interface ConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (config: { required_ppe: string[]; conf_threshold: number; target_fps: number }) => void;
}

const ALL_PPE_ITEMS = [
  { key: 'helmet', label: 'Safety Helmet', icon: 'ti-helmet' },
  { key: 'vest', label: 'High-Visibility Vest', icon: 'ti-shirt' },
  { key: 'gloves', label: 'Safety Gloves', icon: 'ti-hand-stop' },
  { key: 'goggles', label: 'Safety Goggles / Glasses', icon: 'ti-glasses' },
  { key: 'shoes', label: 'Safety Shoes / Boots', icon: 'ti-shoe' },
  { key: 'mask', label: 'Protective Face Mask', icon: 'ti-shield' },
];

export const ConfigModal: React.FC<ConfigModalProps> = ({ isOpen, onClose, onSave }) => {
  const [selectedPPE, setSelectedPPE] = useState<string[]>(['helmet', 'vest', 'gloves', 'goggles', 'shoes']);
  const [confThreshold, setConfThreshold] = useState<number>(0.25);
  const [targetFps, setTargetFps] = useState<number>(20);
  const [isSaving, setIsSaving] = useState(false);

  if (!isOpen) return null;

  const toggleItem = (key: string) => {
    setSelectedPPE((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    );
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await fetch('/api/demo/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          required_ppe: selectedPPE,
          conf_threshold: confThreshold,
          target_fps: targetFps,
        }),
      });
      onSave({ required_ppe: selectedPPE, conf_threshold: confThreshold, target_fps: targetFps });
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSaving(false);
    }
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
          maxWidth: '480px',
          padding: '24px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <i className="ti ti-settings" style={{ fontSize: '20px', color: 'var(--text-accent)' }} />
            <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
              Configure PPE Requirements
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
          Select the mandatory PPE items required for compliance evaluation. Any worker missing an active requirement will trigger a violation alert.
        </p>

        {/* PPE Checklist */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '20px' }}>
          {ALL_PPE_ITEMS.map((item) => {
            const isChecked = selectedPPE.includes(item.key);
            return (
              <div
                key={item.key}
                onClick={() => toggleItem(item.key)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '10px 12px',
                  background: isChecked ? 'var(--bg-accent)' : 'var(--surface-2)',
                  border: isChecked ? '1px solid var(--border-accent)' : '1px solid var(--border)',
                  borderRadius: 'var(--radius)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => {}}
                  style={{ accentColor: '#3b82f6', cursor: 'pointer' }}
                />
                <span style={{ fontSize: '12px', fontWeight: 500, color: isChecked ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                  {item.label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Threshold Sliders */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '24px' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '6px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Detection Confidence Threshold</span>
              <span style={{ color: 'var(--text-accent)', fontFamily: 'var(--font-mono)' }}>{(confThreshold * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.80"
              step="0.05"
              value={confThreshold}
              onChange={(e) => setConfThreshold(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#3b82f6', cursor: 'pointer' }}
            />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '6px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Target Processing Rate</span>
              <span style={{ color: 'var(--text-accent)', fontFamily: 'var(--font-mono)' }}>{targetFps} FPS</span>
            </div>
            <input
              type="range"
              min="10"
              max="30"
              step="2"
              value={targetFps}
              onChange={(e) => setTargetFps(parseInt(e.target.value))}
              style={{ width: '100%', accentColor: '#3b82f6', cursor: 'pointer' }}
            />
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <button
            onClick={onClose}
            style={{
              fontSize: '12px',
              padding: '8px 16px',
              borderRadius: 'var(--radius)',
              background: 'var(--surface-2)',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border)',
              cursor: 'pointer',
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            style={{
              fontSize: '12px',
              padding: '8px 18px',
              borderRadius: 'var(--radius)',
              background: '#3b82f6',
              color: '#ffffff',
              border: 'none',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            {isSaving ? 'Saving...' : 'Apply Rules'}
          </button>
        </div>
      </div>
    </div>
  );
};
