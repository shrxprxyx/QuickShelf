import uuid
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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

    book = relationship("Book", back_populates="issues")
    user = relationship("User", back_populates="issues")

    __table_args__ = (
        Index("idx_issues_user_id_status", "user_id", "status"),
        Index("idx_issues_book_id", "book_id"),
        Index("idx_issues_due_date", "due_date"),
    )

    def __repr__(self):
        return f"<Issue(id={self.id}, book_id={self.book_id}, user_id={self.user_id}, status={self.status})>"