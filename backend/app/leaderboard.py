from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from typing import List
from pydantic import BaseModel
from .database import get_session
from .models import User, Pick, Game, Week

router = APIRouter()

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    user_name: str
    profile_picture: str | None
    correct_picks: int
    total_picks: int
    win_rate: float

@router.get("/", response_model=List[LeaderboardEntry])
def get_leaderboard(week_id: int | None = None, session: Session = Depends(get_session)):
    # Get all completed games
    query = select(Game).where(Game.status == "final")
    if week_id:
        query = query.where(Game.week_id == week_id)
    
    completed_games = session.exec(query).all()
    game_map = {g.id: g for g in completed_games}
    
    if not completed_games:
        return []

    # Determine winners for each game
    game_winners = {} # game_id -> winning_team_id (or None for push)
    for game in completed_games:
        if game.home_score is None or game.away_score is None:
            continue
            
        # Spread logic (Home + Spread vs Away)
        # Example: Home -3.5. Home 20, Away 10. 20 + (-3.5) = 16.5 > 10. Home Wins.
        adjusted_home_score = game.home_score + game.spread
        
        if adjusted_home_score > game.away_score:
            game_winners[game.id] = game.home_team_id
        elif adjusted_home_score < game.away_score:
            game_winners[game.id] = game.away_team_id
        else:
            game_winners[game.id] = None # Push

    # Get all picks for these games
    picks_query = select(Pick).where(Pick.game_id.in_(game_winners.keys()))
    picks = session.exec(picks_query).all()
    
    # Calculate scores
    user_scores = {} # user_id -> {correct: 0, total: 0}
    
    for pick in picks:
        if pick.user_id not in user_scores:
            user_scores[pick.user_id] = {"correct": 0, "total": 0}
        
        winner_id = game_winners.get(pick.game_id)
        if winner_id is not None:
            user_scores[pick.user_id]["total"] += 1
            if pick.selected_team_id == winner_id:
                user_scores[pick.user_id]["correct"] += 1
    
    # Get user details
    users = session.exec(select(User).where(User.id.in_(user_scores.keys()))).all()
    user_map = {u.id: u for u in users}
    
    # Build leaderboard
    leaderboard = []
    for user_id, score in user_scores.items():
        user = user_map.get(user_id)
        if not user:
            continue
            
        win_rate = (score["correct"] / score["total"]) * 100 if score["total"] > 0 else 0.0
        
        leaderboard.append(LeaderboardEntry(
            rank=0, # Placeholder
            user_id=user.id,
            user_name=user.name,
            profile_picture=user.profile_picture,
            correct_picks=score["correct"],
            total_picks=score["total"],
            win_rate=round(win_rate, 1)
        ))
    
    # Sort by correct picks (desc), then win rate (desc)
    leaderboard.sort(key=lambda x: (x.correct_picks, x.win_rate), reverse=True)
    
    # Assign ranks
    for i, entry in enumerate(leaderboard):
        entry.rank = i + 1
        
    return leaderboard
