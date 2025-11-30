from sqlalchemy.orm import Session
from backend.models import Tournament, Match
from typing import List


def generate_bracket_for_tournament(db: Session, tournament: Tournament) -> None:
    """
    Простая генерация сетки:
    - если у турнира уже есть матчи — ничего не делаем
    - иначе создаём матчи 1-го раунда, парами (1–2, 3–4, 5–6, 7–8, ...)
    """

    teams: List = list(tournament.teams)

    # нужно хотя бы 2 команды
    if len(teams) < 2:
        return

    # уже есть матчи — не трогаем (чтобы не дублировать)
    if tournament.matches and len(tournament.matches) > 0:
        return

    # сортируем по id, чтобы порядок был стабильный
    teams_sorted = sorted(teams, key=lambda t: t.id)

    it = iter(teams_sorted)

    for team1 in it:
        try:
            team2 = next(it)
        except StopIteration:
            team2 = None  # нечётное количество — последний без пары

        match = Match(
            tournament_id=tournament.id,
            team1_id=team1.id,
            team2_id=team2.id if team2 else None,
            round_number=1,
            match_date=tournament.start_date,
        )
        db.add(match)

    db.commit()