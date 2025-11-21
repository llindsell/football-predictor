from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel
from datetime import datetime, timezone
from .database import get_session
from .models import Pick, User, Game
from .auth import get_current_user

router = APIRouter()

class PickCreate(BaseModel):
    game_id: int
    selected_team_id: int

@router.post("/", response_model=Pick)
def create_pick(
    pick_data: PickCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check if game exists
    game = session.get(Game, pick_data.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Check if game has started
    if game.status != "scheduled":
        raise HTTPException(status_code=400, detail="Cannot make picks on games that have started")
    
    if game.game_time:
        try:
            # Handle different ISO format variations
            game_time_str = game.game_time
            if 'Z' in game_time_str:
                game_time_str = game_time_str.replace('Z', '+00:00')
            game_time = datetime.fromisoformat(game_time_str)
            
            # Ensure game_time is timezone-aware
            if game_time.tzinfo is None:
                game_time = game_time.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            if now >= game_time:
                raise HTTPException(status_code=400, detail="Cannot make picks on games that have started")
        except ValueError as e:
            # If we can't parse the time, log it but don't block the pick
            print(f"Warning: Could not parse game_time '{game.game_time}': {e}")
        
    # Check if pick already exists for this game/user
    existing_pick = session.exec(
        select(Pick)
        .where(Pick.user_id == current_user.id)
        .where(Pick.game_id == pick_data.game_id)
    ).first()
    
    if existing_pick:
        # Update existing pick
        existing_pick.selected_team_id = pick_data.selected_team_id
        session.add(existing_pick)
        session.commit()
        session.refresh(existing_pick)
        return existing_pick
    else:
        # Create new pick
        pick = Pick(
            user_id=current_user.id,
            game_id=pick_data.game_id,
            selected_team_id=pick_data.selected_team_id
        )
        session.add(pick)
        session.commit()
        session.refresh(pick)
        return pick

@router.get("/me", response_model=List[Pick])
def read_my_picks(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    picks = session.exec(select(Pick).where(Pick.user_id == current_user.id)).all()
    return picks

@router.get("/user/{user_id}", response_model=List[Pick])
def read_user_picks(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    picks = session.exec(select(Pick).where(Pick.user_id == user_id)).all()
    return picks

@router.delete("/{game_id}", response_model=dict)
def delete_pick(
    game_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check if game exists and hasn't started
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Check if game has started
    if game.status != "scheduled":
        raise HTTPException(status_code=400, detail="Cannot delete picks on games that have started")
    
    if game.game_time:
        try:
            # Handle different ISO format variations
            game_time_str = game.game_time
            if 'Z' in game_time_str:
                game_time_str = game_time_str.replace('Z', '+00:00')
            game_time = datetime.fromisoformat(game_time_str)
            
            # Ensure game_time is timezone-aware
            if game_time.tzinfo is None:
                game_time = game_time.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            if now >= game_time:
                raise HTTPException(status_code=400, detail="Cannot delete picks on games that have started")
        except ValueError as e:
            # If we can't parse the time, log it but don't block the delete
            print(f"Warning: Could not parse game_time '{game.game_time}': {e}")
    
    pick = session.exec(
        select(Pick)
        .where(Pick.user_id == current_user.id)
        .where(Pick.game_id == game_id)
    ).first()
    
    if not pick:
        raise HTTPException(status_code=404, detail="Pick not found")
        
    session.delete(pick)
    session.commit()
    
    return {"message": "Pick deleted successfully"}

@router.get("/week/{week_id}/users", response_model=List[User])
def read_users_with_picks(
    week_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    users = session.exec(
        select(User)
        .join(Pick)
        .join(Game)
        .where(Game.week_id == week_id)
        .distinct()
    ).all()
    return users
