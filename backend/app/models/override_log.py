from sqlalchemy import Column, ForeignKey, String, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class OverrideLog(BaseModel):
    __tablename__ = "override_logs"

    visit_id = Column(
        ForeignKey("visits.id"),
        nullable=False
    )

    overridden_field = Column(String, nullable=False)
    original_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)

    doctor_id = Column(String, nullable=True)  # will link to user later
    reason = Column(String, nullable=True)

    visit = relationship("Visit")

    __table_args__ = (
        Index("idx_override_visit_id", "visit_id"),
    )
