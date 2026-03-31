# ============================================================
#  SCHEDULER
#  Runs the scraper every 2 hours automatically
#
#  Two modes:
#  python3 scheduler.py          → uses config.yaml (personal)
#  python3 scheduler.py --public → uses config.public.yaml (public sheet)
# ============================================================

import sys
import time
import schedule
from rich.console import Console
from main import load_config, run_scraper
from enricher import enrich_jobs
from filters import apply_filters
from ai_filter import filter_jobs_by_role
from sheets_exporter import export_to_sheets

console = Console()


def run_scrape(config_path="config.yaml"):
    console.print(f"\n[bold green]⏰ Scheduled run starting ({config_path})...[/bold green]")

    config     = load_config(config_path)
    roles_cfg  = config.get("roles", [])
    sources    = config.get("sources", [])
    output_cfg = config.get("output", {})
    filter_cfg = config.get("filters", {})

    # ── Extract keyword roles for scrapers ────────────────────
    if isinstance(roles_cfg, dict):
        roles = [k.lower() for k in roles_cfg.get("keywords", [])]
    else:
        roles = [r.lower() for r in roles_cfg]

    # ── Scrape all sources ────────────────────────────────────
    all_jobs = []
    for source in sources:
        if not source.get("enabled", True):
            continue
        jobs = run_scraper(source, roles)
        all_jobs.extend(jobs)

    # ── Deduplicate ───────────────────────────────────────────
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = (job.get("role", "").lower(), job.get("company", "").lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    # ── AI role filter ────────────────────────────────────────
    console.print("\n[bold cyan]🤖 Filtering by role...[/bold cyan]")
    unique_jobs = filter_jobs_by_role(unique_jobs, roles_cfg)

    # ── Apply filters ─────────────────────────────────────────
    if filter_cfg:
        console.print("\n[bold cyan]🔽 Applying filters...[/bold cyan]")
        unique_jobs = apply_filters(unique_jobs, filter_cfg)

    # ── Enrich LinkedIn URLs (optional) ──────────────────────
    if output_cfg.get("enrich_linkedin", False):
        unique_jobs = enrich_jobs(unique_jobs)

    # ── Push to Google Sheets ─────────────────────────────────
    sheet_name = output_cfg.get("sheet_name", "Job Scraper - Live")
    sheet_id   = output_cfg.get("sheet_id", None)
    url = export_to_sheets(unique_jobs, sheet_name, sheet_id)

    console.print(f"\n[bold green]✅ Done! {len(unique_jobs)} jobs in sheet.[/bold green]")
    if url:
        console.print(f"[bold]🔗 {url}[/bold]")

    return url


if __name__ == "__main__":

    # ── Detect mode ───────────────────────────────────────────
    if "--public" in sys.argv:
        config_path = "config.public.yaml"
        console.print("[bold green]🌍 Running in PUBLIC mode (config.public.yaml)[/bold green]")
    else:
        config_path = "config.yaml"
        console.print("[bold green]👤 Running in PERSONAL mode (config.yaml)[/bold green]")

    console.print("[bold green]🚀 Scheduler started — runs every 2 hours[/bold green]")

    # ── Run immediately on start ──────────────────────────────
    run_scrape(config_path)

    # ── Schedule every 2 hours ────────────────────────────────
    schedule.every(2).hours.do(run_scrape, config_path=config_path)

    while True:
        schedule.run_pending()
        time.sleep(60)