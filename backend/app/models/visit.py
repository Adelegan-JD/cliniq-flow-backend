from sqlalchemy import Column, String, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import VisitStatus, UrgencyLevel


class Visit(BaseModel):
    __tablename__ = "visits"

    patient_id = Column(ForeignKey("patients.id"), nullable=False)

    visit_status = Column(
        Enum(VisitStatus),
        default=VisitStatus.REGISTERED,
        nullable=False
    )

    urgency_level = Column(
        Enum(UrgencyLevel),
        nullable=True
    )

    language_detected = Column(String, nullable=True)
    chief_complaint = Column(String, nullable=True)

    patient = relationship("Patient", back_populates="visits")

    __table_args__ = (
        Index("idx_visits_patient_id", "patient_id"),
        Index("idx_visits_status", "visit_status"),
        Index("idx_visits_urgency", "urgency_level"),
    )
