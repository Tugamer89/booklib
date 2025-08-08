from sqlalchemy.orm import Session
from db.models import User, Book

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def add_book(db: Session, book: Book):
    db.add(book)
    db.commit()

def delete_book(db: Session, book: Book):
    db.delete(book)
    db.commit()
