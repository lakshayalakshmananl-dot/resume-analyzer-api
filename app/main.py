from fastapi import FastAPI
from app.routers import resumes, analyses
from app.routers.users import router as users_router  # ← add this

app = FastAPI(
    title="Resume Analyzer API",
    description="Upload a PDF resume and score it against a job description using Mistral-7B",
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
    return {"status": "ok", "database": "connected", "llm": "huggingface/mistral-7b"}