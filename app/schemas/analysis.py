from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class AnalysisCreate(BaseModel):
    resume_id: UUID
    job_description: str = Field(min_length=10, max_length=5000)
    job_title: Optional[str] = Field(None, min_length=2, max_length=100)


class AnalysisResponse(BaseModel):
    id: UUID
    resume_id: UUID
    job_title: Optional[str] = None
    score: int
    matched_skills: List[str]
    missing_skills: List[str]
    suggestions: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListResponse(BaseModel):
    id: UUID
    job_title: Optional[str] = None
    score: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedAnalyses(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[AnalysisListResponse]