from sqlalchemy.orm import Session
from db.models import User, Book, UserSession

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

def logout_current(db: Session, token: str):
    db.query(UserSession).filter(UserSession.token == token).delete()
    db.commit()

def logout_all(db: Session, user_id: int):
    db.query(UserSession).filter(UserSession.user_id == user_id).delete()
    db.commit()
