import requests
import openpyxl
from collections import defaultdict
import os

# Config
TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("REPO")
API_URL = f"https://api.github.com/repos/{REPO}/pulls?state=closed&per_page=100"

headers = {"Authorization": f"token {TOKEN}"}

# Score mapping from labels
label_scores = {"level 1": 3, "level 2": 7, "level 3": 10}

contributors = defaultdict(lambda: {"name": "", "email": "example@gmail.com", "link": "", "score": 0})

def fetch_prs(page=1):
    url = f"{API_URL}&page={page}"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

page = 1
while True:
    prs = fetch_prs(page)
    if not prs:
        break
    for pr in prs:
        if not pr.get("merged_at"):
            continue  # only merged PRs
        user = pr["user"]["login"]
        user_url = pr["user"]["html_url"]
        contributors[user]["name"] = user
        contributors[user]["link"] = user_url

        # check labels
        for lbl in pr.get("labels", []):
            label = lbl["name"].lower()
            if label in label_scores:
                contributors[user]["score"] += label_scores[label]
    page += 1

# Write to Excel
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Contributors"

ws.append(["S.NO", "NAME", "EMAIL ID", "GITHUB LINK", "SCORE"])

for i, (user, data) in enumerate(contributors.items(), start=1):
    ws.append([i, data["name"], data["email"], data["link"], data["score"]])

wb.save("contributors.xlsx")
print("✅ contributors.xlsx generated")
