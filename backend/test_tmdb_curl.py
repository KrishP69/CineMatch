import subprocess
import re

p = subprocess.run(["curl.exe", "-s", "-L", "https://www.themoviedb.org/movie/20453-3-idiots"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
print("Length:", len(p.stdout))
og = re.findall(r"https://image\.tmdb\.org/t/p/[^\"]+", p.stdout)
print("Found TMDB images:", og[:5])

