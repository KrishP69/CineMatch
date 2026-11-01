import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from community_service import community_service
from auth_service import auth_service
from database import get_db, init_db

def test_database_regression():
    print("=" * 60)
    print("RUNNING DATABASE REGRESSION & TRANSACTION ISOLATION TEST")
    print("=" * 60)

    init_db()

    # 1. Create a test user
    test_username = f"testuser_{os.urandom(4).hex()}"
    test_email = f"{test_username}@example.com"
    test_password = "SecurePassword123!"

    reg_res = auth_service.register(test_username, test_email, test_password)
    assert reg_res["success"], f"Registration failed: {reg_res}"
    user_id = reg_res["user"]["id"]
    print(f"Created test user: ID {user_id}, {test_username}")

    # Use movie ID 1 (Toy Story) which exists in DB
    movie_id = 1
    with get_db() as conn:
        m = conn.execute("SELECT id FROM movies WHERE id = ?", (movie_id,)).fetchone()
        if not m:
            conn.execute("INSERT OR IGNORE INTO movies (id, title) VALUES (1, 'Toy Story')")
            conn.commit()

    # Clean existing ratings for this test user
    with get_db() as conn:
        conn.execute("DELETE FROM user_ratings WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
        conn.commit()

    # 2. Test Transaction Isolation on First Rating
    print("\n--- Test 1: Immediate committed summary on first rating ---")
    res1 = community_service.rate_movie(user_id=user_id, movie_id=movie_id, rating=9)
    assert res1["success"] is True, f"Rating submission failed: {res1}"
    comm = res1["data"]["community"]
    avg = comm["average_rating"]
    total = comm["total_ratings"]
    print(f"Immediate Response: avg_rating={avg}, total_ratings={total}")
    assert avg is not None, "FAILED: avg_rating is None (Isolation Bug reproduced!)"
    assert total >= 1, f"FAILED: total_ratings ({total}) < 1"
    assert res1["data"]["user_rating"] == 9, "FAILED: user_rating not reflected"
    print("PASS: Immediate committed summary returned correctly.")

    # 3. Test Update / Duplicate Rating Prevention
    print("\n--- Test 2: Update rating (No duplication) ---")
    res2 = community_service.rate_movie(user_id=user_id, movie_id=movie_id, rating=5)
    assert res2["success"] is True
    assert res2["data"]["user_rating"] == 5
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM user_ratings WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)).fetchone()[0]
        assert count == 1, f"FAILED: Duplicate rows found ({count} != 1)"
    print("PASS: Duplicate rating prevented, row successfully updated.")

    # 4. Test Rating Deletion
    print("\n--- Test 3: Rating Deletion ---")
    del_res = community_service.delete_rating(user_id=user_id, movie_id=movie_id)
    assert del_res["success"] is True
    assert del_res["data"]["user_rating"] is None
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM user_ratings WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)).fetchone()[0]
        assert count == 0, "FAILED: Rating still exists after delete"
    print("PASS: Rating deleted successfully.")

    # 5. Test Foreign Key Constraint Enforcement
    print("\n--- Test 4: Foreign Key Enforcement ---")
    fk_failed = False
    try:
        with get_db() as conn:
            conn.execute("INSERT INTO user_ratings (user_id, movie_id, rating) VALUES (99999999, 99999999, 8)")
    except sqlite3.IntegrityError:
        fk_failed = True
    assert fk_failed, "FAILED: Foreign key violation did not raise IntegrityError"
    print("PASS: Foreign key constraints strictly enforced.")

    # 6. Clean up test user
    with get_db() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

    print("\n" + "=" * 60)
    print("ALL DATABASE REGRESSION TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    test_database_regression()
