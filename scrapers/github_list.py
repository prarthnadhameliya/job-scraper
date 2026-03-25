# ============================================================
#  GITHUB LIST SCRAPER
#  Parses markdown job lists from GitHub repos
#  e.g. github.com/poteto/hiring-without-whiteboards
# ============================================================

import re
import requests
from rich.console import Console

console = Console()

def scrape_github_list(source, roles):
    """
    Fetches a raw markdown file from GitHub and extracts
    company names + links from markdown list format.
    """

    url = source["url"]
    console.print(f"  [dim]→ Fetching markdown: {url}[/dim]")

    response = requests.get(url, timeout=20)

    if response.status_code != 200:
        console.print(f"  [red]✗ Request returned {response.status_code}[/red]")
        return []

    content = response.text
    lines = content.split("\n")

    console.print(f"  [dim]→ Total lines in file: {len(lines)}[/dim]")

    matched = []
    for line in lines:
        links = extract_markdown_links(line)

        for company, link in links:
            if not is_company_link(link):
                continue

            matched.append({
                "role":         "See company careers page",
                "company":      company,
                "website":      link,
                "job_url":      link,
                "location":     extract_location_from_line(line),
                "linkedin_url": "",
                "source_type":  "github_list",
                "date_found":   "",
            })

    # Deduplicate by company name
    seen = set()
    unique = []
    for job in matched:
        if job["company"] not in seen:
            seen.add(job["company"])
            unique.append(job)

    return unique


# ── Helpers ───────────────────────────────────────────────────

def extract_markdown_links(line):
    pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
    return re.findall(pattern, line)


def is_company_link(url):
    skip = [
        "github.com",
        "shields.io",
        "travis-ci",
        "codecov",
        "opensource.org",
        "creativecommons.org",
    ]
    return not any(s in url for s in skip)


def extract_location_from_line(line):
    after_link = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', '', line)
    after_link = after_link.strip(" -|•*\t")
    if after_link and len(after_link) < 50:
        return after_link
    return ""