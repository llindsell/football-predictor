import sys
import os
from sqlmodel import Session, select

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import engine
from app.models import Team

def clear_and_reseed_teams():
    print("Updating teams with fresh data from seed_teams.py...")
    
    # Just run the seed script which will update existing teams
    from seed_teams import seed_teams
    seed_teams()
    print("\nDone!")

if __name__ == "__main__":
    clear_and_reseed_teams()
