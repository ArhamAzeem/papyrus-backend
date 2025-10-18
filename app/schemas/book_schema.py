from pydantic import BaseModel
from typing import Optional

class BookCreate(BaseModel):
    title: str
    author_id: Optional[int] = None
    genre_id: Optional[int] = None
    price: float
    stock: int
    description: Optional[str] = None
    is_active: Optional[bool] = True

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author_id: Optional[int] = None
    genre_id: Optional[int] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class BookResponse(BaseModel):
    id: int
    title: str
    price: float
    stock: int
    is_active: bool
    image: Optional[str]

    class Config:
        orm_mode = True
