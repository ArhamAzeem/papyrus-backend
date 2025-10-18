from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AuthorBase(BaseModel):
    full_name: str
    biography: Optional[str] = None
    image: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(BaseModel):
    full_name: Optional[str] = None
    biography: Optional[str] = None
    image: Optional[str] = None

class AuthorResponse(AuthorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True