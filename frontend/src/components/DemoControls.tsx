import React from 'react';
import { VideoInfo } from '../types/dashboard';

interface DemoControlsProps {
  videoInfo: VideoInfo;
  onOpenConfig: () => void;
  onOpenExport: () => void;
  onStart: () => void;
  onPause: () => void;
  onNext: () => void;
  onPrev: () => void;
  onRestart: () => void;
  onSpeed: (speed: number) => void;
}

export const DemoControls: React.FC<DemoControlsProps> = ({
  videoInfo,
  onOpenConfig,
  onOpenExport,
  onStart,
  onPause,
  onNext,
  onPrev,
  onRestart,
}) => {
  const isPlaying = videoInfo.status === 'playing';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {/* Compact Demo Playback Toolbar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'var(--surface-2)',
          border: '0.5px solid var(--border)',
          borderRadius: 'var(--radius)',
          padding: '6px 10px',
        }}
      >
        <span style={{ fontSize: '11px', color: 'var(--text-secondary)', fontWeight: 500 }}>
          Playback Controls:
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          {isPlaying ? (
            <button
              onClick={onPause}
              title="Pause Video"
              style={{
                fontSize: '11px',
                padding: '3px 8px',
                borderRadius: 'var(--radius)',
                background: 'var(--bg-warning)',
                color: 'var(--text-warning)',
                border: '0.5px solid var(--border-warning)',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '3px',
              }}
            >
              <i className="ti ti-player-pause" /> Pause
            </button>
          ) : (
            <button
              onClick={onStart}
              title="Start / Resume Video"
              style={{
                fontSize: '11px',
                padding: '3px 8px',
                borderRadius: 'var(--radius)',
                background: 'var(--bg-success)',
                color: 'var(--text-success)',
                border: '0.5px solid var(--border-success)',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '3px',
              }}
            >
              <i className="ti ti-player-play" /> Start
            </button>
          )}

          <button
            onClick={onPrev}
            title="Previous Video"
            style={{
              fontSize: '11px',
              padding: '3px 6px',
              borderRadius: 'var(--radius)',
              background: 'var(--surface-1)',
              color: 'var(--text-secondary)',
              border: '0.5px solid var(--border)',
              cursor: 'pointer',
            }}
          >
            <i className="ti ti-player-skip-back" />
          </button>

          <button
            onClick={onNext}
            title="Next Video"
            style={{
              fontSize: '11px',
              padding: '3px 6px',
              borderRadius: 'var(--radius)',
              background: 'var(--surface-1)',
              color: 'var(--text-secondary)',
              border: '0.5px solid var(--border)',
              cursor: 'pointer',
            }}
          >
            <i className="ti ti-player-skip-forward" />
          </button>

          <button
            onClick={onRestart}
            title="Restart Video"
            style={{
              fontSize: '11px',
              padding: '3px 6px',
              borderRadius: 'var(--radius)',
              background: 'var(--surface-1)',
              color: 'var(--text-secondary)',
              border: '0.5px solid var(--border)',
              cursor: 'pointer',
            }}
          >
            <i className="ti ti-rotate-clockwise" />
          </button>
        </div>
      </div>

      {/* Action Buttons — Matching Lines 225-234 of HTML */}
      <button
        onClick={onOpenExport}
        style={{
          fontSize: '12px',
          padding: '8px',
          borderRadius: 'var(--radius)',
          background: 'var(--bg-accent)',
          color: 'var(--text-accent)',
          border: '0.5px solid var(--border-accent)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '6px',
        }}
      >
        <i className="ti ti-download" aria-hidden="true" /> Export violation report
      </button>

      <button
        onClick={onOpenConfig}
        style={{
          fontSize: '12px',
          padding: '8px',
          borderRadius: 'var(--radius)',
          background: 'var(--surface-1)',
          color: 'var(--text-secondary)',
          border: '0.5px solid var(--border)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '6px',
        }}
      >
        <i className="ti ti-settings" aria-hidden="true" /> Configure PPE requirements
      </button>
    </div>
  );
};
