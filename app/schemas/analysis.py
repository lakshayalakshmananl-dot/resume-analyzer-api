from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, List


# What the user sends to trigger analysis
class AnalysisCreate(BaseModel):
    resume_id: UUID
    job_description: str
    job_title: Optional[str] = None


# What we return to the user
class AnalysisResponse(BaseModel):
    id: UUID
    resume_id: UUID
    job_title: Optional[str] = None
    score: int
    matched_skills: List[str]
    missing_skills: List[str]
    suggestions: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# What we return in a list
class AnalysisListResponse(BaseModel):
    id: UUID
    job_title: Optional[str] = None
    score: int
    created_at: datetime

    class Config:
        from_attributes = True