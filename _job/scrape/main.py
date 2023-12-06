import os
import requests
import functions_framework
from functools import partial
from datetime import datetime
from google.cloud import bigquery
from xmas.storage import store_json, fetch_json
from xmas.bigquery import insert, merge
from xmas.normalize import to_record

LIMIT = int(os.getenv("REQUEST_LIMIT", 10))
SCRAPE_URL = f"http://newplayer.rogersradio.ca/CHFI/widget/recently_played?num_per_page={LIMIT}"

PROJECT_ID = os.getenv("PROJECT_ID")
INGEST_TABLE_NAME = f"{PROJECT_ID}.{os.getenv('DATASET_ID')}.{os.getenv('INGEST_TABLE_ID')}"
MAIN_TABLE_NAME = f"{PROJECT_ID}.{os.getenv('DATASET_ID')}.{os.getenv('MAIN_TABLE_ID')}"
BUCKET_NAME = os.getenv("BUCKET_NAME")

DRY_RUN = os.getenv("DRY_RUN", False)

XMAS_START = 1700228188 # November 17, 2023 8:36 - when CHFI started playing Xmas music
XMAS_END = 1704085200 # New Years 2024


@functions_framework.cloud_event
def scrape(cloud_event):
    now = datetime.now()

    print("Scraping...")
    result = requests.get(SCRAPE_URL)
    songs = result.json()

    # Backup raw data
    store_json(PROJECT_ID, BUCKET_NAME, now, songs)
    print("Done")


@functions_framework.cloud_event
def index(cloud_event):
    filename = cloud_event.data["name"]
    try:
        songs = fetch_json(PROJECT_ID, BUCKET_NAME, filename)
    except Exception as e:
        print(f"Failed to fetch {filename}: {e}")
        return -1

    # Extract the date from the filename
    scrape_date_str = filename.split("/")[1].replace(".json", "")
    scrape_date = int(datetime.fromisoformat(scrape_date_str).timestamp())

    now_epoch = int(datetime.now().timestamp())
    records = map(partial(to_record, scrape_date=scrape_date, ingest_timestamp=now_epoch), songs)
    records = filter(lambda r: r["timestamp"] > XMAS_START and r["timestamp"] < XMAS_END, records)
    records = list(records)

    if len(records) > 0:
        client = bigquery.Client(project=PROJECT_ID)

        print(f"Indexing {len(records)} songs into {INGEST_TABLE_NAME}...")
        insert(client, INGEST_TABLE_NAME, records, dry_run=DRY_RUN)

        print(f"Merging {INGEST_TABLE_NAME} into {MAIN_TABLE_NAME}...")
        merge(client, INGEST_TABLE_NAME, MAIN_TABLE_NAME, ingest_timestamp=now_epoch)
    else:
        print("No new songs to index")

    print("Done")

