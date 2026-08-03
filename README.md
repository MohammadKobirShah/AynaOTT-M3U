# AynaOTT Live TV Scraper

<div align="center">

```
╔══════════════════════════════════════════════════════════════╗
║           AynaOTT Live TV M3U Playlist Scraper              ║
║                  Auto-Updated Every 6 Hours                 ║
╚══════════════════════════════════════════════════════════════╝
```

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Auto-Update](https://img.shields.io/badge/Auto%20Update-Every%206%20Hours-orange?style=flat-square)
![Channels](https://img.shields.io/badge/Channels-240%2B-red?style=flat-square)

</div>

---

## Features

- **Auto-Updates**: Scrapes AynaOTT every 6 hours via GitHub Actions
- **Dual Format**: Outputs both M3U and JSON formats
- **Full Metadata**: Channel ID, name, logo, categories, access level
- **Parallel Scraping**: 15 concurrent threads for fast extraction
- **Free & Paid**: Includes both free and subscription channels
- **Zero Dependencies**: Uses only Python standard library

---

## Quick Start

### M3U Playlist (Direct Use)

```
https://raw.githubusercontent.com/MohammadKobirShah/aynaott-m3u/main/output/aynaott_live.m3u
```

### JSON Database

```
https://raw.githubusercontent.com/MohammadKobirShah/aynaott-m3u/main/output/aynaott_live.json
```

### Use in IPTV Players

| Player | Platform |
|--------|----------|
| OTT Navigator | Android |
| TiviMate | Android |
| IPTV Smarters | Android/iOS |
| Kodi | All |
| VLC | All |
| Plex | All |

---

## Usage

### Run Locally

```bash
# Clone the repo
git clone https://github.com/MohammadKobirShah/aynaott-m3u.git
cd aynaott-m3u

# Run the scraper
python scrape.py
```

### Output Files

```
output/
├── aynaott_live.m3u    # M3U playlist for IPTV players
└── aynaott_live.json   # JSON database with full metadata
```

---

## JSON Structure

```json
{
  "metadata": {
    "title": "AynaOTT Live TV Playlist",
    "developer": "Kobir Shah",
    "version": "2.0.0",
    "generated_at": "2026-08-03 12:00:00 UTC",
    "source_url": "https://web.aynaott.com"
  },
  "stats": {
    "total_channels": 241,
    "free_channels": 50,
    "paid_channels": 191,
    "categories": ["Bangla", "Hindi", "Sports", "Kids"],
    "total_categories": 15
  },
  "channels": [
    {
      "id": "uuid",
      "slug": "channel-name",
      "title": "Channel Name",
      "logo": "https://...",
      "stream_url": "https://...index.m3u8",
      "access_level": "free|subscription",
      "categories": ["Bangla", "News"]
    }
  ]
}
```

---

## Auto-Update Schedule

| Time (UTC) | Status |
|------------|--------|
| 00:00 | Auto-scrape |
| 06:00 | Auto-scrape |
| 12:00 | Auto-scrape |
| 18:00 | Auto-scrape |

Also supports manual trigger via GitHub Actions.

---

## API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `/api/v5/catalog/contents?type=live-tvs` | List all channels |
| `/api/v5/browse/live-tvs/{slug}` | Get stream URL |
| `/api/v5/app/config` | Tenant configuration |

---

## Project Structure

```
aynaott-m3u/
├── .github/
│   └── workflows/
│       └── scrape.yml          # GitHub Actions (auto-update)
├── output/
│   ├── aynaott_live.m3u        # Generated M3U playlist
│   └── aynaott_live.json       # Generated JSON database
├── scrape.py                   # Main scraper script
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
└── README.md                   # This file
```

---

## Stats

| Metric | Value |
|--------|-------|
| Total Channels | 240+ |
| Free Channels | ~50 |
| Paid Channels | ~190 |
| Categories | 15+ |
| Languages | Bangla, Hindi, English, Tamil, Telugu, Malayalam, Kannada |
| Update Frequency | Every 6 hours |
| Avg Scrape Time | ~30 seconds |

---

## Credits

<div align="center">

**Developer: [Kobir Shah](https://github.com/MohammadKobirShah)**

Built with dedication and late-night coffee sessions.

---

**Disclaimer**: This project is for educational purposes only.
The developer is not responsible for any misuse of this tool.
All channel streams belong to their respective owners.

---

</div>

## License

MIT License - See [LICENSE](LICENSE) for details.

---

<div align="center">

**If this project helps you, give it a star!**

</div>
