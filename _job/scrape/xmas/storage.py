import json
from google.cloud import storage

def store_json(project, bucket, scrape_date, data):
    filename = f"raw/{scrape_date.isoformat()}.json"
    data_str = json.dumps(data)

    storage_client = storage.Client(project=project)
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(filename)

    print(f"Backing up to: {filename}")
    try:
        blob.upload_from_string(data_str, content_type="application/json")
        return blob.id
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None


def fetch_json(project, bucket, filename):
    storage_client = storage.Client(project=project)
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(filename)

    print(f"Fetching from: {filename}")
    try:
        data = blob.download_as_string()
        return json.loads(data)
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None