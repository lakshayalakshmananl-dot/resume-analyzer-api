import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text, nullable=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")