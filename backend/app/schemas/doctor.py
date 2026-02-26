from pydantic import BaseModel
from typing import Optional


class DoctorReviewCreate(BaseModel):
    diagnosis: Optional[str] = None
    prescribed_medication: Optional[str] = None
    notes: Optional[str] = None
    ai_agreement: Optional[bool] = None
