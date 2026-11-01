"""
CineMatch MovieLens 32M Downloader and Data Preparation Pipeline
Source: https://grouplens.org/datasets/movielens/32m/
Files: movies.csv, ratings.csv, tags.csv, links.csv
"""

import os
import sys
import zipfile
import requests
import urllib3
import pandas as pd
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "movielens")
os.makedirs(DATA_DIR, exist_ok=True)

ML32M_ZIP_PATH = os.path.join(DATA_DIR, "ml-32m.zip")
ML32M_EXTRACT_DIR = os.path.join(DATA_DIR, "ml-32m")
URL = "https://files.grouplens.org/datasets/movielens/ml-32m.zip"

def download_ml32m():
    if os.path.exists(ML32M_EXTRACT_DIR) and os.path.exists(os.path.join(ML32M_EXTRACT_DIR, "ratings.csv")):
        print(f"[DATASET] MovieLens 32M already extracted in: {ML32M_EXTRACT_DIR}")
        return True

    print("=" * 60)
    print("DOWNLOADING OFFICIAL MOVIELENS 32M DATASET")
    print(f"Source: {URL}")
    print("=" * 60)

    t0 = time.time()
    try:
        with requests.get(URL, stream=True, verify=False, timeout=60) as r:
            r.raise_for_status()
            total_length = int(r.headers.get("content-length", 0))
            print(f"Total size: {total_length / (1024**2):.1f} MB")
            
            downloaded = 0
            chunk_size = 1024 * 1024 # 1MB chunks
            with open(ML32M_ZIP_PATH, "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = (downloaded / total_length) * 100 if total_length else 0
                        sys.stdout.write(f"\rDownloading: {downloaded / (1024**2):.1f} MB / {total_length / (1024**2):.1f} MB ({percent:.1f}%)")
                        sys.stdout.flush()

        print(f"\nDownload finished in {time.time() - t0:.1f}s. Extracting archive...")
        with zipfile.ZipFile(ML32M_ZIP_PATH, "r") as z:
            z.extractall(DATA_DIR)
        print(f"Extracted to: {ML32M_EXTRACT_DIR}")

        # Remove zip to conserve disk space
        if os.path.exists(ML32M_ZIP_PATH):
            os.remove(ML32M_ZIP_PATH)
            print("Cleaned up temporary zip archive.")
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to download MovieLens 32M: {e}")
        return False

def inspect_and_clean_data():
    print("\n" + "=" * 60)
    print("INSPECTING & VALIDATING MOVIELENS 32M DATASET")
    print("=" * 60)

    movies_path = os.path.join(ML32M_EXTRACT_DIR, "movies.csv")
    ratings_path = os.path.join(ML32M_EXTRACT_DIR, "ratings.csv")
    tags_path = os.path.join(ML32M_EXTRACT_DIR, "tags.csv")
    links_path = os.path.join(ML32M_EXTRACT_DIR, "links.csv")

    for path, name in [(movies_path, "movies.csv"), (ratings_path, "ratings.csv"), (tags_path, "tags.csv"), (links_path, "links.csv")]:
        if not os.path.exists(path):
            print(f"[ERROR] Missing file: {name}")
            return False
        size_mb = os.path.getsize(path) / (1024**2)
        print(f"  - {name}: {size_mb:.1f} MB")

    print("\nLoading and verifying data schemas...")
    movies_df = pd.read_csv(movies_path)
    links_df = pd.read_csv(links_path)
    print(f"  Total movies in dataset: {len(movies_df):,}")
    print(f"  Total link mappings:     {len(links_df):,}")

    # Inspect links and clean tmdbId
    valid_links = links_df.dropna(subset=["tmdbId"]).copy()
    valid_links["tmdbId"] = valid_links["tmdbId"].astype(int)
    print(f"  Valid TMDB mapped movies: {len(valid_links):,}")

    # Inspect sample ratings (read first 500k to verify format & distribution)
    sample_ratings = pd.read_csv(ratings_path, nrows=500000)
    print(f"  Sample 500k ratings range: {sample_ratings['rating'].min()} to {sample_ratings['rating'].max()} (Mean: {sample_ratings['rating'].mean():.2f})")
    print(f"  Sample timestamps range: {pd.to_datetime(sample_ratings['timestamp'], unit='s').min()} to {pd.to_datetime(sample_ratings['timestamp'], unit='s').max()}")

    # Inspect tags
    tags_df = pd.read_csv(tags_path, nrows=100000)
    print(f"  Sample 100k tags: {tags_df['tag'].nunique()} unique tags.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    if download_ml32m():
        inspect_and_clean_data()

