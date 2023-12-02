import os
import re
import json
import requests
import hashlib
import functions_framework
from functools import partial
from datetime import datetime
from google.cloud import bigquery
from google.cloud import storage


LIMIT = int(os.getenv("REQUEST_LIMIT", 10))
SCRAPE_URL = f"http://newplayer.rogersradio.ca/CHFI/widget/recently_played?num_per_page={LIMIT}"

PROJECT_ID = os.getenv("PROJECT_ID")
TABLE_NAME = f"{PROJECT_ID}.{os.getenv('DATASET_ID')}.{os.getenv('TABLE_ID')}"

BUCKET_NAME = os.getenv("BUCKET_NAME")

DRY_RUN = os.getenv("DRY_RUN", False)

client = bigquery.Client(project=PROJECT_ID)

# Clean the title (remove bracketed version info at end, variants of ing vs in', etc.)
def clean_title(title):
    title = title.strip()
    # Remove bracketed version info
    title = re.sub(r"[\(\[][\w\s\-.]+[\)\]]$", "", title)
    # Normalize "in'" to "ing"
    title = re.sub(r"(\w)in'(\s|$)", r"\1ing\2", title)
    return title

# Create a consistent ID for the song
def normalize_title(title):
    id = title.lower()
    id = re.sub(r"[\s\-]", "", id)
    return id

def to_record(song, scrape_date):
    play_id = hashlib.md5((str(song["updated_at"]) + "_" + str(song["started_at"])).encode()).hexdigest()
    song_title_clean = clean_title(song["song_title"])
    song_id = normalize_title(song_title_clean)

    return {
        "timestamp": int(song["updated_at"]),
        "scrape_timestamp": scrape_date,
        "artist": song["artist"],
        "play_id": play_id,
        "song_id": song_id,
        "song_title": song_title_clean,
        "song_title_original": song["song_title"],
        "high_res_art_url": song["high_res_art_url"],
        "itunes_purchase_url": song["itunes_purchase_url"],
        "spotify": song["spotify"],
    }

def backup_raw(scrape_date, data):
    filename = f"raw/{scrape_date.isoformat()}.json"
    data_str = json.dumps(data)

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)

    print(f"Backing up to: {filename}")
    try:
        blob.upload_from_string(data_str, content_type="application/json")
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

@functions_framework.cloud_event
def scrape(cloud_event):
    now = datetime.now()
    now_epoch = int(now.timestamp())

    print("Checking last scraped song date...")
    res = client.query(f"SELECT MAX(timestamp) as last_scrape FROM {TABLE_NAME}")
    last_scraped_res = next(res.result(), None)
    if last_scraped_res and last_scraped_res[0]:
        print(last_scraped_res)
        print(last_scraped_res.get("last_scrape"))
        # Get the epoch time from the last scraped time
        last_scraped = last_scraped_res[0]
        print(f"Last scraped: {last_scraped}")
    else:
        # Nothing - last scraped is the first date of xmas songs played this year
        last_scraped = 1700228188
        print(f"No data, using beginning of xmas songs this year: {last_scraped}")

    print("Scraping...")
    result = requests.get(SCRAPE_URL)
    songs = result.json()

    # Backup raw data
    backup_raw(now, songs)

    # Convert to DB-ready
    records = map(partial(to_record, scrape_date=now_epoch), songs)
    records = filter(lambda r: r["timestamp"] > last_scraped, records)
    records = list(records)

    if len(records) > 0:
        # Add songs to DB
        if DRY_RUN:
            print(f"Would have added {len(records)} songs. Example:")
            print(records[0])
        else:
            try:
                table = client.get_table(TABLE_NAME)
                errors = client.insert_rows(table, records)
                if errors:
                    print("Errors:", errors)
                else:
                    print(f"Inserted {len(records)} songs")
            except Exception as e:
                print(f"Error adding songs: {e}")
    else:
        print("No new songs to add")

    print("Done")