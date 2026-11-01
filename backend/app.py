"""
CineMatch Flask Backend Application
RESTful API for ML Movie Recommendations, Catalog Search, and Legal OTT Availability.
Also serves frontend build in production.
"""

import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

from movie_service import movie_service
from recommender import recommender
from ott_service import ott_service
from neural_recommender import neural_service
from database import init_db, seed_movies_from_json
from auth_service import auth_service
from community_service import community_service
from discovery_service import discovery_service
from tv_service import tv_service

# Initialize database schema and ensure catalog is seeded
init_db()
seed_movies_from_json()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cinematch")

# Dist path
DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

if os.path.exists(DIST_DIR):
    app = Flask(__name__, static_folder=DIST_DIR, static_url_path="")
    logger.info(f"Serving production frontend from: {DIST_DIR}")
else:
    app = Flask(__name__)
    logger.info("Running in API-only mode (frontend dist not found).")

# Enable CORS for all routes (supports development & production)
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    supports_credentials=True
)


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health status and recommender readiness."""
    gpu_status = neural_service.get_status()
    return jsonify({
        "status": "healthy",
        "app": "CineMatch API",
        "version": "1.0.0",
        "movies_indexed": len(movie_service.movies),
        "recommender_ready": recommender.tfidf_matrix is not None,
        "neural_model_ready": neural_service.is_loaded,
        "gpu_device": gpu_status.get("gpu_device"),
        "tmdb_configured": bool(os.getenv("TMDB_API_KEY"))
    }), 200


@app.route("/api/featured", methods=["GET"])
def get_featured():
    """Returns hero movie and curated carousel rows."""
    try:
        data = movie_service.get_featured_content()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        logger.error(f"Error in /api/featured: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/movies", methods=["GET"])
def get_movies():
    """Paginated list of movies with optional filters."""
    try:
        genre = request.args.get("genre")
        year = request.args.get("year")
        min_rating = request.args.get("min_rating")
        sort_by = request.args.get("sort_by", "popularity")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 24))

        results = movie_service.get_all_movies(
            genre=genre,
            year=year,
            min_rating=min_rating,
            sort_by=sort_by,
            page=page,
            per_page=per_page
        )
        return jsonify({"success": True, "data": results}), 200
    except Exception as e:
        logger.error(f"Error in /api/movies: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/movies/<int:movie_id>", methods=["GET"])
def get_movie_detail(movie_id):
    """Returns full metadata for a specific movie."""
    try:
        movie = movie_service.get_movie_by_id(movie_id)
        if not movie:
            return jsonify({"success": False, "error": f"Movie with ID {movie_id} not found"}), 404

        # Include default watch providers for quick display
        country = request.args.get("country", "IN")
        providers = ott_service.get_watch_providers(movie, country=country)

        # Include 6 similar movies immediately
        similar = recommender.recommend_similar_by_id(movie_id, top_n=6)

        return jsonify({
            "success": True,
            "movie": movie,
            "watch_providers": providers,
            "similar_movies": similar
        }), 200
    except Exception as e:
        logger.error(f"Error in /api/movies/{movie_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/search", methods=["GET"])
def search_movies():
    """Multi-attribute instant search."""
    try:
        q = request.args.get("q", "")
        genre = request.args.get("genre")
        min_rating = request.args.get("min_rating")
        sort_by = request.args.get("sort_by", "relevance")
        limit = int(request.args.get("limit", 24))

        results = movie_service.search_movies(
            query=q,
            genre=genre,
            min_rating=min_rating,
            sort_by=sort_by,
            limit=limit
        )
        return jsonify({"success": True, "data": results}), 200
    except Exception as e:
        logger.error(f"Error in /api/search: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/genres", methods=["GET"])
def get_genres():
    """Returns list of distinct genres in dataset."""
    try:
        genres = movie_service.get_genres()
        return jsonify({"success": True, "genres": genres}), 200
    except Exception as e:
        logger.error(f"Error in /api/genres: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/recommend/<int:movie_id>", methods=["GET"])
def recommend_similar(movie_id):
    """
    ML Content-Based Similarity Endpoint:
    Returns 10 similar movies based on TF-IDF cosine similarity.
    """
    try:
        count = int(request.args.get("count", 10))
        recommendations = recommender.recommend_similar_by_id(movie_id, top_n=count)
        return jsonify({
            "success": True,
            "target_movie_id": movie_id,
            "algorithm": "TF-IDF Vectorization & Cosine Similarity on Weighted Metadata",
            "count": len(recommendations),
            "recommendations": recommendations
        }), 200
    except Exception as e:
        logger.error(f"Error in /api/recommend/{movie_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/recommend/personalized", methods=["POST"])
def recommend_personalized():
    """
    Personalized Content-Based Recommendation Endpoint:
    Accepts user profile: liked_movie_ids, watched_movie_ids, favorite_genres.
    Aggregates profile vector and calculates cosine similarity.
    """
    try:
        body = request.get_json() or {}
        liked_ids = body.get("liked_movie_ids", [])
        watched_ids = body.get("watched_movie_ids", [])
        favorite_genres = body.get("favorite_genres", [])
        count = int(body.get("count", 12))

        recommendations = recommender.recommend_personalized(
            liked_ids=liked_ids,
            watched_ids=watched_ids,
            favorite_genres=favorite_genres,
            top_n=count
        )

        return jsonify({
            "success": True,
            "algorithm": "Aggregated User Profile TF-IDF Vector & Cosine Similarity",
            "taste_profile": {
                "liked_count": len(liked_ids),
                "watched_count": len(watched_ids),
                "favorite_genres": favorite_genres
            },
            "count": len(recommendations),
            "recommendations": recommendations
        }), 200
    except Exception as e:
        logger.error(f"Error in /api/recommend/personalized: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/recommend/retrain", methods=["POST"])
def retrain_model_route():
    """
    Continuous Learning Model Retraining Endpoint:
    Dynamically recalculates the user's high-dimensional vector based on recent
    interactions (liked, watched, watchlist, disliked, favorite genres, mood).
    Returns updated recommendations and training telemetry.
    """
    try:
        body = request.get_json() or {}
        liked_ids = body.get("liked_movie_ids", [])
        watched_ids = body.get("watched_movie_ids", [])
        disliked_ids = body.get("disliked_movie_ids", [])
        watchlist_ids = body.get("watchlist_movie_ids", [])
        favorite_genres = body.get("favorite_genres", [])
        mood = body.get("mood")
        era = body.get("era")
        count = int(body.get("count", 12))

        result = recommender.retrain_user_model(
            liked_ids=liked_ids,
            watched_ids=watched_ids,
            disliked_ids=disliked_ids,
            watchlist_ids=watchlist_ids,
            favorite_genres=favorite_genres,
            mood=mood,
            era=era,
            top_n=count
        )

        return jsonify({
            "success": True,
            "message": "Continuous learning model retrained successfully",
            "recommendations": result["recommendations"],
            "model_telemetry": result["model_telemetry"]
        }), 200
    except Exception as e:
        logger.error(f"Error in /api/recommend/retrain: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/recommend/onboarding", methods=["POST"])
def onboarding_mcq_route():
    """
    Onboarding Personalization MCQ Endpoint:
    Accepts MCQ answers (last watched film/series, favorite genres, current mood, era/pacing)
    and computes initial Next to Watch personalized recommendations.
    """
    try:
        body = request.get_json() or {}
        last_watched = body.get("last_watched", "")
        genres = body.get("genres", [])
        mood = body.get("mood", "")
        era_pacing = body.get("era_pacing", "")
        already_watched_ids = body.get("already_watched_ids", [])
        count = int(body.get("count", 10))

        result = recommender.recommend_onboarding_mcq(
            last_watched=last_watched,
            genres=genres,
            mood=mood,
            era_pacing=era_pacing,
            already_watched_ids=already_watched_ids,
            top_n=count
        )

        return jsonify({
            "success": True,
            "data": result
        }), 200
    except Exception as e:
        logger.error(f"Error in /api/recommend/onboarding: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/describe-match", methods=["POST"])
def ai_describe_match_route():
    """
    'For You AI' Agent Natural Language Matcher:
    Accepts user free-text plot/vibe description (e.g. 'high-stakes mind game with a twist in a rainy city')
    and returns top 10 recommended movies with human-readable AI justification and OTT availability.
    """
    try:
        body = request.get_json() or {}
        description = body.get("description", "").strip()
        preferred_genres = body.get("preferred_genres", [])
        mood = body.get("mood", "")
        exclude_ids = body.get("exclude_ids", [])
        count = int(body.get("count", 10))

        if not description and not preferred_genres:
            return jsonify({
                "success": False,
                "error": "Please provide a description or select at least one genre."
            }), 400

        recommendations = recommender.recommend_by_natural_language(
            description=description,
            preferred_genres=preferred_genres,
            mood=mood,
            exclude_ids=exclude_ids,
            top_n=count
        )

        return jsonify({
            "success": True,
            "query": {
                "description": description,
                "preferred_genres": preferred_genres,
                "mood": mood
            },
            "count": len(recommendations),
            "recommendations": recommendations
        }), 200
    except Exception as e:
        logger.error(f"Error in /api/ai/describe-match: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/watch-providers/<int:movie_id>", methods=["GET"])
def get_watch_providers_route(movie_id):
    """
    Returns legal OTT streaming, rent, and buy providers for a movie in a specific country.
    Country defaults to India ('IN').
    """
    try:
        country = request.args.get("country", "IN").upper()
        movie = movie_service.get_movie_by_id(movie_id)
        if not movie:
            return jsonify({"success": False, "error": f"Movie with ID {movie_id} not found"}), 404

        provider_data = ott_service.get_watch_providers(movie, country=country)
        return jsonify({
            "success": True,
            "data": provider_data
        }), 200
    except Exception as e:
        logger.error(f"Error in /api/watch-providers/{movie_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/model/status", methods=["GET"])
def get_model_status():
    """Returns local GPU/neural model status, architecture telemetry and training info."""
    try:
        status = neural_service.get_status()
        return jsonify({"success": True, "data": status}), 200
    except Exception as e:
        logger.error(f"Error in /api/model/status: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/model/train", methods=["POST"])
def retrain_neural_model():
    """Triggers local training of the PyTorch Neural Collaborative Filtering model."""
    try:
        from train_gpu_model import train_neural_model
        meta = train_neural_model()
        neural_service.load_model()
        return jsonify({
            "success": True,
            "message": "Neural Collaborative Filtering model successfully trained locally!",
            "meta": {k: v for k, v in meta.items() if k != "tmdb_to_idx"}
        }), 200
    except Exception as e:
        logger.error(f"Error in /api/model/train: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/recommend/neural", methods=["POST"])
def get_neural_recommendations():
    """
    Computes high-dimensional neural embedding recommendations using the trained
    Neural Collaborative Filtering (NeuMF) dual-tower PyTorch model on the local GPU.
    """
    try:
        body = request.get_json() or {}
        liked_ids = [int(i) for i in body.get("liked_ids", []) if str(i).isdigit()]
        watched_ids = [int(i) for i in body.get("watched_ids", []) if str(i).isdigit()]
        exclude_ids = [int(i) for i in body.get("exclude_ids", []) if str(i).isdigit()]
        top_n = int(body.get("top_n", 12))

        all_input_liked = list(set(liked_ids + watched_ids))
        all_excludes = list(set(exclude_ids + watched_ids))

        all_catalog = movie_service.movies
        recs = neural_service.predict_user_catalog_affinities(
            liked_tmdb_ids=all_input_liked,
            candidate_movies=all_catalog,
            exclude_ids=all_excludes
        )

        if not recs:
            # Fallback to TF-IDF recommender if neural model is not yet loaded
            recs = recommender.recommend_for_user(
                liked_movie_ids=all_input_liked,
                disliked_movie_ids=[],
                watched_movie_ids=all_excludes,
                top_n=top_n
            )
            model_type = "hybrid_tfidf_fallback"
        else:
            recs = recs[:top_n]
            model_type = "neural_ncf_pytorch"

        return jsonify({
            "success": True,
            "model_type": model_type,
            "hardware": neural_service.get_status().get("gpu_device"),
            "count": len(recs),
            "recommendations": recs
        }), 200
    except Exception as e:
        logger.error(f"Error in /api/recommend/neural: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


def get_auth_user():
    """Extracts and verifies JWT token from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    return auth_service.decode_token(token)


