from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.core.auth import current_user
from backend.models import ProfileFrame
from sqlalchemy.orm import joinedload
from backend.core.templates import templates
from backend.models import UserFrame
from fastapi import HTTPException


router = APIRouter()

# ✅ Выдать тестовые монеты игроку
@router.post("/give-coins/{amount}")
def give_coins(amount: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request)
    if not user:
        return RedirectResponse("/auth")

    if amount <= 0:
        return JSONResponse({"error": "Amount must be positive"}, status_code=400)

    user.coins += amount
    db.commit()
    db.refresh(user)  # ОБЯЗАТЕЛЬНО!
    return {"success": True, "new_balance": user.coins}


# ✅ Получить текущий баланс
@router.get("/coins")
def get_balance(request: Request, db: Session = Depends(get_db)):
    user = current_user(request)
    if not user:
        return JSONResponse({"coins": 0})

    return {"coins": user.coins}


@router.get("/store", response_class=HTMLResponse)
def store_page(request: Request, db: Session = Depends(get_db)):
    user = current_user(request)
    if not user:
        return RedirectResponse("/auth")

    frames = db.query(ProfileFrame).all()
    owned = db.query(UserFrame.frame_id).filter(UserFrame.user_id == user.id).all()
    owned_ids = [f[0] for f in owned]

    equipped = db.query(UserFrame).filter(UserFrame.user_id == user.id, UserFrame.equipped == True).first()
    equipped_id = equipped.frame_id if equipped else None

    return templates.TemplateResponse(
        "custom_store.html",
        {
            "request": request,
            "frames": frames,
            "owned_frames": owned_ids,
            "equipped_frame_id": equipped_id,
            "user": user
        },
    )



@router.get("/init-frames")
def init_frames(db: Session = Depends(get_db)):
    frames_data = [
        {"name": "Gold", "image_url": "/static/frames/gold_frame.png", "price": 500},
        {"name": "Silver", "image_url": "/static/frames/silver_frame.png", "price": 400},
        {"name": "Bronze", "image_url": "/static/frames/bronze_frame.png", "price": 300},
        {"name": "Neon", "image_url": "/static/frames/neon_frame.png", "price": 600},
        {"name": "Fire", "image_url": "/static/frames/fire_frame.png", "price": 700},
        {"name": "Ice", "image_url": "/static/frames/ice_frame.png", "price": 700},
    ]

    added = 0
    for frame in frames_data:
        exists = db.query(ProfileFrame).filter_by(name=frame["name"]).first()
        if not exists:
            new_frame = ProfileFrame(**frame)
            db.add(new_frame)
            added += 1

    db.commit()
    return {"success": True, "added": added}


@router.post("/frames/buy/{frame_id}")
def buy_frame(frame_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.id == user_id).first()
    frame = db.query(ProfileFrame).filter(ProfileFrame.id == frame_id).first()

    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found")

    # Проверяем, не купил ли уже
    owned = db.query(UserFrame).filter_by(user_id=user.id, frame_id=frame.id).first()
    if owned:
        raise HTTPException(status_code=400, detail="Already owned")

    # Проверяем монеты
    if user.coins < frame.price:
        raise HTTPException(status_code=400, detail="Not enough coins")

    # Совершаем покупку
    user.coins -= frame.price
    new_ownership = UserFrame(user_id=user.id, frame_id=frame.id)
    db.add(new_ownership)
    db.commit()

    return {"success": True, "coins_left": user.coins, "frame": frame.name}