import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------- Config (read from env or defaults) ----------
REPO = os.getenv("REPO", "Vaishnavi-Manne/LetsDoDsaTogether")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "1icNvrmtp0eeJn5RIt2f8u8fcD_eRsRFpvhLIxBk3WEs")

# Tab containing your curated email mapping (same spreadsheet)
EMAIL_TAB_NAME = os.getenv("EMAIL_TAB_NAME", "Emails")         # <-- change if different
# Output scoreboard tab
OUTPUT_TAB_NAME = os.getenv("OUTPUT_TAB_NAME", "Contributors") # <-- will be created if missing

# Label → score map
SCORE_MAP = {"level 1": 3, "level 2": 7, "level 3": 10}
FALLBACK_EMAIL = "example@gmail.com"

# ---------- Helpers ----------
def norm_link(url: str) -> str:
    return (url or "").strip().lower().rstrip("/")

def gh_headers():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"token {GITHUB_TOKEN}"
    return h

def fetch_all_merged_prs(repo: str):
    """Paginate all closed PRs and yield only merged ones."""
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo}/pulls?state=closed&per_page=100&page={page}"
        r = requests.get(url, headers=gh_headers(), timeout=30)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        for pr in batch:
            if pr.get("merged_at"):
                yield pr
        page += 1

def highest_label_score(labels):
    best = 0
    for lbl in labels or []:
        name = (lbl.get("name") or "").strip().lower()
        if name in SCORE_MAP:
            best = max(best, SCORE_MAP[name])
    return best

# ---------- Google Sheets auth ----------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# The workflow will write a service_account.json file before running this script
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# Open spreadsheet
ss = client.open_by_key(SPREADSHEET_ID)

# --- Load email mapping tab ---
try:
    email_ws = ss.worksheet(EMAIL_TAB_NAME)
except gspread.exceptions.WorksheetNotFound:
    raise SystemExit(f"❌ Email mapping tab '{EMAIL_TAB_NAME}' not found. Create it in the same spreadsheet.")

email_records = email_ws.get_all_records()  # list of dicts, header row required
# Expect at least "GITHUB LINK" and "EMAIL" columns in the mapping tab
email_map = {}
for row in email_records:
    link = norm_link(str(row.get("GITHUB LINK", "")))
    email = str(row.get("EMAIL", "")).strip()
    if link:
        email_map[link] = email

# --- Load or create scoreboard tab ---
try:
    out_ws = ss.worksheet(OUTPUT_TAB_NAME)
except gspread.exceptions.WorksheetNotFound:
    out_ws = ss.add_worksheet(title=OUTPUT_TAB_NAME, rows="100", cols="10")
    out_ws.update("A1:E1", [["S.NO", "NAME", "EMAIL", "GITHUB LINK", "SCORE"]])

# Ensure headers exist
existing_values = out_ws.get_all_values()
if not existing_values:
    out_ws.update("A1:E1", [["S.NO", "NAME", "EMAIL", "GITHUB LINK", "SCORE"]])
    existing_values = [["S.NO", "NAME", "EMAIL", "GITHUB LINK", "SCORE"]]

# Build current state maps from scoreboard
headers = [h.strip().upper() for h in existing_values[0]]
def col_idx(col_name): return headers.index(col_name) + 1  # 1-based
try:
    col_sno = col_idx("S.NO")
    col_name = col_idx("NAME")
    col_email = col_idx("EMAIL")
    col_link = col_idx("GITHUB LINK")
    col_score = col_idx("SCORE")
except ValueError as e:
    raise SystemExit("❌ Scoreboard tab must have headers: S.NO | NAME | EMAIL | GITHUB LINK | SCORE")

rows = existing_values[1:]  # excluding header
link_to_row = {}   # normalized link -> (row_index, current_score)
max_sno = 0

for i, row in enumerate(rows, start=2):  # actual sheet row index
    try:
        sno = int((row[col_sno-1] or "0"))
    except ValueError:
        sno = 0
    max_sno = max(max_sno, sno)

    link_val = norm_link(row[col_link-1] if len(row) >= col_link else "")
    score_val = 0
    try:
        score_val = int((row[col_score-1] or "0"))
    except ValueError:
        score_val = 0
    if link_val:
        link_to_row[link_val] = (i, score_val)

# --- Aggregate scores from merged PRs ---
# Use contributor HTML URL as the key (that’s your matching field)
agg = {}  # link -> {"login": ..., "link": ..., "score": int}
for pr in fetch_all_merged_prs(REPO):
    login = pr["user"]["login"]
    link = pr["user"]["html_url"]  # e.g., https://github.com/username
    link_n = norm_link(link)

    pr_score = highest_label_score(pr.get("labels", []))
    if pr_score <= 0:
        continue  # no level label → no points

    if link_n not in agg:
        agg[link_n] = {"login": login, "link": link, "score": 0}
    agg[link_n]["score"] += pr_score

# --- Prepare updates ---
updates_scores = []  # (row_index, new_score)
updates_emails = []  # (row_index, new_email)
new_rows = []        # rows to append

for link_n, info in agg.items():
    login = info["login"]
    link = info["link"]
    inc_score = info["score"]
    email = email_map.get(norm_link(link), FALLBACK_EMAIL)

    if link_n in link_to_row:
        # Update existing contributor's score (additive)
        row_idx, old_score = link_to_row[link_n]
        new_score = int(old_score) + int(inc_score)
        updates_scores.append((row_idx, new_score))

        # If email cell is blank or placeholder, update it
        current_email = out_ws.cell(row_idx, col_email).value or ""
        if (not current_email.strip()) or (current_email.strip().lower() == FALLBACK_EMAIL):
            updates_emails.append((row_idx, email or FALLBACK_EMAIL))
    else:
        # Append a new contributor
        max_sno += 1
        new_rows.append([max_sno, login, email or FALLBACK_EMAIL, link, inc_score])

# --- Apply updates ---
# Update scores
for row_idx, new_score in updates_scores:
    out_ws.update_cell(row_idx, col_score, new_score)

# Update emails where needed
for row_idx, new_email in updates_emails:
    out_ws.update_cell(row_idx, col_email, new_email)

# Append new rows
if new_rows:
    out_ws.append_rows(new_rows, value_input_option="USER_ENTERED")

print(f"✅ Done. Updated {len(updates_scores)} existing contributors, appended {len(new_rows)} new.")
