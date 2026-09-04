# Industrial PPE Kit Detection & Compliance Monitor

A standalone, real-time Industrial PPE (Personal Protective Equipment) Kit Detection and Compliance Monitoring Demo Application built for client demonstrations.

The application combines **YOLOv11 computer vision models (`models/new_best(2).pt`)**, **anatomical spatial associator**, **synchronized Before & After video comparison**, **dynamic video queue auto-discovery**, and a modern **React 18 + TypeScript industrial dashboard**.

---

## 🌟 Key Features

1. **Synchronized Dual-Stream (Before & After)**:
   - **BEFORE Stream**: Raw synchronized video feed without overlays (`/api/videos/stream/raw`).
   - **AFTER Stream**: AI Detection stream with color-coded bounding boxes (green = compliant, red = violation), worker tags, and inference HUD overlay (`/api/videos/stream/live`).
   - **Display Mode Switcher**: Side-by-Side Dual View, AI Detection Only, or Original Feed Only.

2. **Unified Gradio + FastAPI Entry Point (`app.py`)**:
   - Directly serves the high-performance React Industrial Dashboard at `/`, WebSocket telemetry at `/ws`, and Swagger API documentation at `/docs`.

3. **YOLO Detection & Anatomical Spatial Associator**:
   - Model inference using weights in `models/new_best(2).pt`.
   - Maps detected safety gear (Helmet, Vest, Gloves, Goggles, Shoes, Mask) to workers by anatomical zone.
   - Computes compliance rate, active violations, and worker-specific missing gear.

4. **Dynamic Video Queue & Real-Time Auto-Discovery**:
   - Drop any new video file (`.mp4`, `.avi`, `.mkv`, `.mov`) into `videos/`.
   - The backend automatically discovers new files within 2 seconds and updates the playlist over WebSocket without page reload.

---

## 📁 Repository Structure

```text
.
│
├── app.py                      # 🚀 Gradio + FastAPI entry point
├── requirements.txt            # 📦 Python dependencies
├── packages.txt                # 🐧 Debian packages for OpenCV (ffmpeg, libgl1, etc.)
├── README.md                   # 📄 Space metadata header (sdk: gradio, app_file: app.py)
├── .gitignore                  # 🔒 Configured to only track models/new_best(2).pt
│
├── backend/
│   ├── app/
│   │   ├── api/                # Video, Dashboard, and Demo REST endpoints
│   │   ├── core/               # Detection engine, spatial associator, video processor
│   │   ├── config.py           # Configuration loader (defaults to models/new_best(2).pt)
│   │   └── main.py             # FastAPI app and WebSocket endpoint
│   ├── requirements.txt        # Local backend requirements
│   └── run_backend.py          # Local runner script
│
├── frontend/
│   ├── dist/                   # Built production assets (bundled React SPA)
│   ├── src/                    # Frontend source code
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── config/
│   └── config.yaml             # Configured to use models/new_best(2).pt
│
├── models/
│   ├── new_best(2).pt          # ✅ Only this model is tracked in git
│   ├── new_best(1).pt          # 🔒 Kept safely on local disk (ignored by Git)
│   └── ppe_multiclass_best.pt  # 🔒 Kept safely on local disk (ignored by Git)
│
└── videos/
    └── *.mp4                   # Sample surveillance videos for playlist playback
```

---

## 🚀 Quickstart Guide

### Option 1: 1-Click Windows Launch (Local)
Double-click:
```bat
start_demo.bat
```
or run via PowerShell:
```powershell
.\start_demo.ps1
```

### Option 2: Direct Python Runner
```bash
python app.py
```
- **React Dashboard**: `http://localhost:7860/`
- **API Swagger Docs**: `http://localhost:7860/docs`

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the full React 18 Industrial Dashboard SPA |
| `GET` | `/api/dashboard` | Real-time dashboard telemetry, KPIs, and workers state |
| `GET` | `/api/videos` | Playlist queue and current video index |
| `GET` | `/api/videos/stream/live` | **AFTER**: Real-time MJPEG AI Detection stream |
| `GET` | `/api/videos/stream/raw` | **BEFORE**: Real-time MJPEG raw surveillance stream |
| `POST` | `/api/videos/select` | Switches active video by index or filename |
| `POST` | `/api/demo/start` | Starts / resumes video processing |
| `POST` | `/api/demo/pause` | Pauses video processing |
| `POST` | `/api/demo/next` | Advances to the next video in queue |
| `POST` | `/api/demo/prev` | Returns to previous video in queue |
| `POST` | `/api/demo/restart` | Restarts current video playback |
| `POST` | `/api/demo/speed` | Adjusts playback speed (`{"speed": 1.5}`) |
| `POST` | `/api/demo/config` | Updates mandatory PPE rules and confidence threshold |
| `GET` | `/api/export/report` | Exports logged safety violations as CSV or JSON |
| `WS` | `/ws` | Real-time WebSocket connection for telemetry & playlist events |

---

## ⚙️ Configuration

All runtime settings — zone name, model weights path, detection thresholds, required PPE list, and video streaming options — live in [`config/config.yaml`](config/config.yaml). Edit that file directly to change behavior; defaults point to `models/new_best(2).pt` at `conf_threshold: 0.25`.
