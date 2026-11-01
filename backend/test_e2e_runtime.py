"""
End-to-End Application and API Verification Script for CineMatch
Tests both Vite (5173) and Flask (5000).
"""

import urllib.request
import json
import sys

def test_endpoint(url, desc):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CineMatch-Verifier/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
            print(f"PASS: [{desc}] Status: {status}, Content-Type: {content_type}, Size: {len(data)} bytes")
            if "application/json" in content_type:
                return json.loads(data.decode("utf-8"))
            return data.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"FAIL: [{desc}] Error: {e}")
        return None

def run_e2e_verification():
    print("=" * 70)
    print("RUNNING E2E LOCAL INTEGRATION TESTS")
    print("=" * 70)

    # 1. Test Flask server index & API
    print("\n--- 1. Testing Flask Backend (Port 5000) ---")
    flask_health = test_endpoint("http://127.0.0.1:5000/api/health", "Flask Health Check")
    assert flask_health and flask_health.get("status") == "healthy"

    flask_featured = test_endpoint("http://127.0.0.1:5000/api/featured", "Flask /api/featured")
    assert flask_featured and flask_featured.get("success")
    hero_title = flask_featured["data"]["hero"]["title"]
    sections = len(flask_featured["data"]["sections"])
    print(f"      Hero Spotlight: '{hero_title}', Sections Count: {sections}")

    # 2. Test Vite Dev Server (Port 5173)
    print("\n--- 2. Testing Vite Frontend Dev Server (Port 5173) ---")
    vite_home = test_endpoint("http://127.0.0.1:5173/", "Vite Home HTML Page")
    assert vite_home and "index.html" in vite_home or "<div id=\"root\">" in vite_home

    # 3. Test Vite Proxy to Backend
    print("\n--- 3. Testing Vite Proxy forwarding /api to Flask ---")
    vite_proxy_featured = test_endpoint("http://127.0.0.1:5173/api/featured", "Vite Proxy /api/featured")
    assert vite_proxy_featured and vite_proxy_featured.get("success")

    # 4. Test Movie Catalog & Instant Search
    print("\n--- 4. Testing Movies API ---")
    movies_res = test_endpoint("http://127.0.0.1:5000/api/movies?page=1&per_page=12", "Flask /api/movies")
    assert movies_res and len(movies_res["data"]["movies"]) > 0
    print(f"      Total indexed movies: {movies_res['data']['total']}")

    search_res = test_endpoint("http://127.0.0.1:5000/api/search?q=Inception", "Flask /api/search?q=Inception")
    assert search_res and len(search_res["data"]) > 0

    # 5. Test Dedicated Web Series APIs
    print("\n--- 5. Testing Dedicated Web Series APIs ---")
    tv_trending = test_endpoint("http://127.0.0.1:5000/api/tv/trending?page=1&per_page=10", "GET /api/tv/trending")
    assert tv_trending and len(tv_trending["data"]["shows"]) > 0
    print(f"      Total stored series: {tv_trending['data']['total']}")

    tv_popular = test_endpoint("http://127.0.0.1:5000/api/tv/popular?page=1&per_page=10", "GET /api/tv/popular")
    assert tv_popular and len(tv_popular["data"]["shows"]) > 0

    tv_top = test_endpoint("http://127.0.0.1:5000/api/tv/top-rated?page=1&per_page=10", "GET /api/tv/top-rated")
    assert tv_top and len(tv_top["data"]["shows"]) > 0

    tv_search = test_endpoint("http://127.0.0.1:5000/api/tv/search?q=Lupin", "GET /api/tv/search?q=Lupin")
    assert tv_search and len(tv_search["data"]["shows"]) > 0

    # 6. Test TV Show Detail, Seasons, and Episodes
    sample_show = tv_trending["data"]["shows"][0]
    sample_tmdb_id = sample_show["tmdb_id"]
    sample_name = sample_show["name"]
    print(f"\n--- 6. Testing TV Show Details for '{sample_name}' (TMDB {sample_tmdb_id}) ---")

    tv_detail = test_endpoint(f"http://127.0.0.1:5000/api/tv/{sample_tmdb_id}", f"GET /api/tv/{sample_tmdb_id}")
    assert tv_detail and tv_detail["data"]["name"] == sample_name
    print(f"      Poster URL:   {tv_detail['data']['poster_path']}")
    print(f"      Backdrop URL: {tv_detail['data']['backdrop_path']}")
    print(f"      Seasons count: {len(tv_detail['data']['seasons'])}")

    tv_seasons = test_endpoint(f"http://127.0.0.1:5000/api/tv/{sample_tmdb_id}/seasons", f"GET /api/tv/{sample_tmdb_id}/seasons")
    assert tv_seasons and len(tv_seasons["data"]) > 0

    first_season_num = tv_seasons["data"][0]["season_number"]
    tv_episodes = test_endpoint(f"http://127.0.0.1:5000/api/tv/{sample_tmdb_id}/seasons/{first_season_num}", f"GET Season {first_season_num} episodes")
    assert tv_episodes and tv_episodes.get("success")
    print(f"      Season {first_season_num} episodes count: {len(tv_episodes['season']['episodes'])}")

    print("\n" + "=" * 70)
    print("ALL E2E INTEGRATION & RUNTIME CHECKS PASSED PERFECTLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_e2e_verification()

