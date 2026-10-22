"""Immutable target from one YOLO detection; no frame-count or dwell condition."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    object_id: int
    instance: int
    name: str
    xyz: tuple
    orientation: tuple
    confidence: float
    timestamp: float
    frame_id: int
    calibration_id: str
    config_version: int
