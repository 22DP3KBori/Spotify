from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from backend.database import get_db
from backend.models import User
from starlette import status

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# ---------------- REGISTER ----------------
@router.post("/register")
def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Проверяем, есть ли уже такой пользователь
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return {"error": "Email already registered"}

    hashed_password = get_password_hash(password)
    user = User(email=email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    # ✅ устанавливаем cookie (сохраняем ID пользователя)
    response = RedirectResponse(url="/setup-profile", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="user_id", value=str(user.id))
    return response


# ---------------- LOGIN ----------------
@router.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        return {"error": "Invalid email or password"}

    # ✅ создаём cookie
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="user_id", value=str(user.id))
    return response


# ---------------- LOGOUT ----------------
@router.get("/logout")
def logout_user():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("user_id")
    return response
