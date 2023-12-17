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
FROM `{table}`
    {where}
group by song_id
order by plays {order}
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
    from `{table}`
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
FROM `{table}`
    {where}
group by song_title, artist
order by plays {order}
LIMIT {limit}
"""

QUERY_DEEP_CUT_VERSIONS = """
SELECT TODAY.song_id, TODAY.song_title, TODAY.artist, TODAY.plays, ALL_TIME.all_plays FROM (
    SELECT
        song_id,
        min(song_title) as song_title,
        artist,
        count(*) as plays,
        RANK() OVER(ORDER BY COUNT(*) DESC) rank
    FROM `{table}`
        {where}
    group by song_id, artist
    order by plays ASC
) as TODAY
LEFT JOIN (
  SELECT
        song_id,
        artist,
        count(*) as all_plays
  FROM `{table}`
  group by song_id, artist
  order by all_plays ASC
) as ALL_TIME
on TODAY.song_id = ALL_TIME.song_id and TODAY.artist = ALL_TIME.artist
WHERE TODAY.plays=1
order by ALL_TIME.all_plays ASC
LIMIT {limit}
"""

QUERY_TOP_ARTISTS = """
SELECT
    artist,
    count(distinct song_id) as song_count,
    count(*) as plays,
    RANK() OVER(ORDER BY COUNT(*) DESC) rank
FROM `{table}`
    {where}
group by artist
order by plays {order}
LIMIT {limit}
"""


SUMMARY_QUERY = """
SELECT
    count(*) as total_plays,
    count(distinct song_id) as song_count,
    count(distinct artist) as artist_count
FROM `{table}`
    {where}
"""

VERSION_COUNT_QUERY = """
SELECT
    count(*) as version_count,
FROM (
    SELECT DISTINCT song_title, artist
    FROM `{table}`
    {where}
)
"""

DAYS_QUERY = """
SELECT
    min(timestamp) as min,
    max(timestamp) as max
FROM `{table}`
    {where}
"""

def get_total_days(client: Client, where: str, table: str) -> float:
    res = client.query(DAYS_QUERY.format(where=where, table=table))
    date_range = next(res.result())
    return (date_range.max - date_range.min) / (60 * 60 * 24)

def ranked_songs(client: Client, where_ranks: str, where_global: str, limit: int, table: str, top: bool=True):
    query = QUERY_TOP.format(where=where_ranks, limit=limit, table=table, order="DESC" if top else "ASC")
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
    if where_global is not None:
        # Get the song IDs for the top songs
        id_list = ",".join(map(lambda d: f'"{d["song_id"]}"', data))

        comp_query = QUERY_BY_ID.format(where=where_global, id_list=id_list, table=table)
        res = client.query(comp_query)
        for row in res:
            record = next((r for r in data if r["song_id"] == row.song_id), None)
            if record:
                record["compPlays"] = row.plays
                record["compRank"] = row.rank
            else:
                print(f"Could not find record for {row.song_id} in ranked data")

        # Find total number of days in the data
        days = get_total_days(client, where_global, table=table)

        # Add the average plays per day for the top 12 songs
        for record in data:
            # All time data, create average
            record["avgCompPlays"] = round(record["compPlays"] / days)

    return data

def ranked_versions(client: Client, where: str, limit: int, table: str, top: bool=True):
    query = QUERY_TOP_VERSIONS.format(where=where, limit=limit, table=table, order="DESC" if top else "ASC")
    res = client.query(query)
    data = list(map(lambda row: {
        "song_id": row.song_id,
        "artist": row.artist,
        "title": row.song_title,
        "plays": row.plays,
        "rank": row.rank
    }, res))
    return data

def ranked_artists(client: Client, where: str, limit: int, table: str, top: bool=True):
    query = QUERY_TOP_ARTISTS.format(where=where, limit=limit, table=table, order="DESC" if top else "ASC")
    res = client.query(query)
    data = list(map(lambda row: {
        "artist": row.artist,
        "song_count": row.song_count,
        "plays": row.plays,
        "rank": row.rank
    }, res))
    return data

def deep_cuts(client: Client, where: str, limit: int, table: str):
    # Get songs with a single play
    query = QUERY_DEEP_CUT_VERSIONS.format(where=where, limit=limit, table=table)
    res = client.query(query)
    data = list(map(lambda row: {
        "song_id": row.song_id,
        "artist": row.artist,
        "title": row.song_title,
        "plays": row.plays,
        "all_plays": row.all_plays
    }, res))

    return data


def summary(client: Client, where: str, where_global: str, table: str):
    summary_data = {}

    if where:
        query = SUMMARY_QUERY.format(where=where, table=table)
        res = client.query(query)
        data = next(res.result())
        summary_data["today"] = {
            "total_plays": data.total_plays,
            "song_count": data.song_count,
            "artist_count": data.artist_count,
        }

        query = VERSION_COUNT_QUERY.format(where=where, table=table)
        res = client.query(query)
        data = next(res.result())
        summary_data['today']['version_count'] = data.version_count

    # All time
    query = SUMMARY_QUERY.format(where=where_global, table=table)
    res = client.query(query)
    data = next(res.result())
    summary_data["all"] = {
        "total_plays": data.total_plays,
        "song_count": data.song_count,
        "artist_count": data.artist_count,
    }

    query = VERSION_COUNT_QUERY.format(where=where_global, table=table)
    res = client.query(query)
    data = next(res.result())
    summary_data['all']['version_count'] = data.version_count

    days = get_total_days(client, where_global, table=table)
    summary_data['all']['average_plays'] = round(summary_data['all']['total_plays'] / days)
    summary_data['all']['days'] = round(days)

    return summary_data

def query_day(client: Client, query_date: date, table: str) -> dict:
    min_date = datetime.combine(query_date, datetime.min.time()).timestamp()
    max_date = datetime.combine(query_date, datetime.max.time()).timestamp()
    date_filter = f"where timestamp >= {min_date} and timestamp < {max_date}"
    before_end_of_today = f"where timestamp < {max_date}"

    today_data = ranked_songs(client,
        where_ranks=date_filter,
        where_global=before_end_of_today,
        limit=50,
        table=table
    )

    today_version_data = ranked_versions(client,
        where=date_filter,
        limit=50,
        table=table
    )

    artist_data = ranked_artists(client,
        where=date_filter,
        limit=50,
        table=table
    )

    summary_data = summary(client,
        where=date_filter,
        where_global=before_end_of_today,
        table=table
    )

    rare = deep_cuts(client,
        where=date_filter,
        limit=10,
        table=table
    )

    return {
        "today": today_data,
        "today_version": today_version_data,
        "artist": artist_data,
        "summary": summary_data,
        "deep_cuts": rare
    }

def query_all(client: Client, table: str) -> dict:
    summary_data = summary(client,
        where=None,
        where_global="",
        table=table
    )

    today_data = ranked_songs(client,
        where_ranks="",
        where_global=None,
        limit=50,
        table=table
    )

    today_version_data = ranked_versions(client,
        where="",
        limit=50,
        table=table
    )

    artist_data = ranked_artists(client,
        where="",
        limit=50,
        table=table
    )

    return {
        "today": today_data,
        "today_version": today_version_data,
        "artist": artist_data,
        "summary": summary_data,
    }