"""
CineMatch SQLite Relational Database Engine
Production-grade schema with WAL mode, foreign keys, constraints, and indexes.
Tables:
  - users
  - movies
  - external_ratings
  - user_ratings
  - external_reviews
  - user_reviews
  - review_votes
  - review_reports
  - watchlist
  - watch_history
  - user_preferences
"""

import os
import sqlite3
import json
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cinematch.db")

@contextmanager
def get_db():
    """Provides a SQLite connection with foreign keys and row factory enabled."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initializes schema and tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            avatar TEXT DEFAULT '🎬',
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Movies Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY, -- Matches TMDB ID
            title TEXT NOT NULL,
            original_title TEXT,
            overview TEXT,
            genres TEXT, -- JSON array of genre names
            release_date TEXT,
            release_year INTEGER,
            runtime INTEGER,
            poster_path TEXT,
            backdrop_path TEXT,
            tmdb_rating REAL,
            tmdb_vote_count INTEGER,
            popularity REAL,
            keywords TEXT, -- JSON array or space-separated
            director TEXT,
            cast_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. External Ratings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS external_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
            source TEXT NOT NULL, -- 'TMDB' or 'IMDb' (authorized)
            rating REAL NOT NULL,
            vote_count INTEGER NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(movie_id, source)
        );
        """)

        # 4. User Ratings Table (1 - 10)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, movie_id)
        );
        """)

        # 5. External Reviews Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS external_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            rating REAL,
            url TEXT,
            created_at TEXT
        );
        """)

        # 6. User Reviews Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 10),
            sentiment TEXT NOT NULL CHECK (sentiment IN ('positive', 'neutral', 'negative')),
            sentiment_score REAL NOT NULL,
            contains_spoilers BOOLEAN DEFAULT 0,
            helpful_count INTEGER DEFAULT 0,
            unhelpful_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 7. Review Helpful / Unhelpful Votes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS review_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER NOT NULL REFERENCES user_reviews(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            vote_type INTEGER NOT NULL CHECK (vote_type IN (1, -1)), -- 1 for helpful, -1 for unhelpful
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(review_id, user_id)
        );
        """)

        # 8. Review Moderation Reports
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS review_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER NOT NULL REFERENCES user_reviews(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 9. Watchlist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, movie_id)
        );
        """)

        # 10. Watch History (Already Watched)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS watch_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
            watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_completed BOOLEAN DEFAULT 1,
            UNIQUE(user_id, movie_id)
        );
        """)

        # 11. User Preferences & Taste Profile
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            favorite_genres TEXT, -- JSON
            current_mood TEXT,
            viewing_style TEXT,
            preferred_language TEXT DEFAULT 'Any',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # -------------------------------------------------------------
        # TV SHOWS CORE TABLES
        # -------------------------------------------------------------
        # 12. TV Shows Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tv_shows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tmdb_id INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            original_name TEXT,
            overview TEXT,
            poster_path TEXT,
            backdrop_path TEXT,
            first_air_date TEXT,
            last_air_date TEXT,
            status TEXT,
            original_language TEXT,
            origin_country TEXT, -- JSON array of country codes
            number_of_seasons INTEGER DEFAULT 1,
            number_of_episodes INTEGER DEFAULT 0,
            tmdb_rating REAL DEFAULT 0.0,
            tmdb_vote_count INTEGER DEFAULT 0,
            popularity REAL DEFAULT 0.0,
            genres TEXT, -- JSON array of genre strings or objects
            creators TEXT, -- JSON array of creator names
            networks TEXT, -- JSON array of network names
            metadata_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 13. TV Seasons Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tv_seasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tv_show_id INTEGER NOT NULL REFERENCES tv_shows(id) ON DELETE CASCADE,
            tmdb_season_id INTEGER UNIQUE,
            season_number INTEGER NOT NULL,
            name TEXT,
            overview TEXT,
            poster_path TEXT,
            air_date TEXT,
            episode_count INTEGER DEFAULT 0,
            UNIQUE(tv_show_id, season_number)
        );
        """)

        # 14. TV Episodes Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tv_episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tv_season_id INTEGER NOT NULL REFERENCES tv_seasons(id) ON DELETE CASCADE,
            tmdb_episode_id INTEGER UNIQUE,
            episode_number INTEGER NOT NULL,
            name TEXT,
            overview TEXT,
            air_date TEXT,
            runtime INTEGER,
            still_path TEXT,
            vote_average REAL DEFAULT 0.0,
            UNIQUE(tv_season_id, episode_number)
        );
        """)

        # -------------------------------------------------------------
        # TV SHOWS USER INTERACTION TABLES
        # -------------------------------------------------------------
        # 15. TV User Ratings (1 - 10)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tv_user_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            tv_show_id INTEGER NOT NULL REFERENCES tv_shows(id) ON DELETE CASCADE,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, tv_show_id)
        );
        """)

        # 16. TV User Reviews
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tv_user_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            tv_show_id INTEGER NOT NULL REFERENCES tv_shows(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 10),
            sentiment TEXT NOT NULL CHECK (sentiment IN ('positive', 'neutral', 'negative')),
            sentiment_score REAL NOT NULL,
            contains_spoilers BOOLEAN DEFAULT 0,
            helpful_count INTEGER DEFAULT 0,
            unhelpful_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 17. TV Review Helpful / Unhelpful Votes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tv_review_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER NOT NULL REFERENCES tv_user_reviews(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            vote_type INTEGER NOT NULL CHECK (vote_type IN (1, -1)),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(review_id, user_id)
        );
        """)

        # 18. TV Review Moderation Reports
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tv_review_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER NOT NULL REFERENCES tv_user_reviews(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 19. TV Watchlist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tv_watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            tv_show_id INTEGER NOT NULL REFERENCES tv_shows(id) ON DELETE CASCADE,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, tv_show_id)
        );
        """)

        # 20. TV Watch Progress
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tv_watch_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            tv_show_id INTEGER NOT NULL REFERENCES tv_shows(id) ON DELETE CASCADE,
            status TEXT NOT NULL CHECK (status IN ('watching', 'completed', 'dropped', 'plan_to_watch')),
            watched_season INTEGER DEFAULT 1,
            watched_episode INTEGER DEFAULT 0,
            last_watched_episode TEXT, -- episode name or S01E01 descriptor
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, tv_show_id)
        );
        """)

        # Indexes for query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movies_year ON movies(release_year);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movies_rating ON movies(tmdb_rating);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_ratings_movie ON user_ratings(movie_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_ratings_user ON user_ratings(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_reviews_movie ON user_reviews(movie_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_reviews_user ON user_reviews(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlist(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_watch_history_user ON watch_history(user_id);")

        # TV Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_shows_tmdb ON tv_shows(tmdb_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_shows_first_air ON tv_shows(first_air_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_shows_popularity ON tv_shows(popularity);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_shows_rating ON tv_shows(tmdb_rating);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_seasons_show ON tv_seasons(tv_show_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_seasons_tmdb ON tv_seasons(tmdb_season_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_episodes_season ON tv_episodes(tv_season_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_episodes_tmdb ON tv_episodes(tmdb_episode_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_user_ratings_show ON tv_user_ratings(tv_show_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_user_ratings_user ON tv_user_ratings(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_user_reviews_show ON tv_user_reviews(tv_show_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_user_reviews_user ON tv_user_reviews(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_watchlist_user ON tv_watchlist(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_watchlist_show ON tv_watchlist(tv_show_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_progress_user ON tv_watch_progress(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tv_progress_show ON tv_watch_progress(tv_show_id);")

        logger.info("Initialized CineMatch SQLite database schema successfully.")

def seed_movies_from_json():
    """Seeds the database movies table from movies.json if empty."""
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "movies.json")
    if not os.path.exists(json_path):
        return

    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
        if count > 0:
            return # Already seeded

        with open(json_path, "r", encoding="utf-8") as f:
            movies = json.load(f)

        for m in movies:
            mid = int(m["id"])
            title = m.get("title", "")
            original_title = m.get("original_title", title)
            overview = m.get("overview", "")
            genres = json.dumps(m.get("genres", []))
            release_date = m.get("release_date", "")
            release_year = int(m.get("release_year") or (release_date[:4] if release_date else 2000))
            runtime = int(m.get("runtime", 120))
            poster_path = m.get("poster_path", "")
            backdrop_path = m.get("backdrop_path", "")
            tmdb_rating = float(m.get("vote_average", 7.5))
            tmdb_vote_count = int(m.get("vote_count", 1000))
            popularity = float(m.get("popularity", 50.0))
            keywords = json.dumps(m.get("keywords", []))
            director = m.get("director", "")
            cast_json = json.dumps(m.get("cast", []))

            conn.execute("""
            INSERT OR REPLACE INTO movies (
                id, title, original_title, overview, genres, release_date, release_year,
                runtime, poster_path, backdrop_path, tmdb_rating, tmdb_vote_count,
                popularity, keywords, director, cast_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mid, title, original_title, overview, genres, release_date, release_year,
                runtime, poster_path, backdrop_path, tmdb_rating, tmdb_vote_count,
                popularity, keywords, director, cast_json
            ))

            # Also seed TMDB external rating
            conn.execute("""
            INSERT OR REPLACE INTO external_ratings (movie_id, source, rating, vote_count)
            VALUES (?, 'TMDB', ?, ?)
            """, (mid, tmdb_rating, tmdb_vote_count))

        logger.info(f"Seeded {len(movies)} movies into database.")

if __name__ == "__main__":
    init_db()
    seed_movies_from_json()
    print("Database initialization and movie seeding completed.")

