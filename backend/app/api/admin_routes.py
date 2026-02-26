from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/metrics")
def admin_metrics():
    # TODO: Replace deterministic values with storage-backed aggregates.
    return {
        "total_intakes": 0,
        "urgency_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "EMERGENCY": 0},
        "top_red_flags": [],
        "unsafe_dose_warnings": 0,
        "overrides": 0,
    }
