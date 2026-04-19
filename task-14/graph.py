from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PageResult:
    """data container for fetched URL"""
    url: str
    status: int
    depth: int
    elapsed: float
    redirect_chain: list[str] = field(default_factory=list)
    error: Optional[str] = None


class CrawlGraph:
    """
    Tracks crawl state: visited/queued URLs, link graph, inbound counts,
    robots.txt skips, and duplicates.
    """

    def __init__(self):
        self.visited: set[str] = set()
        self.queued: set[str] = set()
        self.results: dict[str, PageResult] = {}
        self.adjacency: dict[str, list[str]] = {}
        self.inbound_count: dict[str, int] = {}
        self.skipped_robots: list[str] = []
        self.duplicate_count: int = 0

    def mark_queued(self, url: str) -> bool:
        if url in self.queued or url in self.visited:
            self.duplicate_count += 1
            return False
        self.queued.add(url)
        return True

    def mark_visited(self, url: str, result: PageResult):
        self.visited.add(url)
        self.queued.discard(url)
        self.results[url] = result

    def add_links(self, from_url: str, to_urls: list[str]):
        self.adjacency[from_url] = to_urls
        for url in to_urls:
            self.inbound_count[url] = self.inbound_count.get(url, 0) + 1

    def skip_robots(self, url: str):
        self.skipped_robots.append(url)

    def get_orphans(self) -> list[str]:
        """
        Pages with zero inbound links from other crawled pages.
        """
        orphans = []
        for url in self.visited:
            if self.inbound_count.get(url, 0) == 0:
                orphans.append(url)
        return orphans

    def get_broken_links(self) -> dict[str, list[str]]:
        """
        A broken link is any URL with status 404.
        Store broken links with referrers.
        """
        broken: dict[str, list[str]] = {}
        for result in self.results.values():
            if result.status == 404:
                broken[result.url] = []

        for from_url, to_urls in self.adjacency.items():
            for to_url in to_urls:
                if to_url in broken:
                    broken[to_url].append(from_url)
        return broken

    def get_redirects(self) -> list[tuple[str, list[str]]]:
        """
        Returns list of (original_url, redirect_chain) for all redirected pages.
        """
        redirects = []
        for result in self.results.values():
            if result.redirect_chain:
                redirects.append((result.url, result.redirect_chain))
        return redirects

    @property
    def pages_crawled(self) -> int:
        return len(self.visited)

    @property
    def unique_urls_found(self) -> int:
        all_urls = set(self.visited)
        all_urls.update(self.queued)
        all_urls.update(self.skipped_robots)
        return len(all_urls)
