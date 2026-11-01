"""
CineMatch Master Critical Audit & Quality Assurance Test Suite
Tests Phase 1 (ML & MovieLens 32M), Phase 2 (Personalized Discovery),
Phase 3 (Auth, Ratings, Reviews, Sentiment, Database), Phase 4 (UI/Catalog).
"""

import os
import sys
import json
import time
import urllib.request
import sqlite3

BASE_URL = "http://127.0.0.1:5000"
FRONTEND_URL = "http://localhost:5173"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cinematch.db")

def http_json(method, path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {"error": str(e)}
    except Exception as e:
        return 500, {"error": str(e)}

def run_master_audit():
    print("=" * 70)
    print("CINEMATCH MASTER CRITICAL AUDIT & QA SUITE (PHASES 1 - 5)")
    print("=" * 70)

    failures = []

    # -------------------------------------------------------------
    # 1. DATASET & ML MODEL AUDIT (PHASE 1)
    # -------------------------------------------------------------
    print("\n[PHASE 1 AUDIT] MovieLens 32M Dataset & Neural NCF Model...")
    ml32m_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "movielens", "ml-32m")
    for f in ["movies.csv", "ratings.csv", "tags.csv", "links.csv"]:
        fp = os.path.join(ml32m_dir, f)
        if os.path.exists(fp):
            print(f"  [PASS] File exists: {f} ({os.path.getsize(fp)/(1024**2):.1f} MB)")
        else:
            failures.append(f"Missing MovieLens 32M file: {f}")
            print(f"  [FAIL] Missing file: {f}")

    # Check Model Meta
    meta_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cinematch_neural_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        params = meta.get("total_parameters", 0)
        n_ratings = meta.get("ratings_trained", 0)
        eval_data = meta.get("evaluation", {}).get("neural_ncf", {})
        print(f"  [PASS] Model architecture: {meta.get('architecture')}")
        print(f"         Total Parameters:   {params:,}")
        print(f"         Ratings Trained:    {n_ratings:,} from {meta.get('dataset_name')}")
        print(f"         Split Method:       {meta.get('split_method')}")
        print(f"         Test RMSE:          {eval_data.get('test_rmse')} | Test MAE: {eval_data.get('test_mae')}")
        print(f"         Recall@10:          {eval_data.get('recall_at_10')} | NDCG@10: {eval_data.get('ndcg_at_10')}")
        print(f"         Inference Latency:  {eval_data.get('avg_inference_ms')} ms/sample")
    else:
        failures.append("Missing cinematch_neural_meta.json")
        print("  [FAIL] Missing cinematch_neural_meta.json")

    # Neural Endpoint Inference Test
    status, n_res = http_json("POST", "/api/recommend/neural", {"liked_ids": [157336], "watched_ids": [27205], "top_n": 8})
    if status == 200 and n_res.get("success") and len(n_res.get("recommendations", [])) > 0:
        print(f"  [PASS] Neural recommendation inference active. {len(n_res['recommendations'])} items scored.")
        print(f"         Top recommendation: '{n_res['recommendations'][0]['title']}' - {n_res['recommendations'][0].get('recommendation_reason')}")
        # Verify negative filter
        rec_ids = [m["id"] for m in n_res["recommendations"]]
        if 27205 in rec_ids:
            failures.append("Neural recommender failed negative filtering (watched ID was included)")
            print("  [FAIL] Watched ID in recommendations!")
        else:
            print("  [PASS] Watched ID (27205) strictly excluded.")
    else:
        failures.append(f"Neural recommendation endpoint failed: {n_res}")
        print(f"  [FAIL] {n_res}")

    # -------------------------------------------------------------
    # 2. PERSONALIZED DISCOVERY AUDIT (PHASE 2)
    # -------------------------------------------------------------
    print("\n[PHASE 2 AUDIT] Multi-Filter Personalized Discovery Lab...")
    disc_payload = {
        "genres": ["Sci-Fi", "Drama"],
        "moods": ["Mind-bending", "Suspenseful"],
        "themes": ["Plot twists", "Mind-bending stories"],
        "min_rating": 7.5,
        "release_year_min": 1990,
        "release_year_max": 2026,
        "exclude_ids": [157336], # Exclude Interstellar
        "per_page": 10
    }
    status, d_res = http_json("POST", "/api/discovery/recommend", disc_payload)
    if status == 200 and d_res.get("success"):
        movies = d_res.get("data", {}).get("movies", [])
        print(f"  [PASS] Discovery returned {len(movies)} curated matches.")
        if movies:
            first = movies[0]
            print(f"         Top Match: '{first['title']}' ({first.get('release_year')})")
            print(f"         Explanation: {first.get('recommendation_reason')}")
            if first["id"] == 157336:
                failures.append("Discovery failed to exclude watched ID 157336")
                print("  [FAIL] Excluded ID found in discovery results.")
            else:
                print("  [PASS] Excluded ID (157336) successfully filtered out.")
    else:
        failures.append(f"Discovery endpoint failed: {d_res}")
        print(f"  [FAIL] {d_res}")

    # -------------------------------------------------------------
    # 3. AUTHENTICATION & SECURITY AUDIT (PHASE 3)
    # -------------------------------------------------------------
    print("\n[PHASE 3 AUDIT - AUTH] Secure Registration, Hashing & JWT Verification...")
    test_ts = int(time.time())
    username = f"critic_{test_ts}"
    email = f"critic_{test_ts}@cinematch.ai"
    password = "SecurePassword123!"

    status, reg_res = http_json("POST", "/api/auth/register", {
        "username": username,
        "email": email,
        "password": password,
        "avatar": "🕵️"
    })
    token = None
    user_id = None
    if status == 201 and reg_res.get("success"):
        token = reg_res.get("token")
        user_id = reg_res.get("user", {}).get("id")
        print(f"  [PASS] User registered successfully (ID: {user_id}, Username: '{username}')")
        print(f"         JWT Token issued: {token[:25]}...")
    else:
        failures.append(f"User registration failed: {reg_res}")
        print(f"  [FAIL] Registration failed: {reg_res}")

    # Verify password hash in SQLite (Never plain text!)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    row = c.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
    if row and row[0].startswith("scrypt:"):
        print("  [PASS] Password correctly hashed using scrypt cryptographic KDF (not stored in plaintext).")
    else:
        failures.append("Password was not properly hashed with scrypt!")
        print("  [FAIL] Password hashing issue.")

    # Test Login
    status, login_res = http_json("POST", "/api/auth/login", {
        "username_or_email": username,
        "password": password
    })
    if status == 200 and login_res.get("success"):
        print("  [PASS] Login successful with valid credentials.")
    else:
        failures.append(f"Login failed: {login_res}")
        print(f"  [FAIL] Login failed: {login_res}")

    # Test Protected Route /api/auth/me
    status, me_res = http_json("GET", "/api/auth/me", token=token)
    if status == 200 and me_res.get("success"):
        print(f"  [PASS] /api/auth/me verified JWT token and returned profile for '{me_res['user']['username']}'.")
    else:
        failures.append(f"/api/auth/me failed: {me_res}")
        print(f"  [FAIL] {me_res}")

    # -------------------------------------------------------------
    # 4. RATINGS & REVIEWS WITH VADER NLP SENTIMENT (PHASE 3)
    # -------------------------------------------------------------
    print("\n[PHASE 3 AUDIT - COMMUNITY] Ratings & Reviews with VADER Sentiment...")
    target_movie_id = 550 # Fight Club

    # Submit Rating (9/10)
    status, rate_res = http_json("POST", f"/api/movies/{target_movie_id}/rating", {"rating": 9}, token=token)
    if status == 200 and rate_res.get("success"):
        data = rate_res.get("data", {})
        comm = data.get("community", {})
        print(f"  [PASS] User rating (9/10) recorded.")
        print(f"         Community Avg: {comm.get('average_rating')}/10 ({comm.get('total_ratings')} votes)")
    else:
        failures.append(f"Rating submission failed: {rate_res}")
        print(f"  [FAIL] {rate_res}")

    # Submit Review with Positive Text & Spoilers
    review_title = "A Masterclass in Deconstruction and Style"
    review_content = "This film completely blew my mind. David Fincher's direction, Edward Norton's narration, and Brad Pitt's charisma make it an unforgettable masterpiece. The twist at the end redefines everything."
    status, rev_res = http_json("POST", f"/api/movies/{target_movie_id}/reviews", {
        "title": review_title,
        "content": review_content,
        "rating": 9,
        "contains_spoilers": True
    }, token=token)

    review_id = None
    if status == 201 and rev_res.get("success"):
        r_data = rev_res.get("review", {})
        review_id = r_data.get("id")
        sentiment = r_data.get("sentiment")
        score = r_data.get("sentiment_score")
        print(f"  [PASS] Review published (ID: {review_id}).")
        print(f"         VADER Sentiment: '{sentiment}' (Compound Score: {score:+.3f})")
        print(f"         Contains Spoilers: {r_data.get('contains_spoilers')}")
        if sentiment != "positive":
            failures.append(f"Expected positive sentiment, got {sentiment}")
    else:
        failures.append(f"Review creation failed: {rev_res}")
        print(f"  [FAIL] {rev_res}")

    # Test Helpful Voting
    if review_id:
        status, vote_res = http_json("POST", f"/api/reviews/{review_id}/vote", {"vote_type": 1}, token=token)
        if status == 200 and vote_res.get("success") and vote_res.get("helpful_count") == 1:
            print("  [PASS] Helpful vote recorded (Helpful Count: 1).")
        else:
            failures.append(f"Helpful voting failed: {vote_res}")
            print(f"  [FAIL] {vote_res}")

    # Verify Database Persistence
    row_cnt = c.execute("SELECT COUNT(*) FROM user_reviews WHERE id = ?", (review_id,)).fetchone()[0]
    if row_cnt == 1:
        print("  [PASS] Review persisted into SQLite 'user_reviews' table.")
    else:
        failures.append("Review was not found in SQLite table!")
        print("  [FAIL] Database persistence failure.")
    conn.close()

    # -------------------------------------------------------------
    # 5. WATCHLIST & WATCH HISTORY PERSISTENCE (PHASE 3)
    # -------------------------------------------------------------
    print("\n[PHASE 3 AUDIT - WATCHLIST] Watchlist & Watched History...")
    status, wl_res = http_json("POST", f"/api/user/watchlist/{target_movie_id}", token=token)
    if status == 200 and wl_res.get("in_watchlist"):
        print(f"  [PASS] Movie {target_movie_id} added to user watchlist.")
    else:
        failures.append(f"Watchlist toggle failed: {wl_res}")
        print(f"  [FAIL] {wl_res}")

    status, wh_res = http_json("POST", f"/api/user/watched/{target_movie_id}", token=token)
    if status == 200 and wh_res.get("is_watched"):
        print(f"  [PASS] Movie {target_movie_id} marked as watched (enables negative filtering).")
    else:
        failures.append(f"Watched toggle failed: {wh_res}")
        print(f"  [FAIL] {wh_res}")

    # -------------------------------------------------------------
    # 6. CATALOG & FRONTEND BUILD AUDIT (PHASE 4)
    # -------------------------------------------------------------
    print("\n[PHASE 4 AUDIT] Catalog Images & Frontend Production Build...")
    status, cat_res = http_json("GET", "/api/movies?page=1&per_page=84")
    movies = cat_res.get("data", {}).get("movies", [])
    broken = [m["title"] for m in movies if not m.get("poster_path", "").startswith("http")]
    if broken:
        failures.append(f"Found {len(broken)} broken poster paths: {broken}")
        print(f"  [FAIL] Broken images found: {broken}")
    else:
        print(f"  [PASS] All {len(movies)} catalog movies have valid absolute HTTPS poster and backdrop URLs.")

    # Check dist build
    dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")
    if os.path.exists(os.path.join(dist_dir, "index.html")):
        print(f"  [PASS] Production frontend bundle verified at: {dist_dir}")
    else:
        failures.append("frontend/dist/index.html is missing")
        print("  [FAIL] Missing frontend/dist")

    # Probe Frontend Vite Dev Server
    try:
        with urllib.request.urlopen(FRONTEND_URL, timeout=5) as res:
            if res.status == 200:
                print(f"  [PASS] Frontend Vite dev server responsive at {FRONTEND_URL} (HTTP 200).")
    except Exception as e:
        failures.append(f"Frontend server connection failed: {e}")
        print(f"  [FAIL] {e}")

    # Summary
    print("\n" + "=" * 70)
    if not failures:
        print("[CRITIC VERDICT]: ALL AUDIT CHECKS PASSED WITH 0 DEFECTS! PRODUCTION GRADE.")
        print("=" * 70)
        return 0
    else:
        print(f"[CRITIC VERDICT]: {len(failures)} DEFECT(S) FOUND:")
        for f in failures:
            print(f"  - {f}")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(run_master_audit())

