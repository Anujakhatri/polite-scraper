import json
import os
import re
from typing import Optional

from pydantic import BaseModel, ValidationError, HttpUrl

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
BOOKS_JSON_PATH = os.path.join(OUTPUT_DIR, "books.json")
ERRORS_JSON_PATH = os.path.join(OUTPUT_DIR, "errors.json")

#define clean record
class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl          
    price_text: str               
    price_gbp: float              
    availability_text: str
    rating_text: str
    description: Optional[str] = None
    source_page: str
    fetched_at: str

# raw text = clean value  
def normalize_price(price_text : str) -> float:
    if price_text is None:
        raise ValueError("Price text is None, cannot be normalize")
    
    cleaned = re.sub(r"[^\d.]", "", price_text)
    
    if not cleaned:
        raise ValueError(f"Could not extract a number from the price text '{price_text}'")
    
    return float(cleaned)

def validate_record(raw_record: dict) -> tuple[Optional[dict], Optional[str]]:    
    try:
        price_gbp = normalize_price(raw_record.get("price_text"))
        
        book = BookRecord(
            title = raw_record.get("title"),
            product_url = raw_record.get("product_url"),
            price_text = raw_record.get("price_text"),
            price_gbp = price_gbp,
            availability_text = raw_record.get("availability_text"),
            rating_text = raw_record.get("rating_text"),
            description = raw_record.get("description"),
            source_page = raw_record.get("source_page"),
            fetched_at = raw_record.get("fetched_at"),
        )
        clean_dict = json.loads(book.model_dump_json())
        return clean_dict , None
        
    except (ValidationError, ValueError, TypeError) as e:
        return None, str(e)
        
def validate_and_store(raw_records: list[dict]) -> dict:
    valid_records_by_url = {}
    error_records = {}
    
    for raw_record in raw_records:
        clean_record, error_reason = validate_record(raw_record)
    
        if clean_record is not None:
            canonical_url = clean_record["product_url"]
            valid_records_by_url[canonical_url] = clean_record
        else:
            error_records.append({
                "raw_record": raw_record,
                "reason": error_reason,
            })
            
    valid_records = list(valid_records_by_url.values())
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(BOOKS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2, ensure_ascii=False)

    with open(ERRORS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(error_records, f, indent=2, ensure_ascii=False)

    return {
        "valid_count": len(valid_records),
        "error_count": len(error_records),
    }

if __name__ == "__main__":
    from discover_links import discover_all_book_urls
    from extract_books import extract_all_books

    unique_urls, pages_visited, source_page_map = discover_all_book_urls(max_pages=3)
    raw_records = extract_all_books(unique_urls, source_page_map)

    result = validate_and_store(raw_records)

    print(f"\nvalid_records={result['valid_count']}")
    print(f"error_records={result['error_count']}")
    print(f"\nSaved to: {BOOKS_JSON_PATH}")
    print(f"Saved to: {ERRORS_JSON_PATH}")

