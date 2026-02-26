from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class RecordingCreate(BaseModel):
    visit_id: UUID
    audio_url: str
    transcript_raw: Optional[str] = None
    transcript_normalized: Optional[str] = None
    language: Optional[str] = None
    confidence_score: Optional[float] = None


class RecordingResponse(BaseModel):
    id: UUID
    visit_id: UUID
    audio_url: str
    transcript_raw: Optional[str]
    transcript_normalized: Optional[str]
    language: Optional[str]
    confidence_score: Optional[float]

    class Config:
        from_attributes = True
