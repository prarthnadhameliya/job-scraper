# ============================================================
#  AI FILTER
#  Uses Claude API to intelligently filter job titles
#  Falls back to keyword matching if no API key
# ============================================================

import os
import json
from rich.console import Console

console = Console()

# ── Cache to avoid re-checking same titles ────────────────────
_cache = {}


def filter_jobs_by_role(jobs, config_roles):
    """
    Main entry point.
    Uses AI if api_key exists, otherwise keyword matching.
    """

    # Check if AI filtering is enabled
    if not isinstance(config_roles, dict):
        # Old format: list of keywords — use keyword matching
        roles = [r.lower() for r in config_roles]
        return [j for j in jobs if keyword_match(j["role"], roles)]

    # New format: dict with use_ai + description
    use_ai = config_roles.get("use_ai", False)
    description = config_roles.get("description", "")
    keywords = [k.lower() for k in config_roles.get("keywords", [])]
    api_key = config_roles.get("api_key", "") or os.getenv("ANTHROPIC_API_KEY", "")

    if use_ai and api_key:
        console.print("  [dim]→ Using Claude AI for role filtering...[/dim]")
        return ai_filter(jobs, description, api_key)
    else:
        if use_ai and not api_key:
            console.print("  [yellow]⚠️  No API key found — falling back to keyword matching[/yellow]")
        return [j for j in jobs if keyword_match(j["role"], keywords)]


def ai_filter(jobs, description, api_key):
    """
    Uses Claude API to filter jobs in batches of 20.
    """
    try:
        import anthropic
    except ImportError:
        console.print("  [red]✗ anthropic not installed — run: pip install anthropic[/red]")
        return jobs

    client = anthropic.Anthropic(api_key=api_key)
    matched = []
    batch_size = 20

    # Split jobs into batches
    batches = [jobs[i:i+batch_size] for i in range(0, len(jobs), batch_size)]
    console.print(f"  [dim]→ Checking {len(jobs)} titles in {len(batches)} batches...[/dim]")

    for i, batch in enumerate(batches):
        console.print(f"  [dim]→ Batch {i+1}/{len(batches)}...[/dim]")

        # Build list of titles to check
        titles_to_check = []
        cached_results = {}

        for job in batch:
            title = job["role"]
            if title in _cache:
                cached_results[title] = _cache[title]
            else:
                titles_to_check.append(title)

        # Add cached matches directly
        for job in batch:
            if job["role"] in cached_results and cached_results[job["role"]]:
                matched.append(job)

        if not titles_to_check:
            continue

        # Ask Claude to filter
        prompt = f"""You are a job filter. I'm looking for: {description}

Here are {len(titles_to_check)} job titles. Reply with ONLY a JSON array of 
true/false values in the same order — true if relevant, false if not.
No explanation, just the JSON array.

Titles:
{json.dumps(titles_to_check, indent=2)}

Reply format: [true, false, true, ...]"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            text = response.content[0].text.strip()
            # Clean up any markdown
            text = text.replace("```json", "").replace("```", "").strip()
            results = json.loads(text)

            # Match results to titles
            for j, title in enumerate(titles_to_check):
                is_match = results[j] if j < len(results) else False
                _cache[title] = is_match

                # Find the job with this title and add if matched
                for job in batch:
                    if job["role"] == title and is_match:
                        matched.append(job)

        except Exception as e:
            console.print(f"  [yellow]⚠️  AI batch failed: {e} — keeping all jobs in batch[/yellow]")
            matched.extend([j for j in batch if j["role"] in titles_to_check])

    console.print(f"  [dim]→ AI filter: {len(matched)}/{len(jobs)} jobs matched[/dim]")
    return matched


def keyword_match(title, keywords):
    """Simple keyword matching fallback."""
    if not keywords:
        return True
    title_lower = title.lower()
    return any(kw in title_lower for kw in keywords)