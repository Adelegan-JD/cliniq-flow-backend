"""Record-officer-specific endpoints.

These routes handle patient registration and visit creation before clinical intake.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.utils.auth import AuthContext
from app.utils.auth import require_role
from app.utils.errors import error_payload
from app.utils.storage import add_audit_log
from app.utils.storage import create_patient
from app.utils.storage import create_visit
from app.utils.storage import get_patient
from app.utils.storage import get_visit

router = APIRouter(prefix="/record-officer", tags=["Record Officer"])


class PatientCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=2)
    date_of_birth: str | None = None
    gender: str | None = None
    phone: str | None = None


class VisitCreateRequest(BaseModel):
    patient_id: str = Field(...)
    visit_status: str = Field(default="open")


@router.post("/patients")
def create_patient_route(
    payload: PatientCreateRequest,
    auth: AuthContext = Depends(require_role("record_officer", "admin")),
):
    patient_id = str(uuid.uuid4())
    patient = create_patient(
        patient_id=patient_id,
        full_name=payload.full_name,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        phone=payload.phone,
    )
    add_audit_log(
        audit_id=str(uuid.uuid4()),
        actor_role=auth.role,
        action="create_patient",
        entity_type="patient",
        entity_id=patient_id,
        metadata={"full_name": payload.full_name},
    )
    return patient


@router.get("/patients/{patient_id}")
def get_patient_route(
    patient_id: str,
    auth: AuthContext = Depends(require_role("record_officer", "admin", "nurse", "doctor")),
):
    _ = auth
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail=error_payload("NOT_FOUND", "Patient not found", {"patient_id": patient_id}))
    return patient


@router.post("/visits")
def create_visit_route(
    payload: VisitCreateRequest,
    auth: AuthContext = Depends(require_role("record_officer", "admin")),
):
    patient = get_patient(payload.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail=error_payload("NOT_FOUND", "Patient not found", {"patient_id": payload.patient_id}))

    visit_id = str(uuid.uuid4())
    visit = create_visit(visit_id=visit_id, patient_id=payload.patient_id, visit_status=payload.visit_status)
    add_audit_log(
        audit_id=str(uuid.uuid4()),
        actor_role=auth.role,
        action="create_visit",
        entity_type="visit",
        entity_id=visit_id,
        metadata={"patient_id": payload.patient_id},
    )
    return visit


@router.get("/visits/{visit_id}")
def get_visit_route(
    visit_id: str,
    auth: AuthContext = Depends(require_role("record_officer", "admin", "nurse", "doctor")),
):
    _ = auth
    visit = get_visit(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail=error_payload("NOT_FOUND", "Visit not found", {"visit_id": visit_id}))
    return visit
