import sys
import os
from sqlmodel import Session, select

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import engine
from app.models import Team

teams_data = [
    {"abbreviation": "ari", "name": "Arizona Cardinals"},
    {"abbreviation": "atl", "name": "Atlanta Falcons"},
    {"abbreviation": "bal", "name": "Baltimore Ravens"},
    {"abbreviation": "buf", "name": "Buffalo Bills"},
    {"abbreviation": "car", "name": "Carolina Panthers"},
    {"abbreviation": "chi", "name": "Chicago Bears"},
    {"abbreviation": "cin", "name": "Cincinnati Bengals"},
    {"abbreviation": "cle", "name": "Cleveland Browns"},
    {"abbreviation": "dal", "name": "Dallas Cowboys"},
    {"abbreviation": "den", "name": "Denver Broncos"},
    {"abbreviation": "det", "name": "Detroit Lions"},
    {"abbreviation": "gb", "name": "Green Bay Packers"},
    {"abbreviation": "hou", "name": "Houston Texans"},
    {"abbreviation": "ind", "name": "Indianapolis Colts"},
    {"abbreviation": "jax", "name": "Jacksonville Jaguars"},
    {"abbreviation": "kc", "name": "Kansas City Chiefs"},
    {"abbreviation": "lar", "name": "Los Angeles Rams"},
    {"abbreviation": "lac", "name": "Los Angeles Chargers"},
    {"abbreviation": "lv", "name": "Las Vegas Raiders"},
    {"abbreviation": "mia", "name": "Miami Dolphins"},
    {"abbreviation": "min", "name": "Minnesota Vikings"},
    {"abbreviation": "ne", "name": "New England Patriots"},
    {"abbreviation": "no", "name": "New Orleans Saints"},
    {"abbreviation": "nyg", "name": "New York Giants"},
    {"abbreviation": "nyj", "name": "New York Jets"},
    {"abbreviation": "phi", "name": "Philadelphia Eagles"},
    {"abbreviation": "pit", "name": "Pittsburgh Steelers"},
    {"abbreviation": "sea", "name": "Seattle Seahawks"},
    {"abbreviation": "sf", "name": "San Francisco 49ers"},
    {"abbreviation": "tb", "name": "Tampa Bay Buccaneers"},
    {"abbreviation": "ten", "name": "Tennessee Titans"},
    {"abbreviation": "was", "name": "Washington Commanders"},
]

def seed_teams():
    with Session(engine) as session:
        for team_data in teams_data:
            team = session.exec(select(Team).where(Team.abbreviation == team_data["abbreviation"])).first()
            if not team:
                team = Team(
                    name=team_data["name"],
                    abbreviation=team_data["abbreviation"],
                    logo_path=f"/logos/{team_data['abbreviation']}.svg"
                )
                session.add(team)
                print(f"Added {team.name}")
            else:
                print(f"Skipped {team.name} (already exists)")
        session.commit()

if __name__ == "__main__":
    seed_teams()
