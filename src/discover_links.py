#find all 3 pages
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from fetch_utils import fetch_page

CATALOGUE_START_URL = "https://books.toscrape.com/catalogue/page-1.html"


def extract_book_links(html: str, page_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []

    # Every book is inside "article.product_pod" tag
    for article in soup.select("article.product_pod"):
        a_tag = article.select_one("h3 a")
        if a_tag and a_tag.get("href"):
            relative_url = a_tag["href"]
            # Relative URL ("a-light-in-the-attic_1000/index.html") to
            # absolute URL ma convert garne - string glue GARDAINA
            absolute_url = urljoin(page_url, relative_url)
            links.append(absolute_url)

    return links


def find_next_page_url(html: str, page_url: str) -> str | None:
  
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")

    if next_link and next_link.get("href"):
        return urljoin(page_url, next_link["href"])

    return None


def discover_all_book_urls(max_pages: int | None = None) -> tuple[list[str], int, dict]:
    all_links = []
    source_page_map = {}
    current_url = CATALOGUE_START_URL
    page_number = 1
    
    while current_url is not None:
        if max_pages is not None and page_number > max_pages:
            break
        
        cache_filename = f"catalogue-page-{page_number}.html"
        html = fetch_page(current_url, cache_filename)
        
        page_links = extract_book_links(html, current_url)
        all_links.extend(page_links)
        
        for link in page_links:
            if link not in source_page_map:
                source_page_map[link] = current_url
        
        current_url = find_next_page_url(html, current_url)
        page_number += 1
    
    unique_links = list(dict.fromkeys(all_links))
    return unique_links, page_number - 1, source_page_map


if __name__ == "__main__":
    unique_urls, pages_visited, source_page_map = discover_all_book_urls(max_pages=3)

    print(f"\ncatalogue_pages={pages_visited}")
    print(f"discovered={len(unique_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    print("\nFirst 3 URLs (sample):")
    for url in unique_urls[:3]:
        print(f"  - {url}")