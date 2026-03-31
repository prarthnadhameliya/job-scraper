# ============================================================
#  FILTERS
#  Filters jobs based on config.yaml filter settings
# ============================================================

from datetime import datetime, timedelta
from rich.console import Console

console = Console()

def apply_filters(jobs, filter_cfg):
    if not filter_cfg:
        return jobs

    original_count = len(jobs)

    # ── Location filter ───────────────────────────────────────
    locations = [l.lower() for l in filter_cfg.get("locations", [])]
    if locations:
        jobs = [j for j in jobs if matches_location(j, locations)]
        console.print(f"  [dim]→ After location filter: {len(jobs)} jobs[/dim]")

    # ── Experience filter ─────────────────────────────────────
    experience = [e.lower() for e in filter_cfg.get("experience", [])]
    if experience:
        jobs = [j for j in jobs if matches_experience(j, experience)]
        console.print(f"  [dim]→ After experience filter: {len(jobs)} jobs[/dim]")

    # ── Job type filter ───────────────────────────────────────
    job_types = [t.lower() for t in filter_cfg.get("job_types", [])]
    if job_types:
        jobs = [j for j in jobs if matches_job_type(j, job_types)]
        console.print(f"  [dim]→ After job type filter: {len(jobs)} jobs[/dim]")

    # ── Date filter ───────────────────────────────────────────
    days_old = filter_cfg.get("days_old", 0)
    if days_old > 0:
        jobs = [j for j in jobs if matches_date(j, days_old)]
        console.print(f"  [dim]→ After date filter: {len(jobs)} jobs[/dim]")

    filtered_count = original_count - len(jobs)
    console.print(f"\n[dim]Filtered out {filtered_count} jobs, {len(jobs)} remaining[/dim]")

    return jobs


# ── Individual filters ────────────────────────────────────────

def matches_location(job, locations):
    job_location = job.get("location", "").lower()
    if not job_location:
        return True
    return any(loc in job_location for loc in locations)


def matches_experience(job, experience_levels):
    title = job.get("role", "").lower()
    if not experience_levels:
        return True
    return any(level in title for level in experience_levels)


def matches_job_type(job, job_types):
    jtype = job.get("job_type", "").lower()
    title = job.get("role", "").lower()

    if not job_types:
        return True

    type_keywords = {
        "full-time": ["full-time", "full time"],
        "contract": ["contract", "contractor", "freelance"],
        "internship": ["intern", "internship", "co-op"],
        "part-time": ["part-time", "part time"],
    }

    for jt in job_types:
        keywords = type_keywords.get(jt, [jt])
        if any(kw in title for kw in keywords):
            return True

    if not jtype:
        return True

    return False


def matches_date(job, days_old):
    date_str = job.get("date_found", "")
    if not date_str:
        return True
    try:
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
            try:
                job_date = datetime.strptime(date_str[:10], fmt[:8])
                cutoff = datetime.now() - timedelta(days=days_old)
                return job_date >= cutoff
            except ValueError:
                continue
    except Exception:
        pass
    return True