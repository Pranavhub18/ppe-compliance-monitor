import React, { useState } from 'react';
import { VideoInfo, ComplianceData, VideoPlaylistItem } from '../types/dashboard';

interface VideoPlayerProps {
  videoInfo: VideoInfo;
  compliance: ComplianceData;
  onSelectVideo: (index: number) => void;
  playlist: VideoPlaylistItem[];
}

type ViewMode = 'after' | 'before' | 'split';

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  videoInfo,
  compliance,
  onSelectVideo,
  playlist,
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('after');
  const [splitPos, setSplitPos] = useState<number>(50); // percentage for split slider

  const displayPlaylist = playlist && playlist.length > 0 ? playlist : [
    { index: 0, filename: 'video_01.mp4', title: 'CAM-01 Zone A', size_mb: 1.2, is_current: true },
    { index: 1, filename: 'video_02.mp4', title: 'CAM-02 Zone B', size_mb: 2.1, is_current: false },
    { index: 2, filename: 'video_03.mp4', title: 'CAM-03 Zone C', size_mb: 1.8, is_current: false },
  ];

  const currentCamName = `CAM-0${(videoInfo.video_index % 3) + 1} — Zone ${String.fromCharCode(65 + (videoInfo.video_index % 3))}`;

  return (
    <div>
      {/* Camera canvas - Exact HTML dimensions & styling */}
      <div
        style={{
          background: '#1a1a1a',
          borderRadius: '12px',
          height: '280px',
          position: 'relative',
          overflow: 'hidden',
          marginBottom: '12px',
        }}
      >
        {/* Background scene gradient */}
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%)' }} />

        {/* Video Rendering according to View Mode */}
        {viewMode === 'after' && (
          <img
            src="/api/videos/stream/live"
            alt="AI Detection Stream"
            style={{ width: '100%', height: '100%', objectFit: 'contain', position: 'relative', zIndex: 2 }}
          />
        )}

        {viewMode === 'before' && (
          <img
            src="/api/videos/stream/raw"
            alt="Original Raw Stream"
            style={{ width: '100%', height: '100%', objectFit: 'contain', position: 'relative', zIndex: 2 }}
          />
        )}

        {viewMode === 'split' && (
          <div style={{ position: 'relative', width: '100%', height: '100%', zIndex: 2 }}>
            {/* Side-by-Side Dual Video inside 280px container */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', width: '100%', height: '100%', gap: '2px', background: '#000' }}>
              <div style={{ position: 'relative', height: '100%', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', top: '8px', left: '8px', background: 'rgba(0,0,0,0.7)', borderRadius: '3px', padding: '2px 6px', zIndex: 5, fontSize: '9px', color: '#fff', textTransform: 'uppercase' }}>
                  Before: Original
                </div>
                <img
                  src="/api/videos/stream/raw"
                  alt="Before"
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </div>
              <div style={{ position: 'relative', height: '100%', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', top: '8px', left: '8px', background: 'rgba(0,0,0,0.7)', borderRadius: '3px', padding: '2px 6px', zIndex: 5, fontSize: '9px', color: '#3fb950', textTransform: 'uppercase' }}>
                  After: AI Detection
                </div>
                <img
                  src="/api/videos/stream/live"
                  alt="After"
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Top-Left: Before & After Effect Switcher Badge */}
        <div
          style={{
            position: 'absolute',
            top: '10px',
            left: '10px',
            background: 'rgba(0,0,0,0.75)',
            backdropFilter: 'blur(4px)',
            borderRadius: '6px',
            padding: '2px',
            display: 'flex',
            gap: '2px',
            zIndex: 10,
            border: '0.5px solid rgba(255,255,255,0.1)',
          }}
        >
          <button
            onClick={() => setViewMode('after')}
            style={{
              fontSize: '10px',
              padding: '2px 7px',
              borderRadius: '4px',
              background: viewMode === 'after' ? 'var(--bg-accent)' : 'transparent',
              color: viewMode === 'after' ? 'var(--text-accent)' : '#8b949e',
              border: viewMode === 'after' ? '0.5px solid var(--border-accent)' : 'none',
              cursor: 'pointer',
              fontWeight: viewMode === 'after' ? 600 : 400,
            }}
          >
            After (AI Detection)
          </button>
          <button
            onClick={() => setViewMode('before')}
            style={{
              fontSize: '10px',
              padding: '2px 7px',
              borderRadius: '4px',
              background: viewMode === 'before' ? 'var(--bg-accent)' : 'transparent',
              color: viewMode === 'before' ? 'var(--text-accent)' : '#8b949e',
              border: viewMode === 'before' ? '0.5px solid var(--border-accent)' : 'none',
              cursor: 'pointer',
              fontWeight: viewMode === 'before' ? 600 : 400,
            }}
          >
            Before (Original)
          </button>
          <button
            onClick={() => setViewMode('split')}
            style={{
              fontSize: '10px',
              padding: '2px 7px',
              borderRadius: '4px',
              background: viewMode === 'split' ? 'var(--bg-accent)' : 'transparent',
              color: viewMode === 'split' ? 'var(--text-accent)' : '#8b949e',
              border: viewMode === 'split' ? '0.5px solid var(--border-accent)' : 'none',
              cursor: 'pointer',
              fontWeight: viewMode === 'split' ? 600 : 400,
            }}
          >
            Side-by-Side
          </button>
        </div>

        {/* Top-Right: Camera Label (Matching Line 74-77 of HTML) */}
        <div
          style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            background: 'rgba(0,0,0,0.6)',
            borderRadius: '4px',
            padding: '3px 8px',
            zIndex: 10,
          }}
        >
          <span style={{ fontSize: '10px', color: '#fff', fontFamily: 'monospace' }}>
            {currentCamName}
          </span>
        </div>

        {/* Bottom-Left: Inference Stats Overlay (Matching Line 67-72 of HTML) */}
        <div
          style={{
            position: 'absolute',
            bottom: '10px',
            left: '10px',
            background: 'rgba(0,0,0,0.7)',
            borderRadius: '6px',
            padding: '6px 10px',
            display: 'flex',
            gap: '16px',
            zIndex: 10,
          }}
        >
          <span style={{ fontSize: '10px', color: '#fff', fontFamily: 'monospace' }}>
            {videoInfo.inference_ms > 0 ? `${videoInfo.inference_ms}ms inference` : '265ms inference'}
          </span>
          <span style={{ fontSize: '10px', color: '#22c55e', fontFamily: 'monospace' }}>
            {compliance.total_workers} workers detected
          </span>
          <span
            style={{
              fontSize: '10px',
              color: compliance.non_compliant_workers > 0 ? '#ef4444' : '#22c55e',
              fontFamily: 'monospace',
            }}
          >
            {compliance.non_compliant_workers} violation{compliance.non_compliant_workers !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Camera selector tabs (Matching Line 80-86 of HTML) */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', overflowX: 'auto', paddingBottom: '2px' }}>
        {displayPlaylist.map((vid) => {
          const isActive = vid.index === videoInfo.video_index;
          const camLabel = `CAM-0${(vid.index % 3) + 1} Zone ${String.fromCharCode(65 + (vid.index % 3))}`;

          return (
            <button
              key={vid.index}
              onClick={() => onSelectVideo(vid.index)}
              style={{
                fontSize: '11px',
                padding: '4px 10px',
                borderRadius: 'var(--radius)',
                background: isActive ? 'var(--bg-accent)' : 'var(--surface-1)',
                color: isActive ? 'var(--text-accent)' : 'var(--text-secondary)',
                border: isActive ? '0.5px solid var(--border-accent)' : '0.5px solid var(--border)',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                fontWeight: isActive ? 500 : 400,
              }}
            >
              {camLabel}
            </button>
          );
        })}
      </div>
    </div>
  );
};
