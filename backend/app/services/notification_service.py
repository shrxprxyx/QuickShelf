from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User
from app.models.issue import Issue
from app.models.book import Book
from app.models.reservation import Reservation


def create_notification(
    db: Session,
    user_id: str,
    message: str,
    notification_type: str,
) -> Notification:

    notification = Notification(
        user_id=user_id,
        message=message,
        type=notification_type,
        is_read=False,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def create_overdue_reminder(
    db: Session,
    issue: Issue,
) -> Notification:

    book = db.query(Book).filter(Book.id == issue.book_id).first()
    book_title = book.title if book else "Unknown Book"
    
    days_overdue = (datetime.now(timezone.utc).date() - issue.due_date.date()).days
    
    message = (
        f"Your book '{book_title}' is {days_overdue} days overdue. "
        f"Please return it as soon as possible to avoid additional fines."
    )
    
    return create_notification(
        db=db,
        user_id=str(issue.user_id),
        message=message,
        notification_type="overdue_reminder",
    )


def create_fine_notification(
    db: Session,
    issue: Issue,
) -> Notification:

    if issue.fine_amount <= 0:
        return None
    
    message = f"You have an overdue fine of ${issue.fine_amount}. Please pay it at the library counter."
    
    return create_notification(
        db=db,
        user_id=str(issue.user_id),
        message=message,
        notification_type="overdue_reminder",
    )


def create_reservation_ready_notification(
    db: Session,
    reservation: Reservation,
) -> Notification:

    book = db.query(Book).filter(Book.id == reservation.book_id).first()
    book_title = book.title if book else "Unknown Book"
    
    message = f"Your reservation for '{book_title}' is ready! Please pick it up from the library."
    
    return create_notification(
        db=db,
        user_id=str(reservation.user_id),
        message=message,
        notification_type="reservation_ready",
    )


def get_user_notifications(
    db: Session,
    user_id: str,
    unread_only: bool = False,
) -> list[Notification]:

    query = db.query(Notification).filter(
        Notification.user_id == user_id,
    ).order_by(Notification.created_at.desc())
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    return query.all()


def mark_notification_as_read(
    db: Session,
    notification_id: str,
) -> Notification:
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise ValueError(f"Notification {notification_id} not found")
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_user_notifications_as_read(
    db: Session,
    user_id: str,
) -> int:
    result = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False,
    ).update({"is_read": True})
    
    db.commit()
    return result


def delete_notification(
    db: Session,
    notification_id: str,
) -> bool:
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        return False
    
    db.delete(notification)
    db.commit()
    return True