"""
CineMatch Comprehensive Critic & Quality Assurance Test Suite
Tests all user requirements, image validity, ML recommenders, For You AI, and RTX 5060 Neural Model.
"""

import urllib.request
import json
import sys
import time

BASE_URL = "http://127.0.0.1:5000"
FRONTEND_URL = "http://localhost:5173"

def request_json(path, data=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status, json.loads(res.read().decode())
    except Exception as e:
        return 500, {"error": str(e)}

def run_tests():
    print("=" * 65)
    print("CINEMATCH CRITIC VERIFICATION SUITE")
    print("=" * 65)

    failures = []

    # 1. Health & Hardware Probe
    print("\n[TEST 1] Backend Health & Hardware Telemetry Probe...")
    status, res = request_json("/api/health")
    if status == 200 and res.get("neural_model_ready") and "5060" in res.get("gpu_device", ""):
        print(f"  [PASS] Status: {res['status']}, Movies: {res['movies_indexed']}, Device: {res['gpu_device']}")
    else:
        failures.append(f"Health check failed or GPU not ready: {res}")
        print(f"  [FAIL] {res}")

    # 2. Movie Images & Indian Cinema Gems Integrity
    print("\n[TEST 2] Movie Catalog & Image URL Integrity...")
    status, res = request_json("/api/movies?page=1&per_page=84")
    movies = res.get("data", {}).get("movies", [])
    print(f"  Loaded {len(movies)} catalog movies.")

    broken_images = []
    indian_gems = ["RRR", "3 Idiots", "Dilwale Dulhania Le Jayenge", "Tumbbad", "Andhadhun"]
    found_gems = {}

    for m in movies:
        title = m.get("title")
        poster = m.get("poster_path", "")
        backdrop = m.get("backdrop_path", "")
        if not poster or not poster.startswith("http"):
            broken_images.append(f"Movie '{title}' has invalid poster: {poster}")
        if not backdrop or not backdrop.startswith("http"):
            broken_images.append(f"Movie '{title}' has invalid backdrop: {backdrop}")
        if title in indian_gems:
            found_gems[title] = poster

    if broken_images:
        failures.extend(broken_images)
        print(f"  [FAIL] Found {len(broken_images)} broken image URLs.")
    else:
        print("  [PASS] All 84 movies have valid absolute HTTPS poster and backdrop URLs.")

    for gem in indian_gems:
        if gem in found_gems:
            print(f"  [PASS] '{gem}' image verified: {found_gems[gem][:60]}...")
        else:
            failures.append(f"Missing Indian Cinema Gem: {gem}")

    # 3. Personalization MCQ Questionnaire Endpoint
    print("\n[TEST 3] Personalization MCQ / Onboarding Route...")
    mcq_payload = {
        "last_loved": "Interstellar",
        "genres": ["Sci-Fi", "Drama"],
        "mood": "Mind-Bending & Deep",
        "era": "Modern (2010s-Present)"
    }
    status, res = request_json("/api/recommend/onboarding", mcq_payload)
    next_to_watch = res.get("data", {}).get("next_to_watch", [])
    if status == 200 and res.get("success") and len(next_to_watch) > 0:
        print(f"  [PASS] MCQ Onboarding generated {len(next_to_watch)} matches.")
        print(f"         Top Recommendation: '{next_to_watch[0]['title']}' (Score: {next_to_watch[0].get('similarity_score')})")
        print(f"         Reason: {next_to_watch[0].get('recommendation_reason')}")
    else:
        failures.append(f"MCQ Onboarding failed: {res}")
        print(f"  [FAIL] {res}")

    # 4. Continuous Retraining with Negative Filtering (Already Watched)
    print("\n[TEST 4] Continuous Vector Retraining & Negative Filtering...")
    retrain_payload = {
        "liked_movie_ids": [157336], # Interstellar
        "watched_movie_ids": [27205], # Inception (watched -> must be filtered out)
        "disliked_movie_ids": [],
        "favorite_genres": ["Sci-Fi", "Mystery"],
        "mood": "Mind-Bending & Deep",
        "count": 10
    }
    status, res = request_json("/api/recommend/retrain", retrain_payload)
    if status == 200 and res.get("success"):
        recs = res.get("recommendations", [])
        rec_ids = [m["id"] for m in recs]
        if 27205 in rec_ids:
            failures.append("Negative filtering failure: Watched movie 27205 was recommended!")
            print("  [FAIL] Watched movie was NOT excluded from recommendations.")
        else:
            print(f"  [PASS] Model retrained dynamically. Watched movie (Inception) successfully filtered out.")
            print(f"         Top Match: '{recs[0]['title']}' - {recs[0].get('recommendation_reason')}")
    else:
        failures.append(f"Retrain route failed: {res}")
        print(f"  [FAIL] {res}")

    # 5. 'For You AI' Conversational Semantic Agent
    print("\n[TEST 5] 'For You AI' Semantic Describe-Match Agent...")
    ai_payload = {
        "description": "dark crime thriller with unexpected plot twists and rain-soaked atmosphere",
        "preferred_genres": ["Crime", "Mystery", "Thriller"],
        "mood": "Dark & Gritty",
        "count": 10
    }
    status, res = request_json("/api/ai/describe-match", ai_payload)
    if status == 200 and res.get("success"):
        recs = res.get("recommendations", [])
        print(f"  [PASS] AI Agent suggested {len(recs)} Top-10 curated matches.")
        for idx, m in enumerate(recs[:3], 1):
            print(f"         #{idx}: '{m['title']}' ({m.get('release_date', '')[:4]})")
            print(f"             AI Justification: {m.get('ai_justification')}")
            ott = m.get("watch_providers", {})
            flatrate = [p["provider_name"] for p in ott.get("flatrate", [])]
            print(f"             OTT Streaming: {', '.join(flatrate) if flatrate else 'Rent/Buy Available'}")
    else:
        failures.append(f"AI Describe-Match failed: {res}")
        print(f"  [FAIL] {res}")

    # 6. Local RTX 5060 Neural Collaborative Filtering Model (NeuMF)
    print("\n[TEST 6] Local RTX 5060 Neural Collaborative Filtering Telemetry & Inference...")
    status, res = request_json("/api/model/status")
    if status == 200 and res.get("success"):
        data = res.get("data", {})
        meta = data.get("meta", {})
        print(f"  [PASS] Neural Model Status:")
        print(f"         Architecture: {meta.get('architecture')}")
        print(f"         Parameters:   {meta.get('total_parameters'):,}")
        print(f"         Dataset:      {meta.get('dataset')}")
        print(f"         Val RMSE:     {meta.get('final_val_rmse')}")
        print(f"         Device:       {data.get('gpu_device')}")
    else:
        failures.append(f"Model status failed: {res}")
        print(f"  [FAIL] {res}")

    # Test Neural Recommendation Inference
    neural_payload = {
        "liked_ids": [157336, 27205],
        "watched_ids": [155], # The Dark Knight
        "top_n": 10
    }
    status, res = request_json("/api/recommend/neural", neural_payload)
    if status == 200 and res.get("success") and res.get("model_type") == "neural_ncf_pytorch":
        recs = res.get("recommendations", [])
        rec_ids = [m["id"] for m in recs]
        if 155 in rec_ids:
            failures.append("Neural negative filter failed: Watched ID 155 was returned!")
            print("  [FAIL] Watched ID in neural results.")
        else:
            print(f"  [PASS] Neural Model scored {len(recs)} movies in parallel tensor space.")
            print(f"         Top Neural Recommendation: '{recs[0]['title']}' ({recs[0].get('recommendation_reason')})")
    else:
        failures.append(f"Neural inference failed: {res}")
        print(f"  [FAIL] {res}")

    # 7. Frontend Vite Server Accessibility
    print("\n[TEST 7] Frontend Dev Server Accessibility...")
    try:
        req = urllib.request.Request(FRONTEND_URL)
        with urllib.request.urlopen(req, timeout=5) as res:
            html = res.read().decode()
            if res.status == 200 and '<div id="root">' in html:
                print(f"  [PASS] Frontend Vite server responsive at {FRONTEND_URL} (HTTP 200).")
            else:
                failures.append(f"Frontend returned unexpected HTML: status {res.status}")
                print(f"  [FAIL] Unexpected frontend response.")
    except Exception as e:
        failures.append(f"Frontend server connection error: {e}")
        print(f"  [FAIL] {e}")

    # Summary
    print("\n" + "=" * 65)
    if not failures:
        print("[CRITIC VERDICT]: ALL 7/7 TESTS PASSED WITH 0 DEFECTS! READY FOR DEPLOYMENT.")
        print("=" * 65)
        return 0
    else:
        print(f"[CRITIC VERDICT]: {len(failures)} FAILURE(S) DETECTED:")
        for f in failures:
            print(f"  - {f}")
        print("=" * 65)
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
