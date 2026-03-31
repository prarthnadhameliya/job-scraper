# ============================================================
#  JOB SCRAPER - MAIN ENTRY POINT
#  Run this file to start scraping: python main.py
# ============================================================

import yaml
from rich.console import Console
from rich.table import Table
from scrapers.greenhouse import scrape_greenhouse
from scrapers.lever import scrape_lever
from scrapers.ashby import scrape_ashby
from scrapers.indeed import scrape_indeed
from scrapers.github_list import scrape_github_list
from scrapers.linkedin import scrape_linkedin
from scrapers.generic import scrape_generic
from scrapers.custom import scrape_custom
from exporter import export_jobs
from enricher import enrich_jobs
from filters import apply_filters
from scrapers.ycombinator import scrape_ycombinator
from ai_filter import filter_jobs_by_role

console = Console()

# ── 1. Load config ───────────────────────────────────────────
def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

# ── 2. Route each source to the right scraper ────────────────
def run_scraper(source, roles):
    name = source.get("name", "Unknown")
    stype = source.get("type")

    console.print(f"\n[bold cyan]🔍 Scraping:[/bold cyan] {name} ([yellow]{stype}[/yellow])")

    try:
        if stype == "greenhouse":
            return scrape_greenhouse(source, roles)
        elif stype == "lever":
            return scrape_lever(source, roles)
        elif stype == "ashby":
            return scrape_ashby(source, roles)
        elif stype == "indeed":
            return scrape_indeed(source, roles)
        elif stype == "github_list":
            return scrape_github_list(source, roles)
        elif stype == "linkedin":
            return scrape_linkedin(source, roles)
        elif stype == "scrape":
            return scrape_generic(source, roles)
        elif stype == "custom":
            return scrape_custom(source, roles)
        elif stype == "ycombinator":
            return scrape_ycombinator(source, roles)
        else:
            console.print(f"[red]⚠️  Unknown source type: {stype}[/red]")
            return []
    except Exception as e:
        console.print(f"[red]❌ Failed to scrape {name}: {e}[/red]")
        return []

# ── 3. Print a preview table in the terminal ─────────────────
def print_preview(jobs):
    if not jobs:
        console.print("\n[red]No jobs found.[/red]")
        return

    table = Table(title="Jobs Found", show_lines=True)
    table.add_column("Role", style="bold white", max_width=35)
    table.add_column("Company", style="cyan", max_width=25)
    table.add_column("Source", style="yellow", max_width=15)

    for job in jobs[:20]:
        table.add_row(
            job.get("role", ""),
            job.get("company", ""),
            job.get("source_type", "")
        )

    console.print(table)
    if len(jobs) > 20:
        console.print(f"[dim]... and {len(jobs) - 20} more jobs in the output file.[/dim]")

# ── 4. Main ───────────────────────────────────────────────────
def main():
    console.print("[bold green]\n🚀 Job Scraper Starting...[/bold green]")

    # Load config
    config = load_config()
    roles_cfg = config.get("roles", [])
    # Keep backward compatible roles list for scrapers
    if isinstance(roles_cfg, dict):
        roles = [k.lower() for k in roles_cfg.get("keywords", [])]
    else:
        roles = [r.lower() for r in roles_cfg]

    # roles = [r.lower() for r in config.get("roles", [])]
    sources = config.get("sources", [])
    output_cfg = config.get("output", {})
    filter_cfg = config.get("filters", {})

    console.print(f"[dim]Roles: {', '.join(roles)}[/dim]")
    console.print(f"[dim]Sources enabled: {sum(1 for s in sources if s.get('enabled', True))}[/dim]")

    # Run all enabled scrapers
    all_jobs = []
    for source in sources:
        if not source.get("enabled", True):
            console.print(f"\n[dim]⏭️  Skipping: {source.get('name')}[/dim]")
            continue
        jobs = run_scraper(source, roles)
        console.print(f"[green]✅ Found {len(jobs)} matching jobs[/green]")
        all_jobs.extend(jobs)

    # Deduplicate by role + company
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = (job.get("role", "").lower(), job.get("company", "").lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

     # AI role filter
    console.print("\n[bold cyan]🤖 Filtering by role...[/bold cyan]")
    unique_jobs = filter_jobs_by_role(unique_jobs, roles_cfg)

    # Apply filters
    if filter_cfg:
        console.print("\n[bold cyan]🔽 Applying filters...[/bold cyan]")
        unique_jobs = apply_filters(unique_jobs, filter_cfg)

    # Enrich with LinkedIn URLs (optional)
    if output_cfg.get("enrich_linkedin", False):
        unique_jobs = enrich_jobs(unique_jobs)

    console.print(f"\n[bold]Total unique jobs found: {len(unique_jobs)}[/bold]")

    # Preview in terminal
    print_preview(unique_jobs)

    # Export to file
    export_jobs(unique_jobs, output_cfg)

if __name__ == "__main__":
    main()