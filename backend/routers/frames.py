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
@router.get("/", response_class=HTMLResponse)
def list_frames(request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    frames = db.query(ProfileFrame).order_by(ProfileFrame.price.asc()).all()

    return templates.TemplateResponse(
        "custom_store.html",
        {
            "request": request,
            "frames": frames,
            "user": user
        }
    )



@router.post("/equip/{frame_id}")
def equip_frame(
    frame_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(current_user)
):
    user_frame = db.query(UserFrame).filter_by(
        user_id=user.id,
        frame_id=frame_id
    ).first()

    if not user_frame:
        raise HTTPException(status_code=400, detail="Frame not owned")

    # Unequip all in 1 atomic operation
    db.query(UserFrame).filter(
        UserFrame.user_id == user.id,
        UserFrame.equipped == True
    ).update({"equipped": False})

    user_frame.equipped = True
    db.commit()

    return {"success": True}



