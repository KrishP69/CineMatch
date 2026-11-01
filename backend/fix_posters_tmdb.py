import json
import os
import re
import subprocess
import time

MOVIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "movies.json")

def get_verified_poster(tmdb_id, title):
    # Fetch TMDB page
    url = f"https://www.themoviedb.org/movie/{tmdb_id}"
    cmd = ["curl.exe", "-s", "-L", "--max-time", "10", url]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = res.stdout

    # Find TMDB image path
    # Look for /t/p/w.../something.jpg or og:image
    m = re.findall(r"https://image\.tmdb\.org/t/p/(?:w500|w300_and_h450_bestv2|original)/([a-zA-Z0-9_\-\.]+\.(?:jpg|png|jpeg))", html)
    if not m:
        m = re.findall(r"/t/p/(?:w500|w300_and_h450_bestv2|original)/([a-zA-Z0-9_\-\.]+\.(?:jpg|png|jpeg))", html)

    if m:
        poster_file = m[0]
        # Verify 200 OK with curl -I
        test_url = f"https://image.tmdb.org/t/p/w500/{poster_file}"
        check_cmd = ["curl.exe", "-s", "-I", "--max-time", "5", test_url]
        check_res = subprocess.run(check_cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if "200 OK" in check_res.stdout or "HTTP/1.1 200" in check_res.stdout or "HTTP/2 200" in check_res.stdout:
            return test_url, f"/{poster_file}"
        else:
            print(f"  Warning: {test_url} did not return 200 OK")

    return None, None

def main():
    print("Loading movies.json...")
    with open(MOVIES_FILE, "r", encoding="utf-8") as f:
        movies = json.load(f)

    wiki_indices = []
    for idx, m in enumerate(movies):
        poster = m.get("poster") or ""
        ppath = m.get("poster_path") or ""
        if "wikimedia" in poster or "wikimedia" in ppath:
            wiki_indices.append((idx, m.get("id"), m.get("title")))

    print(f"Found {len(wiki_indices)} movies with Wikimedia poster URLs.")

    fixed_count = 0
    for idx, mid, title in wiki_indices:
        print(f"Processing ({fixed_count+1}/{len(wiki_indices)}): [{mid}] {title}...")
        full_url, rel_path = get_verified_poster(mid, title)
        if full_url and rel_path:
            movies[idx]["poster"] = full_url
            movies[idx]["poster_path"] = full_url
            print(f"  -> SUCCESS: {full_url}")
            fixed_count += 1
        else:
            print(f"  -> FAILED to find TMDB poster for {title}")
        time.sleep(0.5)

    print(f"\nSuccessfully replaced and verified {fixed_count} / {len(wiki_indices)} posters.")

    # Save updated movies.json
    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)
    print("Saved updated movies.json!")

if __name__ == "__main__":
    main()

