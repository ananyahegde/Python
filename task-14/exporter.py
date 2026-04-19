import json
import os
from datetime import datetime
from graph import CrawlGraph


def export(graph: CrawlGraph, out_dir: str = "output"):
    os.makedirs(out_dir, exist_ok=True)
    _export_json(graph, out_dir)
    _export_sitemap(graph, out_dir)


def _export_json(graph: CrawlGraph, out_dir: str):
    path = os.path.join(out_dir, "crawl_graph.json")
    data = {
        "pages": {
            url: {
                "status": r.status,
                "depth": r.depth,
                "elapsed": r.elapsed,
                "redirect_chain": r.redirect_chain,
                "error": r.error,
            }
            for url, r in graph.results.items()
        },
        "adjacency": graph.adjacency,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nCrawl graph saved to: {path}")


def _export_sitemap(graph: CrawlGraph, out_dir: str):
    path = os.path.join(out_dir, "sitemap.xml")
    now = datetime.utcnow().strftime("%Y-%m-%d")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url, result in graph.results.items():
        if result.status == 200:
            lines.append(f"  <url>")
            lines.append(f"    <loc>{url}</loc>")
            lines.append(f"    <lastmod>{now}</lastmod>")
            lines.append(f"  </url>")
    lines.append("</urlset>")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"Site map saved to:    {path}")
