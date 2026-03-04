"""
module: FastAPI routes for NLP & Clinical Structuring layer.
NOW INCLUDES: Urgency scoring for nurse triage UI.

Exposes:
  POST /nlp/extract          — extract structured data from transcript
  POST /nlp/soap             — generate SOAP note from structured data
  POST /nlp/process          — full pipeline: extract + format + validate + URGENCY
  GET  /nlp/schema           — return the clinical schema definition
  POST /nlp/validate         — validate existing structured data / SOAP note
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.models.clinical_schema import (
    NLPRequest,
    NLPResponse,
    SOAPNote,
    StructuredClinicalData,
    ValidationResult,
)
from app.services.nlp.soap_formatter import SOAPFormatter
from app.services.nlp.symptom_extractor import SymptomExtractor
from app.services.nlp.urgency_scorer import UrgencyScorer
from app.services.nlp.validators import ClinicalValidator

router = APIRouter(prefix="/nlp", tags=["NLP & Clinical Structuring"])

# Singletons — initialised once at startup
_extractor = SymptomExtractor()
_formatter = SOAPFormatter()
_validator = ClinicalValidator()
_urgency_scorer = UrgencyScorer() 



# Request / Response models

class ExtractRequest(BaseModel):
    transcript: str = Field(..., min_length=5, description="Raw transcript text")
    patient_age: Optional[str] = Field(None, example="5 years")
    patient_sex: Optional[str] = Field(None, example="male")
    session_id: Optional[str] = Field(None, description="Optional — auto-generated if omitted")


class ExtractResponse(BaseModel):
    session_id: str
    structured_data: StructuredClinicalData
    extraction_method: str
    processing_time_ms: float


class SOAPRequest(BaseModel):
    structured_data: StructuredClinicalData


class SOAPResponse(BaseModel):
    session_id: str
    soap_note: SOAPNote
    processing_time_ms: float


class ValidateRequest(BaseModel):
    structured_data: StructuredClinicalData
    soap_note: SOAPNote


class ValidateResponse(BaseModel):
    session_id: str
    validation: ValidationResult


class FullProcessRequest(BaseModel):
    transcript: str = Field(..., min_length=5)
    patient_age: Optional[str] = None
    patient_sex: Optional[str] = None
    session_id: Optional[str] = None


class NLPResponseWithUrgency(BaseModel):
    """Extended response with urgency scoring."""
    session_id: str
    structured_data: StructuredClinicalData
    soap_note: SOAPNote
    validation: ValidationResult
    urgency: Dict[str, Any]  #  {level, score, reasons, critical_flags}
    processing_time_ms: float



# Routes
@router.post(
    "/extract",
    response_model=ExtractResponse,
    summary="Extract structured clinical data from transcript",
    description=(
        "Takes a raw transcript and returns structured JSON with symptoms, "
        "demographics, vital signs, and clinical flags. "
        "Uses hybrid rule-based + LLM extraction."
    ),
)
async def extract_structured_data(request: ExtractRequest) -> ExtractResponse:
    session_id = request.session_id or str(uuid.uuid4())
    start = time.perf_counter()

    try:
        structured_data, method = _extractor.extract(
            transcript=request.transcript,
            session_id=session_id,
            patient_age=request.patient_age,
            patient_sex=request.patient_sex,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}",
        )

    elapsed_ms = (time.perf_counter() - start) * 1000

    return ExtractResponse(
        session_id=session_id,
        structured_data=structured_data,
        extraction_method=method.value,
        processing_time_ms=round(elapsed_ms, 2),
    )


@router.post(
    "/soap",
    response_model=SOAPResponse,
    summary="Generate SOAP note from structured clinical data",
    description=(
        "Takes StructuredClinicalData and returns a formatted SOAP note. "
        "The note contains NO diagnosis and NO treatment decisions."
    ),
)
async def generate_soap_note(request: SOAPRequest) -> SOAPResponse:
    start = time.perf_counter()

    try:
        soap_note = _formatter.format(request.structured_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SOAP formatting failed: {str(e)}",
        )

    elapsed_ms = (time.perf_counter() - start) * 1000

    return SOAPResponse(
        session_id=request.structured_data.session_id,
        soap_note=soap_note,
        processing_time_ms=round(elapsed_ms, 2),
    )


@router.post(
    "/process",
    response_model=NLPResponseWithUrgency,
    summary="NLP pipeline: extract → format → validate → URGENCY",
    description=(
        "Input: transcript text. "
        "Output: structured data + SOAP note + validation + urgency level. "
        "This is the main endpoint for nurse intake integration."
    ),
)
async def process_transcript(request: FullProcessRequest) -> NLPResponseWithUrgency:
    session_id = request.session_id or str(uuid.uuid4())
    start = time.perf_counter()

    # Step 1: Extract
    try:
        structured_data, method = _extractor.extract(
            transcript=request.transcript,
            session_id=session_id,
            patient_age=request.patient_age,
            patient_sex=request.patient_sex,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction step failed: {str(e)}",
        )

    # Step 2: Format SOAP
    try:
        soap_note = _formatter.format(structured_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SOAP formatting step failed: {str(e)}",
        )

    # Step 3: Validate
    try:
        validation = _validator.validate_all(structured_data, soap_note)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation step failed: {str(e)}",
        )

    # Step 4: Urgency Scoring
    try:
        urgency = _urgency_scorer.score(structured_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Urgency scoring failed: {str(e)}",
        )

    elapsed_ms = (time.perf_counter() - start) * 1000

    return NLPResponseWithUrgency(
        session_id=session_id,
        structured_data=structured_data,
        soap_note=soap_note,
        validation=validation,
        urgency=urgency.to_dict(),  
        processing_time_ms=round(elapsed_ms, 2),
    )


@router.post(
    "/validate",
    response_model=ValidateResponse,
    summary="Validate existing structured data and SOAP note",
    description="Run validation checks on pre-existing data. Useful for pipeline testing.",
)
async def validate_clinical_data(request: ValidateRequest) -> ValidateResponse:
    try:
        validation = _validator.validate_all(request.structured_data, request.soap_note)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}",
        )

    return ValidateResponse(
        session_id=request.structured_data.session_id,
        validation=validation,
    )


@router.get(
    "/schema",
    summary="Return clinical schema definition",
    description="Returns the JSON schema for StructuredClinicalData and SOAPNote.",
)
async def get_clinical_schema() -> Dict[str, Any]:
    return {
        "structured_clinical_data": StructuredClinicalData.schema(),
        "soap_note": SOAPNote.schema(),
        "validation_result": ValidationResult.schema(),
    }


@router.get(
    "/health",
    summary="NLP service health check",
)
async def nlp_health() -> Dict[str, str]:
    return {
        "service": "nlp",
        "status": "healthy",
        "extractor": "ready",
        "formatter": "ready",
        "validator": "ready",
        "urgency_scorer": "ready",
    }
