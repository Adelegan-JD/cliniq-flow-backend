from sqlalchemy import Column, ForeignKey, Float, String, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class AIAnalysis(BaseModel):
    __tablename__ = "ai_analyses"

    visit_id = Column(
        ForeignKey("visits.id"),
        nullable=False
    )

    structured_data = Column(JSONB, nullable=True)  # SOAP format
    summary = Column(String, nullable=True)

    red_flags = Column(JSONB, nullable=True)
    urgency_score = Column(Float, nullable=True)

    dose_check_result = Column(JSONB, nullable=True)

    model_version = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)

    visit = relationship("Visit")

    __table_args__ = (
        Index("idx_ai_visit_id", "visit_id"),
    )
