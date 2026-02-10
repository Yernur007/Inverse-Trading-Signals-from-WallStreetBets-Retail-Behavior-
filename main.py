import requests
import re
import time
import sys
import csv
from datetime import datetime

RUN_ID = datetime.utcnow().strftime("%Y%m%d_%H%M%S")


# CONFIG
URL = "https://www.reddit.com/r/wallstreetbets/rising.json?limit=100"
HEADERS = {"User-Agent": "Mozilla/5.0 (educational sentiment project)"}
TIMEOUT = 10
RECENT_WINDOW = 3 * 60 * 60  # 3 hours in seconds
CSV_FILE = "wsb_inverse_signals.csv"

# SAFE FETCH
def fetch_reddit_data():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limited (429). Try later.")
            sys.exit()
        elif response.status_code == 403:
            print("Access forbidden (403). Check User-Agent.")
            sys.exit()
        else:
            print("HTTP error:", response.status_code)
            sys.exit()

    except requests.exceptions.RequestException as e:
        print("Network error:", e)
        sys.exit()

# HELPERS
def find_tickers(text):
    candidates = re.findall(r"\b[A-Z]{2,5}\b", text)
    stop_words = {
        "CALL", "CALLS", "PUT", "PUTS", "BUY", "SELL",
        "ARE", "FREE", "MONEY", "NOW", "YOLO", "DD"
    }
    return [w for w in candidates if w not in stop_words]

bullish_words = ["buy", "call", "calls", "moon", "rocket", "free money"]
bearish_words = ["put", "puts", "short", "overvalued", "trap"]

def sentiment_score(text):
    text = text.lower()
    score = 0
    for w in bullish_words:
        score += text.count(w)
    for w in bearish_words:
        score -= text.count(w)
    return score

# MAIN LOGIC
if __name__ == "__main__":

    data = fetch_reddit_data()
    posts = data["data"]["children"]

    NOW = int(time.time())
    recent_hype = {}
    older_hype = {}

    for post in posts:
        p = post["data"]
        title = p.get("title", "")
        upvotes = p.get("score", 0)
        created = p.get("created_utc", 0)

        score = sentiment_score(title)
        tickers = set(find_tickers(title))

        if score == 0 or not tickers:
            continue

        for ticker in tickers:
            weighted = score * upvotes
            if NOW - created <= RECENT_WINDOW:
                recent_hype[ticker] = recent_hype.get(ticker, 0) + weighted
            else:
                older_hype[ticker] = older_hype.get(ticker, 0) + weighted

    # SAVE TO CSV
    timestamp = datetime.utcnow().isoformat()
    rows = []

    for ticker in set(recent_hype) | set(older_hype):
        recent = recent_hype.get(ticker, 0)
        older = older_hype.get(ticker, 0)
        delta = recent - older

        if delta > 2000:
            signal = "SELL"
        elif delta < -3000:
            signal = "BUY"
        else:
            signal = "NO_TRADE"

        rows.append([
            RUN_ID,
            timestamp,
            ticker,
            recent,
            older,
            delta,
            signal
        ])

    file_exists = False
    try:
        with open(CSV_FILE, "r"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "run_id",
                "timestamp",
                "ticker",
                "recent_hype",
                "older_hype",
                "delta",
                "signal"
            ])

        writer.writerows(rows)

    print(f"\nSaved {len(rows)} rows to {CSV_FILE}")
