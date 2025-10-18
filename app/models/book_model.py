from sqlalchemy import Column, Integer, String, Text, DateTime,Float,Boolean,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=True)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    description = Column(Text, nullable=False)
    image = Column(String(255), nullable=True)
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("Author", back_populates="books")
    genre = relationship("Genre", back_populates="books")