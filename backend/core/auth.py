# backend/core/auth.py
from backend.database import SessionLocal
from backend.models import User
from fastapi import Request
from sqlalchemy.orm import joinedload

def current_user(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None

    db = SessionLocal()
    user = db.query(User).options(joinedload(User.frames)).filter(User.id == user_id).first()
    db.close()
    return user
