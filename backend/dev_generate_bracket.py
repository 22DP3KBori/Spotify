from backend.database import SessionLocal
from backend.models import Tournament, Match
from sqlalchemy.orm import joinedload

TOURNAMENT_ID = 1  # поменяй если нужно

db = SessionLocal()

# Загружаем турнир с командами
tournament = (
    db.query(Tournament)
    .options(joinedload(Tournament.teams))
    .filter(Tournament.id == TOURNAMENT_ID)
    .first()
)

if not tournament:
    print("Tournament not found")
    exit()

teams = tournament.teams

if len(teams) != 8:
    print("Этот генератор работает только если команд ровно 8.")
    print("Сейчас:", len(teams))
    exit()

# --------------------------
# Удаляем старые матчи
# --------------------------

db.query(Match).filter(Match.tournament_id == TOURNAMENT_ID).delete()
db.commit()

print("Старые матчи удалены.")

# --------------------------
# Создание Round 1
# --------------------------

# seed: 1 vs 8, 4 vs 5, 2 vs 7, 3 vs 6
seeded = [
    (teams[0], teams[7]),
    (teams[3], teams[4]),
    (teams[1], teams[6]),
    (teams[2], teams[5]),
]

round1_matches = []

for teamA, teamB in seeded:
    match = Match(
        tournament_id=TOURNAMENT_ID,
        team1_id=teamA.id,
        team2_id=teamB.id,
        round_number=1
    )
    db.add(match)
    round1_matches.append(match)

db.commit()
print("Round 1 создан.")

# --------------------------
# Создание Round 2 (плейсхолдеры)
# --------------------------

round2_matches = []
for _ in range(2):
    match = Match(
        tournament_id=TOURNAMENT_ID,
        team1_id=None,  # появятся победители
        team2_id=None,
        round_number=2
    )
    db.add(match)
    round2_matches.append(match)

db.commit()
print("Round 2 создан.")

# --------------------------
# Создание Final (Round 3)
# --------------------------

final_match = Match(
    tournament_id=TOURNAMENT_ID,
    team1_id=None,
    team2_id=None,
    round_number=3
)

db.add(final_match)
db.commit()

print("Final создан.")
print("Bracket успешно сгенерирован!")