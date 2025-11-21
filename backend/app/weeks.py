from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from .database import get_session
from .models import Week, Game, Team

router = APIRouter()

@router.get("/", response_model=List[Week])
def read_weeks(session: Session = Depends(get_session)):
    weeks = session.exec(select(Week).order_by(Week.season.desc(), Week.week_number.desc())).all()
    return weeks

@router.get("/{week_id}/games", response_model=List[dict])
def read_week_games(week_id: int, session: Session = Depends(get_session)):
    games = session.exec(select(Game).where(Game.week_id == week_id)).all()
    
    result = []
    for game in games:
        home_team = session.get(Team, game.home_team_id)
        away_team = session.get(Team, game.away_team_id)
        result.append({
            "id": game.id,
            "week_id": game.week_id,
            "home_team": home_team,
            "away_team": away_team,
            "spread": game.spread,
            "home_score": game.home_score,
            "away_score": game.away_score,
            "status": game.status,
            "game_time": game.game_time,
            "over_under": game.over_under
        })
    return result
