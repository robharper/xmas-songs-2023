

def insert(client, table_name, records, dry_run=False):
    # Write
    if len(records) > 0:
        # Add songs to DB
        if dry_run:
            print(f"Would have added {len(records)} songs. Example:")
            print(records[0])
        else:
            try:
                table = client.get_table(table_name)
                errors = client.insert_rows(table, records)
                if errors:
                    print("Errors:", errors)
                else:
                    print(f"Inserted {len(records)} songs")
            except Exception as e:
                print(f"Error adding songs: {e}")
    else:
        print("No new songs to add")

def merge(client, from_table, to_table, ingest_timestamp):
    # Merge new songs into main table, specifically the songs from this ingest
    merge_sql = f"""
        MERGE `{to_table}` D
        USING (SELECT * FROM `{from_table}` WHERE ingest_timestamp={ingest_timestamp}) S
        ON D.play_id = S.play_id
        WHEN NOT MATCHED THEN
            INSERT(timestamp, ingest_timestamp, scrape_timestamp, artist, play_id, song_id, song_title, song_title_original, high_res_art_url, itunes_purchase_url, spotify)
            VALUES(timestamp, ingest_timestamp, scrape_timestamp, artist, play_id, song_id, song_title, song_title_original, high_res_art_url, itunes_purchase_url, spotify)
    """
    try:
        res = client.query(merge_sql)
        res.result()
    except Exception as e:
        print(f"Error merging: {e}")
