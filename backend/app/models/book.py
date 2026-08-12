import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    cover_url = Column(String, nullable=True)
    ebook_url = Column(String, nullable=True)
    total_copies = Column(Integer, nullable=False, default=1)
    available_copies = Column(Integer, nullable=False, default=1)
    qr_code_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("Category")