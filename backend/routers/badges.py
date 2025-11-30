from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.core.auth import current_user
from backend.models import ProfileBadge, UserBadge, User, ProfileFrame
from backend.core.templates import templates

router = APIRouter(prefix="/badges", tags=["Badges"])


# ----------------------------
#  INIT DEFAULT BADGES
# ----------------------------
@router.post("/init")
def init_badges(db: Session = Depends(get_db)):
    badges_data = [
        {"name": "Bronze Medal",  "price": 50,     "description": "Этот значок можно купить в магазине. Стоимость — 50 монет.",    "icon_url": "/static/badges/badge_50.png"},
        {"name": "Silver Medal",  "price": 100,    "description": "Этот значок можно купить в магазине. Стоимость — 100 монет.",   "icon_url": "/static/badges/badge_100.png"},
        {"name": "Speed Runner",  "price": 250,    "description": "Этот значок можно купить в магазине. Стоимость — 250 монет.",   "icon_url": "/static/badges/badge_250.png"},
        {"name": "Pro Athlete",   "price": 500,    "description": "Этот значок можно купить в магазине. Стоимость — 500 монет.",   "icon_url": "/static/badges/badge_500.png"},
        {"name": "Champion",      "price": 2000,   "description": "Этот значок можно купить в магазине. Стоимость — 2000 монет.",  "icon_url": "/static/badges/badge_2000.png"},
        {"name": "Elite Medal",   "price": 5000,   "description": "Этот значок можно купить в магазине. Стоимость — 5000 монет.",  "icon_url": "/static/badges/badge_5000.png"},
        {"name": "Legend Trophy", "price": 10000,  "description": "Этот значок можно купить в магазине. Стоимость — 10000 монет.", "icon_url": "/static/badges/badge_10000.png"},
        {"name": "Mythic Glory",  "price": 50000,  "description": "Этот значок можно купить в магазине. Стоимость — 50000 монет.", "icon_url": "/static/badges/badge_50000.png"},
    ]

    added = 0
    for b in badges_data:
        exists = db.query(ProfileBadge).filter_by(name=b["name"]).first()
        if not exists:
            db.add(ProfileBadge(**b))
            added += 1

    db.commit()
    return {"success": True, "added": added}


# ----------------------------
#  LIST ALL BADGES (for store)
# ----------------------------
@router.get("/list")
def list_badges(db: Session = Depends(get_db)):
    return db.query(ProfileBadge).all()


# ----------------------------
#  BUY BADGE (main store logic)
# ----------------------------
@router.post("/buy/{badge_id}")
def buy_badge(
    badge_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db)
):
    badge = db.query(ProfileBadge).filter_by(id=badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")

    # Уже куплено?
    owned = db.query(UserBadge).filter_by(user_id=user.id, badge_id=badge_id).first()
    if owned:
        raise HTTPException(status_code=400, detail="You already own this badge")

    # Хватает монет?
    if user.coins < badge.price:
        raise HTTPException(status_code=400, detail="Not enough coins")

    # списываем монеты
    user.coins -= badge.price

    db.add(UserBadge(user_id=user.id, badge_id=badge.id))
    db.commit()

    return {"success": True, "coins": user.coins}


# ----------------------------
#  GET USER BADGES
# ----------------------------
@router.get("/user")
def get_user_badges(
    user: User = Depends(current_user),
    db: Session = Depends(get_db)
):
    badges = (
        db.query(UserBadge)
        .filter_by(user_id=user.id)
        .all()
    )

    return {"success": True, "badges": badges}


from backend.models import ProfileBadge, UserBadge

@router.get("/store")
def store_page(request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):

    frames = db.query(ProfileFrame).all()

    badges = db.query(ProfileBadge).all()  # ← ДОБАВИЛИ

    owned_frames = [f.frame_id for f in user.frames]
    owned_badges = [b.badge_id for b in user.badges]   # ← ДОБАВИЛИ

    return templates.TemplateResponse(
        "store.html",
        {
            "request": request,
            "user": user,
            "frames": frames,
            "badges": badges,            # ← ПЕРЕДАЧА
            "owned_frames": owned_frames,
            "owned_badges": owned_badges,  # ← ПЕРЕДАЧА
        }
    )


@router.post("/equip-badge/{badge_id}")
def equip_badge(badge_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):

    user_db = db.query(User).filter(User.id == user.id).first()

    owned = db.query(UserBadge).filter_by(user_id=user_db.id, badge_id=badge_id).first()
    if not owned:
        raise HTTPException(400, "Badge not owned")

    try:
        # снять все значки
        db.query(UserBadge).filter(UserBadge.user_id == user_db.id).update({"equipped": False})

        # надеть выбранный
        owned.equipped = True
        db.commit()
    except:
        db.rollback()
        raise

    return {"success": True}

@router.post("/unequip-badge/{badge_id}")
def unequip_badge(badge_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):

    owned = db.query(UserBadge).filter_by(user_id=user.id, badge_id=badge_id).first()
    if not owned:
        raise HTTPException(400, "Badge not owned")

    owned.equipped = False
    db.commit()

    return {"success": True}

