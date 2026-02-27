"""Doctor-facing endpoints.

Handles medication orders and override actions used during clinical decision flow.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.utils.auth import require_role
from app.utils.errors import error_payload
from app.utils.storage import add_audit_log
from app.utils.storage import create_med_order
from app.utils.storage import get_visit
from app.utils.storage import list_visit_med_orders
from app.utils.storage import log_override

router = APIRouter()


class OverrideRequest(BaseModel):
    reason: str = Field(..., min_length=3)


class MedOrderCreateRequest(BaseModel):
    visit_id: str = Field(...)
    drug_name: str = Field(..., min_length=2)
    dose_mg_per_day: int = Field(..., gt=0)
    frequency_per_day: int = Field(..., ge=1)
    is_safe: bool = False
    dose_check_result: dict = Field(default_factory=dict)


@router.post("/med-orders")
def create_med_order_route(
    payload: MedOrderCreateRequest,
    _role: str = Depends(require_role("doctor", "admin")),
):
    visit = get_visit(payload.visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail=error_payload("NOT_FOUND", "Visit not found", {"visit_id": payload.visit_id}))

    med_order_id = str(uuid.uuid4())
    med_order = create_med_order(
        med_order_id=med_order_id,
        visit_id=payload.visit_id,
        drug_name=payload.drug_name,
        dose_mg_per_day=payload.dose_mg_per_day,
        frequency_per_day=payload.frequency_per_day,
        dose_check_result=payload.dose_check_result,
        is_safe=payload.is_safe,
    )
    add_audit_log(
        audit_id=str(uuid.uuid4()),
        actor_role=_role,
        action="create_med_order",
        entity_type="med_order",
        entity_id=med_order_id,
        metadata={"visit_id": payload.visit_id, "drug_name": payload.drug_name},
    )
    return med_order


@router.get("/visits/{visit_id}/med-orders")
def list_med_orders_route(
    visit_id: str,
    _role: str = Depends(require_role("doctor", "admin")),
):
    return {"visit_id": visit_id, "items": list_visit_med_orders(visit_id)}


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
    add_audit_log(
        audit_id=str(uuid.uuid4()),
        actor_role=_role,
        action="override_med_order",
        entity_type="med_order",
        entity_id=med_order_id,
        metadata={"doctor_id": x_doctor_id},
    )
    return {
        "override_logged": True,
        "event_id": event_id,
        "med_order_id": med_order_id,
    }
