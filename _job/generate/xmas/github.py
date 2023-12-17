import requests
import base64

def upload(gh_token, repo, path, content, dry_run=False):
    if dry_run:
        print("Dry run: Would upload:")
        print(content)
        print(f"to {repo}/{path}")
    else:
        headers = {"Authorization": f"Bearer {gh_token}"}

        # Get the file if it exists
        sha = None
        r = requests.get(f"https://api.github.com/repos/{repo}/contents/{path}", headers=headers)
        if r.status_code == 200:
            response = r.json()
            sha = response['sha']
            action = 'Updating'
        else:
            action = 'Adding'

        # Upload
        data = {
            "sha": sha,
            "message": f"Automated commit: {action} {path}",
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8")
        }
        r = requests.put(f"https://api.github.com/repos/{repo}/contents/{path}", headers=headers, json=data)
        r.raise_for_status()
