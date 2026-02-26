from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.visit import Visit
from app.models.patient import Patient
from app.schemas.visit import VisitCreate, VisitResponse

router = APIRouter(prefix="/visits", tags=["Visits"])


@router.post("/", response_model=VisitResponse)
def create_visit(payload: VisitCreate, db: Session = Depends(get_db)):
    # Check patient exists
    patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    visit = Visit(
        patient_id=payload.patient_id,
        chief_complaint=payload.chief_complaint
    )

    db.add(visit)
    db.commit()
    db.refresh(visit)

    return visit
