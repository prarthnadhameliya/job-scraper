# ============================================================
#  GENERIC SCRAPER
#  Uses Playwright headless browser for any career page
#  For developers who want to add custom sites
# ============================================================

import time
from rich.console import Console

console = Console()

def scrape_generic(source, roles):
    """
    Generic Playwright scraper for any career page.
    Tries common job listing patterns automatically.
    """

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        console.print("  [red]✗ Playwright not installed[/red]")
        return []

    url = source["url"]
    console.print(f"  [dim]→ Launching headless browser for: {url}[/dim]")

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

            # ── Try common job title selectors ────────────────
            job_titles = try_selectors(page, [
                "h2.job-title",
                "h3.job-title",
                "a.job-title",
                "span.job-title",
                "div.job-title",
                "h2.position-title",
                "h3.position-title",
                "td.title",
                "li.job a",
                "div.opening a",
                "h4.job-name",
            ])

            console.print(f"  [dim]→ Found {len(job_titles)} potential job elements[/dim]")

            for el in job_titles:
                try:
                    title = el.inner_text().strip()
                    link = el.get_attribute("href") or url

                    if not title or len(title) < 3:
                        continue

                    if not matches_role(title, roles):
                        continue

                    # Make relative URLs absolute
                    if link.startswith("/"):
                        from urllib.parse import urlparse
                        parsed = urlparse(url)
                        link = f"{parsed.scheme}://{parsed.netloc}{link}"

                    matched.append({
                        "role":         title,
                        "company":      source["name"],
                        "website":      url,
                        "job_url":      link,
                        "location":     "",
                        "linkedin_url": "",
                        "source_type":  "generic",
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

def try_selectors(page, selectors):
    """
    Tries a list of CSS selectors and returns
    the first one that finds elements.
    """
    for selector in selectors:
        try:
            elements = page.query_selector_all(selector)
            if elements:
                return elements
        except Exception:
            continue
    return []


def matches_role(title, roles):
    title_lower = title.lower()
    return any(role in title_lower for role in roles)