# ============================================================
#  REMOTEOK SCRAPER (replaces Indeed RSS)
#  Uses RemoteOK's free public JSON API — no auth needed
#  API: https://remoteok.com/api
# ============================================================

import requests
from rich.console import Console

console = Console()

def scrape_indeed(source, roles):
    """
    Scrapes remote jobs from RemoteOK's public API.
    Kept the function name as scrape_indeed so main.py needs no changes.
    """

    url = "https://remoteok.com/api"
    console.print(f"  [dim]→ Fetching RemoteOK API: {url}[/dim]")

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code != 200:
        console.print(f"  [red]✗ API returned {response.status_code}[/red]")
        return []

    data = response.json()

    # First item is metadata, skip it
    raw_jobs = [j for j in data if isinstance(j, dict) and "position" in j]

    console.print(f"  [dim]→ Total jobs in feed: {len(raw_jobs)}[/dim]")

    matched = []
    for job in raw_jobs:
        title = job.get("position", "")

        if not matches_role(title, roles):
            continue

        matched.append({
            "role":         title,
            "company":      job.get("company", source["name"]),
            "website":      job.get("url", ""),
            "job_url":      job.get("url", ""),
            "location":     "Remote",
            "linkedin_url": "",
            "source_type":  "remoteok",
            "date_found":   job.get("date", ""),
        })

    return matched


# ── Helpers ───────────────────────────────────────────────────

def matches_role(title, roles):
    title_lower = title.lower()
    return any(role in title_lower for role in roles)