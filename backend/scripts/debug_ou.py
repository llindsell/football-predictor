from bs4 import BeautifulSoup
import re

def debug_ou():
    with open("yahoo_nfl.html", "r") as f:
        content = f.read()
    
    soup = BeautifulSoup(content, "html.parser")
    game_items = soup.find_all("li", {"data-tst": re.compile(r"^GameItem-")})
    
    print(f"Found {len(game_items)} game items.")
    
    for i, item in enumerate(game_items):
        print(f"Game {i}:")
        # Try current logic
        ou_div = item.find("div", class_="odds total")
        if ou_div:
            print(f"  Found O/U div: {ou_div.get_text(strip=True)}")
        else:
            print("  O/U div NOT found with class_='odds total'")
            # Try finding any div with 'total' in class
            total_div = item.find("div", class_=lambda x: x and 'total' in x)
            if total_div:
                print(f"  Found div with 'total' in class: {total_div.get('class')} - Text: {total_div.get_text(strip=True)}")
            else:
                print("  No div with 'total' found.")

if __name__ == "__main__":
    debug_ou()
