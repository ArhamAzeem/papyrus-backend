from sqlalchemy import Column, Integer, String, Boolean,DateTime
from datetime import datetime
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    full_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=False,unique=True,index=True)
    password = Column(String(255))
    image = Column(String(255), nullable=True)
    is_active = Column(Boolean,default=True)
    is_verified = Column(Boolean,default=True)
    verification_token = Column(String(255),nullable=True)
    reset_token = Column(String(255),nullable=True)
    fcm_token = Column(String(255),nullable=True)
    created_at = Column(DateTime,default=datetime.utcnow)
    updated_at = Column(DateTime,default=datetime.utcnow)