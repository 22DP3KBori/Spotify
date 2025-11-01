from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="backend/templates")

from fastapi.templating import Jinja2Templates
from backend.database import SessionLocal
from backend.models import User


def current_user(request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    return user

templates.env.globals["current_user"] = current_user
