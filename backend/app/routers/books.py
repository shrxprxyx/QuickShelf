import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.deps import get_current_user, require_role
from app.models.book import Book
from app.models.category import Category
from app.schemas.book import BookCreate, BookUpdate, BookOut, CategoryOut, CategoryCreate
from app.services.qr_service import generate_book_qr, delete_book_qr

router = APIRouter(prefix="/api/v1/books", tags=["books"])
categories_router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


# ---------- Books ----------

@router.get("", response_model=list[BookOut])
def list_books(
    q: Optional[str] = Query(default=None, description="Search title/author/isbn"),
    category: Optional[int] = Query(default=None),
    available: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),  # any logged-in user can browse
):
    query = db.query(Book)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(Book.title.ilike(like), Book.author.ilike(like), Book.isbn.ilike(like))
        )
    if category is not None:
        query = query.filter(Book.category_id == category)
    if available is True:
        query = query.filter(Book.available_copies > 0)
    elif available is False:
        query = query.filter(Book.available_copies == 0)

    return query.order_by(Book.title).all()


@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: uuid.UUID, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("", response_model=BookOut, status_code=201)
def create_book(
    payload: BookCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role("admin", "librarian")),
):
    book = Book(
        id=uuid.uuid4(),
        title=payload.title,
        author=payload.author,
        isbn=payload.isbn,
        category_id=payload.category_id,
        cover_url=payload.cover_url,
        ebook_url=payload.ebook_url,
        total_copies=payload.total_copies,
        available_copies=payload.total_copies,  # all copies start available
        description=payload.description,
    )
    db.add(book)
    db.commit()
    db.refresh(book)

    # generate QR after the row exists, since the QR payload encodes book.id
    book.qr_code_url = generate_book_qr(book.id)
    db.commit()
    db.refresh(book)

    return book


@router.put("/{book_id}", response_model=BookOut)
def update_book(
    book_id: uuid.UUID,
    payload: BookUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role("admin", "librarian")),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    data = payload.model_dump(exclude_unset=True)

    # if total_copies changes, shift available_copies by the same delta
    # so currently-issued copies stay consistent
    if "total_copies" in data:
        delta = data["total_copies"] - book.total_copies
        book.available_copies = max(0, book.available_copies + delta)

    for field, value in data.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(
    book_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role("admin", "librarian")),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    delete_book_qr(book_id)
    return None


# ---------- Categories ----------

@categories_router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    return db.query(Category).order_by(Category.name).all()


@categories_router.post("", response_model=CategoryOut, status_code=201)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role("admin", "librarian")),
):
    existing = db.query(Category).filter(Category.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")

    category = Category(name=payload.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category