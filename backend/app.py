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
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health status and recommender readiness."""
    return jsonify({
        "status": "healthy",
        "app": "CineMatch API",
        "version": "1.0.0",
        "movies_indexed": len(movie_service.movies),
        "recommender_ready": recommender.tfidf_matrix is not None,
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
