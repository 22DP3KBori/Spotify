from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.core.templates import templates, current_user
from backend.models import User
from fastapi import UploadFile, File, HTTPException
import os
import shutil

router = APIRouter(prefix="/profile", tags=["Avatar"])

@router.get("/customize", response_class=HTMLResponse)
def customize_avatar_page(request: Request, db: Session = Depends(get_db)):
    user = current_user(request)
    if not user:
        return RedirectResponse("/auth")
    db_user = db.query(User).filter(User.id == user.id).first()
    return templates.TemplateResponse("avatar_settings.html", {"request": request, "user": db_user})

AVATAR_DIR = "backend/static/avatars"

@router.post("/upload-avatar")
async def upload_avatar(request: Request, avatar: UploadFile = File(...), db: Session = Depends(get_db)):
    user = current_user(request)
    if not user:
        raise HTTPException(401, "Unauthorized")

    os.makedirs(AVATAR_DIR, exist_ok=True)
    filename = f"{user.id}_{avatar.filename}"
    path = os.path.join(AVATAR_DIR, filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(avatar.file, buffer)

    db_user = db.query(User).filter(User.id == user.id).first()
    db_user.avatar = f"/static/avatars/{filename}"
    db.commit()

    return {"success": True}


