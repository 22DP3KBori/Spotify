from datetime import date, datetime, timedelta
from pathlib import Path
import uuid, random

from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, EmailVerificationCode, UserFrame
from backend.routers.country_list import countries
from backend.core.templates import templates
from backend.core.auth import current_user
from backend.services.email_service import send_email
from sqlalchemy.orm import joinedload


router = APIRouter()

AVATAR_DIR = Path("backend/static/avatars")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)


# ✅ Сохранение профиля после Google регистрации
@router.post("/save-profile")
async def save_profile(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    nickname: str = Form(...),
    country: str = Form(...),
    dob: str = Form(...),
    category: list[str] = Form(...),
    avatar: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse("/login")

    # ✅ Возраст
    today = date.today()
    birth = datetime.strptime(dob, "%Y-%m-%d").date()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

    if age < 12:
        return templates.TemplateResponse("setup_profile.html", {
            "request": request, "error": "Are you serious right now bruh?",
            "countries": countries
        })

    # ✅ Обновляем данные
    user.first_name = first_name
    user.last_name = last_name
    user.nickname = nickname
    user.country = country
    user.dob = dob
    user.category = ",".join(category)
    user.profile_completed = True

    # ✅ Если аватар не загружен — ставим дефолт
    if (not avatar) or (not avatar.filename) or (not avatar.filename.strip()):
        user.avatar = "/static/avatars/default.png"

    # ✅ Сохраняем аватар
    if avatar is not None and avatar.filename and avatar.filename.strip():
        data = await avatar.read()
        if data:
            ext = Path(avatar.filename).suffix or ".png"
            filename = f"user_{user.id}_{uuid.uuid4().hex}{ext}"
            file_path = AVATAR_DIR / filename

            with open(file_path, "wb") as f:
                f.write(data)

            user.avatar = f"/static/avatars/{filename}"

    db.commit()

    # ✅ Остаёмся в той же сессии, refresh не нужен

    response = RedirectResponse("/", status_code=302)
    response.set_cookie("user_id", str(user.id))
    return response


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

    # ✅ Сохраняем аватар
    if avatar is not None and avatar.filename and avatar.filename.strip():
        data = await avatar.read()
        if data:
            ext = Path(avatar.filename).suffix or ".png"
            filename = f"user_{user.id}_{uuid.uuid4().hex}{ext}"
            file_path = AVATAR_DIR / filename

            with open(file_path, "wb") as f:
                f.write(data)

            user.avatar = f"/static/avatars/{filename}"

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

    db.add(EmailVerificationCode(
        user_id=user.id, code=code, email=new_email, expires_at=expires
    ))
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


"""@router.get("/profile/customize", response_class=HTMLResponse)
def avatar_settings(
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse("/auth")

    # ✅ повторно загружаем юзера внутри активной сессии
    user_db = (
        db.query(User)
        .options(
            joinedload(User.frames).joinedload(UserFrame.frame),          # рамки
            joinedload(User.inventory).joinedload(UserInventory.theme),   # темы
        )
        .filter(User.id == user.id)
        .first()
    )

    if not user_db:
        raise HTTPException(404, "User not found")

    # ✅ Собираем купленные темы
    owned_themes = []
    for item in user_db.inventory:
        if item.theme_id:
            owned_themes.append({
                "id": item.theme.id,
                "name": item.theme.name,
                "preview": item.theme.preview_image,
                "css_class": item.theme.css_class,
                "equipped": item.equipped,
            })

    return templates.TemplateResponse(
        "avatar_settings.html",
        {
            "request": request,
            "user": user_db,  # важный момент — пользователь привязан к сессии
            "themes": owned_themes
        }
    )"""