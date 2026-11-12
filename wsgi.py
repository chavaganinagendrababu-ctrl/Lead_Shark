"""
WSGI / ASGI Entrypoint for Lead Shark.
Exposes 'app' and 'application' for ASGI / Gunicorn Uvicorn workers.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

if os.path.isdir(os.path.join(BACKEND_DIR, "app")) and BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if os.path.isdir(os.path.join(BASE_DIR, "app")) and BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.main import app

application = app
