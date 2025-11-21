import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlmodel import Session, select
from app.database import engine
from app.models import Team, Game, Week

def get_current_week():
    # Start date: September 2, 2025 (Monday before Week 1)
    start_date = datetime(2025, 9, 2)
    today = datetime.now()
    
    # Calculate days passed
    days_passed = (today - start_date).days
    
    # Calculate week number (integer division by 7, plus 1)
    # If days_passed is negative (before season), default to Week 1
    if days_passed < 0:
        return 1
        
    week_number = (days_passed // 7) + 1
    return week_number

def scrape_yahoo_nfl():
    url = "https://sports.yahoo.com/nfl/scoreboard/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }

    cache_file = "yahoo_nfl.html"
    content = None

    if os.path.exists(cache_file):
        last_modified = os.path.getmtime(cache_file)
        if time.time() - last_modified < 86400:  # 24 hours
            print(f"Using cached file: {cache_file}")
            with open(cache_file, "rb") as f:
                content = f.read()

    if content is None:
        print("Fetching from URL...")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            content = response.content
            with open(cache_file, "wb") as f:
                f.write(content)
        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")
            return

    soup = BeautifulSoup(content, "html.parser")
    
    # Parse JSON data for game times
    game_times = {}
    try:
        script_tags = soup.find_all("script")
        for script in script_tags:
            if script.string and "root.App.main =" in script.string:
                content_str = script.string
                start_marker = "root.App.main ="
                start_index = content_str.find(start_marker)
                if start_index != -1:
                    start_index += len(start_marker)
                    end_index = content_str.find(";\n", start_index)
                    if end_index == -1:
                        end_index = content_str.find(";", start_index)
                    
                    if end_index != -1:
                        json_str = content_str[start_index:end_index].strip()
                        try:
                            data = json.loads(json_str)
                            def extract_game_times(obj):
                                if isinstance(obj, dict):
                                    for k, v in obj.items():
                                        if isinstance(k, str) and k.startswith("nfl.g.") and isinstance(v, dict):
                                            if "start_time" in v:
                                                game_times[k] = v["start_time"]
                                        extract_game_times(v)
                                elif isinstance(obj, list):
                                    for item in obj:
                                        extract_game_times(item)
                            
                            extract_game_times(data)
                        except json.JSONDecodeError:
                            pass
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        pass

    current_week_num = get_current_week()
    print(f"Current Week: {current_week_num}")

    with Session(engine) as session:
        # Find or create Week
        # We assume the season is 2025 based on the prompt context
        season = 2025
        week = session.exec(select(Week).where(Week.season == season, Week.week_number == current_week_num)).first()
        if not week:
            # If week doesn't exist, create it with dummy dates for now or calculate them
            # Start date = Sept 2 + (week-1)*7 days
            week_start = datetime(2025, 9, 2) + timedelta(weeks=current_week_num - 1)
            week_end = week_start + timedelta(days=6)
            week = Week(
                season=season,
                week_number=current_week_num,
                start_date=week_start.strftime("%Y-%m-%d"),
                end_date=week_end.strftime("%Y-%m-%d")
            )
            session.add(week)
            session.commit()
            session.refresh(week)
            print(f"Created Week {current_week_num}")
        else:
            print(f"Found Week {current_week_num}")

        # Find all game items
        game_items = soup.find_all("li", {"data-tst": re.compile(r"^GameItem-")})

        for item in game_items:
            try:
                # Game ID
                game_id_str = item.get("data-tst", "").replace("GameItem-", "")
                
                # Teams
                team_items = item.find_all("li", class_="team")
                if len(team_items) < 2:
                    continue

                # Away Team
                away_team_item = team_items[0]
                away_city = away_team_item.find("span", {"data-tst": "first-name"})
                away_name = away_team_item.find("span", {"data-tst": "last-name"})
                if away_city and away_name:
                    away_team_name = f"{away_city.get_text(strip=True)} {away_name.get_text(strip=True)}"
                else:
                    continue # Skip if name not found

                # Home Team
                home_team_item = team_items[1]
                home_city = home_team_item.find("span", {"data-tst": "first-name"})
                home_name = home_team_item.find("span", {"data-tst": "last-name"})
                if home_city and home_name:
                    home_team_name = f"{home_city.get_text(strip=True)} {home_name.get_text(strip=True)}"
                else:
                    continue # Skip if name not found

                # Find Teams in DB
                away_team = session.exec(select(Team).where(Team.name == away_team_name)).first()
                home_team = session.exec(select(Team).where(Team.name == home_team_name)).first()

                if not away_team:
                    print(f"Warning: Away team '{away_team_name}' not found in DB.")
                    continue
                if not home_team:
                    print(f"Warning: Home team '{home_team_name}' not found in DB.")
                    continue

                # Odds / Spread
                spread = 0.0
                odds_div = item.find("div", class_="odds", title=True)
                if odds_div and "total" not in odds_div.get("class", []):
                    raw_odds = odds_div.get_text(strip=True)
                    # Extract number: "-5" or "+3.5"
                    odds_match = re.search(r"([+-]?\d+(\.\d+)?)", raw_odds.split()[-1])
                    if odds_match:
                        try:
                            spread = float(odds_match.group(1))
                        except ValueError:
                            pass

                # Over/Under
                over_under = None
                ou_div = item.select_one("div.odds.total")
                if ou_div:
                    raw_ou = ou_div.get_text(strip=True)
                    ou_match = re.search(r"(\d+(\.\d+)?)", raw_ou)
                    if ou_match:
                        try:
                            over_under = float(ou_match.group(1))
                        except ValueError:
                            pass

                # Game Time
                game_time_str = None
                if game_id_str in game_times:
                    game_time_str = game_times[game_id_str]

                # Find existing game or create new
                # We match on week, home_team, away_team
                game = session.exec(select(Game).where(
                    Game.week_id == week.id,
                    Game.home_team_id == home_team.id,
                    Game.away_team_id == away_team.id
                )).first()

                if not game:
                    game = Game(
                        week_id=week.id,
                        home_team_id=home_team.id,
                        away_team_id=away_team.id,
                        spread=spread,
                        over_under=over_under,
                        game_time=game_time_str,
                        status="scheduled"
                    )
                    session.add(game)
                    print(f"Added game: {away_team.name} @ {home_team.name}")
                else:
                    # Update existing game
                    game.spread = spread
                    game.over_under = over_under
                    game.game_time = game_time_str
                    session.add(game)
                    print(f"Updated game: {away_team.name} @ {home_team.name}")

            except Exception as e:
                print(f"Error processing game item: {e}")
                continue
        
        session.commit()

if __name__ == "__main__":
    scrape_yahoo_nfl()

