# app/schemas/admin_schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminResponse(BaseModel):
    id: Optional[int]
    full_name: Optional[str]
    email: Optional[str]

    model_config = {"from_attributes": True}