# ============================================================
#  VERIFY COMMAND
#  Checks all sources in config.yaml are still alive
#  Run: python verify.py
# ============================================================

import yaml
import requests
from rich.console import Console
from rich.table import Table

console = Console()

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def check_source(source):
    """
    Checks if a source URL is alive.
    Returns (status, message) tuple.
    """
    name   = source.get("name", "Unknown")
    stype  = source.get("type")
    url    = source.get("url", "")
    enabled = source.get("enabled", True)

    if not enabled:
        return "SKIPPED", "disabled in config"

    if not url:
        return "ERROR", "no URL defined"

    try:
        if stype == "greenhouse":
            return check_greenhouse(source)
        elif stype == "lever":
            return check_lever(source)
        elif stype == "ashby":
            return check_ashby(source)
        elif stype in ("indeed", "remoteok"):
            return check_url(url)
        elif stype == "github_list":
            return check_url(url)
        elif stype == "linkedin":
            return "SKIPPED", "LinkedIn check skipped (requires browser)"
        else:
            return check_url(url)

    except requests.exceptions.ConnectionError:
        return "DEAD", "connection error"
    except requests.exceptions.Timeout:
        return "DEAD", "timed out"
    except Exception as e:
        return "ERROR", str(e)


def check_greenhouse(source):
    slug = source["url"].rstrip("/").split("/")[-1]
    api  = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    r    = requests.get(api, timeout=10)
    if r.status_code == 200:
        count = len(r.json().get("jobs", []))
        return "✅ ALIVE", f"{count} jobs on board"
    return "❌ DEAD", f"HTTP {r.status_code}"


def check_lever(source):
    slug = source["url"].rstrip("/").split("/")[-1]
    api  = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    r    = requests.get(api, timeout=10)
    if r.status_code == 200:
        count = len(r.json())
        return "✅ ALIVE", f"{count} jobs on board"
    return "❌ DEAD", f"HTTP {r.status_code} — company may have left Lever"


def check_ashby(source):
    slug = source["url"].rstrip("/").split("/")[-1]
    api  = f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true"
    r    = requests.get(api, timeout=10)
    if r.status_code == 200:
        count = len(r.json().get("jobs", []))
        return "✅ ALIVE", f"{count} jobs on board"
    return "❌ DEAD", f"HTTP {r.status_code} — company may have left Ashby"


def check_url(url):
    r = requests.get(url, timeout=10, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    })
    if r.status_code == 200:
        return "✅ ALIVE", f"HTTP {r.status_code}"
    return "❌ DEAD", f"HTTP {r.status_code}"


def main():
    console.print("[bold green]\n🔍 Verifying all sources in config.yaml...[/bold green]\n")

    config  = load_config()
    sources = config.get("sources", [])

    table = Table(show_lines=True)
    table.add_column("Source",  style="bold white", max_width=25)
    table.add_column("Type",    style="yellow",     max_width=12)
    table.add_column("Status",  max_width=12)
    table.add_column("Details", style="dim",        max_width=40)

    alive   = 0
    dead    = 0
    skipped = 0

    for source in sources:
        name    = source.get("name", "Unknown")
        stype   = source.get("type", "")
        status, message = check_source(source)

        if "ALIVE" in status:
            alive += 1
            status_display = f"[green]{status}[/green]"
        elif "DEAD" in status:
            dead += 1
            status_display = f"[red]{status}[/red]"
        else:
            skipped += 1
            status_display = f"[dim]{status}[/dim]"

        table.add_row(name, stype, status_display, message)

    console.print(table)
    console.print(f"\n[green]✅ Alive: {alive}[/green]  "
                  f"[red]❌ Dead: {dead}[/red]  "
                  f"[dim]⏭️  Skipped: {skipped}[/dim]")

    if dead > 0:
        console.print("\n[yellow]💡 Tip: Remove or replace dead sources in config.yaml[/yellow]")


if __name__ == "__main__":
    main()