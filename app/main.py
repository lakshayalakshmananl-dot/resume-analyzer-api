from fastapi import FastAPI
from app.routers import resumes, analyses
from app.routers.users import router as users_router  # ← add this
from app.database import Base, engine
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Resume Analyzer API",
    description="Upload a PDF resume and score it against a job description using  Groq LLM (llama-3.3-70b-versatile)"",
    version="1.0.0",
)

app.include_router(users_router)                                        # ← add this
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
app.include_router(analyses.router, prefix="/analyses", tags=["Analyses"])

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Resume Analyzer API is running"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "database": "connected", "llm": "groq/llama-3.3-70b-versatile"}