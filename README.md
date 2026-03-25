# 🔍 Job Scraper

A configurable job scraping tool that aggregates listings from multiple sources and exports them to an Excel sheet. No manual job searching — just run it and get a clean spreadsheet.

## ✨ Features

- Scrapes **Greenhouse, Lever, Ashby** via public JSON APIs (no auth needed)
- Pulls remote jobs from **RemoteOK**
- Parses **GitHub markdown job lists** (like hiring-without-whiteboards)
- Supports **LinkedIn** via Playwright stealth or Apify
- **Custom portals** — add any career page using CSS selectors, no coding needed
- Exports to **Excel (.xlsx) or CSV**
- Auto-finds **LinkedIn company URLs** (optional enrichment)
- `verify.py` — checks which sources are still alive before scraping

## 📸 Demo
```
🚀 Job Scraper Starting...
✅ Found 49 matching jobs  (Stripe)
✅ Found 33 matching jobs  (Airbnb)
✅ Found 17 matching jobs  (Perplexity)
✅ Found 901 companies     (Hiring Without Whiteboards)
Total unique jobs found: 1003
✅ Excel saved: jobs_output_2026-03-24.xlsx
```

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/job-scraper.git
cd job-scraper
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Configure your search
Edit `config.yaml`:
```yaml
roles:
  - "Software Engineer"
  - "Backend Engineer"

sources:
  - name: "Stripe"
    type: greenhouse
    url: "https://boards.greenhouse.io/stripe"
    enabled: true
```

### 5. Run it
```bash
python3 main.py
```

### 6. Verify your sources are alive
```bash
python3 verify.py
```

## ⚙️ Config Guide

### Adding a built-in source
```yaml
# Greenhouse
- name: "Stripe"
  type: greenhouse
  url: "https://boards.greenhouse.io/stripe"
  enabled: true

# Lever
- name: "Payjoy"
  type: lever
  url: "https://jobs.lever.co/payjoy"
  enabled: true

# Ashby
- name: "Perplexity"
  type: ashby
  url: "https://jobs.ashbyhq.com/perplexity"
  enabled: true
```

### Adding a custom career page (no coding needed)
1. Open the careers page in Chrome
2. Right click a job title → **Inspect**
3. Find the CSS selectors and paste them in config:
```yaml
- name: "My Dream Company"
  type: custom
  url: "https://careers.example.com"
  job_container: "div.job-listing"
  role_selector: "h2.job-title"
  link_selector: "a.apply-btn"
  location_selector: "span.location"
  enabled: true
```

### Adding a GitHub job list
```yaml
- name: "Hiring Without Whiteboards"
  type: github_list
  url: "https://raw.githubusercontent.com/poteto/hiring-without-whiteboards/master/README.md"
  enabled: true
```

### Enable LinkedIn URL enrichment
```yaml
output:
  enrich_linkedin: true   # auto-finds LinkedIn URLs for all companies
```

## 📁 Project Structure
```
job-scraper/
├── scrapers/
│   ├── greenhouse.py    # Greenhouse API
│   ├── lever.py         # Lever API
│   ├── ashby.py         # Ashby API
│   ├── indeed.py        # RemoteOK API
│   ├── github_list.py   # GitHub markdown parser
│   ├── linkedin.py      # LinkedIn (Playwright/Apify)
│   ├── generic.py       # Generic headless browser
│   └── custom.py        # CSS selector based scraper
├── main.py              # Entry point
├── verify.py            # Source health checker
├── exporter.py          # Excel/CSV export
├── enricher.py          # LinkedIn URL enrichment
├── config.yaml          # Your configuration
└── requirements.txt     # Dependencies
```

## 🤝 Contributing

Want to add a new job portal scraper? See [CONTRIBUTING.md](CONTRIBUTING.md)

The easiest way is to add a new scraper in `scrapers/` following the same pattern — every scraper returns the same dict structure:
```python
{
    "role":         "Software Engineer",
    "company":      "Stripe",
    "website":      "https://stripe.com/jobs",
    "job_url":      "https://...",
    "location":     "San Francisco, CA",
    "linkedin_url": "",
    "source_type":  "greenhouse",
    "date_found":   "",
}
```

## ⚠️ Disclaimer

This tool is for personal job searching only. Always respect websites' `robots.txt` and terms of service.

## 📄 License

MIT License — free to use, modify and distribute.