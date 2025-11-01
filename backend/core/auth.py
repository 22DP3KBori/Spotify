# backend/core/auth.py
from backend.database import SessionLocal
from backend.models import User
from fastapi import Request

def current_user(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None

    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    return user
