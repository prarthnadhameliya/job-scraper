# ============================================================
#  GOOGLE SHEETS EXPORTER
#  Single tab: All Jobs with native header filters
# ============================================================

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from rich.console import Console

console = Console()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )
    return gspread.authorize(creds)


def export_to_sheets(jobs, sheet_name="Job Scraper", sheet_id=None):
    if not jobs:
        console.print("[red]No jobs to export to Google Sheets.[/red]")
        return None

    console.print(f"\n[bold cyan]📊 Exporting to Google Sheets...[/bold cyan]")

    client = get_client()

    # ── Open sheet ────────────────────────────────────────────
    try:
        if sheet_id:
            spreadsheet = client.open_by_key(sheet_id)
            console.print(f"  [dim]→ Opened sheet by ID[/dim]")
        else:
            spreadsheet = client.open(sheet_name)
            console.print(f"  [dim]→ Opened sheet by name[/dim]")
    except Exception as e:
        console.print(f"  [red]✗ Could not open sheet: {e}[/red]")
        console.print(f"  [yellow]→ Make sure you shared the sheet with your service account email[/yellow]")
        return None

    # ── Clean up extra tabs ───────────────────────────────────
    cleanup_extra_tabs(spreadsheet)

    # ── Get or create single Jobs tab ─────────────────────────
    worksheet = get_or_create_tab(spreadsheet, "Jobs")

    # ── Push data ─────────────────────────────────────────────
    push_raw_data(worksheet, jobs)

    url = spreadsheet.url
    console.print(f"\n[bold green]✅ Google Sheet updated![/bold green]")
    console.print(f"[bold]🔗 Link: {url}[/bold]")
    console.print(f"[dim]Total rows: {len(jobs)} jobs[/dim]")

    return url


# ── Tab helpers ───────────────────────────────────────────────

def get_or_create_tab(spreadsheet, name):
    try:
        return spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=name, rows=2000, cols=10)


def cleanup_extra_tabs(spreadsheet):
    """Removes Dashboard, How to Use, All Jobs tabs — keeps only Jobs."""
    tabs_to_remove = ["Dashboard", "How to Use", "All Jobs", "Sheet1"]
    worksheets = spreadsheet.worksheets()

    # Need at least one sheet — create Jobs first if needed
    existing_names = [ws.title for ws in worksheets]
    if "Jobs" not in existing_names:
        spreadsheet.add_worksheet(title="Jobs", rows=2000, cols=10)

    # Now remove unwanted tabs
    for ws in spreadsheet.worksheets():
        if ws.title in tabs_to_remove:
            try:
                spreadsheet.del_worksheet(ws)
                console.print(f"  [dim]→ Removed tab: {ws.title}[/dim]")
            except Exception:
                pass


def push_raw_data(worksheet, jobs):
    """Pushes all job data with native header filters."""

    headers = [
        "Role", "Company", "Location",
        "Job URL", "Website", "LinkedIn URL",
        "Source", "Date Found"
    ]

    rows = [headers]
    for job in jobs:
        rows.append([
            job.get("role", ""),
            job.get("company", ""),
            job.get("location", "") or "Remote",
            job.get("job_url", ""),
            job.get("website", ""),
            job.get("linkedin_url", ""),
            job.get("source_type", ""),
            job.get("date_found", "") or datetime.today().strftime("%Y-%m-%d"),
        ])

    worksheet.clear()
    worksheet.update(rows)

    # ── Header formatting ─────────────────────────────────────
    worksheet.format("A1:H1", {
        "backgroundColor": {"red": 0.13, "green": 0.13, "blue": 0.13},
        "textFormat": {
            "bold": True,
            "fontSize": 11,
            "foregroundColor": {"red": 1, "green": 1, "blue": 1}
        },
        "horizontalAlignment": "CENTER",
    })

    # ── Freeze header ─────────────────────────────────────────
    worksheet.freeze(rows=1)

    # ── Native filter arrows on header ────────────────────────
    worksheet.set_basic_filter(name="A1:H1")

    # ── Alternate row colors ──────────────────────────────────
    requests = [{
        "addBanding": {
            "bandedRange": {
                "range": {
                    "sheetId": worksheet.id,
                    "startRowIndex": 1,
                    "endRowIndex": len(rows),
                    "startColumnIndex": 0,
                    "endColumnIndex": 8,
                },
                "rowProperties": {
                    "firstBandColor": {
                        "red": 1, "green": 1, "blue": 1
                    },
                    "secondBandColor": {
                        "red": 0.95, "green": 0.95, "blue": 0.98
                    },
                }
            }
        }
    }]

    try:
        worksheet.spreadsheet.batch_update({"requests": requests})
    except Exception:
        pass

    console.print(f"  [dim]→ Jobs tab updated: {len(jobs)} rows[/dim]")