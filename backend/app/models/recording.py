from sqlalchemy import Column, String, ForeignKey, Float, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Recording(BaseModel):
    __tablename__ = "recordings"

    visit_id = Column(
        ForeignKey("visits.id"),
        nullable=False
    )

    audio_url = Column(String, nullable=False)

    transcript_raw = Column(String, nullable=True)
    transcript_normalized = Column(String, nullable=True)

    language = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)

    visit = relationship("Visit")

    __table_args__ = (
        Index("idx_recordings_visit_id", "visit_id"),
    )