# -----------------------------------------------------------------
# AUTHENTICATION ENDPOINTS (JWT + Werkzeug Hashing)
# -----------------------------------------------------------------
@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    data = request.get_json() or {}
    username = data.get("username", "")
    email = data.get("email", "")
    password = data.get("password", "")
    avatar = data.get("avatar", "🎬")

    result = auth_service.register(username, email, password, avatar=avatar)
    status_code = 201 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json() or {}
    username_or_email = data.get("username_or_email", "")
    password = data.get("password", "")

    result = auth_service.login(username_or_email, password)
    status_code = 200 if result.get("success") else 401
    return jsonify(result), status_code


@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    profile = auth_service.get_user_profile(payload["sub"])
    if not profile:
        return jsonify({"success": False, "error": "User not found"}), 404

    return jsonify({"success": True, "user": profile}), 200


# -----------------------------------------------------------------
# COMMUNITY RATINGS (1-10)
# -----------------------------------------------------------------
@app.route("/api/movies/<int:movie_id>/ratings", methods=["GET"])
def get_movie_ratings(movie_id):
    payload = get_auth_user()
    user_id = payload["sub"] if payload else None
    summary = community_service.get_movie_ratings_summary(movie_id, user_id=user_id)
    return jsonify({"success": True, "data": summary}), 200


