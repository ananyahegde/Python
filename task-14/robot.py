from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import aiohttp


class RobotsCache:
    def __init__(self, user_agent: str = "PyCrawler"):
        self.user_agent = user_agent
        self._cache: dict[str, RobotFileParser] = {}

    async def fetch(self, session: aiohttp.ClientSession, base_url: str):
        domain = self._domain(base_url)
        if domain in self._cache:
            return
        robots_url = f"{domain}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        try:
            async with session.get(robots_url) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    rp.parse(text.splitlines())
                else:
                    rp.parse([])
        except Exception:
            rp.parse([])
        self._cache[domain] = rp

    def allowed(self, url: str) -> bool:
        domain = self._domain(url)
        rp = self._cache.get(domain)
        if rp is None:
            return True
        return rp.can_fetch(self.user_agent, url)

    def _domain(self, url: str) -> str:
        p = urlparse(url)
        return f"{p.scheme}://{p.netloc}"
