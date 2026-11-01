"""
Initial TMDB TV Ingestion Script
Fetches real, rich metadata from TMDB across:
- Popular TV series (multiple pages)
- Top Rated TV series
- Trending TV series
- On The Air / Currently Airing series

Stores shows persistently in tv_shows, tv_seasons, and tv_episodes.
Ensures idempotency, transactional upserts, and zero duplicate entries.
"""

import os
import sys
import time
import requests
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import init_db, get_db
from tv_service import tv_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_tv")

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "a07e22bc18f5cb106bfe4cc1f83ad8ed").strip()
BASE_URL = "https://api.themoviedb.org/3"

def fetch_json(endpoint: str, params: dict = None):
    all_params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    if params:
        all_params.update(params)
    url = f"{BASE_URL}/{endpoint}"
    resp = requests.get(url, params=all_params, headers={"User-Agent": "CineMatch-Ingestion/1.0"}, timeout=12)
    if resp.status_code == 200:
        return resp.json()
    else:
        logger.warning(f"Endpoint {endpoint} failed with code {resp.status_code}")
        return None

def ingest_catalogue(max_pages_per_category: int = 2):
    """
    Ingests TV shows from Trending, Popular, Top Rated, and On The Air.
    Also ingests all seasons and first-season episode details for deep rich seed metadata.
    """
    init_db()
    endpoints = [
        ("trending/tv/week", {}),
        ("tv/popular", {}),
        ("tv/top_rated", {}),
        ("tv/on_the_air", {})
    ]

    seen_tmdb_ids = set()
    show_summaries = []

    for endpoint, base_params in endpoints:
        logger.info(f"Ingesting endpoint: {endpoint} (pages 1 to {max_pages_per_category})...")
        for page in range(1, max_pages_per_category + 1):
            p = dict(base_params)
            p["page"] = page
            data = fetch_json(endpoint, p)
            if not data or "results" not in data:
                continue

            for item in data["results"]:
                tid = item.get("id")
                if tid and tid not in seen_tmdb_ids:
                    seen_tmdb_ids.add(tid)
                    show_summaries.append(item)

    logger.info(f"Discovered {len(show_summaries)} unique TV series to ingest.")

    ingested_shows = 0
    ingested_seasons = 0
    ingested_episodes = 0

    with get_db() as conn:
        for idx, summary in enumerate(show_summaries, start=1):
            tmdb_id = summary["id"]
            name = summary.get("name", "Unknown")
            logger.info(f"[{idx}/{len(show_summaries)}] Processing '{name}' (TMDB {tmdb_id})...")

            # Fetch detailed show information (includes creators, networks, seasons list)
            details = tv_service.fetch_tmdb_tv_details(tmdb_id)
            if not details:
                # Fallback to summary
                details = summary

            tv_show_id = tv_service.upsert_tv_show(details, conn=conn)
            ingested_shows += 1

            # Ingest seasons
            seasons = details.get("seasons", [])
            for s in seasons:
                s_num = s.get("season_number", 1)
                # Store season record
                tv_season_id = tv_service.upsert_tv_season(tv_show_id, s, conn=conn)
                ingested_seasons += 1

                # For Season 1 of each show, ingest its complete episode breakdown
                if s_num == 1:
                    s_details = tv_service.fetch_tmdb_season_details(tmdb_id, 1)
                    if s_details and "episodes" in s_details:
                        for ep in s_details["episodes"]:
                            tv_service.upsert_tv_episode(tv_season_id, ep, conn=conn)
                            ingested_episodes += 1

            # Commit periodically
            if idx % 10 == 0:
                conn.commit()

        conn.commit()

    logger.info("Ingestion completed successfully!")
    logger.info(f"Total shows in DB: {ingested_shows}, seasons: {ingested_seasons}, episodes: {ingested_episodes}")

if __name__ == "__main__":
    ingest_catalogue(max_pages_per_category=2)

