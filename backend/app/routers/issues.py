from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import uuid

from app.database import get_db
from app.utils.clerk_auth import verify_token, get_current_user
from app.models.user import User
from app.models.issue import Issue
from app.models.book import Book
from app.schemas.issue import (
    IssueCreateRequest,
    IssueOut,
    QRScanRequest,
    QRScanResponse,
    IssueReturnRequest,
    IssueReturnResponse,
    MarkFineAsPaidRequest,
    UserActiveIssuesResponse,
    FineListResponse,
    IssueDetailedOut,
    BookInfoForIssue,
    UserInfoForIssue,
)
from app.services import issue_service

router = APIRouter(prefix="/api/issues", tags=["issues"])


@router.post("/qr-scan", response_model=QRScanResponse)
def qr_scan_issue(
    req: QRScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Scan a book's QR code to issue it to a student.
    
    QR payload format: "book:<book_id>"
    Librarian provides student's email; endpoint verifies librarian role.
    """
    if current_user.role not in ["librarian", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only librarians can issue books",
        )

    try:
        prefix, book_id_str = req.qr_payload.split(":", 1)
        if prefix != "book":
            raise ValueError("Invalid QR prefix")
        book_id = uuid.UUID(book_id_str)
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid QR payload. Expected format: 'book:<uuid>'",
        )

    try:
        student = issue_service.get_user_by_email(db, req.user_email)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with email {req.user_email} not found",
        )

    try:
        due_date = datetime.now(timezone.utc) + timedelta(days=14)
        
        issue = issue_service.issue_book(
            db=db,
            book_id=str(book_id),
            user_id=str(student.id),
            due_date=due_date,
        )
        
        return QRScanResponse(
            success=True,
            message=f"Book issued successfully to {student.name}",
            issue=IssueOut.from_attributes(issue),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/issue", response_model=IssueOut)
def create_issue(
    req: IssueCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually issue a book to a user (librarian/admin only).
    """
    if current_user.role not in ["librarian", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only librarians can issue books",
        )

    try:
        issue = issue_service.issue_book(
            db=db,
            book_id=str(req.book_id),
            user_id=str(req.user_id),
            due_date=req.due_date,
        )
        return IssueOut.from_attributes(issue)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/return", response_model=IssueReturnResponse)
def return_issue(
    req: IssueReturnRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a book as returned and calculate fine if overdue.
    """
    issue = db.query(Issue).filter(Issue.id == req.issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue {req.issue_id} not found",
        )

    if current_user.role not in ["librarian", "admin"] and issue.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only return your own books",
        )

    try:
        return_date = req.return_date or datetime.now(timezone.utc)
        returned_issue = issue_service.return_book(
            db=db,
            issue_id=str(req.issue_id),
            return_date=return_date,
        )
        
        message = f"Book returned successfully. Status: {returned_issue.status}"
        if returned_issue.fine_amount > 0:
            message += f". Fine: ${returned_issue.fine_amount}"

        return IssueReturnResponse(
            issue_id=returned_issue.id,
            status=returned_issue.status,
            fine_amount=float(returned_issue.fine_amount),
            fine_paid=returned_issue.fine_paid,
            message=message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get("/me", response_model=UserActiveIssuesResponse)
def get_my_issues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all active (unreturned) issues for the current user.
    """
    issues = issue_service.get_user_active_issues(db, str(current_user.id))
    
    # Enrich with book and user info
    detailed_issues = []
    for issue in issues:
        book = db.query(Book).filter(Book.id == issue.book_id).first()
        detailed_issues.append(
            IssueDetailedOut(
                id=issue.id,
                book=BookInfoForIssue.from_attributes(book) if book else None,
                user=UserInfoForIssue.from_attributes(current_user),
                issue_date=issue.issue_date,
                due_date=issue.due_date,
                return_date=issue.return_date,
                status=issue.status,
                fine_amount=float(issue.fine_amount),
                fine_paid=issue.fine_paid,
            )
        )
    
    return UserActiveIssuesResponse(
        count=len(detailed_issues),
        issues=detailed_issues,
    )

@router.get("/fines/me", response_model=FineListResponse)
def get_my_fines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all unpaid fines for the current user.
    """
    issues = issue_service.get_user_unpaid_fines(db, str(current_user.id))
    
    total_fines = sum(float(issue.fine_amount) for issue in issues)
    
    return FineListResponse(
        total_unpaid_fines=total_fines,
        count=len(issues),
        issues=[IssueOut.from_attributes(issue) for issue in issues],
    )


@router.post("/fines/pay")
def pay_fine(
    req: MarkFineAsPaidRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a fine as paid.
    """
    issue = db.query(Issue).filter(Issue.id == req.issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue {req.issue_id} not found",
        )

    if current_user.role not in ["admin"] and issue.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only pay your own fines",
        )

    if issue.fine_amount == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This issue has no fine",
        )

    try:
        paid_date = req.paid_date or datetime.now(timezone.utc)
        updated_issue = issue_service.mark_fine_as_paid(
            db=db,
            issue_id=str(req.issue_id),
            paid_date=paid_date,
        )
        return {
            "success": True,
            "message": f"Fine of ${updated_issue.fine_amount} marked as paid",
            "issue": IssueOut.from_attributes(updated_issue),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/overdue", response_model=list[IssueOut])
def get_overdue_issues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all overdue issues (admin only).
    """
    if current_user.role not in ["admin", "librarian"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all overdue issues",
        )

    issues = issue_service.get_overdue_issues(db)
    return [IssueOut.from_attributes(issue) for issue in issues]


@router.get("/{issue_id}", response_model=IssueOut)
def get_issue(
    issue_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific issue by ID.
    """
    try:
        issue_uuid = uuid.UUID(issue_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid issue ID format",
        )

    issue = db.query(Issue).filter(Issue.id == issue_uuid).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue {issue_id} not found",
        )

    if current_user.role not in ["admin"] and issue.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own issues",
        )

    return IssueOut.from_attributes(issue)