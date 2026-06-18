from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class ResumeResponse(BaseModel):
    id: UUID
    filename: str
    extracted_text: Optional[str] = None
    upload_date: datetime

    model_config = {"from_attributes": True}


class ResumeListResponse(BaseModel):
    id: UUID
    filename: str
    upload_date: datetime

    model_config = {"from_attributes": True}


class PaginatedResumes(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[ResumeListResponse]