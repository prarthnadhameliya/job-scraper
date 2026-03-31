# ============================================================
#  JOBICY SCRAPER (replaces Indeed)
#  Uses Jobicy's free public RSS/JSON API
#  No auth needed, no blocking
# ============================================================

import requests
from rich.console import Console

console = Console()

def scrape_indeed(source, roles):
    """
    Scrapes remote tech jobs from Jobicy's free API.
    Kept function name as scrape_indeed so main.py needs no changes.
    """

    console.print(f"  [dim]→ Fetching Jobicy API...[/dim]")

    # Jobicy free API — returns latest remote jobs
    api_url = "https://jobicy.com/api/v2/remote-jobs?count=50&industry=engineering"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=20)

        if response.status_code != 200:
            console.print(f"  [red]✗ API returned {response.status_code}[/red]")
            # Fallback to RemoteOK
            return scrape_remoteok(roles)

        data = response.json()
        raw_jobs = data.get("jobs", [])
        console.print(f"  [dim]→ Total jobs in feed: {len(raw_jobs)}[/dim]")

        matched = []
        for job in raw_jobs:
            title = job.get("jobTitle", "")

            if not matches_role(title, roles):
                continue

            matched.append({
                "role":         title,
                "company":      job.get("companyName", ""),
                "website":      job.get("companyUrl", ""),
                "job_url":      job.get("url", ""),
                "location":     job.get("jobGeo", "Remote"),
                "linkedin_url": "",
                "source_type":  "jobicy",
                "date_found":   job.get("pubDate", ""),
            })

        # If Jobicy returns results use them, else fallback
        if matched:
            return matched
        else:
            console.print(f"  [dim]→ No matches from Jobicy, trying RemoteOK...[/dim]")
            return scrape_remoteok(roles)

    except Exception as e:
        console.print(f"  [yellow]⚠️  Jobicy failed: {e} — trying RemoteOK[/yellow]")
        return scrape_remoteok(roles)


def scrape_remoteok(roles):
    """Fallback to RemoteOK if Jobicy fails."""
    url = "https://remoteok.com/api"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            return []

        data = response.json()
        raw_jobs = [j for j in data if isinstance(j, dict) and "position" in j]
        console.print(f"  [dim]→ RemoteOK fallback: {len(raw_jobs)} jobs[/dim]")

        matched = []
        for job in raw_jobs:
            title = job.get("position", "")
            if not matches_role(title, roles):
                continue
            matched.append({
                "role":         title,
                "company":      job.get("company", ""),
                "website":      job.get("url", ""),
                "job_url":      job.get("url", ""),
                "location":     "Remote",
                "linkedin_url": "",
                "source_type":  "remoteok",
                "date_found":   job.get("date", ""),
            })
        return matched

    except Exception:
        return []


def matches_role(title, roles):
    title_lower = title.lower()
    return any(role in title_lower for role in roles)