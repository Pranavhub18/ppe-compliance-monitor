import React, { useState } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { Header } from './components/Header';
import { VideoPlayer } from './components/VideoPlayer';
import { PPEDetectionBreakdown } from './components/PPEDetectionBreakdown';
import { ComplianceCards } from './components/ComplianceCards';
import { ActiveAlert } from './components/ActiveAlert';
import { WorkerDetails } from './components/WorkerDetails';
import { SessionSummary } from './components/SessionSummary';
import { DemoControls } from './components/DemoControls';
import { ConfigModal } from './components/ConfigModal';
import { ExportReportModal } from './components/ExportReportModal';

export const App: React.FC = () => {
  const { state, playlist, isConnected } = useWebSocket();
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);

  const handleStart = () => {
    fetch('/api/demo/start', { method: 'POST' }).catch(() => {});
  };

  const handlePause = () => {
    fetch('/api/demo/pause', { method: 'POST' }).catch(() => {});
  };

  const handleNext = () => {
    fetch('/api/demo/next', { method: 'POST' }).catch(() => {});
  };

  const handlePrev = () => {
    fetch('/api/demo/prev', { method: 'POST' }).catch(() => {});
  };

  const handleRestart = () => {
    fetch('/api/demo/restart', { method: 'POST' }).catch(() => {});
  };

  const handleSpeed = (speed: number) => {
    fetch('/api/demo/speed', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ speed }),
    }).catch(() => {});
  };

  const handleSelectVideo = (index: number) => {
    fetch('/api/videos/select', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ index }),
    }).catch(() => {});
  };

  return (
    <div style={{ fontFamily: 'var(--font-sans)', padding: 0, background: 'var(--surface-0)', minHeight: '100vh' }}>
      <h2 style={{ position: 'absolute', width: '1px', height: '1px', padding: 0, margin: '-1px', overflow: 'hidden', clip: 'rect(0,0,0,0)', border: 0 }}>
        PPE Compliance Detection Demo Dashboard for client presentation
      </h2>

      {/* Header — Exact HTML structure */}
      <Header
        videoInfo={state.video_info}
        sessionStats={state.session_stats}
        isConnected={isConnected}
      />

      {/* Main Grid — Exact HTML layout: 1fr 340px */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 0, minHeight: 'calc(100vh - 49px)' }}>
        {/* Left: Camera Feed & PPE Detection by Type (Exact HTML structure) */}
        <div style={{ padding: '16px', borderRight: '0.5px solid var(--border)' }}>
          <VideoPlayer
            videoInfo={state.video_info}
            compliance={state.compliance}
            onSelectVideo={handleSelectVideo}
            playlist={playlist}
          />
          <PPEDetectionBreakdown breakdown={state.compliance.ppe_breakdown} />
        </div>

        {/* Right Panel: Analytics, Cards, Alerts, Controls (Exact HTML structure) */}
        <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', overflowY: 'auto' }}>
          {/* Compliance Summary Cards */}
          <ComplianceCards compliance={state.compliance} />

          {/* Active Alert */}
          <ActiveAlert
            alerts={state.compliance.active_alerts}
            location={state.video_info.camera_label}
            timestamp={state.compliance.timestamp}
          />

          {/* Worker Details */}
          <WorkerDetails workers={state.compliance.workers} />

          {/* Today's Summary */}
          <SessionSummary stats={state.session_stats} />

          {/* Action Buttons & Playback Toolbar */}
          <DemoControls
            videoInfo={state.video_info}
            onOpenConfig={() => setIsConfigOpen(true)}
            onOpenExport={() => setIsExportOpen(true)}
            onStart={handleStart}
            onPause={handlePause}
            onNext={handleNext}
            onPrev={handlePrev}
            onRestart={handleRestart}
            onSpeed={handleSpeed}
          />
        </div>
      </div>

      {/* Modals */}
      <ConfigModal
        isOpen={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
        onSave={() => {}}
      />

      <ExportReportModal
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
      />
    </div>
  );
};

export default App;
