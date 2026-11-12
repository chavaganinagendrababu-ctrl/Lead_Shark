#!/usr/bin/env bash
# Lead Shark Production Server Startup Script for Render
set -e

PORT="${PORT:-8000}"
echo "=== Starting Lead Shark Backend on port $PORT ==="

if [ -f "app/main.py" ]; then
    echo "Found app/main.py (running from backend root directory)"
    exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
elif [ -f "backend/app/main.py" ]; then
    echo "Found backend/app/main.py (running from repo root)"
    exec uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port "$PORT"
else
    echo "Searching python path for app.main..."
    exec python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
fi
