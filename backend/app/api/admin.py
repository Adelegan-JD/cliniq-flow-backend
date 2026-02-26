from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.visit import Visit
from app.models.doctor_decision import DoctorDecision
from app.models.override_log import OverrideLog
from app.core.auth import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/metrics")
def get_metrics(
    db: Session = Depends(get_db),
    user=Depends(require_role("admin"))
):
    total_visits = db.query(func.count(Visit.id)).scalar()

    status_counts = (
        db.query(Visit.visit_status, func.count(Visit.id))
        .group_by(Visit.visit_status)
        .all()
    )

    urgency_distribution = (
        db.query(Visit.urgency_level, func.count(Visit.id))
        .group_by(Visit.urgency_level)
        .all()
    )

    agreement_stats = (
        db.query(
            DoctorDecision.ai_agreement,
            func.count(DoctorDecision.id)
        )
        .group_by(DoctorDecision.ai_agreement)
        .all()
    )

    override_count = db.query(func.count(OverrideLog.id)).scalar()

    return {
        "total_visits": total_visits,
        "status_distribution": dict(status_counts),
        "urgency_distribution": dict(urgency_distribution),
        "ai_agreement_stats": dict(agreement_stats),
        "total_overrides": override_count,
    }
