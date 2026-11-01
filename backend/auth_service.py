"""
CineMatch Authentication & User Service
Secure password hashing (Werkzeug), JWT tokens, and user profile management.
"""

import os
import jwt
import datetime
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    is_prod = os.getenv("FLASK_ENV") == "production" or os.getenv("ENV") == "production"
    if is_prod:
        raise RuntimeError("FATAL SECURITY ERROR: JWT_SECRET must be configured via environment variable in production mode!")
    import secrets
    JWT_SECRET = secrets.token_hex(32)
    logger.warning("WARNING: JWT_SECRET environment variable not configured. Using ephemeral cryptographic secret for local session.")

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 72

class AuthService:
    def hash_password(self, password: str) -> str:
        return generate_password_hash(password, method="scrypt")

    def verify_password(self, password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, password)

    def generate_token(self, user_id: int, username: str) -> str:
        payload = {
            "sub": str(user_id),
            "username": username,
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            payload["sub"] = int(payload["sub"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT decode error: {e}")
            return None

    def register(self, username: str, email: str, password: str, avatar: str = "🎬"):
        username = username.strip()
        email = email.strip().lower()
        if len(username) < 3:
            return {"success": False, "error": "Username must be at least 3 characters"}
        if len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}
        if "@" not in email or "." not in email:
            return {"success": False, "error": "Please provide a valid email address"}

        password_hash = self.hash_password(password)

        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO users (username, email, password_hash, avatar)
                VALUES (?, ?, ?, ?)
                """, (username, email, password_hash, avatar))
                user_id = cursor.lastrowid

                # Initialize empty preferences
                cursor.execute("""
                INSERT OR IGNORE INTO user_preferences (user_id, favorite_genres, current_mood, viewing_style)
                VALUES (?, '[]', 'Mind-bending', 'Plot twists')
                """, (user_id,))

                token = self.generate_token(user_id, username)
                return {
                    "success": True,
                    "token": token,
                    "user": {
                        "id": user_id,
                        "username": username,
                        "email": email,
                        "avatar": avatar,
                        "role": "user"
                    }
                }
        except Exception as e:
            err_msg = str(e).lower()
            if "unique" in err_msg and "username" in err_msg:
                return {"success": False, "error": "Username is already taken"}
            elif "unique" in err_msg and "email" in err_msg:
                return {"success": False, "error": "Email is already registered"}
            logger.error(f"Registration error: {e}")
            return {"success": False, "error": "Registration failed. Please try again."}

    def login(self, username_or_email: str, password: str):
        identifier = username_or_email.strip()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, username, email, password_hash, avatar, role
            FROM users
            WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)
            """, (identifier, identifier))
            row = cursor.fetchone()

            if not row or not self.verify_password(password, row["password_hash"]):
                return {"success": False, "error": "Invalid username/email or password"}

            token = self.generate_token(row["id"], row["username"])
            return {
                "success": True,
                "token": token,
                "user": {
                    "id": row["id"],
                    "username": row["username"],
                    "email": row["email"],
                    "avatar": row["avatar"],
                    "role": row["role"]
                }
            }

    def get_user_profile(self, user_id: int):
        with get_db() as conn:
            cursor = conn.cursor()
            user = cursor.execute("""
            SELECT id, username, email, avatar, role, created_at
            FROM users WHERE id = ?
            """, (user_id,)).fetchone()

            if not user:
                return None

            # Get counts
            ratings_count = cursor.execute("SELECT COUNT(*) FROM user_ratings WHERE user_id = ?", (user_id,)).fetchone()[0]
            reviews_count = cursor.execute("SELECT COUNT(*) FROM user_reviews WHERE user_id = ?", (user_id,)).fetchone()[0]
            watchlist_count = cursor.execute("SELECT COUNT(*) FROM watchlist WHERE user_id = ?", (user_id,)).fetchone()[0]
            watched_count = cursor.execute("SELECT COUNT(*) FROM watch_history WHERE user_id = ?", (user_id,)).fetchone()[0]

            # Preferences
            prefs = cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)).fetchone()
            pref_data = {}
            if prefs:
                pref_data = {
                    "favorite_genres": prefs["favorite_genres"],
                    "current_mood": prefs["current_mood"],
                    "viewing_style": prefs["viewing_style"],
                    "preferred_language": prefs["preferred_language"]
                }

            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "avatar": user["avatar"],
                "role": user["role"],
                "created_at": user["created_at"],
                "stats": {
                    "ratings_count": ratings_count,
                    "reviews_count": reviews_count,
                    "watchlist_count": watchlist_count,
                    "watched_count": watched_count
                },
                "preferences": pref_data
            }

auth_service = AuthService()
