from backend.database import SessionLocal
from backend.models import Match

db = SessionLocal()

matches = db.query(Match).order_by(Match.id).all()

for m in matches:
    print(
        f"ID={m.id}, t_id={m.tournament_id}, "
        f"teams=({m.team1_id},{m.team2_id}), "
        f"round={m.round_number}"
    )