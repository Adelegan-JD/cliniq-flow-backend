from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from app.models.enums import VisitStatus, UrgencyLevel


class VisitCreate(BaseModel):
    patient_id: UUID
    chief_complaint: Optional[str] = None


class VisitResponse(BaseModel):
    id: UUID
    patient_id: UUID
    visit_status: VisitStatus
    urgency_level: Optional[UrgencyLevel]
    chief_complaint: Optional[str]

    class Config:
        from_attributes = True
