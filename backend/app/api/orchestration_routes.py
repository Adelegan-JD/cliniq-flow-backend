from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.dose import DoseCheckRequest, DoseCheckResponse
from app.schemas.intake import IntakeRequest
from app.services.orchestration.pipeline import process_intake
from app.utils.auth import require_role
from app.utils.errors import error_payload
from app.utils.storage import log_dose_check

router = APIRouter()

# Guideline subset for demo use (pediatric mg/kg/day + max daily).
FORMULARY = {
    "amoxicillin": {"min_mg_per_kg_day": 20.0, "max_mg_per_kg_day": 40.0, "max_daily_mg": 1000.0},
    "paracetamol": {"min_mg_per_kg_day": 40.0, "max_mg_per_kg_day": 60.0, "max_daily_mg": 4000.0},
    "ibuprofen": {"min_mg_per_kg_day": 20.0, "max_mg_per_kg_day": 30.0, "max_daily_mg": 2400.0},
    "artemether_lumefantrine": {"min_mg_per_kg_day": 4.0, "max_mg_per_kg_day": 8.0, "max_daily_mg": 480.0},
}


@router.post("/process_intake")
def process_intake_route(
    payload: IntakeRequest,
    _role: str = Depends(require_role("nurse", "doctor", "admin")),
):
    try:
        return process_intake(payload.model_dump())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_payload("INTERNAL_ERROR", "Unable to process intake", str(exc)),
        ) from exc


@router.post("/dose-check", response_model=DoseCheckResponse)
def dose_check_route(
    payload: DoseCheckRequest,
    _role: str = Depends(require_role("doctor", "admin")),
) -> DoseCheckResponse:
    drug_key = payload.drug.strip().lower()
    rule = FORMULARY.get(drug_key)
    event_id = str(uuid.uuid4())

    if rule is None:
        # Safe fallback for unknown drugs in blocker pass.
        response = DoseCheckResponse(
            safe=True,
            warnings=["No formulary rule found for drug; clinician review required"],
            recommended_range_mg_per_day={"min": 0, "max": payload.chosen_dose_mg_per_day},
            max_mg_per_day=payload.chosen_dose_mg_per_day,
            event_id=event_id,
            allow_override=True,
        )
        log_dose_check(
            event_id=event_id,
            visit_id=payload.visit_id,
            drug_name=payload.drug,
            chosen_dose_mg_per_day=payload.chosen_dose_mg_per_day,
            safe=response.safe,
            warnings=response.warnings,
        )
        return response

    recommended_min = round(rule["min_mg_per_kg_day"] * payload.weight_kg)
    recommended_max = round(rule["max_mg_per_kg_day"] * payload.weight_kg)
    max_daily = round(min(rule["max_daily_mg"], recommended_max))

    warnings = []
    safe = True
    if payload.chosen_dose_mg_per_day < recommended_min:
        safe = False
        warnings.append("Dose is below recommended mg/kg/day range")
    if payload.chosen_dose_mg_per_day > recommended_max:
        safe = False
        warnings.append("Dose exceeds recommended mg/kg/day range")
    if payload.chosen_dose_mg_per_day > max_daily:
        safe = False
        warnings.append("Dose exceeds max daily limit")

    response = DoseCheckResponse(
        safe=safe,
        warnings=warnings,
        recommended_range_mg_per_day={"min": recommended_min, "max": recommended_max},
        max_mg_per_day=max_daily,
        event_id=event_id,
        allow_override=True,
    )
    log_dose_check(
        event_id=event_id,
        visit_id=payload.visit_id,
        drug_name=payload.drug,
        chosen_dose_mg_per_day=payload.chosen_dose_mg_per_day,
        safe=response.safe,
        warnings=response.warnings,
    )
    return response
