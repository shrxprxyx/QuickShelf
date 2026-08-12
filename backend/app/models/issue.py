import uuid
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Issue(Base):
    __tablename__ = "issues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False, default="issued")  # issued | returned | overdue
    fine_amount = Column(Numeric, default=0)
    fine_paid = Column(Boolean, default=False)