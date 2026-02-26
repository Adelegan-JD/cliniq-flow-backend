"""
FastAPI application entry point for CliniqFlow backend.
Registers all route modules for NLP and contract-compatible MVP routes.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

from app.api.admin_routes import router as admin_router
from app.api.doctor_routes import router as doctor_router
from app.api.nlp_routes import router as nlp_router
from app.api.orchestration_routes import router as orchestration_router

load_dotenv()

app = FastAPI(
    title="CliniqFlow API",
    description="AI-assisted pre-consultation platform for Nigerian paediatric healthcare",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep existing NLP routes for frontend compatibility
app.include_router(nlp_router)
app.include_router(orchestration_router, prefix="/ai", tags=["Orchestration"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(doctor_router, tags=["Doctor"])




@app.get("/", tags=["Root"])
async def root():
    return {"message": "CliniqFlow API is running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "cliniq-flow-backend"}
