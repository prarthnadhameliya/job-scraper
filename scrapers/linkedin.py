# ============================================================
#  LINKEDIN SCRAPER
#  Two methods:
#  1. playwright_stealth — free but fragile
#  2. apify — reliable but requires paid token
# ============================================================

import requests
from rich.console import Console

console = Console()

def scrape_linkedin(source, roles):
    method = source.get("method", "playwright_stealth")

    if method == "apify":
        return scrape_via_apify(source, roles)
    else:
        return scrape_via_playwright(source, roles)


# ── Method 1: Apify (reliable, paid) ─────────────────────────

def scrape_via_apify(source, roles):
    token = source.get("apify_token", "")
    if not token:
        console.print("  [red]✗ No Apify token provided in config.yaml[/red]")
        return []

    console.print("  [dim]→ Using Apify LinkedIn scraper...[/dim]")

    # Start Apify actor run
    actor_url = "https://api.apify.com/v2/acts/curious_coder~linkedin-jobs-scraper/runs"
    payload = {
        "queries": [r.replace(" ", "%20") for r in roles],
        "locationQuery": "United States",
        "maxResults": 50,
    }

    response = requests.post(
        actor_url,
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )

    if response.status_code not in (200, 201):
        console.print(f"  [red]✗ Apify returned {response.status_code}[/red]")
        return []

    run_id = response.json().get("data", {}).get("id")
    console.print(f"  [dim]→ Apify run started: {run_id}[/dim]")
    console.print("  [dim]→ Waiting for results (this may take 1-2 min)...[/dim]")

    # Poll for results
    import time
    for _ in range(24):  # wait up to 2 minutes
        time.sleep(5)
        result_url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items"
        r = requests.get(result_url, headers={"Authorization": f"Bearer {token}"})
        items = r.json()
        if items:
            break

    console.print(f"  [dim]→ Total jobs from Apify: {len(items)}[/dim]")

    matched = []
    for job in items:
        title = job.get("title", "")
        if not matches_role(title, roles):
            continue
        matched.append({
            "role":         title,
            "company":      job.get("companyName", ""),
            "website":      job.get("companyUrl", source["url"]),
            "job_url":      job.get("jobUrl", ""),
            "location":     job.get("location", ""),
            "linkedin_url": job.get("companyUrl", ""),
            "source_type":  "linkedin",
            "date_found":   job.get("postedAt", ""),
        })

    return matched


# ── Method 2: Playwright Stealth (free but fragile) ───────────

def scrape_via_playwright(source, roles):
    console.print("  [dim]→ Using Playwright stealth (may be blocked by LinkedIn)...[/dim]")

    try:
        from playwright.sync_api import sync_playwright
        import time
    except ImportError:
        console.print("  [red]✗ Playwright not installed[/red]")
        return []

    url = source["url"]
    matched = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        try:
            console.print(f"  [dim]→ Navigating to: {url}[/dim]")
            page.goto(url, timeout=30000)
            time.sleep(3)  # wait for JS to load

            # Check if we hit a login wall
            if "authwall" in page.url or "login" in page.url:
                console.print("  [yellow]⚠️  LinkedIn redirected to login wall — try Apify method instead[/yellow]")
                browser.close()
                return []

            # Find job cards
            cards = page.query_selector_all("div.job-search-card")
            console.print(f"  [dim]→ Found {len(cards)} job cards[/dim]")

            for card in cards:
                title_el = card.query_selector("h3.base-search-card__title")
                company_el = card.query_selector("h4.base-search-card__subtitle")
                location_el = card.query_selector("span.job-search-card__location")
                link_el = card.query_selector("a.base-card__full-link")

                title = title_el.inner_text().strip() if title_el else ""
                company = company_el.inner_text().strip() if company_el else ""
                location = location_el.inner_text().strip() if location_el else ""
                link = link_el.get_attribute("href") if link_el else ""

                if not matches_role(title, roles):
                    continue

                matched.append({
                    "role":         title,
                    "company":      company,
                    "website":      source["url"],
                    "job_url":      link,
                    "location":     location,
                    "linkedin_url": f"https://www.linkedin.com/company/{company.lower().replace(' ', '-')}",
                    "source_type":  "linkedin",
                    "date_found":   "",
                })

        except Exception as e:
            console.print(f"  [red]✗ Playwright error: {e}[/red]")
        finally:
            browser.close()

    return matched


# ── Helpers ───────────────────────────────────────────────────

def matches_role(title, roles):
    title_lower = title.lower()
    return any(role in title_lower for role in roles)