"""Shared clinical endpoints.

Provides general workflow APIs used across roles:
patient/visit lookup, latest intake retrieval, and doctor conversation summary.
"""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.services.nlp.soap_formatter import SOAPFormatter
from app.services.nlp.symptom_extractor import SymptomExtractor
from app.services.nlp.urgency_scorer import UrgencyScorer
from app.services.nlp.validators import ClinicalValidator
from app.utils.auth import require_role
from app.utils.errors import error_payload
from app.utils.storage import add_audit_log
from app.utils.storage import create_doctor_conversation
from app.utils.storage import create_patient
from app.utils.storage import create_visit
from app.utils.storage import get_latest_doctor_conversation
from app.utils.storage import get_latest_intake
from app.utils.storage import get_patient
from app.utils.storage import get_visit

router = APIRouter(tags=["Clinical"])


class PatientCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=2)
    date_of_birth: str | None = None
    gender: str | None = None
    phone: str | None = None


class VisitCreateRequest(BaseModel):
    patient_id: str = Field(...)
    visit_status: str = Field(default="open")


class DoctorConversationRequest(BaseModel):
    transcript: str = Field(..., min_length=5)
    patient_age: str | None = None
    patient_sex: str | None = None
    audio_reference: str | None = None


@router.post("/patients")
def create_patient_route(
    payload: PatientCreateRequest,
    _role: str = Depends(require_role("record_officer", "nurse", "doctor", "admin")),
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
        actor_role=_role,
        action="create_patient",
        entity_type="patient",
        entity_id=patient_id,
        metadata={"full_name": payload.full_name},
    )
    return patient


@router.get("/patients/{patient_id}")
def get_patient_route(
    patient_id: str,
    _role: str = Depends(require_role("record_officer", "nurse", "doctor", "admin")),
):
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail=error_payload("NOT_FOUND", "Patient not found", {"patient_id": patient_id}))
    return patient


@router.post("/visits")
def create_visit_route(
    payload: VisitCreateRequest,
    _role: str = Depends(require_role("record_officer", "nurse", "doctor", "admin")),
):
    patient = get_patient(payload.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail=error_payload("NOT_FOUND", "Patient not found", {"patient_id": payload.patient_id}))
    visit_id = str(uuid.uuid4())
    visit = create_visit(visit_id=visit_id, patient_id=payload.patient_id, visit_status=payload.visit_status)
    add_audit_log(
        audit_id=str(uuid.uuid4()),
        actor_role=_role,
        action="create_visit",
        entity_type="visit",
        entity_id=visit_id,
        metadata={"patient_id": payload.patient_id},
    )
    return visit


@router.get("/visits/{visit_id}")
def get_visit_route(
    visit_id: str,
    _role: str = Depends(require_role("record_officer", "nurse", "doctor", "admin")),
):
    visit = get_visit(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail=error_payload("NOT_FOUND", "Visit not found", {"visit_id": visit_id}))
    return visit


@router.get("/visits/{visit_id}/latest-intake")
def latest_intake_route(
    visit_id: str,
    _role: str = Depends(require_role("nurse", "doctor", "admin")),
):
    row = get_latest_intake(visit_id)
    if not row:
        raise HTTPException(status_code=404, detail=error_payload("NOT_FOUND", "No intake found for visit", {"visit_id": visit_id}))

    for field in ("structured_json", "red_flags_json", "summary_json"):
        raw = row.get(field)
        if isinstance(raw, str):
            try:
                row[field] = json.loads(raw)
            except Exception:
                pass
    return row


@router.post("/visits/{visit_id}/doctor-conversation")
def doctor_conversation_route(
    visit_id: str,
    payload: DoctorConversationRequest,
    _role: str = Depends(require_role("doctor", "admin")),
):
    visit = get_visit(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail=error_payload("NOT_FOUND", "Visit not found", {"visit_id": visit_id}))

    extractor = SymptomExtractor()
    formatter = SOAPFormatter()
    validator = ClinicalValidator()
    urgency_scorer = UrgencyScorer()

    structured_data, _ = extractor.extract(
        transcript=payload.transcript,
        session_id=f"doctor-{visit_id}-{uuid.uuid4()}",
        patient_age=payload.patient_age,
        patient_sex=payload.patient_sex,
    )
    soap_note = formatter.format(structured_data)
    validation = validator.validate_all(structured_data, soap_note)
    urgency = urgency_scorer.score(structured_data)

    conversation_id = str(uuid.uuid4())
    stored = create_doctor_conversation(
        conversation_id=conversation_id,
        visit_id=visit_id,
        transcript=payload.transcript,
        structured_json=structured_data.model_dump(mode="json"),
        soap_json={
            "subjective": soap_note.subjective,
            "objective": soap_note.objective,
            "assessment": soap_note.assessment,
            "plan": soap_note.plan,
            "disclaimer": soap_note.disclaimer,
        },
        urgency_json=urgency.to_dict(),
        validation_json=validation.model_dump(mode="json"),
        audio_reference=payload.audio_reference,
    )
    add_audit_log(
        audit_id=str(uuid.uuid4()),
        actor_role=_role,
        action="doctor_conversation_summary",
        entity_type="visit",
        entity_id=visit_id,
        metadata={"conversation_id": conversation_id},
    )

    return {
        "visit_id": visit_id,
        "conversation_id": conversation_id,
        "structured_data": structured_data,
        "soap_note": soap_note,
        "validation": validation,
        "urgency": urgency.to_dict(),
        "stored": stored,
    }


@router.get("/visits/{visit_id}/doctor-conversation/latest")
def latest_doctor_conversation_route(
    visit_id: str,
    _role: str = Depends(require_role("doctor", "admin")),
):
    row = get_latest_doctor_conversation(visit_id)
    if not row:
        raise HTTPException(status_code=404, detail=error_payload("NOT_FOUND", "No doctor conversation found", {"visit_id": visit_id}))
    for field in ("structured_json", "soap_json", "urgency_json", "validation_json"):
        raw = row.get(field)
        if isinstance(raw, str):
            try:
                row[field] = json.loads(raw)
            except Exception:
                pass
    return row
