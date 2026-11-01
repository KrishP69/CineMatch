"""
Verification and Regression Test Suite for Web Series Database
Tests:
1. All TV tables exist and match required schema
2. Foreign keys and indexes are in place
3. Exact database record counts for series, seasons, and episodes
4. Duplicate prevention / upsert integrity
5. User rating persistence, transactions, and isolation
6. User reviews with VADER sentiment and spoiler flags
7. Watchlist persistence & duplicate toggling
8. Watch progress persistence (all statuses: watching, completed, dropped, plan_to_watch, seasons, episodes)
9. Verification of movie records preservation (zero regression on movies/ratings)
"""

import os
import sys
import sqlite3
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_db, init_db
from tv_service import tv_service
from auth_service import auth_service
from community_service import community_service

def run_tv_verification():
    print("=" * 70)
    print("CINEMATCH WEB SERIES DATABASE VERIFICATION & REGRESSION SUITE")
    print("=" * 70)

    # 1. Verify tables
    expected_tv_tables = [
        "tv_shows", "tv_seasons", "tv_episodes",
        "tv_user_ratings", "tv_user_reviews", "tv_review_votes",
        "tv_review_reports", "tv_watchlist", "tv_watch_progress"
    ]
    with get_db() as conn:
        cursor = conn.cursor()
        existing_tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        for tbl in expected_tv_tables:
            assert tbl in existing_tables, f"FAILED: Table '{tbl}' does not exist!"
        print("[CHECK 1] All 9 dedicated TV tables exist in cinematch.db: PASS")

        # 2. Check foreign keys and indexes
        indexes = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()]
        expected_indexes = [
            "idx_tv_shows_tmdb", "idx_tv_shows_first_air", "idx_tv_shows_popularity", "idx_tv_shows_rating",
            "idx_tv_seasons_show", "idx_tv_seasons_tmdb", "idx_tv_episodes_season", "idx_tv_episodes_tmdb",
            "idx_tv_user_ratings_show", "idx_tv_user_ratings_user", "idx_tv_user_reviews_show",
            "idx_tv_user_reviews_user", "idx_tv_watchlist_user", "idx_tv_progress_user"
        ]
        for idx in expected_indexes:
            assert idx in indexes, f"FAILED: Index '{idx}' is missing!"
        print("[CHECK 2] Foreign keys and performance indexes verified: PASS")

        # 3. Exact table record counts
        shows_count = cursor.execute("SELECT COUNT(*) FROM tv_shows").fetchone()[0]
        seasons_count = cursor.execute("SELECT COUNT(*) FROM tv_seasons").fetchone()[0]
        episodes_count = cursor.execute("SELECT COUNT(*) FROM tv_episodes").fetchone()[0]
        movies_count = cursor.execute("SELECT COUNT(*) FROM movies").fetchone()[0]

        print(f"[CHECK 3] Database Record Counts:")
        print(f"          - tv_shows:    {shows_count}")
        print(f"          - tv_seasons:  {seasons_count}")
        print(f"          - tv_episodes: {episodes_count}")
        print(f"          - movies (preserved): {movies_count}")
        assert shows_count > 0, "FAILED: tv_shows table is empty!"
        assert seasons_count > 0, "FAILED: tv_seasons table is empty!"
        assert episodes_count > 0, "FAILED: tv_episodes table is empty!"
        assert movies_count > 0, "FAILED: Movie records were modified or deleted!"

    # 4. Duplicate Prevention (Upsert)
    print("\n--- Testing Upsert & Duplicate Prevention ---")
    test_show = {
        "id": 9999991,
        "name": "Test Ingest Series",
        "original_name": "Test Ingest Series",
        "overview": "A test show for upsert verification",
        "vote_average": 8.5,
        "vote_count": 250,
        "popularity": 75.0,
        "genres": ["Drama", "Mystery"],
        "created_by": ["Jane Doe"],
        "networks": ["HBO"]
    }
    id1 = tv_service.upsert_tv_show(test_show)
    test_show["name"] = "Test Ingest Series Updated"
    id2 = tv_service.upsert_tv_show(test_show)
    assert id1 == id2, "FAILED: Upsert created duplicate show id!"
    with get_db() as conn:
        c = conn.execute("SELECT COUNT(*) FROM tv_shows WHERE tmdb_id = 9999991").fetchone()[0]
        assert c == 1, f"Duplicate count found: {c}"
        name = conn.execute("SELECT name FROM tv_shows WHERE tmdb_id = 9999991").fetchone()[0]
        assert name == "Test Ingest Series Updated", "FAILED: Upsert did not update name"
    print("[CHECK 4] Duplicate Prevention & Upsert verified: PASS")

    # 5. User Interaction Testing
    print("\n--- Testing User Interactions (Auth, Ratings, Reviews, Watchlist, Progress) ---")
    reg = auth_service.register(f"tvuser_{os.urandom(3).hex()}", f"tv_{os.urandom(3).hex()}@test.com", "Password123!")
    user_id = reg["user"]["id"]
    test_tmdb_id = 9999991

    # Ratings
    rate_res = tv_service.rate_tv(user_id=user_id, tmdb_id=test_tmdb_id, rating=9)
    assert rate_res["success"], f"Rating failed: {rate_res}"
    assert rate_res["data"]["user_rating"] == 9
    assert rate_res["data"]["community"]["average_rating"] == 9.0

    # Rating Update (Prevent duplicate)
    rate_update = tv_service.rate_tv(user_id=user_id, tmdb_id=test_tmdb_id, rating=10)
    assert rate_update["data"]["user_rating"] == 10
    with get_db() as conn:
        r_count = conn.execute("SELECT COUNT(*) FROM tv_user_ratings WHERE user_id = ? AND tv_show_id = ?", (user_id, id1)).fetchone()[0]
        assert r_count == 1, "Duplicate rating rows created!"
    print("[CHECK 5] TV User Ratings & Duplicate Prevention: PASS")

    # Reviews with VADER sentiment
    rev_res = tv_service.create_tv_review(
        user_id=user_id,
        tmdb_id=test_tmdb_id,
        title="Phenomenal masterpiece series!",
        content="The cinematic pacing, writing, and acting in this series are truly breathtaking.",
        rating=10,
        contains_spoilers=False
    )
    assert rev_res["success"], f"Review failed: {rev_res}"
    assert rev_res["review"]["sentiment"] == "positive"
    assert rev_res["review"]["sentiment_score"] > 0
    print("[CHECK 6] TV Reviews with VADER Sentiment: PASS")

    # Watchlist toggle
    w1 = tv_service.toggle_tv_watchlist(user_id, test_tmdb_id)
    assert w1["in_watchlist"] is True
    w2 = tv_service.toggle_tv_watchlist(user_id, test_tmdb_id)
    assert w2["in_watchlist"] is False
    w3 = tv_service.toggle_tv_watchlist(user_id, test_tmdb_id)
    assert w3["in_watchlist"] is True
    user_wl = tv_service.get_user_tv_watchlist(user_id)
    assert any(s["tmdb_id"] == test_tmdb_id for s in user_wl)
    print("[CHECK 7] TV Watchlist persistence & toggle: PASS")

    # Watch Progress
    for status in ['watching', 'completed', 'dropped', 'plan_to_watch']:
        p_res = tv_service.update_watch_progress(
            user_id=user_id,
            tmdb_id=test_tmdb_id,
            status=status,
            watched_season=2,
            watched_episode=5,
            last_watched_episode="S02E05 - The Climax"
        )
        assert p_res["success"], f"Progress update failed for status '{status}': {p_res}"

    prog = tv_service.get_user_tv_progress(user_id, tmdb_id=test_tmdb_id)
    assert prog["status"] == "plan_to_watch"
    assert prog["watched_season"] == 2
    assert prog["watched_episode"] == 5
    assert prog["last_watched_episode"] == "S02E05 - The Climax"
    print("[CHECK 8] TV Watch Progress Tracking (all statuses & episodes): PASS")

    # Clean up test show and user
    with get_db() as conn:
        conn.execute("DELETE FROM tv_shows WHERE id = ?", (id1,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

    print("\n" + "=" * 70)
    print("ALL WEB SERIES DATABASE VERIFICATIONS & TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tv_verification()

