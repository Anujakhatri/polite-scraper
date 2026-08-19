#one bad page must not kill the run

import json
import os
import time
from datetime import datetime, timezone

from fetch_utils import FetchError
from discover_links import discover_all_book_urls
from extract_books import extract_book_details, _url_to_cache_filename
from fetch_utils import fetch_page
from validate import validate_and_store

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
REPORT_PATH = os.path.join(OUTPUT_DIR, "report.json")

def extract_all_books_safely(book_urls: list[str], source_page_map: dict) -> tuple[list[dict], int]:
    records = []
    failed_count = 0
    
    for url in book_urls:
        try:
            cache_filename = _url_to_cache_filename(url)
            html = fetch_page(url, cache_filename)
            source_page = source_page_map.get(url, "unknown")
            record = extract_book_details(html, url, source_page)
            records.append(record)
        except FetchError as e:
            # one page fail -> log it and skip it
            print(f"SKIPPED | {url} | reason={e}")
            failed_count += 1
            continue  #one fail but still go to next page
    return records, failed_count

def run() -> None:
    start_time = time.time()
    start_time_iso = datetime.now(timezone.utc).isoformat()
    
    unique_urls, pages_visited, source_page_map = discover_all_book_urls(max_pages=3)
    
    raw_records, failed_pages = extract_all_books_safely(unique_urls, source_page_map)
    result = validate_and_store(raw_records)
    duration_seconds = round(time.time() - start_time,2)
    
    # make run reports with honest number
    report = {
        "start_time": start_time_iso,
        "duration_seconds": duration_seconds,
        "catalogue_pages_fetched": pages_visited,
        "book_urls_discovered": len(unique_urls),
        "valid_records": result["valid_count"],
        "invalid_records": result["error_count"],
        "failed_pages": failed_pages,
    }
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print("\n--- RUN REPORT ---")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
if __name__ == "__main__":
    run()