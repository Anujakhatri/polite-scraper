## Target classification
- **Site:** https://books.toscrape.com
- **What it is:** A public sandbox built specifically for scraping practice.
- **Scope:** First 3 catalogue pages only (~60 books).
- **Data collected:** Book title, price, availability, rating, description, product URL.
- **robots.txt result:** no robots file found(404)
- I will not reuse this code on another site without checking its rules and terms first.

## How to Run

### Requirements
- Python 3.10+

### Setup
```bash
git clone https://github.com/Anujakhatri/polite-scraper.git
cd polite-scraper
pip install -r requirements.txt
```

### Run Command
```bash
cd src
python run_scraper.py
```

### Run Command
```bash
cd src
python run_scraper.py
```

This will:
1. Fetch the first 3 catalogue pages (cached after first run)
2. Discover and visit all 60 book detail pages
3. Clean and validate the data against a schema
4. Save results to `output/books.json`, `output/errors.json`, and `output/run-report.json`

## Record Schema

| Field | Type | Description |
|---|---|---|
| title | string | Book title |
| product_url | string (URL) | Canonical identity of the record |
| price_text | string | Original price text (e.g. "£51.77") |
| price_gbp | number | Normalized price as a number |
| availability_text | string | Stock status text |
| rating_text | string | Star rating (One–Five) |
| description | string or null | Book description (null if not present on page) |
| source_page | string | Which catalogue page this book was discovered on |
| fetched_at | string (ISO datetime) | When this record was fetched |

## Politeness Rules

- **User-Agent:** Identifies this scraper honestly (`FlyRankInternshipA9/1.0`)
- **Delay:** Waits 0.5s between real (non-cached) requests
- **Timeout:** Gives up after 10s per request
- **Caching:** Development and re-runs read from `cache/` instead of re-fetching the site
- **Retry:** Retries once on timeout/5xx server errors; never retries 404/403 (asking again won't help)

## Sample Run Report

```json
{
  "start_time": "2026-08-19T03:06:34.472598+00:00",
  "duration_seconds": 0.29,
  "catalogue_pages_fetched": 3,
  "book_urls_discovered": 60,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}
```

## Why No Browser Was Needed

All book data (title, price, availability, rating, description) is already 
present in the server-rendered HTML that `requests` retrieves — no JavaScript 
execution is needed to reveal it. Using a browser (e.g. Playwright) here would 
only add startup time and memory cost with no benefit.

## Known Limitation

Retry logic is a single fixed-delay retry rather than full exponential backoff with jitter.

## Ethics Note

This scraper only targets `books.toscrape.com`, a public sandbox explicitly 
built for scraping practice — confirmed by the site's own description and 
the absence of any restrictive `robots.txt`. In general: always check for an 
official API before scraping, never bypass logins or paywalls, and collect 
only the data actually needed. This code will not be reused on another site 
without checking that site's own rules and terms first.