@app.route("/api/movies/<int:movie_id>/rating", methods=["POST"])
def submit_movie_rating(movie_id):
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required to submit rating"}), 401

    data = request.get_json() or {}
    rating = data.get("rating")
    if rating is None or not isinstance(rating, int):
        return jsonify({"success": False, "error": "Rating must be an integer between 1 and 10"}), 400

    result = community_service.rate_movie(payload["sub"], movie_id, rating)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/api/movies/<int:movie_id>/rating", methods=["DELETE"])
def delete_movie_rating(movie_id):
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401

    result = community_service.delete_rating(payload["sub"], movie_id)
    return jsonify(result), 200


# -----------------------------------------------------------------
# COMMUNITY REVIEWS WITH VADER SENTIMENT CLASSIFICATION
# -----------------------------------------------------------------
@app.route("/api/movies/<int:movie_id>/reviews", methods=["GET"])
def get_movie_reviews_endpoint(movie_id):
    payload = get_auth_user()
    user_id = payload["sub"] if payload else None
    sort_by = request.args.get("sort_by", "most_helpful")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    result = community_service.get_movie_reviews(
        movie_id=movie_id,
        sort_by=sort_by,
        page=page,
        per_page=per_page,
        current_user_id=user_id
    )
    return jsonify({"success": True, "data": result}), 200


