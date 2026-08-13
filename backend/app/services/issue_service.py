
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.issue import Issue
from app.models.book import Book
from app.models.user import User
from app.models.notification import Notification
from app.config import settings


def calculate_fine(due_date: datetime, return_date: datetime, fine_per_day: int = None) -> Decimal:
    if fine_per_day is None:
        fine_per_day = settings.fine_per_day

    if return_date.date() <= due_date.date():
        return Decimal(0)

    overdue_days = (return_date.date() - due_date.date()).days
    return Decimal(overdue_days * fine_per_day)


def issue_book(
    db: Session,
    book_id: str,  # UUID as string
    user_id: str,  # UUID as string
    due_date: datetime,
) -> Issue:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise ValueError(f"Book {book_id} not found")

    if book.available_copies <= 0:
        raise ValueError(f"Book '{book.title}' has no available copies")

    issue = Issue(
        book_id=book_id,
        user_id=user_id,
        due_date=due_date,
        status="issued",
        fine_amount=Decimal(0),
        fine_paid=False,
    )
    
    book.available_copies -= 1
    
    db.add(issue)
    db.commit()
    db.refresh(issue)
    
    return issue


def return_book(
    db: Session,
    issue_id: str,  # UUID as string
    return_date: datetime = None,
) -> Issue:
    if return_date is None:
        return_date = datetime.now(timezone.utc)

    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise ValueError(f"Issue {issue_id} not found")

    if issue.status in ["returned", "cancelled"]:
        raise ValueError(f"Issue {issue_id} is already {issue.status}")

    issue.return_date = return_date

    fine_amount = calculate_fine(issue.due_date, return_date)
    issue.fine_amount = fine_amount
    
    if return_date.date() > issue.due_date.date():
        issue.status = "overdue"
    else:
        issue.status = "returned"

    book = db.query(Book).filter(Book.id == issue.book_id).first()
    if book:
        book.available_copies += 1

    db.commit()
    db.refresh(issue)
    
    if fine_amount > 0:
        create_fine_notification(db, issue.user_id, issue_id, fine_amount)
    
    return issue


def get_user_active_issues(db: Session, user_id: str) -> list[Issue]:
    return db.query(Issue).filter(
        Issue.user_id == user_id,
        Issue.status.in_(["issued", "overdue"]),
    ).all()


def get_overdue_issues(db: Session, user_id: str = None) -> list[Issue]:
    query = db.query(Issue).filter(Issue.status == "overdue")
    if user_id:
        query = query.filter(Issue.user_id == user_id)
    return query.all()


def get_user_unpaid_fines(db: Session, user_id: str) -> list[Issue]:

    return db.query(Issue).filter(
        Issue.user_id == user_id,
        Issue.fine_amount > 0,
        Issue.fine_paid == False,
    ).all()


def mark_fine_as_paid(
    db: Session,
    issue_id: str,
    paid_date: datetime = None,
) -> Issue:

    if paid_date is None:
        paid_date = datetime.now(timezone.utc)

    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise ValueError(f"Issue {issue_id} not found")

    issue.fine_paid = True
    db.commit()
    db.refresh(issue)
    
    return issue


def get_user_by_email(db: Session, email: str) -> User:

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError(f"User with email {email} not found")
    return user


def create_fine_notification(
    db: Session,
    user_id: str,
    issue_id: str,
    fine_amount: Decimal,
) -> Notification:

    notification = Notification(
        user_id=user_id,
        message=f"You have an overdue fine of ${fine_amount} for issue {issue_id}",
        type="overdue_reminder",
        is_read=False,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def create_overdue_notification(
    db: Session,
    issue: Issue,
) -> Notification:

    book = db.query(Book).filter(Book.id == issue.book_id).first()
    book_title = book.title if book else "Unknown Book"
    
    notification = Notification(
        user_id=issue.user_id,
        message=f"Your book '{book_title}' is overdue. Please return it as soon as possible.",
        type="overdue_reminder",
        is_read=False,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification