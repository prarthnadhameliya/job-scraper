# 🔍 Job Scraper

A configurable job scraping tool that aggregates listings from multiple sources and exports them to a live Google Sheet or Excel file — automatically, every 2 hours.

---

## ✨ Two Ways to Use This

### 👀 Option 1 — Just use the Google Sheet (no code)
Access the live job board directly:

🔗 **[Open Live Job Sheet](https://docs.google.com/spreadsheets/d/16JWn9ueySrsHxvMSQ6TxiPIRKdEfggKoC4cdK3GLphg)**

- Updates every 2 hours automatically
- Targets New Grad + Junior Software Engineer roles
- All locations included
- Filter by location, experience, and job type using dropdowns
- No account needed — just open and use!

---

### 💻 Option 2 — Run it yourself (full control)
Clone the repo and customize everything — your own roles, sources, locations, and Google Sheet.

---

## 🚀 Getting Started (Code Users)

### 1. Clone the repo
```bash
git clone https://github.com/prarthnadhameliya/job-scraper.git
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

filters:
  locations:
    - "Remote"
    - "San Francisco"
  experience:
    - "Senior"
  job_types: []
  days_old: 30
```

### 5. Run it
```bash
# Generate Excel file
python3 main.py

# Run with auto-refresh every 2 hours + Google Sheets
python3 scheduler.py
```

### 6. Verify your sources
```bash
python3 verify.py
```

---

## ⚙️ Config Guide

### Adding built-in sources
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
3. Find the CSS selectors and paste in config:
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

### Setting up Google Sheets export
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project → Enable Google Sheets API + Google Drive API
3. Create a Service Account → Download JSON key → rename to `credentials.json`
4. Create a Google Sheet → Share it with your service account email
5. Add sheet ID to `config.yaml`:
```yaml
output:
  sheet_name: "My Job Sheet"
  sheet_id: "YOUR_SHEET_ID_HERE"
```

6. Run scheduler:
```bash
python3 scheduler.py
```

### Enable filters
```yaml
filters:
  locations:
    - "Remote"
    - "San Francisco"
  experience:
    - "Junior"
    - "Senior"
  job_types:
    - "Full-time"
  days_old: 30   # 0 = no date filter
```

---

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
├── main.py              # Entry point — generates Excel
├── scheduler.py         # Auto-refresh every 2 hours
├── verify.py            # Source health checker
├── exporter.py          # Excel/CSV export
├── sheets_exporter.py   # Google Sheets export
├── enricher.py          # LinkedIn URL enrichment
├── filters.py           # Job filters
├── config.yaml          # Your personal config
├── config.public.yaml   # Config for public sheet
└── requirements.txt     # Dependencies
```

---

## 🖥️ Demo Output
```
🚀 Job Scraper Starting...
✅ Found 49 matching jobs  — Stripe
✅ Found 33 matching jobs  — Airbnb
✅ Found 17 matching jobs  — Perplexity
✅ Found 901 companies     — Hiring Without Whiteboards

🔽 Applying filters...
  → After location filter: 120 jobs
  → After experience filter: 45 jobs

Total unique jobs found: 45
✅ Excel saved: jobs_output_2026-03-24.xlsx
✅ Google Sheet updated!
🔗 https://docs.google.com/spreadsheets/d/...
```

---

## 🤝 Contributing

Want to add a new job portal? Every scraper returns the same dict:
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

1. Add a new file in `scrapers/`
2. Register it in `main.py`
3. Submit a pull request!

---

## ⚠️ Disclaimer

This tool is for personal job searching only. Always respect websites'
`robots.txt` and terms of service.

## 📄 License

MIT License — free to use, modify and distribute.