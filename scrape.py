#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                  AynaOTT Live TV Scraper                       ║
║                  Developer: Kobir Shah                         ║
║                  Version: 2.0.0                                ║
║                  License: MIT                                  ║
╚══════════════════════════════════════════════════════════════════╝

Scrapes all live TV channels from AynaOTT platform.
Generates M3U playlist and JSON database with full metadata.
Auto-runs every 6 hours via GitHub Actions.
"""

import urllib.request
import ssl
import json
import time
import os
import sys
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════

BASE_URL = "https://web.aynaott.com"
TENANT_ID = "019dd92f-107c-7056-9e79-e5233f6e51d9"
BLOCK_ID = "019efa5d-2eb7-7ac1-a880-647e38ba7141"

MAX_WORKERS = 15
REQUEST_TIMEOUT = 15
RETRY_COUNT = 3
RETRY_DELAY = 2

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"

OUTPUT_DIR = Path(__file__).parent / "output"
M3U_FILE = OUTPUT_DIR / "aynaott_live.m3u"
JSON_FILE = OUTPUT_DIR / "aynaott_live.json"

# ══════════════════════════════════════════════════════════════════
# SSL CONTEXT
# ══════════════════════════════════════════════════════════════════

def make_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

SSL_CTX = make_ssl_context()

# ══════════════════════════════════════════════════════════════════
# HTTP HELPERS
# ══════════════════════════════════════════════════════════════════

def fetch_json(url, retries=RETRY_COUNT):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "X-Tenant-Id": TENANT_ID
    }
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=REQUEST_TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt < retries:
                time.sleep(RETRY_DELAY * attempt)
    return None

# ══════════════════════════════════════════════════════════════════
# SCRAPER CORE
# ══════════════════════════════════════════════════════════════════

def get_all_channels():
    all_slugs = {}
    page = 1

    while True:
        url = f"{BASE_URL}/api/v5/catalog/contents?type=live-tvs&per_page=100&page={page}"
        data = fetch_json(url)
        if not data:
            break

        records = data.get("records", [])
        if not records:
            break

        for ch in records:
            slug = ch.get("slug", "")
            if slug and slug not in all_slugs:
                all_slugs[slug] = ch

        if len(records) < 100:
            break
        page += 1
        if page > 100:
            break

    return all_slugs


def fetch_channel_stream(slug, channel_data):
    title = channel_data.get("title", "Unknown")
    ch_id = channel_data.get("id", "")
    thumbnail = channel_data.get("images", {}).get("thumbnail_url", "")
    access = channel_data.get("access", {}).get("level", "free")
    description = channel_data.get("description", "")

    if thumbnail and not thumbnail.startswith("http"):
        thumbnail = f"{BASE_URL}{thumbnail}"

    url = f"{BASE_URL}/api/v5/browse/live-tvs/{slug}"
    data = fetch_json(url)
    if not data:
        return None

    rec = data.get("record", data)
    stream = rec.get("stream", {})
    stream_url = ""

    if isinstance(stream, dict):
        stream_url = stream.get("url", "")

    if not stream_url:
        for key in ["stream_url", "hls", "dash", "m3u8", "mpd"]:
            if rec.get(key):
                stream_url = rec[key]
                break

    if not stream_url:
        return None

    # Extract category from taxonomies
    taxonomies = rec.get("taxonomies", {})
    categories = []
    if isinstance(taxonomies, dict):
        cat_list = taxonomies.get("category", [])
        if isinstance(cat_list, list):
            categories = [c.get("title", "") for c in cat_list if isinstance(c, dict)]

    return {
        "id": ch_id,
        "slug": slug,
        "title": title,
        "description": description,
        "logo": thumbnail,
        "stream_url": stream_url,
        "access_level": access,
        "categories": categories,
        "nav_path": f"{BASE_URL}/live-tvs/{slug}"
    }


def scrape_all():
    print(f"[{timestamp()}] Starting AynaOTT scraper...")

    # Step 1: Get all channel slugs
    all_slugs = get_all_channels()
    print(f"[{timestamp()}] Found {len(all_slugs)} unique channels")

    if not all_slugs:
        print(f"[{timestamp()}] ERROR: No channels found!")
        return []

    # Step 2: Fetch stream URLs in parallel
    results = []
    slugs = list(all_slugs.keys())

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_channel_stream, slug, data): slug
            for slug, data in all_slugs.items()
        }
        done = 0
        for future in as_completed(futures):
            done += 1
            result = future.result()
            if result:
                results.append(result)
            if done % 50 == 0:
                print(f"[{timestamp()}] Progress: {done}/{len(slugs)} ({len(results)} streams)")

    print(f"[{timestamp()}] Scraping complete: {len(results)} streams found")
    return results


# ══════════════════════════════════════════════════════════════════
# OUTPUT GENERATORS
# ══════════════════════════════════════════════════════════════════

def timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def generate_m3u(channels):
    now = timestamp()
    lines = [
        "#EXTM3U",
        f"# Generated: {now}",
        f"# Developer: Kobir Shah",
        f"# Source: https://github.com/MohammadKobirShah/aynaott-m3u",
        f"# Total Channels: {len(channels)}",
        "",
    ]

    for ch in sorted(channels, key=lambda x: x["title"]):
        tag = " [PAID]" if ch["access_level"] == "subscription" else ""
        lines.append(
            f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["title"]}" '
            f'tvg-logo="{ch["logo"]}" '
            f'group-title="{", ".join(ch["categories"]) if ch["categories"] else "Live TV"}"'
            f',{ch["title"]}{tag}'
        )
        lines.append(ch["stream_url"])
        lines.append("")

    return "\n".join(lines)


def generate_json(channels):
    now = timestamp()
    free_count = sum(1 for ch in channels if ch["access_level"] == "free")
    paid_count = sum(1 for ch in channels if ch["access_level"] == "subscription")

    all_categories = set()
    for ch in channels:
        for cat in ch["categories"]:
            all_categories.add(cat)

    data = {
        "metadata": {
            "title": "AynaOTT Live TV Playlist",
            "description": "Auto-generated M3U/JSON playlist from AynaOTT platform",
            "developer": "Kobir Shah",
            "github": "https://github.com/MohammadKobirShah/aynaott-m3u",
            "version": "2.0.0",
            "license": "MIT",
            "generated_at": now,
            "source_url": BASE_URL,
            "tenant_id": TENANT_ID,
        },
        "stats": {
            "total_channels": len(channels),
            "free_channels": free_count,
            "paid_channels": paid_count,
            "categories": sorted(list(all_categories)),
            "total_categories": len(all_categories),
        },
        "channels": channels,
    }

    return json.dumps(data, indent=2, ensure_ascii=False)


def save_outputs(channels):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save M3U
    m3u_content = generate_m3u(channels)
    M3U_FILE.write_text(m3u_content, encoding="utf-8")
    print(f"[{timestamp()}] Saved M3U: {M3U_FILE} ({len(channels)} channels)")

    # Save JSON
    json_content = generate_json(channels)
    JSON_FILE.write_text(json_content, encoding="utf-8")
    print(f"[{timestamp()}] Saved JSON: {JSON_FILE}")

    return True


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  AynaOTT Live TV Scraper v2.0.0")
    print("  Developer: Kobir Shah")
    print("  GitHub: https://github.com/MohammadKobirShah/aynaott-m3u")
    print("=" * 60)
    print()

    start_time = time.time()
    channels = scrape_all()

    if channels:
        save_outputs(channels)
        elapsed = time.time() - start_time
        print()
        print(f"[{timestamp()}] Done in {elapsed:.1f}s")
        print(f"[{timestamp()}] Total: {len(channels)} channels")
        print(f"[{timestamp()}] Free: {sum(1 for c in channels if c['access_level'] == 'free')}")
        print(f"[{timestamp()}] Paid: {sum(1 for c in channels if c['access_level'] == 'subscription')}")
    else:
        print(f"[{timestamp()}] ERROR: No channels scraped!")
        sys.exit(1)


if __name__ == "__main__":
    main()
