import os
import requests
import zipfile
import io

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "movielens")
os.makedirs(DATA_DIR, exist_ok=True)

URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"

print(f"Downloading MovieLens dataset from {URL} via requests...")
r = requests.get(URL, verify=False, timeout=30)
print(f"Downloaded {len(r.content)} bytes. Extracting...")
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall(DATA_DIR)
print(f"Extracted to {DATA_DIR}!")

extracted_dir = os.path.join(DATA_DIR, "ml-latest-small")
if os.path.exists(extracted_dir):
    print("Files in dataset:", os.listdir(extracted_dir))