@app.route("/api/movies/<int:movie_id>/reviews", methods=["POST"])
def submit_movie_review_endpoint(movie_id):
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required to post a review"}), 401

    data = request.get_json() or {}
    title = data.get("title", "")
    content = data.get("content", "")
    rating = data.get("rating")
    contains_spoilers = bool(data.get("contains_spoilers", False))

    if rating is None:
        return jsonify({"success": False, "error": "Rating (1-10) is required for review"}), 400

    result = community_service.create_review(
        user_id=payload["sub"],
        movie_id=movie_id,
        title=title,
        content=content,
        rating=int(rating),
        contains_spoilers=contains_spoilers
    )
    status_code = 201 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/api/reviews/<int:review_id>", methods=["PUT"])
def edit_movie_review_endpoint(review_id):
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401

    data = request.get_json() or {}
    result = community_service.edit_review(
        review_id=review_id,
        user_id=payload["sub"],
        title=data.get("title", ""),
        content=data.get("content", ""),
        rating=int(data.get("rating", 7)),
        contains_spoilers=bool(data.get("contains_spoilers", False))
    )
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/api/reviews/<int:review_id>", methods=["DELETE"])
def delete_movie_review_endpoint(review_id):
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401

    result = community_service.delete_review(review_id, payload["sub"])
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/api/reviews/<int:review_id>/vote", methods=["POST"])
def vote_movie_review_endpoint(review_id):
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required to vote"}), 401

    data = request.get_json() or {}
    vote_type = int(data.get("vote_type", 1))
    result = community_service.vote_review(review_id, payload["sub"], vote_type)
    return jsonify(result), 200


