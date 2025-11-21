import sys
import os
from sqlmodel import Session, select
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import engine
from app.models import Week, Game, Team

def seed_weeks_and_games():
    with Session(engine) as session:
        # Create Week 1
        week1 = session.exec(select(Week).where(Week.week_number == 1)).first()
        if not week1:
            week1 = Week(
                season=2024,
                week_number=1,
                start_date="2024-09-05",
                end_date="2024-09-10"
            )
            session.add(week1)
            session.commit()
            session.refresh(week1)
            print("Added Week 1")
        
        # Get some teams
        chiefs = session.exec(select(Team).where(Team.abbreviation == "kc")).first()
        ravens = session.exec(select(Team).where(Team.abbreviation == "bal")).first()
        eagles = session.exec(select(Team).where(Team.abbreviation == "phi")).first()
        packers = session.exec(select(Team).where(Team.abbreviation == "gb")).first()
        
        if chiefs and ravens:
            # Create Game 1: Chiefs vs Ravens
            game1 = session.exec(select(Game).where(Game.week_id == week1.id).where(Game.home_team_id == chiefs.id)).first()
            if not game1:
                game1 = Game(
                    week_id=week1.id,
                    home_team_id=chiefs.id,
                    away_team_id=ravens.id,
                    spread=-3.5, # Chiefs favored by 3.5
                    status="scheduled",
                    game_time="2024-09-05T20:20:00",
                    over_under=46.5
                )
                session.add(game1)
                print("Added Game: Chiefs vs Ravens")

        if eagles and packers:
            # Create Game 2: Eagles vs Packers
            game2 = session.exec(select(Game).where(Game.week_id == week1.id).where(Game.home_team_id == eagles.id)).first()
            if not game2:
                game2 = Game(
                    week_id=week1.id,
                    home_team_id=eagles.id,
                    away_team_id=packers.id,
                    spread=-2.5,
                    status="scheduled",
                    game_time="2024-09-06T20:15:00",
                    over_under=48.5
                )
                session.add(game2)
                print("Added Game: Eagles vs Packers")
        
        session.commit()

if __name__ == "__main__":
    seed_weeks_and_games()
