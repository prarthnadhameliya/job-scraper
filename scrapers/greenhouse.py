# ============================================================
#  GREENHOUSE SCRAPER
#  Uses Greenhouse's public JSON API — no auth needed
#  API format: https://boards-api.greenhouse.io/v1/boards/{company}/jobs
# ============================================================

import requests
from rich.console import Console

console = Console()

def scrape_greenhouse(source, roles):
    """
    Scrapes jobs from a Greenhouse board.
    Returns a list of job dicts matching the roles filter.
    """

    company_slug = extract_slug(source["url"])
    api_url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true"

    console.print(f"  [dim]→ Hitting API: {api_url}[/dim]")

    response = requests.get(api_url, timeout=10)

    if response.status_code != 200:
        console.print(f"  [red]✗ API returned {response.status_code} for {source['name']}[/red]")
        return []

    data = response.json()
    raw_jobs = data.get("jobs", [])

    console.print(f"  [dim]→ Total jobs on board: {len(raw_jobs)}[/dim]")

    matched = []
    for job in raw_jobs:
        title = job.get("title", "")

        # ── Filter by roles ──────────────────────────────────
        if not matches_role(title, roles):
            continue

        matched.append({
            "role":         title,
            "company":      source["name"],
            "website":      source["url"],
            "job_url":      job.get("absolute_url", ""),
            "location":     extract_location(job),
            "linkedin_url": "",   # enricher fills this later
            "source_type":  "greenhouse",
            "date_found":   "",
        })

    return matched


# ── Helpers ───────────────────────────────────────────────────

def extract_slug(url):
    """
    Pulls the company slug from a Greenhouse URL.
    e.g. https://boards.greenhouse.io/stripe  →  stripe
    """
    return url.rstrip("/").split("/")[-1]


def extract_location(job):
    """
    Greenhouse returns location as a dict: {"name": "San Francisco, CA"}
    """
    loc = job.get("location", {})
    if isinstance(loc, dict):
        return loc.get("name", "")
    return str(loc)


def matches_role(title, roles):
    """
    Returns True if the job title contains any of the role keywords.
    Case-insensitive match.
    """
    title_lower = title.lower()
    return any(role in title_lower for role in roles)