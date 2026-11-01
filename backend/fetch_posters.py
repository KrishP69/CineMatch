import json
import re
import urllib.request
import os

MOVIES_FILE = os.path.join(os.path.dirname(__file__), "data", "movies.json")

def fetch_tmdb_poster(tmdb_id):
    url = f"https://www.themoviedb.org/movie/{tmdb_id}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
            # Look for og:image
            og_match = re.search(r'property="og:image"\s+content="https://image\.tmdb\.org/t/p/[^/]+/([^"]+)"', html)
            if og_match:
                return og_match.group(1)
            # Alternate pattern
            img_match = re.search(r'https://image\.tmdb\.org/t/p/(?:w500|w300_and_h450_bestv2|original)/([a-zA-Z0-9_\-\.]+\.(?:jpg|png|jpeg))', html)
            if img_match:
                return img_match.group(1)
    except Exception as e:
        print(f"Failed for {tmdb_id}: {e}")
    return None

if __name__ == "__main__":
    for tid in [20453, 531428, 534780, 19404, 313369]:
        res = fetch_tmdb_poster(tid)
        print(f"{tid} -> {res}")

