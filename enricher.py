# ============================================================
#  ENRICHER
#  Auto-finds LinkedIn company URLs for each job
#  Uses Google search — no API key needed
# ============================================================

import requests
import time
import re
from rich.console import Console

console = Console()

def enrich_jobs(jobs):
    """
    Takes a list of jobs and fills in the linkedin_url
    for each unique company by searching Google.
    """

    if not jobs:
        return jobs

    # Build a unique list of companies to look up
    companies = list({job["company"] for job in jobs if job["company"]})
    console.print(f"\n[bold cyan]🔍 Enriching LinkedIn URLs for {len(companies)} companies...[/bold cyan]")

    # Cache so we don't search the same company twice
    linkedin_cache = {}

    for i, company in enumerate(companies):
        # Skip if already found
        if company in linkedin_cache:
            continue

        console.print(f"  [dim]→ [{i+1}/{len(companies)}] Looking up: {company}[/dim]")

        url = find_linkedin_url(company)
        linkedin_cache[company] = url

        if url:
            console.print(f"  [green]✓ Found: {url}[/green]")
        else:
            console.print(f"  [yellow]✗ Not found: {company}[/yellow]")

        # Be polite — don't hammer Google
        time.sleep(1.5)

    # Fill in linkedin_url for every job
    enriched = []
    for job in jobs:
        company = job["company"]
        job["linkedin_url"] = linkedin_cache.get(company, "")
        enriched.append(job)

    found = sum(1 for j in enriched if j["linkedin_url"])
    console.print(f"\n[bold green]✅ Enriched {found}/{len(enriched)} jobs with LinkedIn URLs[/bold green]")

    return enriched


# ── Helpers ───────────────────────────────────────────────────

def find_linkedin_url(company):
    """
    Searches Google for the company's LinkedIn page.
    Returns the LinkedIn URL if found, empty string otherwise.
    """

    query = f"{company} site:linkedin.com/company"
    url = f"https://www.google.com/search?q={requests.utils.quote(query)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return ""

        # Find linkedin.com/company URLs in the response
        pattern = r'https://(?:www\.)?linkedin\.com/company/[a-zA-Z0-9\-\_]+'
        matches = re.findall(pattern, response.text)

        if matches:
            # Clean and return the first match
            return matches[0].split("?")[0]  # remove query params

    except Exception:
        pass

    return ""