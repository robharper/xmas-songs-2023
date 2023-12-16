import os
import base64
import json
from datetime import date, timedelta
import functions_framework

from xmas.xmas import generate

PROJECT_ID = os.getenv("PROJECT_ID")
TABLE_NAME = f"{PROJECT_ID}.{os.getenv('DATASET_ID')}.{os.getenv('TABLE_ID')}"

GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Register a CloudEvent function with the Functions Framework
@functions_framework.cloud_event
def generate_fn(cloud_event):
    dry_run = os.getenv("DRY_RUN", False)

    post_date = None
    if type(cloud_event.data) == dict:
        input_b64 = cloud_event.data.get("message", {}).get("data")
        if input_b64:
            json_input = base64.b64decode(input_b64).decode()
            try:
                post_date_str = json.loads(json_input).get("date")
                post_date = date.fromisoformat(post_date_str)
            except:
                print(f"Invalid JSON input received: {json_input}")

    # Use yesterday's date if no date was provided
    if not post_date:
        post_date = date.today() - timedelta(days=1)

    print(f"Generating summary for {post_date}")

    generate(
        post_date,
        project_id=PROJECT_ID,
        table_name=TABLE_NAME,
        gh_repo=GITHUB_REPO,
        gh_token=GITHUB_TOKEN,
        dry_run=dry_run
    )