from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.database import Base


class UserSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="sessions")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)

    reset_token = Column(String, unique=True, nullable=True, index=True)
    reset_token_expiry = Column(DateTime(timezone=True), nullable=True)

    is_verified = Column(Boolean, nullable=False, default=False)
    verification_token = Column(String, unique=True, nullable=True, index=True)

    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    books = relationship("Book", back_populates="owner", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    isbn = Column(String, index=True)
    publisher = Column(String)
    location = Column(String, index=True)
    cover_path = Column(String)
    description = Column(String)
    language = Column(String)
    personal_comment = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="books")
