# ============================================================
#  CUSTOM SCRAPER
#  For power users — add CSS selectors in config.yaml
#  No coding needed, just inspect the page in your browser
# ============================================================

import time
from rich.console import Console

console = Console()

def scrape_custom(source, roles):
    """
    Uses CSS selectors defined in config.yaml to scrape any site.

    Required config fields:
        job_container  : CSS selector for each job card/row
        role_selector  : CSS selector for the job title (inside container)
        link_selector  : CSS selector for the apply link (inside container)

    Optional config fields:
        location_selector : CSS selector for location (inside container)
    """

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        console.print("  [red]✗ Playwright not installed[/red]")
        return []

    url = source["url"]

    # ── Validate required selectors ──────────────────────────
    required = ["job_container", "role_selector", "link_selector"]
    for field in required:
        if not source.get(field):
            console.print(f"  [red]✗ Missing '{field}' in config.yaml for {source['name']}[/red]")
            return []

    job_container  = source["job_container"]
    role_selector  = source["role_selector"]
    link_selector  = source["link_selector"]
    loc_selector   = source.get("location_selector", "")

    console.print(f"  [dim]→ Launching browser for: {url}[/dim]")
    console.print(f"  [dim]→ Looking for containers: {job_container}[/dim]")

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

            # Find all job containers
            containers = page.query_selector_all(job_container)
            console.print(f"  [dim]→ Found {len(containers)} job containers[/dim]")

            for container in containers:
                try:
                    # Extract title
                    title_el = container.query_selector(role_selector)
                    title = title_el.inner_text().strip() if title_el else ""

                    if not title:
                        continue

                    if not matches_role(title, roles):
                        continue

                    # Extract link
                    link_el = container.query_selector(link_selector)
                    link = ""
                    if link_el:
                        link = link_el.get_attribute("href") or ""
                        if link.startswith("/"):
                            from urllib.parse import urlparse
                            parsed = urlparse(url)
                            link = f"{parsed.scheme}://{parsed.netloc}{link}"

                    # Extract location (optional)
                    location = ""
                    if loc_selector:
                        loc_el = container.query_selector(loc_selector)
                        location = loc_el.inner_text().strip() if loc_el else ""

                    matched.append({
                        "role":         title,
                        "company":      source["name"],
                        "website":      url,
                        "job_url":      link or url,
                        "location":     location,
                        "linkedin_url": "",
                        "source_type":  "custom",
                        "date_found":   "",
                    })

                except Exception:
                    continue

        except Exception as e:
            console.print(f"  [red]✗ Browser error: {e}[/red]")
        finally:
            browser.close()

    return matched


# ── Helpers ───────────────────────────────────────────────────

def matches_role(title, roles):
    title_lower = title.lower()
    return any(role in title_lower for role in roles)