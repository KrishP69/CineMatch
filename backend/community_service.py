"""
CineMatch Community Service: User Ratings, Explainable Reviews with VADER Sentiment Analysis,
Voting, Moderation, Watchlist, and Watch History.
"""

import logging
from database import get_db
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

# Initialize VADER Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

class CommunityService:
    def classify_sentiment(self, text: str):
        """
        Explainable NLP sentiment classification using VADER.
        Returns:
            sentiment: 'positive' | 'neutral' | 'negative'
            compound: float score (-1.0 to 1.0)
            breakdown: {'pos': ..., 'neu': ..., 'neg': ...}
        """
        scores = analyzer.polarity_scores(text)
        compound = scores["compound"]
        if compound >= 0.05:
            sentiment = "positive"
        elif compound <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        return sentiment, compound, scores

    def _ensure_movie_exists(self, conn, movie_id: int):
        """Ensures the movie ID exists in the relational movies table before foreign key inserts."""
        cursor = conn.cursor()
        row = cursor.execute("SELECT id FROM movies WHERE id = ?", (movie_id,)).fetchone()
        if not row:
            try:
                from movie_service import movie_service
                m = movie_service.get_movie_by_id(movie_id)
            except Exception:
                m = None

            if m:
                cursor.execute("""
                INSERT OR IGNORE INTO movies (
                    id, title, original_title, overview, genres, release_date, release_year,
                    runtime, poster_path, backdrop_path, tmdb_rating, tmdb_vote_count,
                    popularity, keywords, director, cast_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(m["id"]), m.get("title", f"Movie {movie_id}"), m.get("original_title", ""),
                    m.get("overview", ""), json.dumps(m.get("genres", [])),
                    m.get("release_date", ""), int(m.get("release_year") or 2000),
                    int(m.get("runtime", 120)), m.get("poster_path", ""), m.get("backdrop_path", ""),
                    float(m.get("vote_average", 7.0)), int(m.get("vote_count", 100)),
                    float(m.get("popularity", 10.0)), json.dumps(m.get("keywords", [])),
                    m.get("director", ""), json.dumps(m.get("cast", []))
                ))
            else:
                cursor.execute("""
                INSERT OR IGNORE INTO movies (id, title, original_title)
                VALUES (?, ?, ?)
                """, (movie_id, f"Movie {movie_id}", f"Movie {movie_id}"))

    # -------------------------------------------------------------
    # 1. RATINGS (1 - 10)
    # -------------------------------------------------------------
    def rate_movie(self, user_id: int, movie_id: int, rating: int):
        if not (1 <= rating <= 10):
            return {"success": False, "error": "Rating must be an integer between 1 and 10"}

        with get_db() as conn:
            self._ensure_movie_exists(conn, movie_id)
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO user_ratings (user_id, movie_id, rating, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, movie_id) DO UPDATE SET
                rating = excluded.rating,
                updated_at = CURRENT_TIMESTAMP
            """, (user_id, movie_id, rating))
            conn.commit()

            # Fetch updated stats using the committed transaction
            stats = self.get_movie_ratings_summary(movie_id, user_id=user_id, conn=conn)
            return {"success": True, "data": stats}

    def delete_rating(self, user_id: int, movie_id: int):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            DELETE FROM user_ratings WHERE user_id = ? AND movie_id = ?
            """, (user_id, movie_id))
            conn.commit()
            stats = self.get_movie_ratings_summary(movie_id, user_id=user_id, conn=conn)
            return {"success": True, "data": stats}

    def get_movie_ratings_summary(self, movie_id: int, user_id: int = None, conn=None):
        def _execute_summary(c):
            cursor = c.cursor()
            # Community user ratings
            row = cursor.execute("""
            SELECT AVG(rating) as avg_rating, COUNT(rating) as total_ratings
            FROM user_ratings WHERE movie_id = ?
            """, (movie_id,)).fetchone()

            avg_rating = round(row["avg_rating"], 1) if row["avg_rating"] is not None else None
            total_ratings = row["total_ratings"] or 0

            # Distribution (1 to 10)
            dist_rows = cursor.execute("""
            SELECT rating, COUNT(*) as count
            FROM user_ratings WHERE movie_id = ?
            GROUP BY rating
            """, (movie_id,)).fetchall()
            distribution = {r: 0 for r in range(1, 11)}
            for dr in dist_rows:
                distribution[dr["rating"]] = dr["count"]

            # User's own rating if authenticated
            user_rating = None
            if user_id:
                ur = cursor.execute("""
                SELECT rating FROM user_ratings WHERE user_id = ? AND movie_id = ?
                """, (user_id, movie_id)).fetchone()
                if ur:
                    user_rating = ur["rating"]

            # TMDB external rating
            ext = cursor.execute("""
            SELECT source, rating, vote_count FROM external_ratings
            WHERE movie_id = ?
            """, (movie_id,)).fetchall()
            external_ratings = {
                e["source"]: {"rating": e["rating"], "vote_count": e["vote_count"]}
                for e in ext
            }

            return {
                "movie_id": movie_id,
                "community": {
                    "average_rating": avg_rating,
                    "total_ratings": total_ratings,
                    "distribution": distribution
                },
                "user_rating": user_rating,
                "external_ratings": external_ratings
            }

        if conn is not None:
            return _execute_summary(conn)
        else:
            with get_db() as db_conn:
                return _execute_summary(db_conn)

    # -------------------------------------------------------------
    # 2. REVIEWS WITH VADER SENTIMENT & SPOILER CONTROLS
    # -------------------------------------------------------------
    def create_review(self, user_id: int, movie_id: int, title: str, content: str, rating: int, contains_spoilers: bool = False):
        title = title.strip()
        content = content.strip()
        if len(title) < 3:
            return {"success": False, "error": "Review title must be at least 3 characters"}
        if len(content) < 10:
            return {"success": False, "error": "Review description must be at least 10 characters"}
        if not (1 <= rating <= 10):
            return {"success": False, "error": "Rating must be between 1 and 10"}

        # Sentiment Analysis via VADER
        full_text = f"{title}. {content}"
        sentiment, compound, breakdown = self.classify_sentiment(full_text)

        with get_db() as conn:
            self._ensure_movie_exists(conn, movie_id)
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO user_reviews (
                user_id, movie_id, title, content, rating, sentiment,
                sentiment_score, contains_spoilers
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, movie_id, title, content, rating, sentiment, compound, 1 if contains_spoilers else 0))
            review_id = cursor.lastrowid

            # Also ensure rating is saved to user_ratings
            cursor.execute("""
            INSERT INTO user_ratings (user_id, movie_id, rating, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, movie_id) DO UPDATE SET
                rating = excluded.rating,
                updated_at = CURRENT_TIMESTAMP
            """, (user_id, movie_id, rating))

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

    def edit_review(self, review_id: int, user_id: int, title: str, content: str, rating: int, contains_spoilers: bool):
        sentiment, compound, _ = self.classify_sentiment(f"{title}. {content}")
        with get_db() as conn:
            cursor = conn.cursor()
            # Verify ownership
            rev = cursor.execute("SELECT user_id, movie_id FROM user_reviews WHERE id = ?", (review_id,)).fetchone()
            if not rev or rev["user_id"] != user_id:
                return {"success": False, "error": "Unauthorized or review not found"}

            cursor.execute("""
            UPDATE user_reviews
            SET title = ?, content = ?, rating = ?, sentiment = ?, sentiment_score = ?,
                contains_spoilers = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (title, content, rating, sentiment, compound, 1 if contains_spoilers else 0, review_id))

            # Sync user rating
            cursor.execute("""
            UPDATE user_ratings SET rating = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND movie_id = ?
            """, (rating, user_id, rev["movie_id"]))

            return {"success": True}

    def delete_review(self, review_id: int, user_id: int):
        with get_db() as conn:
            cursor = conn.cursor()
            rev = cursor.execute("SELECT user_id FROM user_reviews WHERE id = ?", (review_id,)).fetchone()
            if not rev or rev["user_id"] != user_id:
                return {"success": False, "error": "Unauthorized or review not found"}

            cursor.execute("DELETE FROM user_reviews WHERE id = ?", (review_id,))
            return {"success": True}

    def get_movie_reviews(self, movie_id: int, sort_by: str = "most_helpful", page: int = 1, per_page: int = 10, current_user_id: int = None):
        order_clause = "helpful_count DESC, created_at DESC"
        if sort_by == "newest":
            order_clause = "created_at DESC"
        elif sort_by == "highest_rated":
            order_clause = "rating DESC, created_at DESC"
        elif sort_by == "lowest_rated":
            order_clause = "rating ASC, created_at DESC"

        offset = (page - 1) * per_page
        with get_db() as conn:
            cursor = conn.cursor()
            total = cursor.execute("SELECT COUNT(*) FROM user_reviews WHERE movie_id = ?", (movie_id,)).fetchone()[0]

            rows = cursor.execute(f"""
            SELECT r.*, u.username, u.avatar
            FROM user_reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.movie_id = ?
            ORDER BY {order_clause}
            LIMIT ? OFFSET ?
            """, (movie_id, per_page, offset)).fetchall()

            reviews = []
            for row in rows:
                user_vote = 0
                if current_user_id:
                    v = cursor.execute("""
                    SELECT vote_type FROM review_votes WHERE review_id = ? AND user_id = ?
                    """, (row["id"], current_user_id)).fetchone()
                    if v:
                        user_vote = v["vote_type"]

                reviews.append({
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "username": row["username"],
                    "avatar": row["avatar"],
                    "title": row["title"],
                    "content": row["content"],
                    "rating": row["rating"],
                    "sentiment": row["sentiment"],
                    "sentiment_score": row["sentiment_score"],
                    "contains_spoilers": bool(row["contains_spoilers"]),
                    "helpful_count": row["helpful_count"],
                    "unhelpful_count": row["unhelpful_count"],
                    "created_at": row["created_at"],
                    "user_vote": user_vote
                })

            # Fetch external reviews (TMDB)
            ext_rows = cursor.execute("""
            SELECT author, content, rating, url, created_at
            FROM external_reviews WHERE movie_id = ?
            LIMIT 5
            """, (movie_id,)).fetchall()

            external_reviews = [dict(er) for er in ext_rows]

            return {
                "total": total,
                "page": page,
                "per_page": per_page,
                "reviews": reviews,
                "external_reviews": external_reviews
            }

    def vote_review(self, review_id: int, user_id: int, vote_type: int):
        """1 for helpful, -1 for unhelpful. Toggles vote if same vote submitted again."""
        if vote_type not in (1, -1):
            return {"success": False, "error": "Vote type must be 1 or -1"}

        with get_db() as conn:
            cursor = conn.cursor()
            existing = cursor.execute("""
            SELECT vote_type FROM review_votes WHERE review_id = ? AND user_id = ?
            """, (review_id, user_id)).fetchone()

            if existing:
                if existing["vote_type"] == vote_type:
                    # Toggle remove
                    cursor.execute("DELETE FROM review_votes WHERE review_id = ? AND user_id = ?", (review_id, user_id))
                    new_vote = 0
                else:
                    # Change vote
                    cursor.execute("UPDATE review_votes SET vote_type = ? WHERE review_id = ? AND user_id = ?", (vote_type, review_id, user_id))
                    new_vote = vote_type
            else:
                cursor.execute("""
                INSERT INTO review_votes (review_id, user_id, vote_type) VALUES (?, ?, ?)
                """, (review_id, user_id, vote_type))
                new_vote = vote_type

            # Recalculate counts
            helpful = cursor.execute("SELECT COUNT(*) FROM review_votes WHERE review_id = ? AND vote_type = 1", (review_id,)).fetchone()[0]
            unhelpful = cursor.execute("SELECT COUNT(*) FROM review_votes WHERE review_id = ? AND vote_type = -1", (review_id,)).fetchone()[0]

            cursor.execute("""
            UPDATE user_reviews SET helpful_count = ?, unhelpful_count = ? WHERE id = ?
            """, (helpful, unhelpful, review_id))

            return {
                "success": True,
                "helpful_count": helpful,
                "unhelpful_count": unhelpful,
                "user_vote": new_vote
            }

    def report_review(self, review_id: int, user_id: int, reason: str):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO review_reports (review_id, user_id, reason)
            VALUES (?, ?, ?)
            """, (review_id, user_id, reason.strip()))
            return {"success": True, "message": "Thank you. The review has been reported for moderation."}

    # -------------------------------------------------------------
    # 3. WATCHLIST & WATCH HISTORY (Already Watched)
    # -------------------------------------------------------------
    def toggle_watchlist(self, user_id: int, movie_id: int):
        with get_db() as conn:
            self._ensure_movie_exists(conn, movie_id)
            cursor = conn.cursor()
            exists = cursor.execute("""
            SELECT id FROM watchlist WHERE user_id = ? AND movie_id = ?
            """, (user_id, movie_id)).fetchone()

            if exists:
                cursor.execute("DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
                in_watchlist = False
            else:
                cursor.execute("INSERT INTO watchlist (user_id, movie_id) VALUES (?, ?)", (user_id, movie_id))
                in_watchlist = True

            return {"success": True, "in_watchlist": in_watchlist}

    def toggle_watched(self, user_id: int, movie_id: int):
        with get_db() as conn:
            self._ensure_movie_exists(conn, movie_id)
            cursor = conn.cursor()
            exists = cursor.execute("""
            SELECT id FROM watch_history WHERE user_id = ? AND movie_id = ?
            """, (user_id, movie_id)).fetchone()

            if exists:
                cursor.execute("DELETE FROM watch_history WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
                is_watched = False
            else:
                cursor.execute("INSERT INTO watch_history (user_id, movie_id) VALUES (?, ?)", (user_id, movie_id))
                is_watched = True

            return {"success": True, "is_watched": is_watched}

    def get_user_watchlist(self, user_id: int):
        with get_db() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("""
            SELECT m.*, w.added_at
            FROM watchlist w
            JOIN movies m ON w.movie_id = m.id
            WHERE w.user_id = ?
            ORDER BY w.added_at DESC
            """, (user_id,)).fetchall()
            return [dict(r) for r in rows]

    def get_user_watch_history(self, user_id: int):
        with get_db() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("""
            SELECT m.*, wh.watched_at
            FROM watch_history wh
            JOIN movies m ON wh.movie_id = m.id
            WHERE wh.user_id = ?
            ORDER BY wh.watched_at DESC
            """, (user_id,)).fetchall()
            return [dict(r) for r in rows]

    def get_user_ratings_history(self, user_id: int):
        with get_db() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("""
            SELECT m.*, ur.rating as user_rating, ur.updated_at as rated_at
            FROM user_ratings ur
            JOIN movies m ON ur.movie_id = m.id
            WHERE ur.user_id = ?
            ORDER BY ur.updated_at DESC
            """, (user_id,)).fetchall()
            return [dict(r) for r in rows]

community_service = CommunityService()

