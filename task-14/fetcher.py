import time
import aiohttp
from graph import PageResult


async def fetch(session: aiohttp.ClientSession, url: str, depth: int) -> tuple[PageResult, str]:
    start = time.monotonic()
    redirect_chain = []
    html = ""

    try:
        async with session.get(url, allow_redirects=True) as resp:
            history = resp.history
            if history:
                redirect_chain = [str(r.url) for r in history] + [str(resp.url)]

            elapsed = time.monotonic() - start
            status = resp.status

            if status == 200:
                html = await resp.text(errors="replace")

            result = PageResult(
                url=url,
                status=status,
                depth=depth,
                elapsed=round(elapsed, 2),
                redirect_chain=redirect_chain,
            )
            return result, html

    except aiohttp.ClientError as e:
        elapsed = time.monotonic() - start
        result = PageResult(
            url=url,
            status=-1,
            depth=depth,
            elapsed=round(elapsed, 2),
            error=str(e),
        )
        return result, html
