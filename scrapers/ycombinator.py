# ============================================================
#  YCOMBINATOR SCRAPER
#  Scrapes workatastartup.com using Playwright
#  No public API — uses headless browser
# ============================================================

import time
from rich.console import Console

console = Console()

def scrape_ycombinator(source, roles):
    """
    Scrapes jobs from workatastartup.com
    Returns a list of job dicts matching the roles filter.
    """

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        console.print("  [red]✗ Playwright not installed[/red]")
        return []

    url = source.get("url", "https://www.workatastartup.com/jobs")
    console.print(f"  [dim]→ Launching browser for: {url}[/dim]")

    matched = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        try:
            page.goto(url, timeout=30000)
            time.sleep(3)

            # Scroll to load more jobs
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)

            # Find job listings
            job_cards = page.query_selector_all("div.job-name")
            console.print(f"  [dim]→ Found {len(job_cards)} job cards[/dim]")

            for card in job_cards:
                try:
                    # Get job title
                    title_el = card.query_selector("a")
                    title = title_el.inner_text().strip() if title_el else ""

                    if not title or not matches_role(title, roles):
                        continue

                    # Get link
                    link = title_el.get_attribute("href") if title_el else ""
                    if link and not link.startswith("http"):
                        link = f"https://www.workatastartup.com{link}"

                    # Get company
                    parent = card.evaluate_handle(
                        "el => el.closest('.job')"
                    )
                    company = ""
                    location = ""

                    if parent:
                        company_el = parent.query_selector(
                            "div.company-name, a.company-name"
                        )
                        company = company_el.inner_text().strip() \
                            if company_el else "YC Startup"

                        loc_el = parent.query_selector(
                            "span.job-location, div.location"
                        )
                        location = loc_el.inner_text().strip() \
                            if loc_el else ""

                    matched.append({
                        "role":         title,
                        "company":      company or "YC Startup",
                        "website":      url,
                        "job_url":      link,
                        "location":     location,
                        "linkedin_url": "",
                        "source_type":  "ycombinator",
                        "date_found":   "",
                    })

                except Exception:
                    continue

        except Exception as e:
            console.print(f"  [red]✗ Browser error: {e}[/red]")
        finally:
            browser.close()

    return matched


def matches_role(title, roles):
    title_lower = title.lower()
    return any(role in title_lower for role in roles)