# PowerShell 1-Click Launcher for PPE Demo
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " Starting Industrial PPE Kit Detection Demo System (v2.0)" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan

# 1. Start Backend in new window
Write-Host "`n[1/2] Starting Backend Server on port 8001..." -ForegroundColor Yellow
$BackendPython = Join-Path $ScriptDir "..\.venv\Scripts\python.exe"
if (-not (Test-Path $BackendPython)) {
    $BackendPython = "C:\Users\Admin\AppData\Local\Python\bin\python.exe"
}
if (-not (Test-Path $BackendPython)) {
    $BackendPython = "python.exe"
}
$BackendScript = Join-Path $ScriptDir "backend\run_backend.py"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k `"$BackendPython`" `"$BackendScript`"" -WorkingDirectory $ScriptDir

# 2. Start Frontend in new window
Write-Host "[2/2] Starting React Vite Frontend on port 5173..." -ForegroundColor Yellow
$FrontendDir = Join-Path $ScriptDir "frontend"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k npm run dev" -WorkingDirectory $FrontendDir

# 3. Open Browser
Start-Sleep -Seconds 3
Write-Host "`nOpening Dashboard: http://localhost:5173" -ForegroundColor Green
Start-Process "http://localhost:5173"
