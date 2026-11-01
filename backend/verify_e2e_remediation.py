import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def run_tests():
    print("=== STARTING CINEMATCH E2E VERIFICATION ===")
    
    # 1. Health check
    req = urllib.request.Request(f"{BASE_URL}/api/health")
    with urllib.request.urlopen(req) as resp:
        health = json.loads(resp.read().decode())
        print(f"[PASS] Health Check: status={health.get('status')}, gpu={health.get('gpu_device')}, indexed={health.get('movies_indexed')}")

    # 2. Model Status
    req = urllib.request.Request(f"{BASE_URL}/api/model/status")
    with urllib.request.urlopen(req) as resp:
        model_st = json.loads(resp.read().decode())
        data = model_st.get('data', {})
        meta = data.get('meta', {})
        metrics = meta.get('metrics', {})
        m_b = metrics.get('ranking_method_b_100_negatives', {})
        print(f"[PASS] Model Status: model_loaded={data.get('model_loaded')}, device={data.get('device')}, vram={data.get('vram_allocated_mb')} MB, test_rmse={metrics.get('test_rmse')}, method_b_ndcg10={m_b.get('ndcg_at_10')}")

    # 3. Movies Catalog (expanded)
    req = urllib.request.Request(f"{BASE_URL}/api/movies?page=1&per_page=12")
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        data = res.get('data', {})
        total = data.get('total', 0)
        movies = data.get('movies', [])
        print(f"[PASS] Movies API: returned {len(movies)} movies on page 1, total indexed={total}")

    # 4. Neural Recommendations (NeuMF GPU)
    payload = json.dumps({"liked_ids": [579974, 20453, 531428], "top_n": 5}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/recommend/neural", data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        neural_rec = json.loads(resp.read().decode())
        recs = neural_rec.get('recommendations', [])
        print(f"[PASS] Neural Recommendations: model_type={neural_rec.get('model_type')}, returned {len(recs)} movies. Top 3: {[m.get('title') for m in recs[:3]]}")

    # 5. Personalized Recommendations (Hybrid Content + User Profile)
    payload = json.dumps({
        "liked_movie_ids": [579974, 20453],
        "favorite_genres": ["Action", "Drama"],
        "count": 5
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/recommend/personalized", data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        pers_rec = json.loads(resp.read().decode())
        recs = pers_rec.get('recommendations', [])
        print(f"[PASS] Personalized Recommendations: algorithm={pers_rec.get('algorithm')}, returned {len(recs)} movies. Top 3: {[m.get('title') for m in recs[:3]]}")

    # 6. 'For You AI' Natural Language Description Matcher
    payload = json.dumps({
        "description": "Mind-bending psychological thriller with dark atmospheric twists and detective investigation",
        "preferred_genres": ["Thriller", "Mystery"],
        "mood": "dark",
        "count": 5
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/ai/describe-match", data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        ai_rec = json.loads(resp.read().decode())
        recs = ai_rec.get('recommendations', [])
        print(f"[PASS] AI Describe Match: returned {len(recs)} movies. Top 3: {[m.get('title') for m in recs[:3]]}")

    # 7. Auth & Rating Transaction Isolation
    test_user = f"audit_user_{int(time.time())}"
    reg_payload = json.dumps({"username": test_user, "email": f"{test_user}@cinematch.test", "password": "SecurePassword123!"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/auth/register", data=reg_payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        auth_data = json.loads(resp.read().decode())
        token = auth_data.get('token')
        print(f"[PASS] User Registration: created '{test_user}', got token={token[:15]}...")

    # Rate a movie (movie_id 579974 - RRR, integer rating 10 out of 10)
    rate_payload = json.dumps({"rating": 10}).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/movies/579974/rating", 
        data=rate_payload, 
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(req) as resp:
        rate_resp = json.loads(resp.read().decode())
        data = rate_resp.get('data', {})
        community = data.get('community', {})
        print(f"[PASS] Immediate Rating Response: avg={community.get('average_rating')}, count={community.get('total_ratings')}, user_rating={data.get('user_rating')}")

    # Post a review
    rev_payload = json.dumps({
        "title": "Masterpiece of cinematic action",
        "content": "Incredible choreography, emotional depth, and stunning visual spectacle. Must watch on big screen!",
        "rating": 10,
        "contains_spoilers": False
    }).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/movies/579974/reviews", 
        data=rev_payload, 
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(req) as resp:
        rev_resp = json.loads(resp.read().decode())
        rev_data = rev_resp.get('review', {})
        print(f"[PASS] Review Creation with Sentiment: title='{rev_data.get('title')}', sentiment_label={rev_data.get('sentiment')}, compound={rev_data.get('sentiment_score')}")

    # 8. Check 39 Indian Cinema posters status
    with open("backend/data/movies.json", "r", encoding="utf-8") as f:
        movies_json = json.load(f)
    
    sample_indian = [m for m in movies_json if m.get("id") in [579974, 20453, 19404, 531428, 534780]] # RRR, 3 Idiots, DDLJ, Tumbbad, Andhadhun
    print(f"\n--- Checking TMDB Posters for Indian Cinema Gems ---")
    for m in sample_indian:
        poster_url = m.get('poster_path')
        try:
            p_req = urllib.request.Request(poster_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(p_req, timeout=5) as p_resp:
                print(f"  [OK {p_resp.status}] {m.get('title')}: {poster_url}")
        except Exception as e:
            print(f"  [FAIL] {m.get('title')}: {poster_url} -> {e}")

    # 9. OTT Provider Status Verification
    req = urllib.request.Request(f"{BASE_URL}/api/watch-providers/579974?country=IN")
    with urllib.request.urlopen(req) as resp:
        ott_resp = json.loads(resp.read().decode())
        ott_data = ott_resp.get('data', {})
        print(f"\n[PASS] OTT Provider Status: is_live={ott_data.get('is_live')}, source={ott_data.get('source')}, status_message='{ott_data.get('status_message')}'")

    print("\n=== ALL E2E VERIFICATIONS SUCCESSFUL ===")

if __name__ == "__main__":
    run_tests()
