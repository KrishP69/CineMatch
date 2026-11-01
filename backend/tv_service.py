"""
CineMatch Dedicated TV Database Service
Handles:
- TMDB API fetching, syncing and caching for TV Shows, Seasons, and Episodes
- Relational UPSERT operations (tv_shows, tv_seasons, tv_episodes)
- Dedicated TV user interactions: ratings (1-10), explainable reviews with VADER sentiment, review voting & reports
- Watchlist management and detailed Watch Progress tracking
- Efficient catalog browsing, searching, and filtering
"""

import os
import json
import logging
import datetime
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from database import get_db

# Ensure .env is loaded
load_dotenv()

logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()

class TVService:
    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY", "").strip() or "a07e22bc18f5cb106bfe4cc1f83ad8ed"
        self.base_url = "https://api.themoviedb.org/3"
        self._cache: Dict[str, Any] = {}

    def _get_api_key(self) -> str:
        if not self.api_key:
            self.api_key = os.getenv("TMDB_API_KEY", "").strip() or "a07e22bc18f5cb106bfe4cc1f83ad8ed"
        return self.api_key

    def _classify_sentiment(self, text: str):
        scores = analyzer.polarity_scores(text)
        compound = scores["compound"]
        if compound >= 0.05:
            sentiment = "positive"
        elif compound <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        return sentiment, compound, scores

    # -------------------------------------------------------------
    # TMDB API INGESTION & UPSERT HELPERS
    # -------------------------------------------------------------
    def fetch_tmdb_tv_details(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """Fetches full TV show details from TMDB with caching."""
        api_key = self._get_api_key()
        if not api_key:
            logger.warning("TMDB_API_KEY is not configured.")
            return None

        cache_key = f"tv_details_{tmdb_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            url = f"{self.base_url}/tv/{tmdb_id}"
            resp = requests.get(
                url,
                params={"api_key": api_key, "language": "en-US", "append_to_response": "credits,external_ids"},
                headers={"User-Agent": "CineMatch/1.0"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                self._cache[cache_key] = data
                return data
            else:
                logger.warning(f"TMDB /tv/{tmdb_id} returned status {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching TV details for TMDB {tmdb_id}: {e}")
            return None

    def fetch_tmdb_season_details(self, tmdb_id: int, season_number: int) -> Optional[Dict[str, Any]]:
        """Fetches detailed season & episode metadata from TMDB."""
        api_key = self._get_api_key()
        if not api_key:
            return None

        cache_key = f"tv_season_{tmdb_id}_{season_number}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            url = f"{self.base_url}/tv/{tmdb_id}/season/{season_number}"
            resp = requests.get(
                url,
                params={"api_key": api_key, "language": "en-US"},
                headers={"User-Agent": "CineMatch/1.0"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                self._cache[cache_key] = data
                return data
            else:
                logger.warning(f"TMDB /tv/{tmdb_id}/season/{season_number} returned status {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching season {season_number} for TV {tmdb_id}: {e}")
            return None

    def upsert_tv_show(self, data: Dict[str, Any], conn=None) -> int:
        """
        UPSERTs a TV show record into tv_shows table.
        Returns the internal database primary key id.
        """
        def _execute(c):
            cursor = c.cursor()
            tmdb_id = int(data["id"] if "id" in data and "tmdb_id" not in data else data.get("tmdb_id", data.get("id")))
            name = data.get("name") or data.get("original_name") or f"TV Show {tmdb_id}"
            original_name = data.get("original_name", name)
            overview = data.get("overview") or ""
            
            # Poster and backdrop safely formatted with full TMDB CDN URLs
            poster = data.get("poster_path") or ""
            if poster and not poster.startswith("http"):
                if not poster.startswith("/"):
                    poster = "/" + poster
                poster = "https://image.tmdb.org/t/p/w500" + poster
            backdrop = data.get("backdrop_path") or ""
            if backdrop and not backdrop.startswith("http"):
                if not backdrop.startswith("/"):
                    backdrop = "/" + backdrop
                backdrop = "https://image.tmdb.org/t/p/original" + backdrop

            first_air_date = data.get("first_air_date") or ""
            last_air_date = data.get("last_air_date") or first_air_date
            status = data.get("status") or "Ended"
            original_language = data.get("original_language") or "en"
            
            origin_country = data.get("origin_country", [])
            if isinstance(origin_country, list):
                origin_country_json = json.dumps(origin_country)
            else:
                origin_country_json = json.dumps([str(origin_country)])

            num_seasons = int(data.get("number_of_seasons") or len(data.get("seasons", [])) or 1)
            num_episodes = int(data.get("number_of_episodes") or 0)
            tmdb_rating = float(data.get("vote_average") or data.get("tmdb_rating") or 0.0)
            tmdb_vote_count = int(data.get("vote_count") or data.get("tmdb_vote_count") or 0)
            popularity = float(data.get("popularity") or 0.0)

            # Genres
            raw_genres = data.get("genres", [])
            if raw_genres and isinstance(raw_genres, list):
                if isinstance(raw_genres[0], dict):
                    genres_list = [g.get("name") for g in raw_genres if g.get("name")]
                else:
                    genres_list = [str(g) for g in raw_genres]
            else:
                genres_list = []
            genres_json = json.dumps(genres_list)

            # Creators
            raw_creators = data.get("created_by", data.get("creators", []))
            if raw_creators and isinstance(raw_creators, list):
                if isinstance(raw_creators[0], dict):
                    creators_list = [c.get("name") for c in raw_creators if c.get("name")]
                else:
                    creators_list = [str(c) for c in raw_creators]
            else:
                creators_list = []
            creators_json = json.dumps(creators_list)

            # Networks
            raw_networks = data.get("networks", [])
            if raw_networks and isinstance(raw_networks, list):
                if isinstance(raw_networks[0], dict):
                    networks_list = [n.get("name") for n in raw_networks if n.get("name")]
                else:
                    networks_list = [str(n) for n in raw_networks]
            else:
                networks_list = []
            networks_json = json.dumps(networks_list)

            cursor.execute("""
            INSERT INTO tv_shows (
                tmdb_id, name, original_name, overview, poster_path, backdrop_path,
                first_air_date, last_air_date, status, original_language, origin_country,
                number_of_seasons, number_of_episodes, tmdb_rating, tmdb_vote_count,
                popularity, genres, creators, networks, metadata_updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(tmdb_id) DO UPDATE SET
                name = excluded.name,
                original_name = excluded.original_name,
                overview = excluded.overview,
                poster_path = CASE WHEN excluded.poster_path != '' THEN excluded.poster_path ELSE tv_shows.poster_path END,
                backdrop_path = CASE WHEN excluded.backdrop_path != '' THEN excluded.backdrop_path ELSE tv_shows.backdrop_path END,
                first_air_date = excluded.first_air_date,
                last_air_date = excluded.last_air_date,
                status = excluded.status,
                original_language = excluded.original_language,
                origin_country = excluded.origin_country,
                number_of_seasons = excluded.number_of_seasons,
                number_of_episodes = excluded.number_of_episodes,
                tmdb_rating = excluded.tmdb_rating,
                tmdb_vote_count = excluded.tmdb_vote_count,
                popularity = excluded.popularity,
                genres = excluded.genres,
                creators = excluded.creators,
                networks = excluded.networks,
                metadata_updated_at = CURRENT_TIMESTAMP
            """, (
                tmdb_id, name, original_name, overview, poster, backdrop,
                first_air_date, last_air_date, status, original_language, origin_country_json,
                num_seasons, num_episodes, tmdb_rating, tmdb_vote_count,
                popularity, genres_json, creators_json, networks_json
            ))

            row = cursor.execute("SELECT id FROM tv_shows WHERE tmdb_id = ?", (tmdb_id,)).fetchone()
            return row["id"]

        if conn is not None:
            return _execute(conn)
        else:
            with get_db() as db_conn:
                return _execute(db_conn)

    def upsert_tv_season(self, tv_show_id: int, season_data: Dict[str, Any], conn=None) -> int:
        """UPSERTs a single season record into tv_seasons."""
        def _execute(c):
            cursor = c.cursor()
            season_num = int(season_data.get("season_number", 1))
            tmdb_season_id = season_data.get("id") or season_data.get("tmdb_season_id")
            name = season_data.get("name") or f"Season {season_num}"
            overview = season_data.get("overview") or ""
            poster = season_data.get("poster_path") or ""
            if poster and not poster.startswith("http"):
                if not poster.startswith("/"):
                    poster = "/" + poster
                poster = "https://image.tmdb.org/t/p/w500" + poster
            air_date = season_data.get("air_date") or ""
            ep_count = int(season_data.get("episode_count") or len(season_data.get("episodes", [])) or 0)

            cursor.execute("""
            INSERT INTO tv_seasons (
                tv_show_id, tmdb_season_id, season_number, name, overview, poster_path, air_date, episode_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(tv_show_id, season_number) DO UPDATE SET
                tmdb_season_id = coalesce(excluded.tmdb_season_id, tv_seasons.tmdb_season_id),
                name = excluded.name,
                overview = excluded.overview,
                poster_path = CASE WHEN excluded.poster_path != '' THEN excluded.poster_path ELSE tv_seasons.poster_path END,
                air_date = excluded.air_date,
                episode_count = excluded.episode_count
            """, (tv_show_id, tmdb_season_id, season_num, name, overview, poster, air_date, ep_count))

            row = cursor.execute("SELECT id FROM tv_seasons WHERE tv_show_id = ? AND season_number = ?", (tv_show_id, season_num)).fetchone()
            return row["id"]

        if conn is not None:
            return _execute(conn)
        else:
            with get_db() as db_conn:
                return _execute(db_conn)

    def upsert_tv_episode(self, tv_season_id: int, ep_data: Dict[str, Any], conn=None) -> int:
        """UPSERTs an episode record into tv_episodes."""
        def _execute(c):
            cursor = c.cursor()
            ep_num = int(ep_data.get("episode_number", 1))
            tmdb_ep_id = ep_data.get("id") or ep_data.get("tmdb_episode_id")
            name = ep_data.get("name") or f"Episode {ep_num}"
            overview = ep_data.get("overview") or ""
            air_date = ep_data.get("air_date") or ""
            runtime = ep_data.get("runtime")
            runtime_int = int(runtime) if runtime is not None else None
            still_path = ep_data.get("still_path") or ""
            if still_path and not still_path.startswith("http"):
                if not still_path.startswith("/"):
                    still_path = "/" + still_path
                still_path = "https://image.tmdb.org/t/p/w500" + still_path
            vote_avg = float(ep_data.get("vote_average") or 0.0)

            cursor.execute("""
            INSERT INTO tv_episodes (
                tv_season_id, tmdb_episode_id, episode_number, name, overview, air_date, runtime, still_path, vote_average
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(tv_season_id, episode_number) DO UPDATE SET
                tmdb_episode_id = coalesce(excluded.tmdb_episode_id, tv_episodes.tmdb_episode_id),
                name = excluded.name,
                overview = excluded.overview,
                air_date = excluded.air_date,
                runtime = excluded.runtime,
                still_path = CASE WHEN excluded.still_path != '' THEN excluded.still_path ELSE tv_episodes.still_path END,
                vote_average = excluded.vote_average
            """, (tv_season_id, tmdb_ep_id, ep_num, name, overview, air_date, runtime_int, still_path, vote_avg))

            row = cursor.execute("SELECT id FROM tv_episodes WHERE tv_season_id = ? AND episode_number = ?", (tv_season_id, ep_num)).fetchone()
            return row["id"]

        if conn is not None:
            return _execute(conn)
        else:
            with get_db() as db_conn:
                return _execute(db_conn)

    def sync_full_tv_show(self, tmdb_id: int, fetch_episodes_for_season: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Synchronizes a complete show from TMDB into the database.
        Optionally fetches and stores all episode records for a specific season.
        """
        details = self.fetch_tmdb_tv_details(tmdb_id)
        if not details:
            return None

        with get_db() as conn:
            tv_show_id = self.upsert_tv_show(details, conn=conn)

            # Insert / update all seasons listed in the details
            for s in details.get("seasons", []):
                s_num = s.get("season_number", 0)
                # Skip specials (season 0) if desired, or keep them
                tv_season_id = self.upsert_tv_season(tv_show_id, s, conn=conn)

                # If requested, fetch episode details for this season
                if fetch_episodes_for_season is not None and s_num == fetch_episodes_for_season:
                    season_details = self.fetch_tmdb_season_details(tmdb_id, s_num)
                    if season_details and "episodes" in season_details:
                        for ep in season_details["episodes"]:
                            self.upsert_tv_episode(tv_season_id, ep, conn=conn)

        return self.get_tv_by_tmdb_id(tmdb_id)

    # -------------------------------------------------------------
    # CATALOG QUERY METHODS
    # -------------------------------------------------------------
    def _format_show_row(self, row) -> Dict[str, Any]:
        if not row:
            return None
        d = dict(row)
        for key in ["genres", "creators", "networks", "origin_country"]:
            if key in d and isinstance(d[key], str):
                try:
                    d[key] = json.loads(d[key])
                except Exception:
                    d[key] = []
        return d

    def get_tv_by_tmdb_id(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a TV show by TMDB ID from the database."""
        with get_db() as conn:
            cursor = conn.cursor()
            row = cursor.execute("SELECT * FROM tv_shows WHERE tmdb_id = ?", (tmdb_id,)).fetchone()
            if not row:
                return None
            show = self._format_show_row(row)

            # Attach seasons
            seasons = cursor.execute("""
            SELECT * FROM tv_seasons WHERE tv_show_id = ? ORDER BY season_number ASC
            """, (show["id"],)).fetchall()
            show["seasons"] = [dict(s) for s in seasons]
            return show

    def get_tv_by_id(self, internal_id: int) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            row = cursor.execute("SELECT * FROM tv_shows WHERE id = ?", (internal_id,)).fetchone()
            return self._format_show_row(row)

    def get_shows(self, category: Optional[str] = None, genre: Optional[str] = None,
                  min_rating: Optional[float] = None, sort_by: str = "popularity",
                  page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Lists or filters TV shows persistently stored in cinematch.db.
        category: 'trending', 'popular', 'top_rated', or None
        """
        with get_db() as conn:
            cursor = conn.cursor()
            conditions = []
            params = []

            if category == "top_rated" or sort_by == "rating":
                order_by = "tmdb_rating DESC, tmdb_vote_count DESC"
            elif category == "trending" or sort_by == "popularity":
                order_by = "popularity DESC, tmdb_rating DESC"
            elif sort_by == "newest":
                order_by = "first_air_date DESC"
            elif sort_by == "name":
                order_by = "name ASC"
            else:
                order_by = "popularity DESC"

            if genre:
                conditions.append("genres LIKE ?")
                params.append(f"%{genre}%")

            if min_rating:
                conditions.append("tmdb_rating >= ?")
                params.append(float(min_rating))

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            # Count total
            count_query = f"SELECT COUNT(*) FROM tv_shows {where_clause}"
            total = cursor.execute(count_query, params).fetchone()[0]

            offset = (page - 1) * per_page
            data_query = f"SELECT * FROM tv_shows {where_clause} ORDER BY {order_by} LIMIT ? OFFSET ?"
            query_params = params + [per_page, offset]

            rows = cursor.execute(data_query, query_params).fetchall()
            shows = [self._format_show_row(r) for r in rows]

            return {
                "shows": shows,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": max(1, (total + per_page - 1) // per_page)
            }

    def search_tv(self, query: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Efficient full text / keyword search on name, original_name, overview, genres."""
        query = query.strip()
        if not query:
            return self.get_shows(page=page, per_page=per_page)

        with get_db() as conn:
            cursor = conn.cursor()
            like_pat = f"%{query}%"
            where_sql = """
            WHERE name LIKE ? OR original_name LIKE ? OR overview LIKE ? OR genres LIKE ? OR creators LIKE ?
            """
            params = [like_pat, like_pat, like_pat, like_pat, like_pat]

            count_sql = f"SELECT COUNT(*) FROM tv_shows {where_sql}"
            total = cursor.execute(count_sql, params).fetchone()[0]

            offset = (page - 1) * per_page
            data_sql = f"""
            SELECT * FROM tv_shows {where_sql}
            ORDER BY
                CASE WHEN name LIKE ? THEN 0 ELSE 1 END,
                popularity DESC
            LIMIT ? OFFSET ?
            """
            rows = cursor.execute(data_sql, params + [f"{query}%", per_page, offset]).fetchall()
            shows = [self._format_show_row(r) for r in rows]

            return {
                "shows": shows,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": max(1, (total + per_page - 1) // per_page),
                "query": query
            }

    def get_seasons(self, tmdb_id: int) -> List[Dict[str, Any]]:
        """Returns all stored seasons for a show."""
        show = self.get_tv_by_tmdb_id(tmdb_id)
        if not show:
            # Sync on-demand if missing
            show = self.sync_full_tv_show(tmdb_id)
            if not show:
                return []

        with get_db() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("""
            SELECT * FROM tv_seasons WHERE tv_show_id = ? ORDER BY season_number ASC
            """, (show["id"],)).fetchall()
            return [dict(r) for r in rows]

    def get_season_episodes(self, tmdb_id: int, season_number: int) -> Dict[str, Any]:
        """
        Returns season metadata along with all episode records.
        Lazily syncs episode records from TMDB if not yet cached in db.
        """
        show = self.get_tv_by_tmdb_id(tmdb_id)
        if not show:
            show = self.sync_full_tv_show(tmdb_id)
            if not show:
                return {"success": False, "error": f"TV Show TMDB {tmdb_id} not found"}

        with get_db() as conn:
            cursor = conn.cursor()
            s_row = cursor.execute("""
            SELECT * FROM tv_seasons WHERE tv_show_id = ? AND season_number = ?
            """, (show["id"], season_number)).fetchone()

            # If season doesn't exist or has 0 episodes in db, fetch from TMDB
            need_fetch = False
            if not s_row:
                need_fetch = True
            else:
                ep_count = cursor.execute("SELECT COUNT(*) FROM tv_episodes WHERE tv_season_id = ?", (s_row["id"],)).fetchone()[0]
                if ep_count == 0:
                    need_fetch = True

            if need_fetch:
                # Ingest episodes from TMDB
                season_meta = self.fetch_tmdb_season_details(tmdb_id, season_number)
                if season_meta:
                    s_id = self.upsert_tv_season(show["id"], season_meta, conn=conn)
                    for ep in season_meta.get("episodes", []):
                        self.upsert_tv_episode(s_id, ep, conn=conn)
                    s_row = cursor.execute("SELECT * FROM tv_seasons WHERE id = ?", (s_id,)).fetchone()

            if not s_row:
                return {"success": False, "error": f"Season {season_number} not found for TMDB {tmdb_id}"}

            season_dict = dict(s_row)
            ep_rows = cursor.execute("""
            SELECT * FROM tv_episodes WHERE tv_season_id = ? ORDER BY episode_number ASC
            """, (season_dict["id"],)).fetchall()
            season_dict["episodes"] = [dict(ep) for ep in ep_rows]

            return {
                "success": True,
                "tv_show": {
                    "id": show["id"],
                    "tmdb_id": show["tmdb_id"],
                    "name": show["name"],
                    "poster_path": show["poster_path"]
                },
                "season": season_dict
            }

    # -------------------------------------------------------------
    # USER INTERACTIONS: RATINGS & REVIEWS
    # -------------------------------------------------------------
    def _ensure_tv_exists(self, conn, tmdb_id: int) -> int:
        cursor = conn.cursor()
        row = cursor.execute("SELECT id FROM tv_shows WHERE tmdb_id = ?", (tmdb_id,)).fetchone()
        if row:
            return row["id"]
        # Try fetching & inserting from TMDB
        show = self.sync_full_tv_show(tmdb_id)
        if show:
            return show["id"]
        # Fallback dummy placeholder if offline
        cursor.execute("INSERT OR IGNORE INTO tv_shows (tmdb_id, name) VALUES (?, ?)", (tmdb_id, f"TV Show {tmdb_id}"))
        row = cursor.execute("SELECT id FROM tv_shows WHERE tmdb_id = ?", (tmdb_id,)).fetchone()
        return row["id"]

    def rate_tv(self, user_id: int, tmdb_id: int, rating: int) -> Dict[str, Any]:
        if not (1 <= rating <= 10):
            return {"success": False, "error": "Rating must be an integer between 1 and 10"}

        with get_db() as conn:
            tv_show_id = self._ensure_tv_exists(conn, tmdb_id)
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO tv_user_ratings (user_id, tv_show_id, rating, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, tv_show_id) DO UPDATE SET
                rating = excluded.rating,
                updated_at = CURRENT_TIMESTAMP
            """, (user_id, tv_show_id, rating))
            conn.commit()

            summary = self.get_tv_ratings_summary(tmdb_id, user_id=user_id, conn=conn)
            return {"success": True, "data": summary}

    def delete_tv_rating(self, user_id: int, tmdb_id: int) -> Dict[str, Any]:
        with get_db() as conn:
            tv_show_id = self._ensure_tv_exists(conn, tmdb_id)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tv_user_ratings WHERE user_id = ? AND tv_show_id = ?", (user_id, tv_show_id))
            conn.commit()
            summary = self.get_tv_ratings_summary(tmdb_id, user_id=user_id, conn=conn)
            return {"success": True, "data": summary}

    def get_tv_ratings_summary(self, tmdb_id: int, user_id: Optional[int] = None, conn=None) -> Dict[str, Any]:
        def _execute(c):
            cursor = c.cursor()
            row = cursor.execute("SELECT id, tmdb_rating, tmdb_vote_count FROM tv_shows WHERE tmdb_id = ?", (tmdb_id,)).fetchone()
            if not row:
                return {
                    "tmdb_id": tmdb_id,
                    "community": {"average_rating": None, "total_ratings": 0, "distribution": {i: 0 for i in range(1, 11)}},
                    "user_rating": None,
                    "tmdb_rating": None
                }

            tv_show_id = row["id"]
            stat_row = cursor.execute("""
            SELECT AVG(rating) as avg_rating, COUNT(rating) as total_ratings
            FROM tv_user_ratings WHERE tv_show_id = ?
            """, (tv_show_id,)).fetchone()

            avg_rating = round(stat_row["avg_rating"], 1) if stat_row["avg_rating"] is not None else None
            total_ratings = stat_row["total_ratings"] or 0

            dist_rows = cursor.execute("""
            SELECT rating, COUNT(*) as count FROM tv_user_ratings WHERE tv_show_id = ? GROUP BY rating
            """, (tv_show_id,)).fetchall()
            distribution = {r: 0 for r in range(1, 11)}
            for dr in dist_rows:
                distribution[dr["rating"]] = dr["count"]

            user_rating = None
            if user_id:
                ur = cursor.execute("SELECT rating FROM tv_user_ratings WHERE user_id = ? AND tv_show_id = ?", (user_id, tv_show_id)).fetchone()
                if ur:
                    user_rating = ur["rating"]

            return {
                "tmdb_id": tmdb_id,
                "tv_show_id": tv_show_id,
                "community": {
                    "average_rating": avg_rating,
                    "total_ratings": total_ratings,
                    "distribution": distribution
                },
                "user_rating": user_rating,
                "tmdb_rating": {
                    "rating": row["tmdb_rating"],
                    "vote_count": row["tmdb_vote_count"]
                }
            }

        if conn is not None:
            return _execute(conn)
        else:
            with get_db() as db_conn:
                return _execute(db_conn)

    def create_tv_review(self, user_id: int, tmdb_id: int, title: str, content: str,
                         rating: int, contains_spoilers: bool = False) -> Dict[str, Any]:
        title = title.strip()
        content = content.strip()
        if len(title) < 3:
            return {"success": False, "error": "Review title must be at least 3 characters"}
        if len(content) < 10:
            return {"success": False, "error": "Review description must be at least 10 characters"}
        if not (1 <= rating <= 10):
            return {"success": False, "error": "Rating must be between 1 and 10"}

        sentiment, compound, breakdown = self._classify_sentiment(f"{title}. {content}")

        with get_db() as conn:
            tv_show_id = self._ensure_tv_exists(conn, tmdb_id)
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO tv_user_reviews (
                user_id, tv_show_id, title, content, rating, sentiment,
                sentiment_score, contains_spoilers
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, tv_show_id, title, content, rating, sentiment, compound, 1 if contains_spoilers else 0))
            review_id = cursor.lastrowid

            # Sync user rating
            cursor.execute("""
            INSERT INTO tv_user_ratings (user_id, tv_show_id, rating, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, tv_show_id) DO UPDATE SET
                rating = excluded.rating,
                updated_at = CURRENT_TIMESTAMP
            """, (user_id, tv_show_id, rating))

            return {
                "success": True,
                "review": {
                    "id": review_id,
                    "title": title,
                    "content": content,
                    "rating": rating,
                    "sentiment": sentiment,
                    "sentiment_score": compound,
                    "contains_spoilers": contains_spoilers
                }
            }

    def get_tv_reviews(self, tmdb_id: int, sort_by: str = "most_helpful",
                       page: int = 1, per_page: int = 10, current_user_id: Optional[int] = None) -> Dict[str, Any]:
        order_clause = "r.helpful_count DESC, r.created_at DESC"
        if sort_by == "newest":
            order_clause = "r.created_at DESC"
        elif sort_by == "highest_rated":
            order_clause = "r.rating DESC, r.created_at DESC"
        elif sort_by == "lowest_rated":
            order_clause = "r.rating ASC, r.created_at DESC"

        with get_db() as conn:
            cursor = conn.cursor()
            show = cursor.execute("SELECT id FROM tv_shows WHERE tmdb_id = ?", (tmdb_id,)).fetchone()
            if not show:
                return {"reviews": [], "total": 0, "page": page, "total_pages": 1}

            tv_show_id = show["id"]
            count_row = cursor.execute("SELECT COUNT(*) FROM tv_user_reviews WHERE tv_show_id = ?", (tv_show_id,)).fetchone()
            total = count_row[0] if count_row else 0

            offset = (page - 1) * per_page
            query = f"""
            SELECT
                r.*,
                u.username,
                u.avatar
            FROM tv_user_reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.tv_show_id = ?
            ORDER BY {order_clause}
            LIMIT ? OFFSET ?
            """
            rows = cursor.execute(query, (tv_show_id, per_page, offset)).fetchall()

            reviews = []
            for r in rows:
                rev = dict(r)
                rev["user_vote"] = 0
                if current_user_id:
                    v_row = cursor.execute("SELECT vote_type FROM tv_review_votes WHERE review_id = ? AND user_id = ?", (rev["id"], current_user_id)).fetchone()
                    if v_row:
                        rev["user_vote"] = v_row["vote_type"]
                reviews.append(rev)

            return {
                "reviews": reviews,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": max(1, (total + per_page - 1) // per_page)
            }

    def vote_tv_review(self, review_id: int, user_id: int, vote_type: int) -> Dict[str, Any]:
        if vote_type not in (1, -1):
            return {"success": False, "error": "Vote type must be 1 (helpful) or -1 (unhelpful)"}

        with get_db() as conn:
            cursor = conn.cursor()
            rev = cursor.execute("SELECT user_id FROM tv_user_reviews WHERE id = ?", (review_id,)).fetchone()
            if not rev:
                return {"success": False, "error": "Review not found"}
            if rev["user_id"] == user_id:
                return {"success": False, "error": "You cannot vote on your own review"}

            cursor.execute("""
            INSERT INTO tv_review_votes (review_id, user_id, vote_type)
            VALUES (?, ?, ?)
            ON CONFLICT(review_id, user_id) DO UPDATE SET vote_type = excluded.vote_type
            """, (review_id, user_id, vote_type))

            # Recalculate helpful & unhelpful counts
            counts = cursor.execute("""
            SELECT
                SUM(CASE WHEN vote_type = 1 THEN 1 ELSE 0 END) as helpful,
                SUM(CASE WHEN vote_type = -1 THEN 1 ELSE 0 END) as unhelpful
            FROM tv_review_votes WHERE review_id = ?
            """, (review_id,)).fetchone()

            cursor.execute("""
            UPDATE tv_user_reviews
            SET helpful_count = ?, unhelpful_count = ?
            WHERE id = ?
            """, (counts["helpful"] or 0, counts["unhelpful"] or 0, review_id))

            return {
                "success": True,
                "helpful_count": counts["helpful"] or 0,
                "unhelpful_count": counts["unhelpful"] or 0,
                "user_vote": vote_type
            }

    def report_tv_review(self, review_id: int, user_id: int, reason: str) -> Dict[str, Any]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO tv_review_reports (review_id, user_id, reason)
            VALUES (?, ?, ?)
            """, (review_id, user_id, reason.strip()))
            return {"success": True, "message": "Thank you. The TV review has been reported for moderation."}

    # -------------------------------------------------------------
    # WATCHLIST & WATCH PROGRESS
    # -------------------------------------------------------------
    def toggle_tv_watchlist(self, user_id: int, tmdb_id: int) -> Dict[str, Any]:
        with get_db() as conn:
            tv_show_id = self._ensure_tv_exists(conn, tmdb_id)
            cursor = conn.cursor()
            exists = cursor.execute("""
            SELECT id FROM tv_watchlist WHERE user_id = ? AND tv_show_id = ?
            """, (user_id, tv_show_id)).fetchone()

            if exists:
                cursor.execute("DELETE FROM tv_watchlist WHERE user_id = ? AND tv_show_id = ?", (user_id, tv_show_id))
                in_watchlist = False
            else:
                cursor.execute("INSERT INTO tv_watchlist (user_id, tv_show_id) VALUES (?, ?)", (user_id, tv_show_id))
                in_watchlist = True

            return {"success": True, "in_watchlist": in_watchlist, "tmdb_id": tmdb_id}

    def update_watch_progress(self, user_id: int, tmdb_id: int, status: str,
                              watched_season: int = 1, watched_episode: int = 0,
                              last_watched_episode: Optional[str] = None) -> Dict[str, Any]:
        valid_statuses = ('watching', 'completed', 'dropped', 'plan_to_watch')
        status = status.lower().strip()
        if status not in valid_statuses:
            return {"success": False, "error": f"Invalid status '{status}'. Must be one of {valid_statuses}"}

        if last_watched_episode is None:
            last_watched_episode = f"S{int(watched_season):02d}E{int(watched_episode):02d}"

        with get_db() as conn:
            tv_show_id = self._ensure_tv_exists(conn, tmdb_id)
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO tv_watch_progress (
                user_id, tv_show_id, status, watched_season, watched_episode,
                last_watched_episode, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, tv_show_id) DO UPDATE SET
                status = excluded.status,
                watched_season = excluded.watched_season,
                watched_episode = excluded.watched_episode,
                last_watched_episode = excluded.last_watched_episode,
                last_updated = CURRENT_TIMESTAMP
            """, (user_id, tv_show_id, status, int(watched_season), int(watched_episode), last_watched_episode))

            return {
                "success": True,
                "progress": {
                    "tmdb_id": tmdb_id,
                    "tv_show_id": tv_show_id,
                    "status": status,
                    "watched_season": watched_season,
                    "watched_episode": watched_episode,
                    "last_watched_episode": last_watched_episode
                }
            }

    def get_user_tv_progress(self, user_id: int, tmdb_id: Optional[int] = None) -> Any:
        with get_db() as conn:
            cursor = conn.cursor()
            if tmdb_id:
                show = cursor.execute("SELECT id FROM tv_shows WHERE tmdb_id = ?", (tmdb_id,)).fetchone()
                if not show:
                    return None
                row = cursor.execute("""
                SELECT p.*, s.name, s.tmdb_id, s.poster_path
                FROM tv_watch_progress p
                JOIN tv_shows s ON p.tv_show_id = s.id
                WHERE p.user_id = ? AND p.tv_show_id = ?
                """, (user_id, show["id"])).fetchone()
                return dict(row) if row else None
            else:
                rows = cursor.execute("""
                SELECT p.*, s.name, s.tmdb_id, s.poster_path, s.backdrop_path, s.number_of_seasons, s.number_of_episodes
                FROM tv_watch_progress p
                JOIN tv_shows s ON p.tv_show_id = s.id
                WHERE p.user_id = ?
                ORDER BY p.last_updated DESC
                """, (user_id,)).fetchall()
                return [dict(r) for r in rows]

    def get_user_tv_watchlist(self, user_id: int) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("""
            SELECT s.*, w.added_at
            FROM tv_watchlist w
            JOIN tv_shows s ON w.tv_show_id = s.id
            WHERE w.user_id = ?
            ORDER BY w.added_at DESC
            """, (user_id,)).fetchall()
            return [self._format_show_row(r) for r in rows]

tv_service = TVService()
