from sqlalchemy import Column, ForeignKey, String, Boolean, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class DoctorDecision(BaseModel):
    __tablename__ = "doctor_decisions"

    visit_id = Column(
        ForeignKey("visits.id"),
        nullable=False
    )

    diagnosis = Column(String, nullable=True)
    prescribed_medication = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    ai_agreement = Column(Boolean, nullable=True)

    visit = relationship("Visit")

    __table_args__ = (
        Index("idx_decision_visit_id", "visit_id"),
    )
