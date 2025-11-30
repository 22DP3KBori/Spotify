from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Boolean,
    Table,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from backend.database import Base

# -----------------------------------------------------
# Таблица связей: команды участвуют в турнирах
# -----------------------------------------------------
tournament_participants = Table(
    "tournament_participants",
    Base.metadata,
    Column("team_id", ForeignKey("teams.id"), primary_key=True),
    Column("tournament_id", ForeignKey("tournaments.id"), primary_key=True),
)

# -----------------------------------------------------
# Роли пользователей
# -----------------------------------------------------
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    # связь с пользователями
    users = relationship("User", back_populates="role")


# -----------------------------------------------------
# Пользователи
# -----------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    nickname = Column(String(100))
    country = Column(String(100))
    dob = Column(String(20))
    category = Column(String(50))
    avatar = Column(String(255))
    is_active = Column(Boolean, default=True)
    profile_completed = Column(Boolean, nullable=False, default=False)
    coins = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    #active_theme = Column(Integer, ForeignKey("profile_themes.id"), nullable=True)


    # 🔹 связь с ролью
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    
    # 🔹 обратные связи
    teams = relationship("Team", back_populates="creator")
    tournaments = relationship("Tournament", back_populates="creator")
    comments = relationship("Comment", back_populates="user")
    #theme = relationship("ProfileTheme")
   # active_theme_rel = relationship("ProfileTheme", foreign_keys=[active_theme])
    #themes = relationship("UserTheme", back_populates="user", cascade="all, delete-orphan")
    #inventory = relationship("UserInventory", backref="user")

# -----------------------------------------------------
# Команды
# -----------------------------------------------------
class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="teams")
    tournaments = relationship(
        "Tournament",
        secondary=tournament_participants,
        back_populates="teams",
    )
    matches_as_team1 = relationship(
        "Match", foreign_keys="[Match.team1_id]", back_populates="team1"
    )
    matches_as_team2 = relationship(
        "Match", foreign_keys="[Match.team2_id]", back_populates="team2"
    )


# -----------------------------------------------------
# Турниры
# -----------------------------------------------------
class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    discipline = Column(String(50), nullable=False, default="Unknown")  # <-- ДОБАВИМ ЭТО
    format = Column(String(50), nullable=False)  # single_elim, double_elim, swiss...
    team_count = Column(Integer, default=0)
    status = Column(String(30), default="Planned")  # Planned / Registration / Live / Completed


    creator = relationship("User", back_populates="tournaments")
    teams = relationship(
        "Team",
        secondary=tournament_participants,
        back_populates="tournaments",
    )
    matches = relationship("Match", back_populates="tournament")
    comments = relationship("Comment", back_populates="tournament")


# -----------------------------------------------------
# Матчи
# -----------------------------------------------------
class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    team1_id = Column(Integer, ForeignKey("teams.id"))
    team2_id = Column(Integer, ForeignKey("teams.id"))
    score_team1 = Column(Integer, default=0)
    score_team2 = Column(Integer, default=0)
    match_date = Column(DateTime, default=datetime.utcnow)
    round_number = Column(Integer, nullable=False, default=1)

    tournament = relationship("Tournament", back_populates="matches")
    team1 = relationship("Team", foreign_keys=[team1_id], back_populates="matches_as_team1")
    team2 = relationship("Team", foreign_keys=[team2_id], back_populates="matches_as_team2")



# -----------------------------------------------------
# Комментарии
# -----------------------------------------------------
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="comments")
    tournament = relationship("Tournament", back_populates="comments")


class EmailVerificationCode(Base):
    __tablename__ = "email_verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    code = Column(String(6))
    email = Column(String(255))
    expires_at = Column(DateTime)


# -----------------------------------------------------
# Темы профиля и инвентарь пользователей
# -----------------------------------------------------
'''class ProfileTheme(Base):
    __tablename__ = "profile_themes"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(20))
    price = Column(Integer)
    rarity = Column(String(20))
    preview_image = Column(String(255))
    css_class = Column(String(255))
'''
    # связь с UserTheme
    #users = relationship("UserTheme", back_populates="theme", cascade="all, delete-orphan")


#-----------------------------------------------------
# Связь пользователь–тема
#-----------------------------------------------------
'''class UserTheme(Base):
    __tablename__ = "user_themes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    theme_id = Column(Integer, ForeignKey("profile_themes.id"))
    equipped = Column(Boolean, default=False)

    user = relationship("User", back_populates="themes")
    theme = relat   ionship("ProfileTheme", back_populates="users")
'''


'''
class UserInventory(Base):
    __tablename__ = "user_inventory"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    theme_id = Column(Integer, ForeignKey("profile_themes.id"))
    equipped = Column(Boolean, default=False)

    theme = relationship("ProfileTheme")
'''



# -----------------------------------------------------
# Рамки профиля и инвентарь
# -----------------------------------------------------

class ProfileFrame(Base):
    __tablename__ = "profile_frames"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    image_url = Column(String(255), nullable=False)  # PNG overlay
    price = Column(Integer, nullable=False, default=0)
    rarity = Column(String(50), default="default")

    # Например:
    # name = "Gold Frame"
    # image_url = "/static/frames/gold.png"
    # price = 500


class UserFrame(Base):
    __tablename__ = "user_frames"   

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    frame_id = Column(Integer, ForeignKey("profile_frames.id"))
    equipped = Column(Boolean, default=False)

    user = relationship("User", backref="frames")
    frame = relationship("ProfileFrame")

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon_url = Column(String(255))
    xp_reward = Column(Integer, default=50) 

    def __repr__(self):
        return f"<Achievement(name={self.name})>"


# 🔹 Связь пользователь–ачивка
class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    earned_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")


class ProfileBadge(Base):
    __tablename__ = "profile_badges"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable=False)
    icon_url = Column(String(255), nullable=False)  # путь к иконке
    rarity = Column(String(50), default="common")

    def __repr__(self):
        return f"<ProfileBadge(name={self.name}, price={self.price})>"


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_id = Column(Integer, ForeignKey("profile_badges.id"))
    acquired_at = Column(DateTime, default=datetime.utcnow)
    equipped = Column(Boolean, default=False)

    user = relationship("User", backref="badges")
    badge = relationship("ProfileBadge")
