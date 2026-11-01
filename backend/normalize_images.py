import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_db

with get_db() as conn:
    cursor = conn.cursor()
    # Fix TV shows
    cursor.execute("""
    UPDATE tv_shows
    SET poster_path = 'https://image.tmdb.org/t/p/w500' || poster_path
    WHERE poster_path LIKE '/%' AND poster_path NOT LIKE 'http%';
    """)
    cursor.execute("""
    UPDATE tv_shows
    SET backdrop_path = 'https://image.tmdb.org/t/p/original' || backdrop_path
    WHERE backdrop_path LIKE '/%' AND backdrop_path NOT LIKE 'http%';
    """)
    # Fix TV seasons
    cursor.execute("""
    UPDATE tv_seasons
    SET poster_path = 'https://image.tmdb.org/t/p/w500' || poster_path
    WHERE poster_path LIKE '/%' AND poster_path NOT LIKE 'http%';
    """)
    # Fix TV episodes
    cursor.execute("""
    UPDATE tv_episodes
    SET still_path = 'https://image.tmdb.org/t/p/w500' || still_path
    WHERE still_path LIKE '/%' AND still_path NOT LIKE 'http%';
    """)

    # Clean up test show 1 if empty
    cursor.execute("DELETE FROM movies WHERE id = 1 AND poster_path IS NULL")

    conn.commit()
    print("Database image URLs normalized successfully.")
    sample = cursor.execute("SELECT name, poster_path, backdrop_path FROM tv_shows LIMIT 3").fetchall()
    for s in sample:
        print("Show:", s["name"])
        print("  Poster:  ", s["poster_path"])
        print("  Backdrop:", s["backdrop_path"])

