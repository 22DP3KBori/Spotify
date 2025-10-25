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
from datetime import datetime
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

    # 🔹 связь с ролью
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")

    # 🔹 обратные связи
    teams = relationship("Team", back_populates="creator")
    tournaments = relationship("Tournament", back_populates="creator")
    comments = relationship("Comment", back_populates="user")


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
