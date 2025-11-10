from dotenv import load_dotenv
import os
from starlette.middleware.sessions import SessionMiddleware

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

print("ENV LOADED:", env_path)
print("MAILGUN_API_KEY =", os.getenv("MAILGUN_API_KEY"))



from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from contextlib import asynccontextmanager
from threading import Thread
from datetime import datetime, timedelta
import time

# Project imports
from backend.database import get_db, SessionLocal
from backend.models import User, Tournament, UserFrame
from backend.routers import profile
from backend.routers.country_list import countries

# ---------------------- TEMPLATES ----------------------
from backend.core.templates import templates, current_user
from backend.core.auth import current_user

# ---------------------- JINJA FILTERS ----------------------
def get_flag(country_name: str):
    for c in countries:
        if c["name"] == country_name:
            return c["flag"]
    return ""
    
templates.env.filters["flag"] = get_flag

# ---------------------- Remove unfinished profiles after 24h ----------------------
def delete_incomplete_users():
    while True:
        time.sleep(3600)
        db = next(get_db())
        cutoff = datetime.now() - timedelta(hours=24)

        db.query(User).filter(
            User.profile_completed == False,
            User.created_at < cutoff
        ).delete()

        db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Thread(target=delete_incomplete_users, daemon=True).start()
    yield

# ---------------------- FastAPI App ----------------------
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "supersecretkey123"),  # замени на свой ключ
    same_site="lax",
    max_age=86400 * 7,  # 7 дней
)

app.include_router(profile.router)

# ✅ make current_user available to ALL Jinja templates (но только после include_router!)
templates.env.globals["current_user"] = current_user


app.mount("/static", StaticFiles(directory="backend/static"), name="static")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

WHITELIST = {
    "/auth", "/register", "/login",
    "/setup-profile", "/save-profile",
    "/static", "/check-nickname",
}

# ---------------------- Middleware ----------------------
def path_in_whitelist(path: str) -> bool:
    return any(path.startswith(p) for p in WHITELIST)

@app.middleware("http")
async def enforce_profile_completion(request: Request, call_next):
    if request.url.path.startswith("/static"):
        return await call_next(request)

    user_id = request.cookies.get("user_id")
    if not user_id:
        return await call_next(request)

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user:    
            db.refresh(user)  # ✅ получаем актуальные данные
        if user and user.profile_completed != True:
            if not path_in_whitelist(request.url.path):
                return RedirectResponse("/setup-profile")
    finally:
        db.close()

    return await call_next(request)

# ---------------------- Routes ----------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    tournaments = db.query(Tournament).filter(Tournament.is_active == True).all()
    user = current_user(request)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "tournaments": tournaments, "user": user},
    )

@app.get("/auth", response_class=HTMLResponse)
def auth_page(request: Request):
    return templates.TemplateResponse("register_login.html", {"request": request})

@app.get("/setup-profile", response_class=HTMLResponse)
def setup_profile_page(request: Request):
    return templates.TemplateResponse("setup_profile.html", {"request": request, "countries": countries})

@app.post("/register")
def register(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email already registered")

    new_user = User(email=email, password=pwd_context.hash(password))
    db.add(new_user)
    db.commit()

    response = RedirectResponse("/setup-profile", status_code=303)
    response.set_cookie("user_id", str(new_user.id))
    return response

@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(400, "Invalid email or password")

    response = RedirectResponse("/", status_code=303)
    response.set_cookie("user_id", str(user.id))
    return response

@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("user_id")
    return response

# ---------------------- Profile page ----------------------
from sqlalchemy.orm import joinedload

@app.get("/profile")
def profile_page(request: Request, db: Session = Depends(get_db)):
    user_cookie = current_user(request)
    if not user_cookie:
        return RedirectResponse("/auth")

    # Загружаем пользователя с рамками
    user = db.query(User)\
        .options(joinedload(User.frames).joinedload(UserFrame.frame))\
        .filter(User.id == user_cookie.id)\
        .first()

    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user}
    )


# ---------------------- Edit profile page ✅ ----------------------
@app.get("/edit-profile")
def edit_profile_page(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/auth")

    return templates.TemplateResponse(
        "edit_profile.html",
        {"request": request, "user": user, "countries": countries}
    )

# ---------------------- Security routes ----------------------
from backend.routers import security
app.include_router(security.router)

#---------------------- Economy routes ----------------------
from backend.routers import economy
app.include_router(economy.router)

#---------------------- Frames routes ----------------------
from backend.routers import frames
app.include_router(frames.router)

#---------------------- Avatar settings routes ----------------------
from backend.routers import avatar_settings
app.include_router(avatar_settings.router)

