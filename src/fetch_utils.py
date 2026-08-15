import os
import time
import requests

USER_AGENT = "FlyRankInternshipA9/1.0 (https://github.com/Anujakhatri/polite-scraper)"
TIMEOUT_SECONDS =10
REQUEST_DELAY_SECONDS = 0.5

CACHE_DIR = os.path.join(os.path.dirname(__file__),"..", "cache")

def _cache_path(cache_filename: str) -> str:
    return os.path.join(CACHE_DIR, cache_filename)

def fetch_page(url: str, cache_filename: str) -> str:
    path = _cache_path(cache_filename)
    
    #1. check if it's in cache
    if os.path.exists(path):
        with open(path, "r", encoding = "utf-8") as f:
            html = f.read()
        print(f"CACHE HIT | {cache_filename} | size={len(html)} bytes")
        return html
    
    #2. if it's not in cache then send a real request
    headers = { "User-Agent": USER_AGENT }
    
    response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
    response.encoding = "utf-8"
    
    #3. if it's not 200, then throw an error()
    if response.status_code != 200: 
        raise RuntimeError(
            f"Fetch Failed | {url} | status= {response.status_code}"
        )
    
    html = response.text
    
    #4. create a folder cache and save html in it.
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"FETCH      | {cache_filename} | size={len(html)} bytes | status={response.status_code}")
    
    #5. add a politeness delay
    time.sleep(REQUEST_DELAY_SECONDS)
    
    return html

if __name__ == "__main__":
    url = "https://books.toscrape.com/catalogue/page-1.html"
    #Checkpoint test: first page
    html = fetch_page(url, "catalogue-page-1.html")
    print(f"\nDone. Total HTML length: {len(html)} characters.")