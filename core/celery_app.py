# v2025‑06‑24‑AI-generated
"""
core/celery_app.py
Initialises the shared Celery application object.

Environment variables:
    BROKER_URL            default redis://localhost:6379/0
    CELERY_RESULT_BACKEND default = BROKER_URL
"""

from __future__ import annotations
import core.env
import os
from celery import Celery

BROKER_URL = os.getenv("BROKER_URL", "redis://localhost:6379/0")
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", BROKER_URL)

celery_app = Celery(
    "novelist",
    broker=BROKER_URL,
    backend=BACKEND_URL,
    include=["worker.tasks"],  # auto‑import tasks package
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)
