from urllib.parse import urljoin, urlparse, urlunparse


def extract_links(html: str, base_url: str) -> list[str]:
    """Extract all links from HTML"""
    from html.parser import HTMLParser

    class LinkParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                attrs = dict(attrs)
                href = attrs.get("href")
                if href:
                    self.links.append(href)

    lp = LinkParser()
    lp.feed(html)

    normalized = []
    for href in lp.links:
        url = normalize(urljoin(base_url, href))
        if url:
            normalized.append(url)

    return list(set(normalized))


def normalize(url: str) -> str | None:
    """Normalize URL: lowercase scheme/domain, strip trailing slash and fragment."""
    try:
        p = urlparse(url)
        if p.scheme not in ("http", "https"):
            return None
        normalized = urlunparse((
            p.scheme.lower(),
            p.netloc.lower(),
            p.path.rstrip("/") or "/",
            "",
            p.query,
            "",
        ))
        return normalized
    except Exception:
        return None


def same_domain(url: str, seed: str) -> bool:
    return urlparse(url).netloc == urlparse(seed).netloc
