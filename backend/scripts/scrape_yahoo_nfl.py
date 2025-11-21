import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_yahoo_nfl():
    url = "https://sports.yahoo.com/nfl/scoreboard/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Parse JSON data for game times
    game_times = {}
    try:
        # Find the script tag containing root.App.main
        # We look for the string "root.App.main ="
        script_tags = soup.find_all("script")
        for script in script_tags:
            if script.string and "root.App.main =" in script.string:
                # Extract the JSON object
                # It usually starts after "root.App.main = " and ends before ";" or new line
                content = script.string
                start_marker = "root.App.main ="
                start_index = content.find(start_marker)
                if start_index != -1:
                    start_index += len(start_marker)
                    # Find the end of the JSON object. It's a bit tricky, but usually it's followed by a semicolon
                    # We can try to find the first semicolon after the start
                    # However, the JSON might contain semicolons. 
                    # A safer way might be to look for the next variable assignment or end of script
                    # Let's try to find the matching brace if possible, or just take a large chunk and try to parse?
                    # Actually, looking at the dump, it seems to be `root.App.main = {...};`
                    # So we can strip until the last semicolon
                    
                    # Let's try to find the end of the line or semicolon
                    end_index = content.find(";\n", start_index)
                    if end_index == -1:
                        end_index = content.find(";", start_index)
                    
                    if end_index != -1:
                        json_str = content[start_index:end_index].strip()
                        try:
                            data = json.loads(json_str)
                            # Navigate to game data
                            # Structure seems to be flat or nested under context -> dispatcher -> stores -> ScoreboardStore -> games
                            # But we saw "nfl.g.20251120034": {...} in the dump.
                            # It might be in `context.dispatcher.stores.PageStore.pageData.entityData` or similar?
                            # Actually, the dump showed "nfl.g.20251120034":{...} which suggests it's a key in a large object.
                            # Let's traverse the whole JSON to find keys starting with "nfl.g."
                            
                            # Helper to recursively search for game objects
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
        # print(f"Error parsing JSON: {e}")
        pass

    games = []
    
    # Find all game items
    # Selector: li with data-tst starting with "GameItem-"
    game_items = soup.find_all("li", {"data-tst": re.compile(r"^GameItem-")})

    for item in game_items:
        try:
            game_data = {}
            
            # Game ID
            game_id = item.get("data-tst", "").replace("GameItem-", "")
            
            # Game URL
            link_tag = item.find("a", class_="gamecard-pregame", href=True)
            if link_tag:
                game_data["game_url"] = "https://sports.yahoo.com" + link_tag["href"]
                # Extract date from URL or ID if possible
                match = re.search(r"(\d{8})", link_tag["href"])
                if match:
                    date_str = match.group(1)
                    # Format: YYYYMMDD -> YYYY-MM-DD
                    game_data["game_date"] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                else:
                    game_data["game_date"] = None
            else:
                game_data["game_url"] = None
                game_data["game_date"] = None

            # Teams and Records
            team_items = item.find_all("li", class_="team")
            if len(team_items) >= 2:
                # Away Team
                away_team_item = team_items[0]
                away_city = away_team_item.find("span", {"data-tst": "first-name"})
                away_name = away_team_item.find("span", {"data-tst": "last-name"})
                if away_city and away_name:
                    game_data["away_team"] = f"{away_city.get_text(strip=True)} {away_name.get_text(strip=True)}"
                else:
                    game_data["away_team"] = "Unknown"
                
                # Away Record
                away_record_div = away_team_item.find_all("div")[-1]
                game_data["away_team_record"] = away_record_div.get_text(strip=True) if away_record_div else None

                # Home Team
                home_team_item = team_items[1]
                home_city = home_team_item.find("span", {"data-tst": "first-name"})
                home_name = home_team_item.find("span", {"data-tst": "last-name"})
                if home_city and home_name:
                    game_data["home_team"] = f"{home_city.get_text(strip=True)} {home_name.get_text(strip=True)}"
                else:
                    game_data["home_team"] = "Unknown"

                # Home Record
                home_record_div = home_team_item.find_all("div")[-1]
                game_data["home_team_record"] = home_record_div.get_text(strip=True) if home_record_div else None
            else:
                continue

            # Odds
            odds_div = item.find("div", class_="odds", title=True)
            if odds_div and "total" not in odds_div.get("class", []):
                raw_odds = odds_div.get_text(strip=True)
                # Extract just the number (e.g., "-5" from "BUF -5")
                # Regex to find a number (integer or decimal, positive or negative) at the end of the string
                # or just look for the last number
                odds_match = re.search(r"([+-]?\d+(\.\d+)?)", raw_odds.split()[-1])
                if odds_match:
                    game_data["odds"] = odds_match.group(1)
                else:
                    game_data["odds"] = raw_odds # Fallback
            else:
                game_data["odds"] = None

            # Over/Under
            # div.odds.total
            # Use CSS selector to match multiple classes
            ou_div = item.select_one("div.odds.total")
            if ou_div:
                raw_ou = ou_div.get_text(strip=True)
                # Extract just the number
                ou_match = re.search(r"(\d+(\.\d+)?)", raw_ou)
                if ou_match:
                    game_data["over_under"] = ou_match.group(1)
                else:
                    game_data["over_under"] = raw_ou.replace("O/U", "").strip()
            else:
                game_data["over_under"] = None

            # Game Time
            # Use the game_id to look up start_time in the parsed JSON
            if game_id in game_times:
                # Time format in JSON: "Fri, 21 Nov 2025 01:15:00 +0000"
                # We want to convert this to something more readable or keep it as is?
                # The user mentioned "5:15 PM PST".
                # Let's keep the raw string for now, or try to parse it if needed.
                # But simply returning the string found in JSON is a good start.
                game_data["game_time"] = game_times[game_id]
            else:
                game_data["game_time"] = "TBD"
                
            games.append(game_data)

        except Exception as e:
            # print(f"Error parsing game item: {e}")
            continue

    print(json.dumps(games, indent=2))

if __name__ == "__main__":
    scrape_yahoo_nfl()
