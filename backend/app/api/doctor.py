from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.visit import Visit
from app.models.doctor_decision import DoctorDecision
from app.models.enums import VisitStatus
from app.schemas.doctor import DoctorReviewCreate
from app.models.override_log import OverrideLog
from app.schemas.override import OverrideCreate


router = APIRouter(prefix="/doctor", tags=["Doctor"])


@router.post("/review/{visit_id}")
def review_visit(
    visit_id: str,
    payload: DoctorReviewCreate,
    db: Session = Depends(get_db)
):
    visit = db.query(Visit).filter(Visit.id == visit_id).first()

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    if visit.visit_status != VisitStatus.AI_PROCESSED:
        raise HTTPException(
            status_code=400,
            detail="Visit is not ready for doctor review"
        )

    decision = DoctorDecision(
        visit_id=visit.id,
        diagnosis=payload.diagnosis,
        prescribed_medication=payload.prescribed_medication,
        notes=payload.notes,
        ai_agreement=payload.ai_agreement
    )

    db.add(decision)

    visit.visit_status = VisitStatus.DOCTOR_REVIEWED

    db.commit()

    return {"message": "Doctor review completed"}




@router.post("/override")
def log_override(payload: OverrideCreate, db: Session = Depends(get_db)):
    visit = db.query(Visit).filter(Visit.id == payload.visit_id).first()

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    if visit.visit_status not in [
        VisitStatus.AI_PROCESSED,
        VisitStatus.DOCTOR_REVIEWED
    ]:
        raise HTTPException(
            status_code=400,
            detail="Override not allowed at this stage"
        )

    override = OverrideLog(
        visit_id=payload.visit_id,
        overridden_field=payload.overridden_field,
        original_value=payload.original_value,
        new_value=payload.new_value,
        reason=payload.reason,
        doctor_id=payload.doctor_id
    )

    db.add(override)
    db.commit()

    return {"message": "Override logged successfully"}
