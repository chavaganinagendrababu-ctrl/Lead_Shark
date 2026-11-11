# Lead Shark Development Runner (PowerShell)
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "        LEAD SHARK - Local Development           " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Check Python virtual environment
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    .\.venv\Scripts\pip.exe install -r backend\requirements.txt
}

# Check frontend node_modules
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install --prefix frontend
}

Write-Host "`nStarting Backend (FastAPI on http://127.0.0.1:8000)..." -ForegroundColor Green
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\.venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --app-dir backend --port 8000 --reload"

Write-Host "Starting Frontend (Vite on http://localhost:5173)..." -ForegroundColor Green
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host "`nBoth services launched!" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "Health:   http://127.0.0.1:8000/health" -ForegroundColor White
