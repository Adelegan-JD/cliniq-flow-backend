from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.recording import Recording
from app.models.visit import Visit
from app.schemas.recording import RecordingCreate, RecordingResponse
from app.models.enums import VisitStatus

router = APIRouter(prefix="/recordings", tags=["Recordings"])



@router.post("/", response_model=RecordingResponse)
def create_recording(payload: RecordingCreate, db: Session = Depends(get_db)):
    visit = db.query(Visit).filter(Visit.id == payload.visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    recording = Recording(**payload.model_dump())

    db.add(recording)

    # 🔥 Update visit status
    visit.visit_status = VisitStatus.INTAKE_COMPLETED

    db.commit()
    db.refresh(recording)

    return recording
