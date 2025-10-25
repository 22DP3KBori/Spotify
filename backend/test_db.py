from backend.database import Base, engine
from backend import models  # обязательно импортируем, чтобы SQLAlchemy «увидел» все классы моделей

print("🛠 Creating all database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully.")
