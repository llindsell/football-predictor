import sys
import os
from sqlmodel import Session, select

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import engine
from app.models import Game, Week, Team

def verify_games():
    with Session(engine) as session:
        # Check Week 12
        week = session.exec(select(Week).where(Week.week_number == 12, Week.season == 2025)).first()
        if not week:
            print("Week 12 not found!")
            return

        print(f"Found Week 12: {week.start_date} to {week.end_date}")

        # Check Games
        games = session.exec(select(Game).where(Game.week_id == week.id)).all()
        print(f"Found {len(games)} games for Week 12")
        
        for game in games:
            home_team = session.get(Team, game.home_team_id)
            away_team = session.get(Team, game.away_team_id)
            print(f"{away_team.name} @ {home_team.name} | Spread: {game.spread} | O/U: {game.over_under} | Time: {game.game_time}")

if __name__ == "__main__":
    verify_games()
