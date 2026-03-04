"""Compatibility package for legacy ``app.*`` imports.

This repo is laid out under ``backend/app`` but several modules still import
from ``app`` directly. Expose that directory as the ``app`` package so the
code works from the repository root without requiring ``PYTHONPATH=backend``.
"""

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parent.parent / "backend" / "app")]
