""" 
simplified for nurse vitals input. 
simlified for doctor full pipeline (no urgency scoring in doctor workflow - only vitals-based urgency for nurse triage).

Two main endpoints:
 1. /nlp/vitals-urgency - Nurse enters vitals, gets urgency + BMI
 2. /nlp/process - Doctor's full pipeline (symptoms, SOAP, validation) - FOR DOCTOR USE ONLY
  
"""

from __future__ import annotations


import time
import uuid
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Models and Services
from models.clinical_schema import PatientDemographics, VitalSign
from app.services.nlp.urgency_scorer import UrgencyScorer
from app.services.nlp.symptom_extractor import SymptomExtractor
from app.services.nlp.soap_formatter import SOAPFormatter
from app.services.nlp.validators import ClinicalValidator

router = APIRouter(prefix="/nlp", tags=["NLP & Clinical Structuring"])

# Initialize services
_extractor = SymptomExtractor()
_formatter = SOAPFormatter()
_validator = ClinicalValidator()
_urgency_scorer = UrgencyScorer()



# NURSE WORKFLOW - Vitals Only


class NurseVitalsInput(BaseModel):
    patient_age: str = Field(..., example="5 years")
    patient_sex: str = Field(..., example="male")
    temperature: float = Field(..., ge=30.0, le=45.0, example=37.2)
    heart_rate: int = Field(..., ge=40, le=250, example=100)
    respiratory_rate: int = Field(..., ge=8, le=80, example=20)
    
    # Make weight & height optional for BMI calculation
    weight_kg: Optional[float] = Field(None, le=200, example=18.5)
    height_cm: Optional[float] = Field(None, le=250, example=110.0)
    
    session_id: Optional[str] = None  # optional session ID


class VitalsUrgencyResponse(BaseModel):
    session_id: str
    urgency_level: str
    urgency_score: int
    urgency_reasons: List[str]
    abnormal_vitals: List[str]
    
    # BMI is now optional
    bmi: Optional[float]
    bmi_category: str
    
    vitals: List[dict]
    patient_age: str
    patient_sex: str
    processing_time_ms: float


# BMI category helper
def _assess_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


@router.post(
    "/vitals-urgency",
    response_model=VitalsUrgencyResponse,
    summary="Calculate urgency from nurse vital signs (NURSE WORKFLOW)",
)
async def calculate_vitals_urgency(input: NurseVitalsInput) -> VitalsUrgencyResponse:
    session_id = input.session_id or f"vitals-{int(time.time() * 1000)}"
    start = time.perf_counter()

    try:
        
        # Prepare vitals list
        
        vitals = [
            VitalSign(name="temperature", value=str(input.temperature), unit="°C"),
            VitalSign(name="heart_rate", value=str(input.heart_rate), unit="bpm"),
            VitalSign(name="respiratory_rate", value=str(input.respiratory_rate), unit="breaths/min"),
            # VitalSign(name="oxygen_saturation", value=str(input.oxygen_saturation), unit="%"),
        ]

        
        # Calculate BMI if both weight & height exist
    
        if input.weight_kg and input.height_cm:
            height_m = input.height_cm / 100
            bmi = input.weight_kg / (height_m ** 2)
        else:
            bmi = None  # BMI not calculated if missing data

       
        # Create demographics object
    
        demographics = PatientDemographics(
            age=input.patient_age,
            sex=input.patient_sex,
            weight_kg=input.weight_kg,
            height_cm=input.height_cm,
            bmi=bmi,
        )

    
        # Calculate urgency score
       
        urgency = _urgency_scorer.score(vitals, demographics)

        # Determine BMI category if BMI exists
        bmi_category = _assess_bmi(bmi) if bmi else "Unknown"  

        elapsed_ms = (time.perf_counter() - start) * 1000

      
        # Return response
       
        return VitalsUrgencyResponse(
            session_id=session_id,
            urgency_level=urgency.level.value,
            urgency_score=urgency.score,
            urgency_reasons=urgency.reasons,
            abnormal_vitals=urgency.abnormal_vitals,
            bmi=round(bmi, 2) if bmi else None,
            bmi_category=bmi_category,
            vitals=[{"name": v.name, "value": v.value, "unit": v.unit} for v in vitals],
            patient_age=input.patient_age,
            patient_sex=input.patient_sex,
            processing_time_ms=round(elapsed_ms, 2),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate urgency: {str(e)}"
        )


# DOCTOR WORKFLOW - Full Pipeline

class FullProcessRequest(BaseModel):
    transcript: str = Field(..., min_length=5)
    patient_age: Optional[str] = None
    patient_sex: Optional[str] = None
    session_id: Optional[str] = None


@router.post(
    "/process",
    summary="Full NLP pipeline (DOCTOR WORKFLOW)",
    description="Full pipeline: extract symptoms → SOAP → validate. For doctor use.",
)
async def process_transcript(request: FullProcessRequest):
    session_id = request.session_id or str(uuid.uuid4())
    start = time.perf_counter()

    # Step 1: Extract symptoms
    structured_data, method = _extractor.extract(
        transcript=request.transcript,
        session_id=session_id,
        patient_age=request.patient_age,
        patient_sex=request.patient_sex,
    )

    # Step 2: Generate SOAP
    soap_note = _formatter.format(structured_data)

    # Step 3: Validate
    validation = _validator.validate_all(structured_data, soap_note)

    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "session_id": session_id,
        "structured_data": structured_data.dict(),
        "soap_note": soap_note.dict(),
        "validation": validation.dict(),
        "processing_time_ms": round(elapsed_ms, 2),
    }


# HEALTH CHECK

@router.get("/health")
async def nlp_health():
    return {
        "service": "nlp",
        "status": "healthy",
        "workflows": {
            "nurse": "/nlp/vitals-urgency (vitals-only)",
            "doctor": "/nlp/process (full pipeline)",
        },
    }
