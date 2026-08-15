# extract raw details of each book
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from fetch_utils import fetch_page
from discover_links import discover_all_book_urls

def _url_to_cache_filename(url:str) -> str:
    slug = url.rstrip("/").split("/")[-2]
    return f"book-{slug}.html"

def extract_book_details(html: str, product_url: str, source_page: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    
    # --- title: <h1> tag ma huncha ---
    title_tag = soup.select_one("div.product_main h1")
    title = title_tag.get_text(strip=True) if title_tag else None
    
    # --- price: <p class="price_color"> ---
    price_tag = soup.select_one("div.product_main p.price_color")
    price_text = price_tag.get_text(strip=True) if price_tag else None
    
    # --- availability: <p class="instock availability"> ---
    availability_tag = soup.select_one("div.product_main p.availability")
    availability_text = (
        availability_tag.get_text(strip=True) if availability_tag else None
    )
    
     # --- rating: class ma "star-rating Three" jasto huncha, word nikalne ---
    rating_tag = soup.select_one("p.star-rating")
    rating_text = None
    if rating_tag:
        classes = rating_tag.get("class", [])
        for cls in classes:
            if cls != "star-rating":
                rating_text = cls
                break 
    
    # --- description: id="product_description" pachi ko <p> tag ma ---
    desc_heading = soup.select_one("#product_description")
    description = None
    if desc_heading:
        desc_paragraph = desc_heading.find_next_sibling("p")
        if desc_paragraph:
            description = desc_paragraph.get_text(strip=True)
    
    
    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
 
def extract_all_books(book_urls: list[str], source_page_map: dict) -> list[dict]:
    records = []
 
    for url in book_urls:
        cache_filename = _url_to_cache_filename(url)
        html = fetch_page(url, cache_filename)
 
        source_page = source_page_map.get(url, "unknown")
        record = extract_book_details(html, url, source_page)
        records.append(record)
 
    return records

if __name__ == "__main__":
    unique_urls, pages_visited, source_page_map = discover_all_book_urls(max_pages=3)
 
    records = extract_all_books(unique_urls, source_page_map)
 
    print(f"\ndetail_pages={len(records)}")
    print("\nOne sample record:")
    import json
    print(json.dumps(records[0], indent=2, ensure_ascii=False))