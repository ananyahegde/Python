import asyncio
import argparse
import time
import aiohttp

from graph import CrawlGraph
from fetcher import fetch
from parser import extract_links, normalize, same_domain
from robot import RobotsCache
from reporter import print_report
from exporter import export


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", required=True)
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--concurrency", type=int, default=10)
    return parser.parse_args()


def log_result(result, depth):
    if result.error:
        print(f"[DEPTH {depth}] {result.url}  ERROR  {result.error}")
    elif result.redirect_chain:
        chain = " -> ".join(result.redirect_chain)
        print(f"[DEPTH {depth}] {result.url}  -> {chain}")
    elif result.status == 200:
        print(f"[DEPTH {depth}] {result.url}  OK  {result.elapsed}s")
    elif result.status == 404:
        print(f"[DEPTH {depth}] {result.url}  NOT FOUND")
    else:
        print(f"[DEPTH {depth}] {result.url}  {result.status}")


async def crawl(seed: str, max_depth: int, concurrency: int):
    graph = CrawlGraph()
    robots = RobotsCache()
    sem = asyncio.Semaphore(concurrency)

    print("=== Crawl Started ===")
    print(f"[INFO] Seed: {seed}")
    print(f"[INFO] Max depth: {max_depth} | Concurrency: {concurrency} | Respecting robots.txt: YES")

    normalized_seed = normalize(seed)
    graph.mark_queued(normalized_seed)
    queue = asyncio.Queue()
    queue.put_nowait((normalized_seed, 0))

    start = time.monotonic()

    connector = aiohttp.TCPConnector(limit=concurrency)
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        await robots.fetch(session, normalized_seed)

        async def worker(url, depth):
            async with sem:
                if not robots.allowed(url):
                    graph.skip_robots(url)
                    return

                result, html = await fetch(session, url, depth)
                graph.mark_visited(url, result)
                log_result(result, depth)

                if result.status == 200 and depth < max_depth:
                    links = extract_links(html, url)
                    same_domain_links = [l for l in links if same_domain(l, seed)]
                    graph.add_links(url, same_domain_links)

                    for link in same_domain_links:
                        if graph.mark_queued(link):
                            await robots.fetch(session, link)
                            queue.put_nowait((link, depth + 1))
                else:
                    graph.add_links(url, [])

        while not queue.empty():
            batch = []
            while not queue.empty():
                batch.append(queue.get_nowait())

            await asyncio.gather(*[worker(url, depth) for url, depth in batch])

    elapsed = time.monotonic() - start
    print_report(graph, elapsed)
    export(graph)


def main():
    args = parse_args()
    asyncio.run(crawl(args.seed, args.depth, args.concurrency))


if __name__ == "__main__":
    main()
