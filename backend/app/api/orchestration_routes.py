from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.dose import DoseCheckRequest, DoseCheckResponse
from app.schemas.intake import IntakeRequest
from app.services.orchestration.pipeline import process_intake

router = APIRouter()

# TODO: Replace with guideline-backed formulary table persisted in DB.
FORMULARY = {
    "amoxicillin": {"min_mg_per_kg_day": 20.0, "max_mg_per_kg_day": 30.0, "max_daily_mg": 540.0},
    "paracetamol": {"min_mg_per_kg_day": 40.0, "max_mg_per_kg_day": 60.0, "max_daily_mg": 4000.0},
}


@router.post("/process_intake")
def process_intake_route(payload: IntakeRequest):
    try:
        return process_intake(payload.model_dump())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Unable to process intake",
                    "details": str(exc),
                }
            },
        ) from exc


@router.post("/dose-check", response_model=DoseCheckResponse)
def dose_check_route(payload: DoseCheckRequest) -> DoseCheckResponse:
    drug_key = payload.drug.strip().lower()
    rule = FORMULARY.get(drug_key)

    if rule is None:
        # Safe fallback for unknown drugs in blocker pass.
        return DoseCheckResponse(
            safe=True,
            warnings=["No formulary rule found for drug; clinician review required"],
            recommended_range_mg_per_day={"min": 0, "max": payload.chosen_dose_mg_per_day},
            max_mg_per_day=payload.chosen_dose_mg_per_day,
            event_id=payload.visit_id,
            allow_override=True,
        )

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

    return DoseCheckResponse(
        safe=safe,
        warnings=warnings,
        recommended_range_mg_per_day={"min": recommended_min, "max": recommended_max},
        max_mg_per_day=max_daily,
        event_id=payload.visit_id,
        allow_override=True,
    )
