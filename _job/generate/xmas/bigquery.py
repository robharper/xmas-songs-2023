from datetime import date, datetime
from google.cloud.bigquery import Client

QUERY_TOP = """
SELECT
    song_id,
    APPROX_TOP_COUNT(artist, 1) as artist,
    count(distinct artist) as artist_count,
    min(song_title) as title,
    count(*) as plays,
    RANK() OVER(ORDER BY COUNT(*) DESC) rank
FROM `xmas-scrape.xmas.allSongPlays`
    {where}
group by song_id
order by plays desc
LIMIT {limit}
"""

QUERY_BY_ID = """
SELECT *
FROM (
    SELECT
        song_id,
        min(song_title) as song_title,
        count(*) as plays,
        RANK() OVER(ORDER BY COUNT(*) DESC) rank
    from `xmas-scrape.xmas.allSongPlays`
        {where}
    group by song_id
    order by plays desc
)
WHERE song_id in ({id_list})
"""

QUERY_TOP_VERSIONS = """
SELECT
    min(song_id) as song_id,
    song_title,
    artist,
    count(*) as plays,
    RANK() OVER(ORDER BY COUNT(*) DESC) rank
FROM `xmas-scrape.xmas.allSongPlays`
    {where}
group by song_title, artist
order by plays desc
LIMIT {limit}
"""


DAYS_QUERY = """
SELECT
    min(timestamp) as min,
    max(timestamp) as max
FROM `xmas-scrape.xmas.allSongPlays`
"""

def get_total_days(client: Client) -> float:
    res = client.query(DAYS_QUERY)
    date_range = next(res.result())
    return (date_range.max - date_range.min) / (60 * 60 * 24)

def ranked_songs(client: Client, where_ranks: str, where_comp: str, limit):
    query = QUERY_TOP.format(where=where_ranks, limit=limit)
    res = client.query(query)
    data = list(map(lambda row: {
        "song_id": row.song_id,
        "artist": row.artist[0]["value"],
        "artist_count": row.artist_count,
        "title": row.title,
        "plays": row.plays,
        "rank": row.rank
    }, res))

    # Add comparable data for the top songs
    # Get the song IDs for the top songs
    id_list = ",".join(map(lambda d: f'"{d["song_id"]}"', data))

    comp_query = QUERY_BY_ID.format(where=where_comp, id_list=id_list)
    res = client.query(comp_query)
    for row in res:
        record = next((r for r in data if r["song_id"] == row.song_id), None)
        if record:
            record["compPlays"] = row.plays
            record["compRank"] = row.rank
        else:
            print(f"Could not find record for {row.song_id} in ranked data")

    # Find total number of days in the data
    days = get_total_days(client)

    # Add the average plays per day for the top 12 songs
    for record in data:
        # All time data, create average
        if where_ranks == "":
            record["avgPlays"] = record["plays"] / days
        elif where_comp == "":
            record["avgCompPlays"] = record["compPlays"] / days

    return data

def ranked_versions(client: Client, where_ranks: str, limit):
    query = QUERY_TOP_VERSIONS.format(where=where_ranks, limit=limit)
    res = client.query(query)
    data = list(map(lambda row: {
        "song_id": row.song_id,
        "artist": row.artist,
        "title": row.song_title,
        "plays": row.plays,
        "rank": row.rank
    }, res))
    return data

def query_all(client: Client, query_date: date) -> dict:
    min_date = datetime.combine(query_date, datetime.min.time()).timestamp()
    max_date = datetime.combine(query_date, datetime.max.time()).timestamp()

    today_data = ranked_songs(client,
        where_ranks=f"where timestamp >= {min_date} and timestamp < {max_date}",
        where_comp="",
        limit=50
    )

    all_data = ranked_songs(client,
        where_ranks="",
        where_comp=f"where timestamp >= {min_date} and timestamp < {max_date}",
        limit=50
    )

    today_version_data = ranked_versions(client,
        where_ranks=f"where timestamp >= {min_date} and timestamp < {max_date}",
        limit=50
    )

    return {
        "today": today_data,
        "all": all_data,
        "today_version": today_version_data,
    }
