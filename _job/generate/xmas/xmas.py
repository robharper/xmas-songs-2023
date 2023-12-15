import json
from datetime import date
from google.cloud.bigquery import Client
from xmas.bigquery import query_all

def generate(build_date: date, project_id: str, table_name: str, dry_run: bool):
    client = Client(project=project_id)

    songs = query_all(client, build_date)
    print(json.dumps(songs, indent=2))