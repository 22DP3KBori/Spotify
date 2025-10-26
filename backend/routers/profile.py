from datetime import datetime, date
from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import shutil
import os
import re

from backend.database import get_db
from backend.models import User
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

UPLOAD_DIR = "backend/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/setup-profile")
def setup_profile_page(request: Request):
    return templates.TemplateResponse("setup_profile.html", {"request": request})


@router.post("/save-profile")
async def save_profile(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    nickname: str = Form(...),
    country: str = Form(...),
    dob: str = Form(...),
    category: str = Form(...),
    avatar: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    errors = {}

    # === Проверка имени ===
    if not re.match(r"^[A-Za-zА-Яа-яЁё]{3,30}$", first_name.strip()):
        errors["first_name_error"] = "Invalid first name — only letters, 3–30 characters."

    # === Проверка фамилии ===
    if not re.match(r"^[A-Za-zА-Яа-яЁё]{3,30}$", last_name.strip()):
        errors["last_name_error"] = "Invalid last name — only letters, 3–30 characters."

    # === Проверка других полей ===
    if not all([first_name.strip(), last_name.strip(), nickname.strip(), country.strip(), dob.strip(), category.strip()]):
        errors["general_error"] = "⚠️ Please fill in all required fields."

    # === Проверка даты рождения ===
    try:
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
        today = date.today()
        if dob_date.year < 1900 or dob_date > today:
            errors["dob_error"] = "Are you serious right now bruh?"
    except ValueError:
        errors["dob_error"] = "Are you serious right now bruh?"

    # Если есть ошибки — вернуть страницу обратно с подсветкой
    if errors:
        return templates.TemplateResponse(
            "setup_profile.html",
            {"request": request, **errors},
            status_code=400,
        )

    # === Получаем пользователя ===
    user = db.query(User).order_by(User.id.desc()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # === Обработка фото ===
    avatar_path = None
    if avatar and avatar.filename:
        filename = os.path.basename(avatar.filename)
        file_location = os.path.join(UPLOAD_DIR, filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
        avatar_path = f"/static/uploads/{filename}"

    # === Сохраняем ===
    user.first_name = first_name
    user.last_name = last_name
    user.nickname = nickname
    user.country = country
    user.dob = dob
    user.category = category
    user.avatar = avatar_path

    db.commit()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


# Проверка доступности nickname

from fastapi import Query
from fastapi.responses import JSONResponse

@router.get("/check-nickname")
def check_nickname(nickname: str = Query(...), db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.nickname == nickname).first()
    if existing:
        return JSONResponse({"available": False})
    return JSONResponse({"available": True})
