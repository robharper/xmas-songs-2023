import hashlib
import re

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
    id = re.sub(r"\W", "", id)
    return id

def to_record(song, ingest_timestamp, scrape_date):
    play_id = hashlib.md5((str(song["updated_at"]) + "_" + str(song["started_at"])).encode()).hexdigest()
    song_title_clean = clean_title(song["song_title"])
    song_id = normalize_title(song_title_clean)

    return {
        "timestamp": int(song["updated_at"]),
        "scrape_timestamp": scrape_date,
        "ingest_timestamp": ingest_timestamp,
        "artist": song["artist"],
        "play_id": play_id,
        "song_id": song_id,
        "song_title": song_title_clean,
        "song_title_original": song["song_title"],
        "high_res_art_url": song["high_res_art_url"],
        "itunes_purchase_url": song["itunes_purchase_url"],
        "spotify": song["spotify"],
    }
