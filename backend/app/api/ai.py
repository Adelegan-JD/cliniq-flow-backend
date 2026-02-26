from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.visit import Visit
from app.models.ai_analysis import AIAnalysis
from app.models.enums import VisitStatus

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/process/{visit_id}")
def process_visit_ai(visit_id: str, db: Session = Depends(get_db)):
    visit = db.query(Visit).filter(Visit.id == visit_id).first()

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    if visit.visit_status != VisitStatus.INTAKE_COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Visit is not ready for AI processing"
        )

    # 🔥 Simulated AI output
    ai_result = AIAnalysis(
        visit_id=visit.id,
        structured_data={
            "subjective": "Patient reports fever and headache",
            "objective": "Temperature 38.5C",
            "assessment": "Possible malaria",
            "plan": "Recommend malaria test"
        },
        summary="Patient likely has malaria.",
        red_flags={"high_fever": True},
        urgency_score=0.7,
        dose_check_result={"paracetamol": "safe"},
        model_version="v1.0",
        confidence_score=0.85
    )

    db.add(ai_result)

    # 🔥 Update visit status
    visit.visit_status = VisitStatus.AI_PROCESSED

    db.commit()

    return {"message": "AI processing complete"}
