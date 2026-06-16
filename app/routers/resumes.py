from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse, ResumeListResponse
from typing import List
import uuid
import os
import pdfplumber

router = APIRouter()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from a PDF file using pdfplumber"""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()


@router.post("/upload", response_model=ResumeResponse)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a PDF resume and extract its text"""

    # Validate file is a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save file to disk
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Extract text
    extracted_text = extract_text_from_pdf(file_path)

    # Save to database
    resume = Resume(
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),  # hardcoded until auth
        filename=file.filename,
        file_path=file_path,
        extracted_text=extracted_text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/", response_model=List[ResumeListResponse])
def list_resumes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all uploaded resumes with pagination"""
    resumes = db.query(Resume).offset(skip).limit(limit).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a single resume by ID"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.delete("/{resume_id}")
def delete_resume(resume_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a resume and all its linked analyses"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully"}