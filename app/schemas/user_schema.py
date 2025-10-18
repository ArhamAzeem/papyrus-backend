from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    full_name: Optional[str]
    image: Optional[str]
class UserRegister(BaseModel):
    full_name:str
    email:EmailStr
    password:str

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class ForgotPassword(BaseModel):
    email:EmailStr

class ResetPassword(BaseModel):
    token:str
    new_password:str

class UserResponse(UserBase):
    id: Optional[int]
    is_verified: Optional[bool]

    model_config = {"from_attributes": True}