from yaml import dump
from datetime import date
from google.cloud.bigquery import Client
from xmas.bigquery import query_day, query_all
from xmas.jekyll import build_page
from xmas.github import upload

def generate(build_date: date, project_id: str, table_name: str, gh_repo: str, gh_token: str, dry_run: bool):
    client = Client(project=project_id)

    songs = query_day(client, build_date, table_name)
    post = build_page(build_date, songs)
    upload(gh_token=gh_token, repo=gh_repo, path=f"_posts/{build_date}-viz.markdown", content=post, dry_run=dry_run)

    all_data = query_all(client, table_name)
    all_post = build_page(None, all_data)
    upload(gh_token=gh_token, repo=gh_repo, path=f"index.markdown", content=all_post, dry_run=dry_run)

    print(f"Successfully generated {build_date}")