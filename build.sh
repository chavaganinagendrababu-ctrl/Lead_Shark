#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=== Lead Shark Render Build Hook ==="
echo "Working directory: $(pwd)"
echo "Contents:"
ls -la

if [ -f "requirements.txt" ]; then
    echo "Installing from ./requirements.txt"
    pip install -r requirements.txt
elif [ -f "backend/requirements.txt" ]; then
    echo "Installing from ./backend/requirements.txt"
    pip install -r backend/requirements.txt
elif [ -f "../requirements.txt" ]; then
    echo "Installing from ../requirements.txt"
    pip install -r ../requirements.txt
elif [ -f "../backend/requirements.txt" ]; then
    echo "Installing from ../backend/requirements.txt"
    pip install -r ../backend/requirements.txt
else
    REQ_PATH=$(find . -name "requirements.txt" 2>/dev/null | head -n 1)
    if [ -n "$REQ_PATH" ]; then
        echo "Found requirements file at: $REQ_PATH"
        pip install -r "$REQ_PATH"
    else
        echo "ERROR: requirements.txt not found in repository."
        exit 1
    fi
fi
echo "=== Build Hook Finished Successfully ==="
