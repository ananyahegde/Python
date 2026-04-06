import httpx
import asyncio
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "http://books.toscrape.com/catalogue/"
TOTAL_PAGES = 50

def get_all_urls():
    return [f"{BASE_URL}page-{i}.html" for i in range(1, TOTAL_PAGES + 1)]

async def fetch(client, url, pbar):
    try:
        r = await client.get(url)
        r.raise_for_status()
        pbar.update(1)
        pbar.refresh()
        return r.text
    except httpx.HTTPError as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None

async def scrape_all_async():
    urls = get_all_urls()
    results = []

    async with httpx.AsyncClient() as client:
        with tqdm(total=TOTAL_PAGES, desc="Scraping pages", leave=True) as pbar:
            tasks = [fetch(client, url, pbar) for url in urls]
            pages = await asyncio.gather(*tasks)

    for html in pages:
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            items = soup.find("ol", class_="row").find_all("li")
            results.extend(items)

    return results

def scrape_all():
    return asyncio.run(scrape_all_async())
