from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.session import Base

class BlacklistedToken(Base):
    __tablename__ = "token_blacklist"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)