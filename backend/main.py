"""
FastAPI application entry point for CliniqFlow backend.
Registers all route modules for NLP and contract-compatible MVP routes.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from dotenv import load_dotenv

from app.api.admin_routes import router as admin_router
from app.api.asr_routes import translate_router, conversation_router,limiter,lifespan
from app.api.clinical_routes import router as clinical_router
from app.api.doctor_routes import router as doctor_router
from app.api.nurse_routes import router as nurse_router
from app.api.nlp_routes import router as nlp_router
from app.api.orchestration_routes import router as orchestration_router
from app.api.record_officer_routes import router as record_officer_router
from app.utils.auth import require_role
from app.utils.errors import error_payload
from app.utils.storage import init_db


load_dotenv()

try:
    from app.api.asr_routes import router as asr_router
except Exception:
    asr_router = APIRouter(prefix="/asr", tags=["ASR"])

    class ASRTranscribeRequest(BaseModel):
        audio_base64: str | None = None
        transcript_hint: str | None = None
        language: str | None = Field(default="en")

    @asr_router.post("/transcribe")
    async def transcribe_route(
        payload: ASRTranscribeRequest,
        _role: str = Depends(require_role("nurse", "doctor", "admin")),
    ):
        transcript = (payload.transcript_hint or "").strip()
        if not transcript:
            raise HTTPException(
                status_code=422,
                detail=error_payload(
                    "VALIDATION_ERROR",
                    "Either transcript_hint or audio_base64 is required",
                    None,
                ),
            )

        return {
            "transcript": transcript,
            "confidence": 0.75,
            "language": payload.language or "en",
            "engine": "stub_asr",
        }

app = FastAPI(
    title="CliniqFlow API",
    description="AI-assisted pre-consultation platform for Nigerian paediatric healthcare",
    version="0.1.0", lifespan=lifespan
)

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep existing NLP routes for frontend compatibility
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(nlp_router)
app.include_router(translate_router)
app.include_router(conversation_router)
app.include_router(orchestration_router, prefix="/ai", tags=["Orchestration"])
app.include_router(clinical_router)
app.include_router(nurse_router)
app.include_router(record_officer_router)
# Legacy duplicate include kept for review:
# app.include_router(admin_router, prefix="/admin", tags=["Admin"])
# Commented out because it registered the same admin routes twice.
app.include_router(doctor_router, tags=["Doctor"])


@app.on_event("startup")
def startup_db() -> None:
    init_db()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_payload("VALIDATION_ERROR", "Request validation failed", exc.errors()),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_request, exc: HTTPException) -> JSONResponse:
    detail: Any = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload("HTTP_ERROR", str(detail), None),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=error_payload("INTERNAL_ERROR", "Unexpected server error", str(exc)),
    )




@app.get("/", tags=["Root"])
async def root():
    return {"message": "CliniqFlow API is running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "cliniq-flow-backend"}
