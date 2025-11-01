from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
import shutil, os, random

from backend.database import get_db
from backend.models import User, EmailVerificationCode
from backend.routers.country_list import countries
from backend.core.templates import templates
from backend.core.auth import current_user
from backend.services.email_service import send_email  # ✅ правильный импорт

router = APIRouter()

UPLOAD_DIR = "backend/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ✅ Страница редактирования профиля
@router.get("/edit-profile")
def edit_profile_page(request: Request, db: Session = Depends(get_db)):
    user = current_user(request)
    if not user:
        return RedirectResponse("/auth")

    return templates.TemplateResponse(
        "edit_profile.html",
        {"request": request, "user": user, "countries": countries}
    )


# ✅ Обновление профиля
@router.post("/edit-profile")
async def edit_profile(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    nickname: str = Form(...),
    country: str = Form(...),
    dob: str = Form(...),
    category: list[str] = Form([]),
    avatar: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    user = current_user(request)

    # Validate DOB
    try:
        birth = datetime.strptime(dob, "%Y-%m-%d")
        age = (datetime.now() - birth).days // 365
        if age < 5 or age > 100:
            raise ValueError
    except:
        return templates.TemplateResponse(
            "edit_profile.html",
            {
                "request": request, "user": user, "countries": countries,
                "message": {"type": "error", "text": "⚠️ Age must be between 5 and 100"}
            },
            status_code=400
        )

    # Save avatar
    if avatar and avatar.filename:
        file_location = os.path.join(UPLOAD_DIR, avatar.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
        user.avatar = f"/static/uploads/{avatar.filename}"

    user.first_name = first_name
    user.last_name = last_name
    user.nickname = nickname
    user.country = country
    user.dob = dob
    user.category = ",".join(category)

    db.commit()

    return templates.TemplateResponse(
        "edit_profile.html",
        {
            "request": request, "user": user, "countries": countries,
            "message": {"type": "success", "text": "✅ Profile updated!"}
        }
    )


# ✅ Отправка кода на email
@router.post("/send-email-code")
async def send_email_code(new_email: str = Form(...), request: Request = None, db: Session = Depends(get_db)):
    user = current_user(request)
    if not user:
        return RedirectResponse("/auth")

    code = str(random.randint(100000, 999999))
    expires = datetime.now() + timedelta(minutes=10)

    db_code = EmailVerificationCode(
        user_id=user.id,
        code=code,
        email=new_email,
        expires_at=expires
    )
    db.add(db_code)
    db.commit()

    send_email(new_email, "Verification Code", f"Your code: {code}")

    return {"success": True, "message": "Verification code sent!"}


# ✅ Подтверждение email
@router.post("/verify-email-code")
async def verify_email_code(code: str = Form(...), request: Request = None, db: Session = Depends(get_db)):
    user = current_user(request)

    db_code = db.query(EmailVerificationCode).filter(
        EmailVerificationCode.user_id == user.id,
        EmailVerificationCode.code == code
    ).first()

    if not db_code or db_code.expires_at < datetime.now():
        return {"error": "Invalid or expired code"}

    user.email = db_code.email
    db.delete(db_code)
    db.commit()

    return {"success": True}


# ✅ Проверка никнейма
@router.get("/check-nickname")
def check_nickname(nickname: str = Query(...), db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.nickname == nickname).first()
    return {"available": not bool(exists)}
