from typing import Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str
    profile_picture: Optional[str] = None
    
class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    abbreviation: str
    logo_path: str

class Week(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    season: int
    week_number: int
    start_date: str # ISO format
    end_date: str # ISO format

class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    week_id: int = Field(foreign_key="week.id")
    home_team_id: int = Field(foreign_key="team.id")
    away_team_id: int = Field(foreign_key="team.id")
    spread: float
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str = "scheduled" # scheduled, in_progress, final
    game_time: Optional[str] = None # ISO format datetime
    over_under: Optional[float] = None

class Pick(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    game_id: int = Field(foreign_key="game.id")
    selected_team_id: int = Field(foreign_key="team.id")
