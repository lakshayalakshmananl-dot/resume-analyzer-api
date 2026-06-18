from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.analysis import Analysis
from app.models.resume import Resume
from app.models.user import User
from app.schemas.analysis import AnalysisCreate, AnalysisResponse, AnalysisListResponse, PaginatedAnalyses
from app.dependencies import get_current_user
from typing import List
from groq import Groq
import uuid
import os
import json

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_API_KEY)


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
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3,
        )
        generated = response.choices[0].message.content
        print(f"GROQ RESPONSE: {generated[:300]}")

        json_start = generated.find("{")
        json_end = generated.rfind("}") + 1
        parsed = json.loads(generated[json_start:json_end])
        return parsed, generated

    except Exception as e:
        print(f"LLM ERROR: {e}")
        return {
            "score": 50,
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": ["Could not reach LLM — check your Groq API key"]
        }, ""


@router.post("/", response_model=AnalysisResponse)
def create_analysis(
    payload: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not resume.extracted_text:
        raise HTTPException(status_code=400, detail="Resume has no extracted text")

    result, raw_output = score_resume_with_llm(resume.extracted_text, payload.job_description)

    analysis = Analysis(
        resume_id=payload.resume_id,
        user_id=current_user.id,
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


@router.get("/", response_model=PaginatedAnalyses)
def list_analyses(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"total": total, "skip": skip, "limit": limit, "items": items}


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    db.delete(analysis)
    db.commit()
    return {"message": "Analysis deleted successfully"}