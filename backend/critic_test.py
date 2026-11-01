import requests
import json

BASE = "http://127.0.0.1:5000"

def test_suite():
    print("=== CRITIC TEST SUITE: CineMatch ===")

    # 1. Health check
    h = requests.get(f"{BASE}/api/health")
    assert h.status_code == 200, f"Health check failed: {h.status_code}"
    print("[OK] API & Recommender Health: 200 OK, Indexed:", h.json().get("movies_indexed"))

    # 2. MCQ Personalization Flow Test (Test with Indian and Western anchors)
    mcq1 = requests.post(f"{BASE}/api/recommend/onboarding", json={
        "last_watched": "RRR",
        "genres": ["Action", "History", "Drama"],
        "mood": "High-Octane Adrenaline",
        "era_pacing": "Modern Blockbusters",
        "already_watched_ids": [579974],
        "count": 10
    })
    assert mcq1.status_code == 200, "MCQ 1 failed"
    data1 = mcq1.json()["data"]
    assert len(data1["next_to_watch"]) > 0, "No next_to_watch returned"
    print("[OK] MCQ Onboarding (Anchor: RRR):")
    print(f"   Anchor identified: {data1['anchor_movie']}")
    print(f"   Next to watch count: {len(data1['next_to_watch'])}")
    print(f"   Top 1: {data1['next_to_watch'][0]['title']} ({data1['next_to_watch'][0].get('recommendation_reason')})")

    # 3. Test MCQ with Custom Title (e.g. Inception)
    mcq2 = requests.post(f"{BASE}/api/recommend/onboarding", json={
        "last_watched": "Inception",
        "genres": ["Science Fiction", "Mystery"],
        "mood": "Mind-Bending & Complex",
        "era_pacing": "Golden Era 2000s & 90s",
        "already_watched_ids": [27205],
        "count": 10
    })
    assert mcq2.status_code == 200
    data2 = mcq2.json()["data"]
    print(f"[OK] MCQ Onboarding (Anchor: Inception): Top 1: {data2['next_to_watch'][0]['title']}")

    # 4. Test "For You AI" Agent with 4 Diverse Natural Language Prompts
    prompts = [
        ("dark psychological detective noir in rain", ["Crime", "Thriller"], "Mind-Bending"),
        ("wholesome animated journey about friendship and family", ["Animation", "Comedy"], "Comfort & Feel-Good"),
        ("epic space mission dealing with wormholes and black holes", ["Science Fiction"], "Mind-Bending"),
        ("heartfelt romance with witty banter and music", ["Romance", "Drama"], "Emotional & Profound"),
    ]

    for p, g, m in prompts:
        ai_res = requests.post(f"{BASE}/api/ai/describe-match", json={
            "description": p,
            "preferred_genres": g,
            "mood": m,
            "count": 10
        })
        assert ai_res.status_code == 200, f"AI describe failed for '{p}'"
        recs = ai_res.json()["recommendations"]
        assert len(recs) == 10, f"Expected 10 recs, got {len(recs)}"
        top = recs[0]
        print(f"[OK] For You AI Prompt: '{p[:30]}...' -> #1: {top['title']} ({top['similarity_score']*100:.1f}%)")
        print(f"   AI Justification: {top.get('recommendation_reason')}")

    # 5. Test Continuous Online Retraining & Negative Filtering
    # If user marks 'The Dark Knight' (155) as already watched, it must NOT appear in recommendations!
    retrain_res = requests.post(f"{BASE}/api/recommend/retrain", json={
        "liked_movie_ids": [157336], # Interstellar
        "watched_movie_ids": [155, 27205], # The Dark Knight, Inception
        "disliked_movie_ids": [],
        "watchlist_movie_ids": [579974],
        "favorite_genres": ["Science Fiction", "Action"],
        "count": 15
    })
    assert retrain_res.status_code == 200
    retrain_data = retrain_res.json()
    recs = retrain_data["recommendations"]
    rec_ids = [m["id"] for m in recs]
    assert 155 not in rec_ids, "CRITICAL BUG: Already watched movie (155) appeared in recommendations!"
    assert 27205 not in rec_ids, "CRITICAL BUG: Already watched movie (27205) appeared in recommendations!"
    print("[OK] Continuous Learning & Negative Filtering:")
    print(f"   Telemetry signals: {retrain_data['model_telemetry']['total_signals']}")
    print(f"   Learned keywords: {retrain_data['model_telemetry']['learned_keywords']}")
    print(f"   Excluded watched IDs (155, 27205) verified: NOT in recommendation pool!")

    # 6. Test OTT Watch Providers endpoint for Indian market
    wp = requests.get(f"{BASE}/api/watch-providers/579974?country=IN")
    assert wp.status_code == 200
    wp_data = wp.json()["data"]
    assert wp_data["has_availability"] is True
    print(f"[OK] OTT Watch Providers (RRR in IN): Verified {len(wp_data.get('subscription', []))} subscriptions")

    print("\n=== ALL CRITIC TESTS PASSED WITH 100% SUCCESS! ===")

if __name__ == "__main__":
    test_suite()
