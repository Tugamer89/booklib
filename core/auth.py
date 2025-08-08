from fastapi import HTTPException, Request, Depends
from sqlalchemy.orm import Session
from db.crud import get_user_by_id
from db.database import get_db
from datetime import datetime

def get_authenticated_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    session_token = request.session.get("session_token")
    if not user_id or not session_token:
        raise HTTPException(status_code=401, detail="Non autenticato")

    user = get_user_by_id(db, user_id)
    if not user or user.session_token != session_token:
        raise HTTPException(status_code=401, detail="Sessione non valida")

    if user.session_expiry and user.session_expiry < datetime.now():
        request.session.clear()
        user.session_token = None
        user.session_expiry = None
        db.commit()
        raise HTTPException(status_code=401, detail="Sessione scaduta")

    return user
