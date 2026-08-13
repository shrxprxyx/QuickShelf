import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    category_id: Optional[int] = None
    cover_url: Optional[str] = None
    ebook_url: Optional[str] = None
    total_copies: int = Field(default=1, ge=1)
    description: Optional[str] = None


class BookCreate(BookBase):
    """Payload for POST /books. available_copies is set server-side = total_copies."""
    pass


class BookUpdate(BaseModel):
    """All fields optional — partial update (PUT with only changed fields)."""
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    category_id: Optional[int] = None
    cover_url: Optional[str] = None
    ebook_url: Optional[str] = None
    total_copies: Optional[int] = Field(default=None, ge=1)
    description: Optional[str] = None


class BookOut(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    available_copies: int
    qr_code_url: Optional[str] = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CategoryCreate(BaseModel):
    name: str