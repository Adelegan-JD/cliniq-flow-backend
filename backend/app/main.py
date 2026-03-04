from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router


from app.api.nlp_routes import router as nlp_router
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

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

# Register NLP routes
app.include_router(nlp_router)

app.include_router(api_router, prefix="/api")




@app.get("/", tags=["Root"])
async def root():
    return {"message": "CliniqFlow API is running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "cliniq-flow-backend"}
