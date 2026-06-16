from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


# What we return to the user
class ResumeResponse(BaseModel):
    id: UUID
    filename: str
    extracted_text: Optional[str] = None
    upload_date: datetime

    class Config:
        from_attributes = True


# What we return in a list
class ResumeListResponse(BaseModel):
    id: UUID
    filename: str
    upload_date: datetime

    class Config:
        from_attributes = True