@app.route("/api/reviews/<int:review_id>/report", methods=["POST"])
def report_movie_review_endpoint(review_id):
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401

    data = request.get_json() or {}
    reason = data.get("reason", "Inappropriate content")
    result = community_service.report_review(review_id, payload["sub"], reason)
    return jsonify(result), 200


# -----------------------------------------------------------------
# USER WATCHLIST & WATCH HISTORY (Already Watched)
# -----------------------------------------------------------------
@app.route("/api/user/watchlist/<int:movie_id>", methods=["POST"])
def toggle_user_watchlist(movie_id):
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    result = community_service.toggle_watchlist(payload["sub"], movie_id)
    return jsonify(result), 200


@app.route("/api/user/watched/<int:movie_id>", methods=["POST"])
def toggle_user_watched(movie_id):
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    result = community_service.toggle_watched(payload["sub"], movie_id)
    return jsonify(result), 200


@app.route("/api/user/watchlist", methods=["GET"])
def get_user_watchlist_endpoint():
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    items = community_service.get_user_watchlist(payload["sub"])
    return jsonify({"success": True, "data": items}), 200


@app.route("/api/user/watched", methods=["GET"])
def get_user_watched_endpoint():
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    items = community_service.get_user_watch_history(payload["sub"])
    return jsonify({"success": True, "data": items}), 200


@app.route("/api/user/ratings", methods=["GET"])
def get_user_ratings_endpoint():
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    items = community_service.get_user_ratings_history(payload["sub"])
    return jsonify({"success": True, "data": items}), 200


# -----------------------------------------------------------------
# PERSONALIZED MOVIE DISCOVERY (Multi-filter, Mood, Theme, OTT)
# -----------------------------------------------------------------
@app.route("/api/discovery/recommend", methods=["POST"])
def discovery_recommend():
    try:
        body = request.get_json() or {}
        genres = body.get("genres", [])
        moods = body.get("moods", [])
        themes = body.get("themes", [])
        min_rating = float(body.get("min_rating", 0.0))
        release_year_min = int(body.get("release_year_min", 1900))
        release_year_max = int(body.get("release_year_max", 2030))
        min_runtime = int(body.get("min_runtime", 0)) if body.get("min_runtime") else None
        max_runtime = int(body.get("max_runtime", 300)) if body.get("max_runtime") else None
        language = body.get("language", "Any")
        streaming_platform = body.get("streaming_platform", None)
        exclude_ids = body.get("exclude_ids", [])
        liked_ids = body.get("liked_ids", [])
        sort_by = body.get("sort_by", "relevance")
        page = int(body.get("page", 1))
        per_page = int(body.get("per_page", 18))

        results = discovery_service.discover_movies(
            genres=genres,
            moods=moods,
            themes=themes,
            min_rating=min_rating,
            release_year_min=release_year_min,
            release_year_max=release_year_max,
            min_runtime=min_runtime,
            max_runtime=max_runtime,
            language=language,
            streaming_platform=streaming_platform,
            exclude_ids=exclude_ids,
            liked_ids=liked_ids,
            sort_by=sort_by,
            page=page,
            per_page=per_page
        )
        return jsonify({"success": True, "data": results}), 200
    except Exception as e:
        logger.error(f"Error in /api/discovery/recommend: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# -----------------------------------------------------------------
# TV / WEB SERIES DEDICATED DATABASE API ENDPOINTS
# -----------------------------------------------------------------
@app.route("/api/tv", methods=["GET"])
def get_tv_shows_endpoint():
    """Returns paginated TV shows with filtering and sorting."""
    try:
        genre = request.args.get("genre")
        min_rating = request.args.get("min_rating")
        sort_by = request.args.get("sort_by", "popularity")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))

        data = tv_service.get_shows(
            category=None,
            genre=genre,
            min_rating=float(min_rating) if min_rating else None,
            sort_by=sort_by,
            page=page,
            per_page=per_page
        )
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        logger.error(f"Error in /api/tv: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tv/trending", methods=["GET"])
def get_tv_trending_endpoint():
    """Returns trending TV shows from persistent database."""
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        data = tv_service.get_shows(category="trending", page=page, per_page=per_page)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        logger.error(f"Error in /api/tv/trending: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tv/popular", methods=["GET"])
def get_tv_popular_endpoint():
    """Returns popular TV shows from persistent database."""
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        data = tv_service.get_shows(category="popular", page=page, per_page=per_page)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        logger.error(f"Error in /api/tv/popular: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tv/top-rated", methods=["GET"])
def get_tv_top_rated_endpoint():
    """Returns top rated TV shows from persistent database."""
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        data = tv_service.get_shows(category="top_rated", page=page, per_page=per_page)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        logger.error(f"Error in /api/tv/top-rated: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tv/search", methods=["GET"])
def search_tv_shows_endpoint():
    """Search TV shows by title, overview, genre, or creator."""
    try:
        query = request.args.get("q", request.args.get("query", "")).strip()
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        data = tv_service.search_tv(query=query, page=page, per_page=per_page)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        logger.error(f"Error in /api/tv/search: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tv/<int:tmdb_id>", methods=["GET"])
def get_tv_detail_endpoint(tmdb_id):
    """Returns full metadata and seasons list for a specific TV show."""
    try:
        show = tv_service.get_tv_by_tmdb_id(tmdb_id)
        if not show:
            # Sync lazily from TMDB if not already in catalog
            show = tv_service.sync_full_tv_show(tmdb_id)

        if not show:
            return jsonify({"success": False, "error": f"TV Show with TMDB ID {tmdb_id} not found"}), 404

        # Include OTT providers if available
        country = request.args.get("country", "IN")
        try:
            ott_info = ott_service.get_watch_providers(tmdb_id, country=country, title=show["name"])
        except Exception:
            ott_info = None
        show["watch_providers"] = ott_info

        # Include community ratings summary
        payload = get_auth_user()
        user_id = payload["sub"] if payload else None
        show["community_ratings"] = tv_service.get_tv_ratings_summary(tmdb_id, user_id=user_id)

        # Include user's watch progress if authenticated
        if user_id:
            show["user_progress"] = tv_service.get_user_tv_progress(user_id, tmdb_id=tmdb_id)

        return jsonify({"success": True, "data": show}), 200
    except Exception as e:
        logger.error(f"Error in /api/tv/{tmdb_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tv/<int:tmdb_id>/seasons", methods=["GET"])
