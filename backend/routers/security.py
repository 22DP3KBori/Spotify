from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, EmailVerificationCode
from backend.core.templates import templates
import random
from datetime import datetime, timedelta
from backend.core.auth import current_user
from backend.services.email_service import send_email

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 📍 Страница безопасности
@router.get("/account-security")
def account_security(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/auth")
    return templates.TemplateResponse("account_security.html", {"request": request})


@router.post("/change-email")
async def change_email(
    request: Request,
    new_email: str = Form(...),
    current_password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = current_user(request)
    if not user:
        return RedirectResponse("/auth")

    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # ✅ Проверка пароля
    if not pwd_context.verify(current_password, user.password):
        return templates.TemplateResponse(
            "account_security.html",
            {
                "request": request,
                "message": {"type": "error", "text": "❌ Wrong password!"}
            }
        )

    # ✅ Email уже занят?
    existing = db.query(User).filter(User.email == new_email).first()
    if existing:
        return templates.TemplateResponse(
            "account_security.html",
            {
                "request": request,
                "message": {"type": "error", "text": "⚠️ Email already in use!"}
            }
        )

    # ✅ Генерация и отправка кода
    code = str(random.randint(100000, 999999))
    expires = datetime.now() + timedelta(minutes=10)

    db_code = EmailVerificationCode(user_id=user.id, code=code, email=new_email, expires_at=expires)
    db.add(db_code)
    db.commit()

    print("📧 Sending code to:", new_email, "CODE:", code)
    send_email(new_email, "Email Change Verification", f"Your code: {code}")


    return templates.TemplateResponse(
        "verify_email.html",
        {
            "request": request,
            "email": new_email,
            "message": {"type": "success", "text": "✅ Code sent to your email!"}
        }
    )




@router.post("/change-password")
def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()

    if not pwd_context.verify(current_password, user.password):
        return templates.TemplateResponse(
            "account_security.html",
            {"request": request, "user": user, "message": {"type": "error", "text": "❌ Wrong current password"}}
        )

    if new_password != confirm_password:
        return templates.TemplateResponse(
            "account_security.html",
            {"request": request, "user": user, "message": {"type": "error", "text": "⚠️ Passwords do not match"}}
        )

    user.password = pwd_context.hash(new_password)
    db.commit()

    return templates.TemplateResponse(
        "account_security.html",
        {"request": request, "user": user, "message": {"type": "success", "text": "✅ Password changed successfully!"}}
    )
