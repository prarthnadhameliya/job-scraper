# ============================================================
#  EXPORTER
#  Converts job list to Excel (.xlsx) or CSV
# ============================================================

import pandas as pd
from datetime import datetime
from rich.console import Console

console = Console()

def export_jobs(jobs, output_cfg):
    if not jobs:
        console.print("\n[red]No jobs to export.[/red]")
        return

    filename = output_cfg.get("filename", "jobs_output")
    fmt = output_cfg.get("format", "xlsx")

    # Add today's date to filename
    date_str = datetime.today().strftime("%Y-%m-%d")
    base = f"{filename}_{date_str}"

    # ── Build DataFrame ───────────────────────────────────────
    rows = []
    for job in jobs:
        rows.append({
            "Role":         job.get("role", ""),
            "Company":      job.get("company", ""),
            "Location":     job.get("location", ""),
            "Job URL":      job.get("job_url", ""),
            "Website":      job.get("website", ""),
            "LinkedIn URL": job.get("linkedin_url", ""),
            "Source":       job.get("source_type", ""),
            "Date Found":   job.get("date_found", "") or date_str,
        })

    df = pd.DataFrame(rows)

    # ── Export ────────────────────────────────────────────────
    if fmt in ("xlsx", "both"):
        xlsx_path = f"{base}.xlsx"
        export_xlsx(df, xlsx_path)

    if fmt in ("csv", "both"):
        csv_path = f"{base}.csv"
        df.to_csv(csv_path, index=False)
        console.print(f"\n[bold green]✅ CSV saved:[/bold green] {csv_path}")


def export_xlsx(df, path):
    """Export with clean formatting."""
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Jobs")

        # Auto-size columns
        worksheet = writer.sheets["Jobs"]
        for col in worksheet.columns:
            max_len = max(
                len(str(cell.value)) if cell.value else 0
                for cell in col
            )
            worksheet.column_dimensions[col[0].column_letter].width = min(max_len + 4, 60)

        # Freeze the header row
        worksheet.freeze_panes = "A2"

    console.print(f"\n[bold green]✅ Excel saved:[/bold green] {path}")