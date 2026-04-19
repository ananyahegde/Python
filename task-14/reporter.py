from graph import CrawlGraph


def print_report(graph: CrawlGraph, elapsed: float):
    print(f"\n=== Crawl Complete ({elapsed:.1f}s) ===")
    print(f"Pages crawled:      {graph.pages_crawled}")
    print(f"Unique URLs found:  {graph.unique_urls_found}")
    print(f"Skipped (robots):   {len(graph.skipped_robots)}")
    print(f"Duplicates avoided: {graph.duplicate_count}")

    print("\n=== SEO Audit Report ===")

    broken = graph.get_broken_links()
    print(f"\nBroken Links (404):")
    if broken:
        for url, referrers in broken.items():
            refs = ", ".join(referrers) if referrers else "unknown"
            print(f"  - {url} (linked from: {refs})")
    else:
        print("  None")

    redirects = graph.get_redirects()
    print(f"\nRedirect Chains (301/302):")
    if redirects:
        for original, chain in redirects:
            hops = len(chain) - 1
            path = " -> ".join(chain)
            note = " (consider fixing)" if hops > 1 else ""
            print(f"  - {path} ({hops} hop{'s' if hops > 1 else ''}{note})")
    else:
        print("  None")

    orphans = graph.get_orphans()
    print(f"\nOrphan Pages (no inbound links):")
    if orphans:
        for url in orphans:
            print(f"  - {url}")
    else:
        print("  None")