def get_tv_seasons_endpoint(tmdb_id):
    """Returns seasons list for a specific TV show."""
    try:
        seasons = tv_service.get_seasons(tmdb_id)
        return jsonify({"success": True, "data": seasons}), 200
    except Exception as e:
        logger.error(f"Error in /api/tv/{tmdb_id}/seasons: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tv/<int:tmdb_id>/seasons/<int:season_number>", methods=["GET"])
def get_tv_season_episodes_endpoint(tmdb_id, season_number):
    """Returns season details and full episode list."""
    try:
        res = tv_service.get_season_episodes(tmdb_id, season_number)
        status_code = 200 if res.get("success") else 404
        return jsonify(res), status_code
    except Exception as e:
        logger.error(f"Error in /api/tv/{tmdb_id}/seasons/{season_number}: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tv/<int:tmdb_id>/rate", methods=["POST"])
def rate_tv_endpoint(tmdb_id):
    """Submits or updates a 1-10 rating for a TV show."""
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required to submit rating"}), 401

    data = request.get_json() or {}
    rating = data.get("rating")
    if rating is None or not isinstance(rating, int):
        return jsonify({"success": False, "error": "Rating must be an integer between 1 and 10"}), 400

    result = tv_service.rate_tv(payload["sub"], tmdb_id, rating)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/api/tv/<int:tmdb_id>/rate", methods=["DELETE"])
def delete_tv_rating_endpoint(tmdb_id):
    """Deletes the authenticated user's rating for a TV show."""
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401

    result = tv_service.delete_tv_rating(payload["sub"], tmdb_id)
    return jsonify(result), 200


