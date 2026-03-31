# ============================================================
#  YCOMBINATOR SCRAPER
#  Scrapes workatastartup.com using Playwright
# ============================================================

import time
from rich.console import Console

console = Console()

def scrape_ycombinator(source, roles):
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
            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)

            # Get all job name divs
            job_cards = page.query_selector_all("div.job-name")
            console.print(f"  [dim]→ Found {len(job_cards)} job cards[/dim]")

            for card in job_cards:
                try:
                    # ── Title from anchor tag ─────────────────
                    title_el = card.query_selector("a")
                    if not title_el:
                        continue

                    title = title_el.inner_text().strip()
                    if not title or not matches_role(title, roles):
                        continue

                    # ── Job URL ───────────────────────────────
                    href = title_el.get_attribute("href") or ""
                    link = f"https://www.workatastartup.com{href}" \
                        if href.startswith("/") else href

                    # ── Location + job type from job-details ──
                    location = ""
                    job_type = ""
                    try:
                        details = card.evaluate("""
                            el => {
                                let p = el.nextElementSibling;
                                if (!p) return {location: '', job_type: ''};
                                let spans = p.querySelectorAll('span');
                                return {
                                    job_type: spans[0] ? spans[0].innerText.trim() : '',
                                    location: spans[1] ? spans[1].innerText.trim() : ''
                                };
                            }
                        """)
                        location = details.get("location", "")
                        job_type = details.get("job_type", "")
                    except Exception:
                        pass

                    # ── Company name ──────────────────────────
                    company = ""
                    try:
                        company = card.evaluate("""
                            el => {
                                let row = el.closest('.company-jobs-container, [class*=company]');
                                if (!row) return '';
                                let name = row.querySelector('.company-name, h2, h3, [class*=company-name]');
                                return name ? name.innerText.trim() : '';
                            }
                        """)
                    except Exception:
                        pass

                    matched.append({
                        "role":         title,
                        "company":      company or "YC Startup",
                        "website":      "https://www.workatastartup.com",
                        "job_url":      link,
                        "location":     location,
                        "job_type":     job_type,
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