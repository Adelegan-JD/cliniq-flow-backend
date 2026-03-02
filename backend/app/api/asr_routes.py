"""ASR (audio-to-text) API endpoints.

These endpoints accept audio/text inputs and return transcript text that can
be passed into NLP summarization pipelines.
"""

from __future__ import annotations

import base64
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.utils.auth import require_role
from app.utils.errors import error_payload

router = APIRouter(prefix="/asr", tags=["ASR"])


class ASRTranscribeRequest(BaseModel):
    audio_base64: str | None = None
    transcript_hint: str | None = None
    language: str | None = Field(default="en")


@router.post("/transcribe")
async def transcribe_route(
    payload: ASRTranscribeRequest,
    _role: str = Depends(require_role("nurse", "doctor", "admin")),
):
    transcript = (payload.transcript_hint or "").strip()
    if not transcript and payload.audio_base64:
        try:
            raw = base64.b64decode(payload.audio_base64, validate=False)
            transcript = f"[audio-bytes:{len(raw)}] transcription_placeholder"
        except Exception as exc:
            raise HTTPException(status_code=400, detail=error_payload("VALIDATION_ERROR", "Invalid base64 audio payload", str(exc)))

    if not transcript:
        raise HTTPException(
            status_code=422,
            detail=error_payload("VALIDATION_ERROR", "Either transcript_hint or audio_base64 is required", None),
        )

    return {
        "transcript": transcript,
        "confidence": 0.75,
        "language": payload.language or "en",
        "engine": "stub_asr",
        "request_id": str(uuid.uuid4()),
    }


@router.post("/upload")
async def upload_and_transcribe_route(
    payload: ASRTranscribeRequest,
    _role: str = Depends(require_role("nurse", "doctor", "admin")),
):
    raw = base64.b64decode(payload.audio_base64 or "", validate=False) if payload.audio_base64 else b""
    transcript = payload.transcript_hint or f"[audio-bytes:{len(raw)}] transcription_placeholder"
    return {
        "transcript": transcript,
        "confidence": 0.7,
        "language": payload.language or "en",
        "engine": "stub_asr",
        "request_id": str(uuid.uuid4()),
    }
