# Purpose: Boot FastAPI, wire routers, enable CORS, expose /health.


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.orchestration_routes import router as orchestration_router
from app.api.nlp_routes import router as nlp_router
from app.api.admin_routes import router as admin_router



def create_app() -> FastAPI:
    app = FastAPI(
        title="CLINIQ-FLOW API",
        version="0.1.0",
        description="Offline-first clinical intake + triage + dose safety (demo MVP).",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    app.include_router(orchestration_router, prefix="/ai", tags=["Orchestration"])
    app.include_router(nlp_router, prefix="/ai", tags=["AI"])
    app.include_router(admin_router, prefix="/admin", tags=["Admin"])


    @app.get("/health", tags=["Health"])
    def health():
        return {"status": "ok", "service": "cliniq-flow-backend"}

    return app


app = create_app()
