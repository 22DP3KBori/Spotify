from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.core.auth import current_user
from backend.models import User, ProfileFrame, UserFrame
from fastapi.responses import HTMLResponse
from backend.core.templates import templates
from fastapi.responses import RedirectResponse  

router = APIRouter(prefix="/frames", tags=["Frames"])

# Get store page data
@router.get("/")
def list_frames(request: Request, db: Session = Depends(get_db)):
    user = current_user(request)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    frames = db.query(ProfileFrame).all()

    return {"frames": frames, "user": user}


@router.post("/equip/{frame_id}")
def equip_frame(frame_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_frame = db.query(UserFrame).filter(
        UserFrame.user_id == user.id,
        UserFrame.frame_id == frame_id
    ).first()

    if not user_frame:
        raise HTTPException(status_code=400, detail="Frame not owned")

    # Unequip all
    db.query(UserFrame).filter(UserFrame.user_id == user.id).update({"equipped": False})

    # Equip this one
    user_frame.equipped = True
    db.commit()

    return {"success": True, "message": "Frame equipped successfully"}


