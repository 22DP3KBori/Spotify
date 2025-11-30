from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session, joinedload
from collections import defaultdict
from datetime import datetime

from backend.database import get_db
from backend.models import Tournament, Match, Team
from backend.core.templates import templates

router = APIRouter()

GAME_LOGOS = {
    "CS2": "cs2.webp",
    "Dota": "dota2.png",
    "Valorant": "valorant.png",
    "FIFA": "fifa.webp",
    "UFC": "ufc.webp",
    "LoL": "LoL.png",
    "PUBG": "PUBG.png",
    "Fortnite": "fortnite.png",
    "WoT": "WoT.jpeg",
    "Clash Royale": "clash_royale.webp",
    "Rocket League": "RL.jpg",
    "Apex Legends": "apex_legends.png",
    "Overwatch 2": "overwatch2.png",
    "Chess.com": "chess_com.png",
}

ROUND_LABELS = {
    1: "Quarterfinals",
    2: "Semifinals",
    3: "Final",
    4: "Grand Final",
}

@router.get("/tournaments")
def tournaments_page(
    request: Request,
    game: str = None,
    format: str = None,
    type: str = None,
    price: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Tournament)

    if game:
        query = query.filter(Tournament.discipline == game)
    if format:
        query = query.filter(Tournament.format == format)
    if type:
        query = query.filter(Tournament.type == type)
    if price:
        query = query.filter(Tournament.entry_type == price)
    if status:
        query = query.filter(Tournament.status == status)

    tournaments = query.order_by(Tournament.start_date.asc()).all()

    games = [
        "FIFA", "UFC", "Dota", "CS2", "Valorant",
        "Chess.com", "LoL", "PUBG", "Fortnite",
        "WoT", "Clash Royale", "Rocket League",
        "Apex Legends", "Overwatch 2",
    ]

    return templates.TemplateResponse(
        "tournaments.html",
        {
            "request": request,
            "tournaments": tournaments,
            "games": games,
            "game": game,
            "GAME_LOGOS": GAME_LOGOS,
        }
    )


from math import log2, ceil
from collections import defaultdict


@router.get("/tournament/{tournament_id}")
def tournament_view(
    tournament_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    tournament: Tournament | None = (
        db.query(Tournament)
        .options(
            joinedload(Tournament.teams),
            joinedload(Tournament.matches).joinedload(Match.team1),
            joinedload(Tournament.matches).joinedload(Match.team2),
        )
        .filter(Tournament.id == tournament_id)
        .first()
    )

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    teams = tournament.teams

    # ----- ВСЕ МАТЧИ ТУРНИРА (для Matches + Standings) -----
    matches = sorted(
        tournament.matches,
        key=lambda m: m.match_date or datetime.min,
    )

    # ----- STANDINGS КАК РАНЬШЕ -----
    stats = defaultdict(
        lambda: {
            "team": None,
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "scored": 0,
            "conceded": 0,
            "points": 0,
        }
    )

    for match in matches:
        if not match.team1 or not match.team2:
            continue

        s1 = match.score_team1 or 0
        s2 = match.score_team2 or 0

        for team, scored, conceded, is_win, is_draw in [
            (match.team1, s1, s2, s1 > s2, s1 == s2),
            (match.team2, s2, s1, s2 > s1, s1 == s2),
        ]:
            row = stats[team.id]
            row["team"] = team
            row["played"] += 1
            row["scored"] += scored
            row["conceded"] += conceded

            if is_draw:
                row["draws"] += 1
                row["points"] += 1
            elif is_win:
                row["wins"] += 1
                row["points"] += 3
            else:
                row["losses"] += 1

    standings = sorted(
        stats.values(),
        key=lambda r: (
            -r["points"],
            -(r["scored"] - r["conceded"]),
            -r["scored"],
        ),
    )

    # ----- BRACKET: только матчи, где round_number не None -----
    round_map: dict[int, list[Match]] = defaultdict(list)
    for m in matches:
        if m.round_number is not None:
            round_map[m.round_number].append(m)

    bracket: list[dict] = []
    previous_round_view: list[dict] | None = None

    for rn in sorted(round_map.keys()):
        raw_matches = sorted(round_map[rn], key=lambda m: m.id)
        round_view: list[dict] = []

        for idx, m in enumerate(raw_matches):
            s1 = m.score_team1
            s2 = m.score_team2

            winner_id = None
            if s1 is not None and s2 is not None:
                if s1 > s2:
                    winner_id = m.team1_id
                elif s2 > s1:
                    winner_id = m.team2_id

            # базовые команды из БД
            display_team1 = m.team1
            display_team2 = m.team2

            # автоподстановка победителей из прошлого раунда
            if previous_round_view:
                source_idx1 = idx * 2
                source_idx2 = idx * 2 + 1

                if not display_team1 and source_idx1 < len(previous_round_view):
                    src = previous_round_view[source_idx1]
                    display_team1 = src.get("winner_team") or src.get("team1") or src.get("team2")

                if not display_team2 and source_idx2 < len(previous_round_view):
                    src = previous_round_view[source_idx2]
                    display_team2 = src.get("winner_team") or src.get("team1") or src.get("team2")

            winner_team = None
            if winner_id and (display_team1 and display_team1.id == winner_id):
                winner_team = display_team1
            elif winner_id and (display_team2 and display_team2.id == winner_id):
                winner_team = display_team2

            round_view.append(
                {
                    "id": m.id,
                    "round": rn,
                    "team1": display_team1,
                    "team2": display_team2,
                    "score1": s1,
                    "score2": s2,
                    "winner_id": winner_id,
                    "winner_team": winner_team,
                }
            )

        bracket.append(
            {
                "number": rn,
                "label": ROUND_LABELS.get(rn, f"Round {rn}"),
                "matches": round_view,
            }
        )

        previous_round_view = round_view

    prize = getattr(tournament, "entry_price", None) or 0
    format_ = getattr(tournament, "format", None) or "TBA"
    team_count = len(teams)
    status = getattr(tournament, "status", None) or "Planned"

    return templates.TemplateResponse(
        "tournament_view.html",
        {
            "request": request,
            "tournament": tournament,
            "teams": teams,
            "matches": matches,
            "standings": standings,
            "prize": prize,
            "format": format_,
            "team_count": team_count,
            "status": status,
            "GAME_LOGOS": GAME_LOGOS,
            "bracket": bracket,
        },
    )