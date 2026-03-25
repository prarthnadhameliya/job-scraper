# ============================================================
#  LEVER SCRAPER
#  Uses Lever's public JSON API — no auth needed
#  API format: https://api.lever.co/v0/postings/{slug}
# ============================================================

import requests
from rich.console import Console

console = Console()

def scrape_lever(source, roles):
    """
    Scrapes jobs from a Lever board.
    Returns a list of job dicts matching the roles filter.
    """

    company_slug = extract_slug(source["url"])
    api_url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"

    console.print(f"  [dim]→ Hitting API: {api_url}[/dim]")

    response = requests.get(api_url, timeout=20)

    if response.status_code != 200:
        console.print(f"  [red]✗ API returned {response.status_code} for {source['name']}[/red]")
        return []

    raw_jobs = response.json()

    console.print(f"  [dim]→ Total jobs on board: {len(raw_jobs)}[/dim]")

    matched = []
    for job in raw_jobs:
        title = job.get("text", "")

        if not matches_role(title, roles):
            continue

        matched.append({
            "role":         title,
            "company":      source["name"],
            "website":      source["url"],
            "job_url":      job.get("hostedUrl", ""),
            "location":     extract_location(job),
            "linkedin_url": "",
            "source_type":  "lever",
            "date_found":   "",
        })

    return matched


# ── Helpers ───────────────────────────────────────────────────

def extract_slug(url):
    """
    https://jobs.lever.co/netflix  →  netflix
    """
    return url.rstrip("/").split("/")[-1]


def extract_location(job):
    """
    Lever returns categories dict with location inside.
    """
    categories = job.get("categories", {})
    return categories.get("location", "")


def matches_role(title, roles):
    title_lower = title.lower()
    return any(role in title_lower for role in roles)