from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, ProfileFrame, UserFrame, ProfileBadge, UserBadge
from backend.core.auth import current_user
from backend.core.templates import templates
from sqlalchemy.orm import joinedload


router = APIRouter(prefix="/store", tags=["Store"])


# ✅ Выдать монеты (ТОЛЬКО ADMIN)
@router.post("/give-coins/{amount}")
def give_coins(
    amount: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db)
):
    if user.role_id != 1:  # предполагается id=1 => admin
        raise HTTPException(status_code=403, detail="Admin access required")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    try:
        user.coins += amount
        db.commit()
    except:
        db.rollback()
        raise

    return {"success": True, "new_balance": user.coins}


# ✅ Получение баланса
@router.get("/coins")
def get_balance(user: User = Depends(current_user)):
    return {"coins": user.coins}


@router.get("/", response_class=HTMLResponse)
def store_page(
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db)
):

    # Загружаем пользователя с заранее подгруженными:
    # - рамками
    # - значками
    user_db = (
        db.query(User)
        .options(
            joinedload(User.frames),        # user.frames
            joinedload(User.badges)         # user.badges
        )
        .filter(User.id == user.id)
        .first()
    )

    # Данные рамок
    frames = db.query(ProfileFrame).order_by(ProfileFrame.price.asc()).all()
    owned_frames = [uf.frame_id for uf in user_db.frames]

    # Данные значков
    badges = db.query(ProfileBadge).all()
    owned_badges = [ub.badge_id for ub in user_db.badges]

    # Кто сейчас экипирован
    equipped = (
        db.query(UserFrame)
        .filter(UserFrame.user_id == user.id, UserFrame.equipped == True)
        .first()
    )
    equipped_id = equipped.frame_id if equipped else None

    return templates.TemplateResponse(
        "custom_store.html",
        {
            "request": request,
            "frames": frames,
            "badges": badges,
            "owned_frames": owned_frames,
            "owned_badges": owned_badges,
            "equipped_frame_id": equipped_id,
            "user": user_db,   # <-- ВАЖНО: теперь используем user_db
        },
    )



# ✅ Инициализация рамок (ТОЛЬКО ADMIN)
@router.post("/init-frames")
def init_frames(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role_id != 1:
        raise HTTPException(status_code=403, detail="Admin access required")

    frames_data = [
        {"name": "Gold", "image_url": "/static/frames/gold_frame.png", "price": 500},
        {"name": "Silver", "image_url": "/static/frames/silver_frame.png", "price": 400},
        {"name": "Bronze", "image_url": "/static/frames/bronze_frame.png", "price": 300},
        {"name": "Neon", "image_url": "/static/frames/neon_frame.png", "price": 600},
        {"name": "Fire", "image_url": "/static/frames/fire_frame.png", "price": 700},
        {"name": "Ice", "image_url": "/static/frames/ice_frame.png", "price": 700},
    ]

    added = 0
    try:
        for frame in frames_data:
            exists = db.query(ProfileFrame).filter_by(name=frame["name"]).first()
            if not exists:
                db.add(ProfileFrame(**frame))
                added += 1

        db.commit()
    except:
        db.rollback()
        raise

    return {"success": True, "added": added}


@router.post("/buy-frame/{frame_id}")
def buy_frame(
    frame_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    # Всегда достаём ORM-модель из базы!
    user_db = db.query(User).filter(User.id == user.id).first()
    if not user_db:
        raise HTTPException(404, "User not found")

    frame = db.query(ProfileFrame).filter_by(id=frame_id).first()
    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found")

    owned = db.query(UserFrame).filter_by(user_id=user_db.id, frame_id=frame.id).first()
    if owned:
        raise HTTPException(status_code=400, detail="You already own this frame")

    if user_db.coins < frame.price:
        raise HTTPException(status_code=400, detail="Not enough coins")

    user_db.coins -= frame.price
    db.add(UserFrame(user_id=user_db.id, frame_id=frame.id))
    db.commit()
    db.refresh(user_db)

    return {"success": True, "coins_left": user_db.coins}



@router.post("/buy-badge/{badge_id}")
def buy_badge(
    badge_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db)
):
    user_db = db.query(User).filter(User.id == user.id).first()

    badge = db.query(ProfileBadge).filter_by(id=badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")

    owned = db.query(UserBadge).filter_by(user_id=user_db.id, badge_id=badge.id).first()
    if owned:
        raise HTTPException(status_code=400, detail="You already own this badge")

    if user_db.coins < badge.price:
        raise HTTPException(status_code=400, detail="Not enough coins")

    user_db.coins -= badge.price
    db.add(UserBadge(user_id=user_db.id, badge_id=badge.id))
    db.commit()
    db.refresh(user_db)

    return {"success": True, "coins_left": user_db.coins}




# ✅ Экипировка рамки
@router.post("/equip-frame/{frame_id}")
def equip_frame(
    frame_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db)
):
    owned_frame = db.query(UserFrame).filter_by(
        user_id=user.id,
        frame_id=frame_id
    ).first()

    if not owned_frame:
        raise HTTPException(status_code=400, detail="Frame not owned")

    try:
        # снять все рамки
        db.query(UserFrame).filter(UserFrame.user_id == user.id).update({"equipped": False})

        # экипировать выбранную
        owned_frame.equipped = True
        db.commit()
    except:
        db.rollback()
        raise

    return {"success": True, "message": "Frame equipped successfully"}


"""@router.post("/buy-theme/{theme_id}")
def buy_theme(
    theme_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    # получаем ID через current_user
    user = current_user(request)

    user_db = db.query(User).filter(User.id == user.id).first()
    if not user_db:
        raise HTTPException(401, "User not found")

    theme = db.query(ProfileTheme).filter_by(id=theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    owned = db.query(UserInventory).filter_by(user_id=user_db.id, theme_id=theme.id).first()
    if owned:
        raise HTTPException(status_code=400, detail="You already own this theme")

    if user_db.coins < theme.price:
        raise HTTPException(status_code=400, detail="Not enough coins")

    try:
        user_db.coins -= theme.price
        db.add(UserInventory(user_id=user_db.id, theme_id=theme.id))
        db.commit()
        db.refresh(user_db)
    except:
        db.rollback()
        raise

    return {"success": True, "coins_left": user_db.coins, "theme": theme.name}"""



"""@router.post("/equip-theme/{theme_id}")
def equip_theme(
    theme_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    # Если theme_id == 0 → снять активную тему
    if theme_id == 0:
        try:
            user.active_theme = None
            db.commit()
            return {"success": True, "message": "Theme unequipped"}
        except:
            db.rollback()
            raise

    # Проверить владение темой
    owned = db.query(UserInventory).filter_by(
        user_id=user.id,
        theme_id=theme_id
    ).first()

    if not owned:
        raise HTTPException(
            status_code=400,
            detail="Theme not owned"
        )

    try:
        # Установить тему пользователю
        user.active_theme = theme_id
        db.commit()

    except:
        db.rollback()
        raise

    return {"success": True, "message": "Theme equipped"}


"""