from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field

from app.utils.auth import require_role
from app.utils.storage import log_override

router = APIRouter()


class OverrideRequest(BaseModel):
    reason: str = Field(..., min_length=3)


@router.post("/med-orders/{med_order_id}/override")
def override_med_order(
    med_order_id: str,
    payload: OverrideRequest,
    _role: str = Depends(require_role("doctor", "admin")),
    x_doctor_id: str | None = Header(default=None, alias="X-Doctor-Id"),
):
    event_id = str(uuid.uuid4())
    log_override(
        event_id=event_id,
        med_order_id=med_order_id,
        override_reason=payload.reason,
        actor_role=_role,
        doctor_id=x_doctor_id,
    )
    return {
        "override_logged": True,
        "event_id": event_id,
        "med_order_id": med_order_id,
    }
