from yaml import safe_load
from google.cloud import bigquery
from google.api_core.exceptions import Conflict

env = {}
with open(".env.yaml", "r") as f:
    env = safe_load(f)

# Construct a BigQuery client object.
client = bigquery.Client(project=env["PROJECT_ID"])

dataset_id = f"{env['PROJECT_ID']}.{env['DATASET_ID']}"
dataset = bigquery.Dataset(dataset_id)
dataset.location = "US"

# Create the dataset
try :
    dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
    print("Created dataset {}.{}".format(client.project, dataset.dataset_id))
except Conflict as e:
    print(f"Dataset {dataset_id} already exists")


# Create the table

"""
Example record:
artist: "Serena Ryder" (string)
high_res_art_url: "https%3A%2F%2Fis1-ssl.mzstatic.com%2Fimage%2Fthumb%2FMusic%2F08%2F57%2F0b%2Fmzi.ngwxuwqn.jpg%2F600x600bb.jpg" (string)
itunes_purchase_url: "https%3A%2F%2Fmusic.apple.com%2Fca%2Falbum%2Fcalling-to-say%2F295624696%3Fi%3D295624783%26uo%3D4%26partnerId%3D11%26at%3D10l56V" (string)
play_id: "3aa691f96d97018fa08cba1cda7c1702" (string)
radio_station: "chfi" (string)
scrape_date: 1700336230.549467 (number)
song_id: "callingtosay" (string)
song_title: "Calling to Say" (string)
song_title_original: "Calling to Say" (string)
spotify: "70FI8C0JhbXUaKRn3IGlMf" (string)
started_at: "2:11 pm" (string)
updated_at: 1700334669 (number)

"""
schema = [
    bigquery.SchemaField("timestamp", "INT64", mode="REQUIRED"),
    bigquery.SchemaField("scrape_timestamp", "INT64", mode="REQUIRED"),
    bigquery.SchemaField("ingest_timestamp", "INT64", mode="REQUIRED"),

    bigquery.SchemaField("artist", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("play_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("song_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("song_title", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("song_title_original", "STRING", mode="REQUIRED"),

    bigquery.SchemaField("high_res_art_url", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("itunes_purchase_url", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("spotify", "STRING", mode="NULLABLE"),
]

for table_id in [
    f"{dataset_id}.{env['INGEST_TABLE_ID']}",
    f"{dataset_id}.{env['MAIN_TABLE_ID']}"
]:
    table = bigquery.Table(table_id, schema=schema)
    try:
        table = client.create_table(table)  # Make an API request.
        print(f"Created table {table_id}")
    except Conflict as e:
        print(f"Table {table_id} already exists")