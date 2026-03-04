from fastapi import FastAPI
from app.api import patient, visit, admin, doctor, recording, ai

app = FastAPI(title="Cliniq-Flow Backend")

# Legacy router stack kept for reference:
# - app.api.admin_routes
# - app.api.clinical_routes
# - app.api.doctor_routes
# - app.api.nurse_routes
# - app.api.orchestration_routes
# Active stack below follows the Malik DB-linked API modules.
app.include_router(patient.router)
app.include_router(visit.router)
app.include_router(admin.router)
app.include_router(doctor.router)
app.include_router(recording.router)
app.include_router(ai.router)
