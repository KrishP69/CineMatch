"""
CineMatch Keep-Alive Bot
Periodically pings the live Render deployment to prevent free-tier spin-down.
"""

import time
import requests
from datetime import datetime

TARGET_URL = "https://cinematch-e7sr.onrender.com/api/health"
PING_INTERVAL_SECONDS = 600  # 10 minutes (Render sleeps after 15 mins)

def ping():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        response = requests.get(TARGET_URL, timeout=25)
        print(f"[{now}] Heartbeat sent to {TARGET_URL} -> HTTP {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
    except Exception as e:
        print(f"[{now}] Heartbeat failed: {e}")

if __name__ == "__main__":
    print(f"Starting CineMatch Keep-Alive Bot on {TARGET_URL}")
    print(f"Ping interval: {PING_INTERVAL_SECONDS // 60} minutes")
    while True:
        ping()
        time.sleep(PING_INTERVAL_SECONDS)

