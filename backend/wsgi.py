"""
WSGI / ASGI Entrypoint for Lead Shark.
Exposes 'app' and 'application' for ASGI / Gunicorn Uvicorn workers.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

if os.path.isdir(os.path.join(BASE_DIR, "app")) and BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if os.path.isdir(os.path.join(PARENT_DIR, "app")) and PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from app.main import app

application = app
