from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.analysis import Analysis
from app.models.resume import Resume
from app.schemas.analysis import AnalysisCreate, AnalysisResponse, AnalysisListResponse
from typing import List
import uuid
import httpx
import os
import json

router = APIRouter()

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
HF_MODEL_URL = os.getenv(
    "HF_MODEL_URL",
    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
)


def score_resume_with_llm(resume_text: str, job_description: str):
    prompt = f"""You are an expert technical recruiter. Analyze the resume against the job description.
Return ONLY a valid JSON object with these exact keys:
- score (integer 0-100)
- matched_skills (list of strings)
- missing_skills (list of strings)
- suggestions (list of 3 strings)

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{job_description[:1000]}

JSON:"""

    try:
        response = httpx.post(
            HF_MODEL_URL,
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={
                "inputs": prompt,
                "parameters": {"max_new_tokens": 500}
            },
            timeout=30,
        )
        raw = response.json()

        if isinstance(raw, list):
            generated = raw[0].get("generated_text", "")
        else:
            generated = str(raw)

        json_start = generated.find("{")
        json_end = generated.rfind("}") + 1
        parsed = json.loads(generated[json_start:json_end])
        return parsed, generated

    except Exception:
        return {
            "score": 50,
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": ["Could not reach LLM — check your HuggingFace API key"]
        }, ""


@router.post("/", response_model=AnalysisResponse)
def create_analysis(payload: AnalysisCreate, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == payload.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not resume.extracted_text:
        raise HTTPException(status_code=400, detail="Resume has no extracted text")

    result, raw_output = score_resume_with_llm(resume.extracted_text, payload.job_description)

    analysis = Analysis(
        resume_id=payload.resume_id,
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        job_description=payload.job_description,
        job_title=payload.job_title,
        score=result.get("score", 0),
        matched_skills=result.get("matched_skills", []),
        missing_skills=result.get("missing_skills", []),
        suggestions=result.get("suggestions", []),
        raw_llm_output=raw_output,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("/", response_model=List[AnalysisListResponse])
def list_analyses(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    analyses = db.query(Analysis).offset(skip).limit(limit).all()
    return analyses


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: uuid.UUID, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@router.delete("/{analysis_id}")
def delete_analysis(analysis_id: uuid.UUID, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    db.delete(analysis)
    db.commit()
    return {"message": "Analysis deleted successfully"}