# ============================================================
#  ASHBY SCRAPER
#  Uses Ashby's public JSON API — no auth needed
#  API format: POST https://api.ashbyhq.com/posting-api/job-board/{slug}
# ============================================================

import requests
from rich.console import Console

console = Console()

def scrape_ashby(source, roles):
    """
    Scrapes jobs from an Ashby board.
    Returns a list of job dicts matching the roles filter.
    """

    company_slug = extract_slug(source["url"])
    api_url = f"https://api.ashbyhq.com/posting-api/job-board/{company_slug}?includeCompensation=true"


    console.print(f"  [dim]→ Hitting API: {api_url}[/dim]")

    # Ashby requires a POST request unlike Greenhouse/Lever
    response = requests.get(
        api_url + "?includeCompensation=true",
        timeout=20
    )

    if response.status_code != 200:
        console.print(f"  [red]✗ API returned {response.status_code} for {source['name']}[/red]")
        return []

    data = response.json()
    raw_jobs = data.get("jobs", [])

    console.print(f"  [dim]→ Total jobs on board: {len(raw_jobs)}[/dim]")

    matched = []
    for job in raw_jobs:
        title = job.get("title", "")

        if not matches_role(title, roles):
            continue

        matched.append({
            "role":         title,
            "company":      source["name"],
            "website":      source["url"],
            "job_url":      job.get("jobUrl", ""),
            "location":     extract_location(job),
            "linkedin_url": "",
            "source_type":  "ashby",
            "date_found":   "",
        })

    return matched


# ── Helpers ───────────────────────────────────────────────────

def extract_slug(url):
    """
    https://jobs.ashbyhq.com/linear  →  linear
    """
    return url.rstrip("/").split("/")[-1]


def extract_location(job):
    """
    Ashby returns a list of locations — we join them.
    e.g. ["San Francisco, CA", "Remote"]  →  "San Francisco, CA / Remote"
    """
    locations = job.get("locationNames", [])
    if isinstance(locations, list):
        return " / ".join(locations)
    return str(locations)


def matches_role(title, roles):
    title_lower = title.lower()
    return any(role in title_lower for role in roles)