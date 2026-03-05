from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from dotenv import load_dotenv

from app.api.admin_routes import router as admin_routes_router
from app.api.asr_routes import translate_router, conversation_router, limiter, lifespan
from app.api.clinical_routes import router as clinical_routes_router
from app.api.doctor_routes import router as doctor_routes_router
from app.api.nlp_routes import router as nlp_router
from app.api.nurse_routes import router as nurse_routes_router
from app.api.orchestration_routes import router as orchestration_routes_router
from app.api.record_officer_routes import router as record_officer_routes_router
from app.api.router import api_router
from app.utils.auth import AuthContext
from app.utils.auth import require_role
from app.utils.errors import error_payload

load_dotenv()

app = FastAPI(
    title="CliniqFlow API",
    description="AI-assisted pre-consultation platform for Nigerian paediatric healthcare",
    version="0.1.0",lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Hamids router for ASR
app.include_router(translate_router)
app.include_router(conversation_router)

# Malik router kept active for Supabase-first endpoints under /api.
app.include_router(api_router, prefix="/api")

# Existing NLP service endpoints.
app.include_router(nlp_router)

# Legacy import kept for reference:
# from app.api.asr_routes import router as asr_router
# Commented out because ASR module can fail import/startup in API mode.
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
        auth: AuthContext = Depends(require_role("nurse", "doctor", "admin")),
    ):
        _ = auth
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

# Contract-compatible route stack retained for frontend/test compatibility.
app.include_router(admin_routes_router, prefix="/admin", tags=["Admin"])
app.include_router(asr_router)
app.include_router(orchestration_routes_router, prefix="/ai", tags=["Orchestration"])
app.include_router(clinical_routes_router)
app.include_router(nurse_routes_router)
app.include_router(record_officer_routes_router)
app.include_router(doctor_routes_router, tags=["Doctor"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_payload("VALIDATION_ERROR", "Request validation failed", exc.errors()),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload("HTTP_ERROR", str(exc.detail), None),
    )


@app.get("/", tags=["Root"])
async def root():
    return {"message": "CliniqFlow API is running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "cliniq-flow-backend"}