@app.route("/api/tv/<int:tmdb_id>/review", methods=["POST"])
def submit_tv_review_endpoint(tmdb_id):
    """Submits an explainable user review with VADER sentiment analysis."""
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required to post a review"}), 401

    data = request.get_json() or {}
    title = data.get("title", "")
    content = data.get("content", "")
    rating = data.get("rating")
    contains_spoilers = bool(data.get("contains_spoilers", False))

    if rating is None:
        return jsonify({"success": False, "error": "Rating (1-10) is required for review"}), 400

    result = tv_service.create_tv_review(
        user_id=payload["sub"],
        tmdb_id=tmdb_id,
        title=title,
        content=content,
        rating=int(rating),
        contains_spoilers=contains_spoilers
    )
    status_code = 201 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/api/tv/<int:tmdb_id>/reviews", methods=["GET"])
def get_tv_reviews_endpoint(tmdb_id):
    """Returns paginated reviews for a TV show."""
    payload = get_auth_user()
    user_id = payload["sub"] if payload else None
    sort_by = request.args.get("sort_by", "most_helpful")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    result = tv_service.get_tv_reviews(
        tmdb_id=tmdb_id,
        sort_by=sort_by,
        page=page,
        per_page=per_page,
        current_user_id=user_id
    )
    return jsonify({"success": True, "data": result}), 200


@app.route("/api/tv/reviews/<int:review_id>/vote", methods=["POST"])
def vote_tv_review_endpoint(review_id):
    """Vote helpful (+1) or unhelpful (-1) on a TV show review."""
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required to vote"}), 401

    data = request.get_json() or {}
    vote_type = int(data.get("vote_type", 1))
    result = tv_service.vote_tv_review(review_id, payload["sub"], vote_type)
    return jsonify(result), 200


@app.route("/api/tv/reviews/<int:review_id>/report", methods=["POST"])
def report_tv_review_endpoint(review_id):
    """Report a TV show review for moderation."""
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401

    data = request.get_json() or {}
    reason = data.get("reason", "Inappropriate content")
    result = tv_service.report_tv_review(review_id, payload["sub"], reason)
    return jsonify(result), 200


@app.route("/api/tv/<int:tmdb_id>/watchlist", methods=["POST"])
def toggle_tv_watchlist_endpoint(tmdb_id):
    """Toggles TV show in the authenticated user's watchlist."""
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401

    result = tv_service.toggle_tv_watchlist(payload["sub"], tmdb_id)
    return jsonify(result), 200


@app.route("/api/tv/<int:tmdb_id>/progress", methods=["POST"])
def update_tv_progress_endpoint(tmdb_id):
    """Updates watch progress (status, watched_season, watched_episode, last_watched_episode)."""
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401

    data = request.get_json() or {}
    status = data.get("status", "watching")
    watched_season = int(data.get("watched_season", 1))
    watched_episode = int(data.get("watched_episode", 0))
    last_watched_episode = data.get("last_watched_episode")

    result = tv_service.update_watch_progress(
        user_id=payload["sub"],
        tmdb_id=tmdb_id,
        status=status,
        watched_season=watched_season,
        watched_episode=watched_episode,
        last_watched_episode=last_watched_episode
    )
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/api/user/tv/watchlist", methods=["GET"])
def get_user_tv_watchlist_endpoint():
    """Returns the authenticated user's saved TV shows."""
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    items = tv_service.get_user_tv_watchlist(payload["sub"])
    return jsonify({"success": True, "data": items}), 200


@app.route("/api/user/tv/progress", methods=["GET"])
def get_user_tv_progress_endpoint():
    """Returns all TV shows the authenticated user is currently tracking/watching."""
    payload = get_auth_user()
    if not payload:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    items = tv_service.get_user_tv_progress(payload["sub"])
    return jsonify({"success": True, "data": items}), 200


# Catch-all route to serve React Single Page Application
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if os.path.exists(DIST_DIR):
        file_path = os.path.join(DIST_DIR, path)
        if path != "" and os.path.exists(file_path):
            return send_from_directory(DIST_DIR, path)
        return send_from_directory(DIST_DIR, "index.html")
    return jsonify({
        "message": "CineMatch API is live. In development, run 'npm run dev' inside /frontend or build the dist folder."
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ["true", "1"]
    logger.info(f"Starting CineMatch server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug)
