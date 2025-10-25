from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import shutil
import os

from backend.database import get_db
from backend.models import User
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

UPLOAD_DIR = "backend/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# 📄 Отображение страницы с формой
@router.get("/setup-profile")
def setup_profile_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        # если не вошёл — на логин
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("setup_profile.html", {"request": request, "user": user})


# 📤 Сохранение профиля
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
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Сохраняем аватар, если загружен
    avatar_path = user.avatar
    if avatar and avatar.filename:
        file_location = os.path.join(UPLOAD_DIR, avatar.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
        avatar_path = f"/static/uploads/{avatar.filename}"

    # Обновляем данные пользователя
    user.first_name = first_name
    user.last_name = last_name
    user.nickname = nickname
    user.country = country
    user.dob = dob
    user.category = category
    user.avatar = avatar_path

    db.commit()
    db.refresh(user)

    # После сохранения → переход на главную
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return response
