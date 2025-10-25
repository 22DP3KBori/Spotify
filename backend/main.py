from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Импорты из проекта
from backend.database import get_db
from backend.models import User, Tournament
from backend.routers import profile

app = FastAPI()

app.include_router(profile.router)


# Настройка шрифтов, папок и шаблонов
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

# Шифрование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------- ГЛАВНАЯ ----------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    user = None
    user_id = request.cookies.get("user_id")
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()

    tournaments = db.query(Tournament).filter(Tournament.is_active == True).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "tournaments": tournaments, "user": user},
    )


# ---------------------- СТРАНИЦА LOGIN / REGISTER ----------------------
@app.get("/auth", response_class=HTMLResponse)
def auth_page(request: Request):
    return templates.TemplateResponse("register_login.html", {"request": request})


# ---------------------- СТРАНИЦА ЗАПОЛНЕНИЯ ПРОФИЛЯ ----------------------
@app.get("/setup-profile", response_class=HTMLResponse)
def setup_profile_page(request: Request):
    return templates.TemplateResponse("setup_profile.html", {"request": request})


# ---------------------- РЕГИСТРАЦИЯ ----------------------
@app.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(password)
    new_user = User(email=email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ✅ создаем cookie-сессию
    response = RedirectResponse(url="/setup-profile", status_code=303)
    response.set_cookie(key="user_id", value=str(new_user.id))
    return response


# ---------------------- ЛОГИН ----------------------
@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # ✅ создаем cookie-сессию
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id))
    return response


# ---------------------- ВЫХОД ----------------------
@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_id")
    return response
