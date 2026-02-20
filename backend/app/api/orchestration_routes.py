# Purpose: Expose POST /ai/process_intake

from fastapi import APIRouter
from app.schemas.intake import IntakeRequest
from app.services.orchestration.pipeline import process_intake

router = APIRouter()

@router.post("/process_intake")
def process_intake_route(payload: IntakeRequest):
    return process_intake(payload.model_dump())
