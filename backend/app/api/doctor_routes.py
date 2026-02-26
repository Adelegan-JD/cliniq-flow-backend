from __future__ import annotations

import uuid

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class OverrideRequest(BaseModel):
    reason: str = Field(..., min_length=3)


@router.post("/med-orders/{med_order_id}/override")
def override_med_order(med_order_id: str, payload: OverrideRequest):
    # TODO: Persist override with actor metadata and audit event in DB.
    return {
        "override_logged": True,
        "event_id": str(uuid.uuid4()),
        "med_order_id": med_order_id,
    }
