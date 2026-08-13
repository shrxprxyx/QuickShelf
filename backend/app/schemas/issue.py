import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict



class IssueCreateRequest(BaseModel):
    """Issue a book to a user (admin/librarian only)."""
    book_id: uuid.UUID
    user_id: uuid.UUID
    due_date: datetime


class QRScanRequest(BaseModel):
    """QR scan payload for issuing a book.
    
    QR should encode: "book:<book_id>"
    """
    qr_payload: str  # Format: "book:<book_id>"
    user_email: str  # Librarian provides student email


class IssueReturnRequest(BaseModel):
    """Return a book."""
    issue_id: uuid.UUID
    return_date: Optional[datetime] = None  


class MarkFineAsPaidRequest(BaseModel):
    """Mark a fine as paid."""
    issue_id: uuid.UUID
    paid_date: Optional[datetime] = None


class IssueOut(BaseModel):
    """Basic issue response."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    book_id: uuid.UUID
    user_id: uuid.UUID
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    status: str  # issued | returned | overdue
    fine_amount: float
    fine_paid: bool


class IssueDetailOut(BaseModel):
    """Issue with related book and user details."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    book_id: uuid.UUID
    user_id: uuid.UUID
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    status: str
    fine_amount: float
    fine_paid: bool


class BookInfoForIssue(BaseModel):
    """Minimal book info for issue response."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    author: str
    isbn: Optional[str]


class UserInfoForIssue(BaseModel):
    """Minimal user info for issue response."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    role: str


class IssueDetailedOut(BaseModel):
    """Full issue response with book and user embedded."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    book: BookInfoForIssue
    user: UserInfoForIssue
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    status: str
    fine_amount: float
    fine_paid: bool


class IssueReturnResponse(BaseModel):
    """Response after returning a book."""
    model_config = ConfigDict(from_attributes=True)
    issue_id: uuid.UUID
    status: str
    fine_amount: float
    fine_paid: bool
    message: str


class FineListResponse(BaseModel):
    """List of unpaid fines for a user."""
    total_unpaid_fines: float
    count: int
    issues: list[IssueOut]


class UserActiveIssuesResponse(BaseModel):
    """List of active issues for a user."""
    
    count: int
    issues: list[IssueDetailedOut]


class QRScanResponse(BaseModel):
    """Response from scanning a QR code."""
    success: bool
    message: str
    issue: Optional[IssueOut] = None