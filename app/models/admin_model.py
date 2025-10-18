from sqlalchemy import Column, Integer, String, Boolean,DateTime
from datetime import datetime
from app.db.session import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer,primary_key=True,index=True)
    full_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=False,unique=True,index=True)
    password = Column(String(255))
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime,default=datetime.utcnow)
    updated_at = Column(DateTime,default=datetime.utcnow)